import ROOT  # type:ignore
from counting_experiment import *
from utils.jes_utils import get_jes_variations, get_jes_jer_source_file_for_tf
from W_constraints import do_stat_unc, add_variation

# Define how a control region(s) transfer is made by defining *cmodel*, the calling pattern must be unchanged!
# First define simple string which will be used for the datacard
model = "qcd_zjets"


def cmodel(cid, nam, _f, _fOut, out_ws, diag, year, convention="BU"):

    # Some setup
    _fin = _f.Get("category_%s" % cid)
    _wspace = _fin.Get("wspace_%s" % cid)

    # ############################ USER DEFINED ###########################################################
    # First define the nominal transfer factors (histograms of signal/control, usually MC
    # note there are many tools available inside include/diagonalize.h for you to make
    # special datasets/histograms representing these and systematic effects
    # example below for creating shape systematic for photon which is just every bin up/down 30%

    varname = "mjj"  # Observable variable name

    target = _fin.Get("signal_qcdzjets")  # define monimal (MC) of which process this config will model

    control_samples = {
        "qcd_zmm": _fin.Get("Zmm_qcdzll"),  # defines Zmm MC of which process will be controlled by
        "qcd_zee": _fin.Get("Zee_qcdzll"),  # defines Zmm MC of which process will be controlled by
        "qcd_w": _fin.Get("signal_qcdwjets"),
        "ewkqcd": _fin.Get("signal_ewkzjets"),
        "qcd_photon": _fin.Get("gjets_qcdgjets"),  # defines Gjets MC of which process will be controlled by
    }

    # Create the transfer factors and save them (not here you can also create systematic variations of these
    # transfer factors (named with extention _sysname_Up/Down
    transfer_factors = {region: target.Clone() for region in control_samples.keys()}
    for label, sample in transfer_factors.items():
        sample.SetName(f"{label}_weights_{cid}")
        sample.Divide(control_samples[label])
        # Write out a copy to the directory
        _fOut.WriteTObject(sample)

    # my_function(_wspace, _fin, _fOut, cid, diag, year)

    # target = _fin.Get("signal_qcdzjets")  # define monimal (MC) of which process this config will model
    # qcd_w controlmc_w = _fin.Get("signal_qcdwjets")
    # qcd_photon controlmc_photon = _fin.Get("gjets_qcdgjets")

    #################################################################################################################

    #################################################################################################################
    spectrums = {region: control_samples[region].Clone() for region in ["qcd_w", "qcd_photon"]} | {"qcd_zvv": target.Clone()}
    # for region, sample in spectrums.items():
    #    sample.SetName(f"{region}_spectrum_{cid}_")
    spectrums["qcd_w"].SetName(f"qcd_w_spectrum_{cid}_")
    spectrums["qcd_photon"].SetName(f"qcd_gjets_spectrum_{cid}_")

    _fOut.WriteTObject(spectrums["qcd_w"])
    _fOut.WriteTObject(spectrums["qcd_photon"])

    #################################################################################################################

    vbf_sys = r.TFile.Open("sys/vbf_z_w_gjets_theory_unc_ratio_unc.root")

    ratio_label = {"qcd_w": "zoverw", "qcd_photon": "goverz"}
    prefix_label = {"qcd_w": "z", "qcd_photon": "gjets"}

    other_labels1 = {"qcd_w": "ZnunuWJets", "qcd_photon": "Photon"}
    other_labels2 = {"qcd_w": "qcd_ewk", "qcd_photon": "qcd_photon_ewk"}

    def add_var(num, denom, name, factor):
        new = num.Clone(name)
        new.Divide(denom)
        new.Multiply(factor)
        _fOut.WriteTObject(new)

    for region in ["qcd_w", "qcd_photon"]:

        denom = control_samples[region].Clone()
        denom.SetName(f"{region}_weights_denom_{cid}")
        num = target.Clone()
        num.SetName(f"{region}_weights_nom_{cid}")

        prefix = f"uncertainty_ratio_{prefix_label[region]}_qcd_mjj_unc"
        variations = {
            "ewk": "w_ewkcorr_overz_common",
            "mur": f"{ratio_label[region]}_nlo_mur",
            "muf": f"{ratio_label[region]}_nlo_muf",
            "pdf": f"{ratio_label[region]}_nlo_pdf",
        }
        variation_dict = {f"{varname}_up": vbf_sys.Get(f"{prefix}_{varlabel}_up_{year}") for varname, varlabel in variations.items()} | {
            f"{varname}_down": vbf_sys.Get(f"{prefix}_{varlabel}_down_{year}") for varname, varlabel in variations.items()
        }

        # QCD uncertainties
        # qcd_w_weights_vbf_2018_ZnunuWJets_QCD_renscale_vbf_Up
        # qcd_w_weights_Z_constraints_qcd_withphoton_ZnunuWJets_QCD_renscale_vbf_Up
        # CRs[region].add_nuisance_shape(f"{other_label}_QCD_{var}_vbf", _fOut)
        # add_var(num=Zvv_w, denom=Wsig, name="qcd_w_weights_%s_ZnunuWJets_QCD_renscale_vbf_Up" % nam, factor=uncertainty_zoverw_mur_up)
        add_var(num=num, denom=denom, name=f"{region}_weights_{cid}_{other_labels1[region]}_QCD_renscale_vbf_Up", factor=variation_dict["mur_up"])
        add_var(num=num, denom=denom, name=f"{region}_weights_{cid}_{other_labels1[region]}_QCD_renscale_vbf_Down", factor=variation_dict["mur_down"])
        add_var(num=num, denom=denom, name=f"{region}_weights_{cid}_{other_labels1[region]}_QCD_facscale_vbf_Up", factor=variation_dict["muf_up"])
        add_var(num=num, denom=denom, name=f"{region}_weights_{cid}_{other_labels1[region]}_QCD_facscale_vbf_Down", factor=variation_dict["muf_down"])
        # PDF Uncertainty
        add_var(num=num, denom=denom, name=f"{region}_weights_{cid}_{other_labels1[region]}_QCD_pdf_vbf_Up", factor=variation_dict["pdf_up"])
        add_var(num=num, denom=denom, name=f"{region}_weights_{cid}_{other_labels1[region]}_QCD_pdf_vbf_Down", factor=variation_dict["pdf_down"])

        # EWK uncertainty (decorrelated among bins)
        ratio_ewk_up = target.Clone()
        ratio_ewk_up.SetName(f"{region}_weights_{cid}_ewk_Up")
        ratio_ewk_up.Divide(denom)
        ratio_ewk_up.Multiply(variation_dict["ewk_up"])

        ratio_ewk_down = target.Clone()
        ratio_ewk_down.SetName(f"{region}_weights_{cid}_ewk_Down")
        ratio_ewk_down.Divide(denom)
        ratio_ewk_down.Multiply(variation_dict["ewk_down"])

        num.Divide(denom)

        for b in range(target.GetNbinsX()):
            ewk_up_w = num.Clone()
            ewk_up_w.SetName("%s_weights_%s_%s_%s_bin%d_Up" % (region, cid, other_labels2[region], re.sub("_201(\d)", "", cid), b))
            ewk_down_w = num.Clone()
            ewk_down_w.SetName("%s_weights_%s_%s_%s_bin%d_Down" % (region, cid, other_labels2[region], re.sub("_201(\d)", "", cid), b))

            for i in range(target.GetNbinsX()):
                if i == b:
                    ewk_up_w.SetBinContent(i + 1, ratio_ewk_up.GetBinContent(i + 1))
                    ewk_down_w.SetBinContent(i + 1, ratio_ewk_down.GetBinContent(i + 1))
                    break

            _fOut.WriteTObject(ewk_up_w)
            _fOut.WriteTObject(ewk_down_w)

    #######################################################################################################

    _bins = []  # take bins from some histogram, can choose anything but this is easy
    for b in range(target.GetNbinsX() + 1):
        _bins.append(target.GetBinLowEdge(b + 1))

    # Here is the important bit which "Builds" the control region, make a list of control regions which
    # are constraining this process, each "Channel" is created with ...
    #   (name,_wspace,out_ws,cid+'_'+model,TRANSFERFACTORS)
    # the second and third arguments can be left unchanged, the others instead must be set
    # TRANSFERFACTORS are what is created above, eg WScales

    region_names = {
        "qcd_zmm": "qcd_dimuon",
        "qcd_zee": "qcd_dielectron",
        "qcd_w": "qcd_wjetssignal",
        "ewkqcd": "qcd_photon",
        "qcd_photon": "ewkqcd_signal",
    }
    CRs = {
        sample: Channel(region_names[sample], _wspace, out_ws, cid + "_" + model, transfer_factor, convention=convention)
        for sample, transfer_factor in transfer_factors.items()
    }

    CRs["qcd_w"].add_nuisance(f"CMS_veto{year}_t", -0.01)
    CRs["qcd_w"].add_nuisance(f"CMS_veto{year}_m", -0.015)
    CRs["qcd_w"].add_nuisance(f"CMS_veto{year}_e", -0.03)

    # Get the JES/JER uncertainty file for transfer factors
    # Read the split uncertainties from there
    fjes = get_jes_jer_source_file_for_tf(category="vbf")
    jet_variations = get_jes_variations(fjes, year, proc="qcd")

    label1 = {"qcd_w": "wlnu", "qcd_zmm": "zmumu", "qcd_zee": "zee", "qcd_photon": "gjets"}

    for var in jet_variations:
        for sample in ["qcd_zmm", "qcd_zee", "qcd_w", "qcd_photon"]:
            add_variation(
                transfer_factors[sample],
                fjes,
                f"znunu_over_{label1[sample]}{year-2000}_qcd_{var}Up",
                f"{sample}_weights_{cid}_{var}_Up",
                _fOut,
            )
            add_variation(
                transfer_factors[sample],
                fjes,
                f"znunu_over_{label1[sample]}{year-2000}_qcd_{var}Down",
                f"{sample}_weights_{cid}_{var}_Down",
                _fOut,
            )
            CRs[sample].add_nuisance_shape(var, _fOut)

    # ############################ USER DEFINED ###########################################################
    # Add systematics in the following, for normalisations use name, relative size (0.01 --> 1%)
    # for shapes use add_nuisance_shape with (name,_fOut)
    # note, the code will LOOK for something called NOMINAL_name_Up and NOMINAL_name_Down, where NOMINAL=WScales.GetName()
    # these must be created and writted to the same dirctory as the nominal (fDir)

    # Bin by bin nuisances to cover statistical uncertainties ...
    other_region_names = {
        "qcd_zmm": "qcd_dimuonCR",
        "qcd_zee": "qcd_dielectronCR",
        "qcd_w": "qcd_wzCR",
        "qcd_photon": "qcd_photonCR",
        "ewkqcd": "ewkqcdzCR",
    }

    for sample, transfer_factor in transfer_factors.items():
        do_stat_unc(transfer_factor, proc=sample, region=other_region_names[sample], CR=CRs[sample], cid=cid, outfile=_fOut)

    #######################################################################################################

    nbins = target.GetNbinsX()

    for region, other_label in other_labels1.items():
        for var in ["renscale", "facscale", "pdf"]:
            CRs[region].add_nuisance_shape(f"{other_label}_QCD_{var}_vbf", _fOut)

        for b in range(nbins):
            # CRs[region].add_nuisance_shape(f"{other_labels2[region]}_{re.sub('_201(\d)}', '', cid)}_bin{b}")
            CRs[region].add_nuisance_shape("%s_%s_bin%d" % (other_labels2[region], re.sub("_201(\d)", "", cid), b), _fOut)
            # CRs[region].add_nuisance_shape("qcd_ewk_%s_bin%d" % (re.sub("_201(\d)", "", cid), b), _fOut)
            # CRs[region].add_nuisance_shape("qcd_photon_ewk_%s_bin%d" % (re.sub("_201(\d)", "", cid), b), _fOut)

    #######################################################################################################

    cat = Category(model, cid, nam, _fin, _fOut, _wspace, out_ws, _bins, varname, target.GetName(), list(CRs.values()), diag, convention=convention)
    return cat
