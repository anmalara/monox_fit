from ROOT import *
import math
import os
import numpy as np
from math import sqrt, pow
from array import array
from tdrStyle import *
import sys
import re
DIR=os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(DIR,"../makeWorkspace")))

from parameters import flat_uncertainties

pjoin = os.path.join

setTDRStyle()

def get_ylims(region1, region2):
    '''Get y-limits for the ratio plots (to fix scale).'''
    if region1 is "combined" and region2 is "gjets":
        return (0,0.4)
    elif region1 is "combined" and region2 is "combinedW":
        return (0,0.2)
    elif region1 is "dielectron" and region2 is "gjets":
        return (0,0.2)
    elif region1 is "dimuon" and region2 is "gjets":
        return (0,0.2)
    elif region1 is "combinedW" and region2 is "gjets":
        return (0,5)
    elif region1 is "singleelectron" and region2 is "gjets":
        return (0,2)
    elif region1 is "singlemuon" and region2 is "gjets":
        return (0,2.5)
    elif region1 is "dielectron" and region2 is "singleelectron":
        return (0,0.3)
    elif region1 is "dimuon" and region2 is "singlemuon":
        return (0,0.3)
        
    raise RuntimeError('Could not determine y-limits.')

def quadsum(*args):
    """Quadratic sum"""
    return sqrt(sum([x**2 for x in args]))


def dataValidation(region1,region2,category,ws_file, fitdiag_file, outdir, lumi, year):

    if region1 is "combined" and region2 is "gjets":
        name = "Z(ll)+jets / #gamma+jets"
    if region1 is "combined" and region2 is "combinedW":
        name = "Z(ll)+jets / W(l#nu)+jets"
    if region1 is "dielectron" and region2 is "gjets":
        name = "Z(ee)/#gamma"
    if region1 is "dimuon" and region2 is "gjets":
        name = "Z(mm)/#gamma"
    if region1 is "combinedW" and region2 is "gjets":
        name = "W(l#nu)+jets / #gamma+jets"
    if region1 is "singleelectron" and region2 is "gjets":
        name = "W(en)/#gamma"
    if region1 is "singlemuon" and region2 is "gjets":
        name = "W(mn)/#gamma"
    if region1 is "dielectron" and region2 is "singleelectron":
        name = "Z(ee)/W(en)"
    if region1 is "dimuon" and region2 is "singlemuon":
        name = "Z(mm)/W(mn)"


    if region1 is "dimuon" and region2 is "dielectron":
        name = "Z(mm)/Z(ee)"
    if region1 is "singlemuon" and region2 is "singleelectron":
        name = "W(mn)/W(en)"

    datalab = {"singlemuon":"Wmn", "dimuon":"Zmm", "gjets":"gjets", "signal":"signal", "singleelectron":"Wen", "dielectron":"Zee"}

    f_data = TFile(ws_file,"READ")
    f_data.cd("category_"+category)

    if region1 is "combined":
        h_data_1 = gDirectory.Get("Zmm_data")
        h_data_1_b = gDirectory.Get("Zee_data")
        h_data_1.Add(h_data_1_b)
    elif region1 is "combinedW":
        h_data_1 = gDirectory.Get("Wmn_data")
        h_data_1_b = gDirectory.Get("Wen_data")
        h_data_1.Add(h_data_1_b)

    else:
        h_data_1 = gDirectory.Get(datalab[region1]+"_data")
    h_data_1.Sumw2()
    if "monojet" in category:
        h_data_1.Rebin(2)

    if region2 is "combinedW":
        h_data_2 = gDirectory.Get("Wmn_data")
        h_data_2_b = gDirectory.Get("Wen_data")
        h_data_2.Add(h_data_2_b)
    else:
        h_data_2 = gDirectory.Get(datalab[region2]+"_data")

    h_data_2.Sumw2()
    if "monojet" in category:
        h_data_2.Rebin(2)

    h_data_1.Divide(h_data_2)

    f_mlfit = TFile(fitdiag_file,'READ')

    def get_shape(region, process):
        """Helper function to easily retrieve histograms from diagnostics file"""
        return f_mlfit.Get("shapes_prefit/"+category+"_"+region+"/" + process)

    def get_shape_sum(regions, process):
        """Helper function to get sum of shapes for different regions"""
        histos = [get_shape(x, process) for x in regions]
        h = histos[0]
        for ih in histos[1:]:
            h.Add(ih)
        return h

    channel = {"singlemuon":"singlemu", "dimuon":"dimuon", "gjets":"photon", "signal":"signal", "singleelectron":"singleel", "dielectron":"dielec"}
    leadbg = {"singlemuon":"wjets", "dimuon":"zll", "gjets":"gjets", "singleelectron":"wjets", "dielectron":"zll"}

    h_prefit = {}
    h_qcd_prefit = {}
    h_ewk_prefit = {}

    ### Step 1: Read prefit histogram
    for region in [region1, region2]:
        if region is "combined":
            regions_to_retrieve = ["dimuon","dielec"]
            h_prefit[region] = get_shape_sum(regions_to_retrieve,"total_background")

            if "vbf" in category:
                h_qcd_prefit[region] = get_shape_sum(regions_to_retrieve, "qcd_zll")
                h_ewk_prefit[region] = get_shape_sum(regions_to_retrieve, "ewk_zll")
        elif region is "combinedW":
            regions_to_retrieve = ["singlemu","singleel"]
            h_prefit[region] = get_shape_sum(regions_to_retrieve,"total_background")
            if "vbf" in category:
                h_qcd_prefit[region] = get_shape_sum(regions_to_retrieve,"qcd_wjets")
                h_ewk_prefit[region] = get_shape_sum(regions_to_retrieve,"ewk_wjets")
        elif region == 'gjets':
            h_prefit[region] = get_shape("photon", "total_background")
            if "vbf" in category:
                h_qcd_prefit[region] = get_shape("photon", "qcd_gjets")
                h_ewk_prefit[region] = get_shape("photon", "ewk_gjets")
        else:
            h_prefit[region] = get_shape(channel[region],"total_background")
            if "vbf" in category:

                h_qcd_prefit[region] = get_shape(channel[region], "qcd_"+leadbg[region])
                h_ewk_prefit[region] = get_shape(channel[region], "ewk_"+leadbg[region])
        h_prefit[region].Sumw2()

        if "monojet" in category:
            h_prefit[region].Rebin(2)

    h_prefit[region1].Divide(h_prefit[region2])
    if "mono" in category:
        if region2 is "gjets":
            uncFile     = TFile(os.path.join(DIR,'../makeWorkspace/sys/theory_unc_ZG.root'))
            uncertainties = [
                uncFile.ZG_QCDScale_met,
                uncFile.ZG_QCDShape_met,
                uncFile.ZG_QCDProcess_met,
                uncFile.ZG_NNLOEWK_met,
                uncFile.ZG_Sudakov1_met,
                uncFile.ZG_Sudakov2_met,
                uncFile.ZG_NNLOMiss1_met,
                uncFile.ZG_NNLOMiss2_met,
                uncFile.ZG_MIX_met,
                uncFile.ZG_PDF_met,
                ]
            uncFile_photon = TFile(os.path.join(DIR,'../makeWorkspace/sys/photon_id_unc.root'))
            if 'monojet' in category:
                if year == 2017:
                    uncertainties.append(uncFile_photon.monojet_2017_photon_id_extrap_up)
                    uncertainties.append(uncFile_photon.monojet_2017_photon_id_up)
                elif year == 2018:
                    uncertainties.append(uncFile_photon.monojet_2018_photon_id_extrap_up)
                    uncertainties.append(uncFile_photon.monojet_2018_photon_id_up)
            elif 'monov' in category:
                if year == 2017:
                    uncertainties.append(uncFile_photon.monov_2017_photon_id_extrap_up)
                    uncertainties.append(uncFile_photon.monov_2017_photon_id_up)
                elif year == 2018:
                    uncertainties.append(uncFile_photon.monov_2018_photon_id_extrap_up)
                    uncertainties.append(uncFile_photon.monov_2018_photon_id_up)
        else:
            uncFile     = TFile(os.path.join(DIR,'../makeWorkspace/sys/theory_unc_ZW.root'))
            uncertainties = [
                uncFile.ZW_QCDScale_met,
                uncFile.ZW_QCDShape_met,
                uncFile.ZW_QCDProcess_met,
                uncFile.ZW_NNLOEWK_met,
                uncFile.ZW_Sudakov1_met,
                uncFile.ZW_Sudakov2_met,
                uncFile.ZW_NNLOMiss1_met,
                uncFile.ZW_NNLOMiss2_met,
                uncFile.ZW_MIX_met,
                uncFile.ZW_PDF_met
                ]
        uncertainties += ["experiment"]
    
    # Uncertainties on VBF H(inv)
    else:
        uncFile = TFile(os.path.join(DIR,'../makeWorkspace/sys/particlenet/vbf_z_w_gjets_theory_unc_ratio_unc.root'))
        uncertainties = [
            "w_ewkcorr_overz_common",
            "zoverw_nlo_muf",
            "zoverw_nlo_mur",
            "zoverw_nlo_pdf",
            "experiment"
        ]
    #print uncertainties

    regions = (region1, region2)
    for iBin in range(1, h_prefit[region1].GetNbinsX()):
        
        # Bare minimum is the prefit stat unc.
        sumw2 = pow(h_prefit[region1].GetBinError(iBin),2)

        # Systematic uncertainties
        for uncert in uncertainties:

            ### Experimental uncertainties are treated the same for all channes
            if uncert == "experiment":
                # Photon ID / trig
                if "gjets" in regions:
                    value = quadsum(
                                        flat_uncertainties[year]["eff_photrig"],
                                    )
                    sumw2 += pow(h_prefit[region1].GetBinContent(iBin) * value,2)


                one_muon_unc = quadsum(
                        flat_uncertainties[year]["eff_m"],
                        flat_uncertainties[year]["eff_m_iso"],
                        flat_uncertainties[year]["eff_m_reco"],
                    )
                one_electron_unc = quadsum(
                        flat_uncertainties[year]["eff_e"],
                        flat_uncertainties[year]["eff_e_reco"],
                    )
                # Uncertainty representing the average uncertainty associated to 
                # one additional lepton for combined regions
                one_lepton_unc = 1/sqrt(2) * quadsum(
                    one_muon_unc,
                    one_electron_unc
                )

                if regions==("combined","combinedW") or regions==("combinedW","gjets"):
                    value = one_lepton_unc
                elif regions==("combined","gjets"):
                    value = one_lepton_unc*sqrt(2)
                elif regions==("dimuon","singlemuon") or regions == ("singlemuon","gjets"):
                    value = one_muon_unc
                elif regions==("dielectron","singleelectron") or regions==("singleelectron","gjets"):
                    value = one_electron_unc
                elif regions==("dielectron","gjets"):
                    value = one_electron_unc*sqrt(2)
                elif regions==("dimuon","gjets"):
                    value = one_muon_unc*sqrt(2)

                sumw2 += pow(h_prefit[region1].GetBinContent(iBin) * value,2)
            elif 'mono' in category:
                ### Theory uncertainties for monojet / mono-V
                findbin =  uncert.FindBin(h_prefit[region1].GetBinCenter(iBin))
                unc = uncert.GetBinContent(findbin)
                if unc > 0.5:
                    unc = unc - 1
                sumw2 += pow(h_prefit[region1].GetBinContent(iBin) * unc,2)
            elif 'vbf' in category:
                ### Theory uncertainties for VBF
                # For VBF, we calculate the uncertainty separately for EWK and QCD
                # the uncertainty calculated in each iteration is the absolute
                # uncertainty on the absolute spectrum, i.e. not on the ratio!
                # The uncertainty on the ratio is obtained by dividing after summing
                theory_sumw2 = 0
                for proc in ['qcd','ewk']:
                    for direction in 'up','down':
                        # Uncertainties are stored in histogram form
                        hname = "uncertainty_ratio_z_{PROC}_particlenet_score_unc_{UNC}_{DIR}_{YEAR}".format(PROC=proc, UNC=uncert, DIR=direction, YEAR=year)
                        print hname
                        hist_unc = uncFile.Get(hname)

                        # Find the right bin to read uncertainty from
                        findbin = hist_unc.FindBin(h_prefit[region1].GetBinCenter(iBin))

                        # Nominal QCD / EWK V value
                        nom = (h_qcd_prefit if proc=='qcd' else h_ewk_prefit)[region1].GetBinContent(iBin)

                        # Total nominal value
                        nom_tot = h_prefit[region1].GetBinContent(iBin)

                        # Total unc = relative uncertainty * nominal
                        # factor of 0.5 accounts for symmetrizing up/down                        
                        theory_sumw2 += pow( 0.5 * (hist_unc.GetBinContent(findbin)-1) * nom, 2)
                
                # After QCD and EWK have been summed over, we divide by the denominator
                if h_prefit[region2].GetBinContent(iBin)!=0:
                    theory_sumw2 /= pow(h_prefit[region2].GetBinContent(iBin),2)

                # And add to the total: 
                # Don't do this for now since this theory uncertainty file does not apply to DNN score!
                sumw2 += theory_sumw2

        h_prefit[region1].SetBinError(iBin,sqrt(sumw2))


    c = TCanvas("c","c",600,650)
    SetOwnership(c,False)
    #c.SetTopMargin(0.08)

    c.SetBottomMargin(0.3)
    c.SetRightMargin(0.06)

    c.SetLeftMargin(0.15)

    c.cd()

    h_clone = h_prefit[region1].Clone()
    h_clone.SetFillColor(kGray) #SetFillColor(ROOT.kYellow)
    h_clone.SetLineColor(kGray) #SetLineColor(1)
    h_clone.SetLineWidth(1)
    h_clone.SetMarkerSize(0)
    h_clone.GetXaxis().SetTitle("")
    h_clone.GetXaxis().SetLabelSize(0)
    h_clone.GetYaxis().SetTitle(name)
    #h_clone.GetYaxis().CenterTitle()
    h_clone.GetYaxis().SetTitleSize(0.05)
    h_clone.GetYaxis().SetLabelSize(0.04)
    h_clone.GetYaxis().SetTitleOffset(1.50)

    ylims = get_ylims(region1, region2)
    h_clone.GetYaxis().SetRangeUser(*ylims)

    # h_clone.SetMaximum(h_clone.GetMaximum()*2)

    h_clone.Draw("e2")

    # Draw data/data and MC/MC ratios
    h_prefit[region1].SetLineColor(2)
    h_prefit[region1].Draw("samehist")
    h_data_1.SetLineColor(1)
    h_data_1.SetMarkerColor(1)
    h_data_1.SetMarkerStyle(20)
    h_data_1.Draw("same")


    #legend = TLegend(0.35, 0.79, 0.95, .92);

    legend = TLegend(0.35, 0.77, 0.95, 0.90)

    legend.SetFillStyle(0)
    legend.AddEntry(h_data_1, name+" Data", "elp")

    if region2 is 'gjets' and region1 is 'combinedW':
        legend.AddEntry(h_prefit[region1], name+" MC      ", "l")
    elif region2 is 'gjets' and region1 is 'combined':
        legend.AddEntry(h_prefit[region1], name+" MC        ", "l")
    else:
        legend.AddEntry(h_prefit[region1], name+" MC", "l")

    legend.SetShadowColor(0)
    legend.SetFillColor(0)
    legend.SetLineColor(0)
    legend.SetLineStyle(0)
    legend.SetBorderSize(0)
    legend.Draw("same")

    latex2 = TLatex()
    latex2.SetNDC()
    latex2.SetTextSize(0.6*c.GetTopMargin())
    latex2.SetTextFont(42)
    latex2.SetTextAlign(31) # align right
    latex2.DrawLatex(0.94, 0.95,"{LUMI:.1f} fb^{{-1}} (13 TeV)".format(LUMI=lumi))
    latex2.SetTextSize(0.6*c.GetTopMargin())
    latex2.SetTextFont(62)
    latex2.SetTextAlign(11) # align right
    latex2.DrawLatex(0.200, 0.85, "CMS")
    latex2.SetTextSize(0.6*c.GetTopMargin())
    latex2.SetTextFont(52)
    latex2.SetTextAlign(11)
    offset = 0.005
    #latex2.DrawLatex(0.20, 0.80, "Preliminary")

    categoryLabel = TLatex()
    categoryLabel.SetNDC()
    #categoryLabel.SetTextSize(0.5*c.GetTopMargin());
    categoryLabel.SetTextSize(0.042)
    categoryLabel.SetTextFont(42)
    categoryLabel.SetTextAlign(11)
    categoryLabel.DrawLatex(0.200,0.80,re.sub("_.*","",category))
    categoryLabel.Draw("same")


    pad = TPad("pad", "pad", 0.0, 0.0, 1.0, 0.9)
    SetOwnership(pad,False)

    pad.SetTopMargin(0.7)
    pad.SetRightMargin(0.06)
    pad.SetLeftMargin(0.15)
    pad.SetFillColor(0)
    pad.SetGridy(0)

    pad.SetFillStyle(0)
    pad.Draw()
    pad.cd(0)

    # Ratio pad: Data/data ratio
    dummy2 = h_data_1.Clone("dummy")
    dummy2.Sumw2()
    dummy2.Divide(h_prefit[region1])
    #for i in range(1,dummy2.GetNbinsX()):
    #    print dummy2.GetBinContent(i)
    #    dummy2.SetBinContent(i,1.0)

    dummy2.GetYaxis().SetTitle("Data / Pred.")
    dummy2.GetXaxis().SetTitle("Hadronic recoil p_{T} [GeV]" if "mono" in category else "DNN score")
    dummy2.GetXaxis().SetTitleOffset(1.15)
    dummy2.GetXaxis().SetTitleSize(0.05)
    dummy2.GetXaxis().SetLabelSize(0.04)

    #dummy2.SetLineColor(0)
    #dummy2.SetMarkerColor(0)
    #dummy2.SetLineWidth(0)
    #dummy2.SetMarkerSize(0)
    dummy2.GetYaxis().SetLabelSize(0.04)
    dummy2.GetYaxis().SetNdivisions(5)
    #dummy2.GetXaxis().SetNdivisions(510)
    dummy2.GetYaxis().CenterTitle()
    dummy2.GetYaxis().SetTitleSize(0.04)
#    dummy2.GetYaxis().SetLabelSize(0.04)
    dummy2.GetYaxis().SetTitleOffset(1.5)
    dummy2.SetMaximum(1.6)
    dummy2.SetMinimum(0.4)

    dummy2.Draw()
    
    # Systematic uncertainty on the bkg/bkg ratio
    ratiosys = dummy2.Clone("ratiosys")
    for hbin in range(0,ratiosys.GetNbinsX()+1):
        print "RATIOSYS", ratiosys.GetBinError(hbin+1), h_clone.GetBinError(hbin+1), h_data_1.GetBinError(hbin+1)
        ratiosys.SetBinContent(hbin+1,1.0)
        if h_clone.GetBinContent(hbin+1)>0:
            ratiosys.SetBinError(hbin+1,h_clone.GetBinError(hbin+1)/h_clone.GetBinContent(hbin+1))

    ratiosys.SetFillColor(kGray) #SetFillColor(ROOT.kYellow)
    ratiosys.SetLineColor(kGray) #SetLineColor(1)
    ratiosys.SetLineWidth(1)
    ratiosys.SetMarkerSize(0)
    ratiosys.Draw("e2same")

    dummy2.Draw("same")

    f1 = TF1("f1","1",-5000,5000)
    f1.SetLineColor(1)
    f1.SetLineStyle(2)
    f1.SetLineWidth(1)
    f1.Draw("same")

    pad.RedrawAxis("G sameaxis")
    gPad.RedrawAxis()

    #ratiosys.SetFillColor(kGray) #SetFillColor(ROOT.kYellow)
    #ratiosys.SetLineColor(kGray) #SetLineColor(1)
    #ratiosys.SetLineWidth(1)
    #ratiosys.SetMarkerSize(0)
    #ratiosys.Draw("e2same")
    #g_ratio_pre.Draw("epsame")



    if not os.path.exists(outdir):
        os.makedirs(outdir)

    for fformat in ['pdf', 'png']:
        fname = region1+"_"+region2+"_cat_"+category+"_"+str(year)+"ratio.{}".format(fformat)
        c.SaveAs(pjoin(outdir, fname))

    c.Close()
    f_mlfit.Close()
    f_data.Close()
#dataValidation("dielectron","gjets","monojet")
#dataValidation("dimuon"    ,"gjets","monojet")
# ws_file="../monojet/root/ws_monojet_2017.root"
# fitdiag_file = '../monojet/higgsCombineTest.FitDiagnostics.mH120.root'
# dataValidation("combined"  ,  "gjets",  "monojet", ws_file, fitdiag_file)
# dataValidation("combinedW", "gjets"    ,"monojet", ws_file, fitdiag_file)
# dataValidation("combined" , "combinedW","monojet", ws_file, fitdiag_file)



#dataValidation("singlemuon","singleelectron","monojet")
#dataValidation("dimuon","dielectron","monojet")

#dataValidation("singleelectron","gjets","monojet")
#dataValidation("singlemuon","gjets","monojet")

#dataValidation("dielectron","gjets","monojet")
#dataValidation("dimuon","gjets","monojet")
#dataValidation("dielectron","singleelectron","monojet")
#dataValidation("dimuon","singlemuon","monojet")


#dataValidation("dielectron","gjets","monov")
#dataValidation("dimuon"    ,"gjets","monov")
#dataValidation("combined"  ,"gjets","monov")

#dataValidation("combinedW","gjets"    ,"monov")
#dataValidation("combined" ,"combinedW","monov")

#dataValidation("singlemuon","singleelectron","monov")
#dataValidation("dimuon","dielectron","monov")

#dataValidation("singleelectron","gjets","monov")
#dataValidation("singlemuon","gjets","monov")

#dataValidation("dielectron","gjets","monov")
#dataValidation("dimuon","gjets","monov")
#dataValidation("dielectron","singleelectron","monov")
#dataValidation("dimuon","singlemuon","monov")

