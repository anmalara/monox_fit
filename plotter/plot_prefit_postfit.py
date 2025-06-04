import os
import math
import ROOT as rt  # type: ignore
from array import array
import plotter.cmsstyle as CMS
from utils.generic.logger import initialize_colorized_logger

logger = initialize_colorized_logger(log_level="INFO")


def create_ratios(h_data: rt.TH1, h_all_prefit: rt.TH1, h_all_postfit: rt.TH1) -> tuple[rt.TGraphAsymmErrors, rt.TGraphAsymmErrors, rt.TH1]:
    xval, xerr = [], []
    ratio_pre, ratio_pre_hi, ratio_pre_lo = [], [], []
    ratio_post, ratio_post_hi, ratio_post_lo = [], [], []
    ratiosys = h_all_postfit.Clone()
    for idx in range(1, h_all_prefit.GetNbinsX() + 1):
        yield_data = h_data.GetBinContent(idx)
        yield_pre = h_all_prefit.GetBinContent(idx)
        yield_post = h_all_postfit.GetBinContent(idx)
        postfit_error = h_all_postfit.GetBinError(idx)
        ratiosys.SetBinContent(idx, 1.0)
        xval.append(h_all_prefit.GetBinCenter(idx))
        xerr.append(h_all_prefit.GetBinWidth(idx) / 2)

        if yield_data > 0.0:
            e_data_hi = h_data.GetBinError(idx)
            e_data_lo = h_data.GetBinError(idx)
        else:
            logger.critical("Empty data bin. Is this intendend?")
            # alpha = 1 - 0.6827
            # N = yield_data
            # L = 0 if N == 0 else rt.Math.gamma_quantile(alpha / 2, N, 1.0)
            # U = rt.Math.gamma_quantile_c(alpha / 2, N + 1, 1)
            # e_data_lo = (N - L) / width
            # e_data_hi = (U - N) / width

        if yield_pre > 0.0:
            ratio_pre.append(yield_data / yield_pre)
            ratio_pre_hi.append(e_data_hi / yield_pre)
            ratio_pre_lo.append(e_data_lo / yield_pre)
        else:
            ratio_pre.append(0.0)
            ratio_pre_hi.append(0.0)
            ratio_pre_lo.append(0.0)
            logger.warning("Empty pre-fit MC bin. Is this intendend?")

        if yield_post > 0.0:
            ratio_post.append(yield_data / yield_post)
            ratio_post_hi.append(e_data_hi / yield_post)
            ratio_post_lo.append(e_data_lo / yield_post)
            ratiosys.SetBinError(idx, postfit_error / yield_post)
        else:
            ratio_post.append(0.0)
            ratio_post_hi.append(0.0)
            ratio_post_lo.append(0.0)
            ratiosys.SetBinError(idx, 0.0)
            logger.warning("Empty post-fit MC bin. Is this intendend?")

    xval = array("d", xval)
    xerr = array("d", xerr)

    g_ratio_pre = rt.TGraphAsymmErrors(len(xval), xval, array("d", ratio_pre), xerr, xerr, array("d", ratio_pre_lo), array("d", ratio_pre_hi))
    g_ratio_post = rt.TGraphAsymmErrors(len(xval), xval, array("d", ratio_post), xerr, xerr, array("d", ratio_post_lo), array("d", ratio_post_hi))
    return g_ratio_pre, g_ratio_post, ratiosys


def plot_prefit_postfit(region: str, category: str, ws_filename: str, fitdiag_file: str, outdir: str, lumi: str, year: str, sb: bool = False) -> None:
    logger.debug(f"Input parameters: {locals()}")

    os.makedirs(outdir, exist_ok=True)

    is_SR = "signal" in region

    datalab = {
        "singlemuon": "Wmn",
        "dimuon": "Zmm",
        "gjets": "gjets",
        "signal": "signal",
        "singleelectron": "Wen",
        "dielectron": "Zee",
    }

    channel = {
        "singlemuon": f"{category}_singlemu",
        "dimuon": f"{category}_dimuon",
        "gjets": f"{category}_photon",
        "signal": f"{category}_signal",
        "singleelectron": f"{category}_singleel",
        "dielectron": f"{category}_dielec",
    }[region]

    f_mlfit = rt.TFile(fitdiag_file, "READ")
    f_data = rt.TFile(ws_filename, "READ")

    # using this instead of the graph from shapes_fit_b to avoid conversion
    h_data = f_data.Get(f"category_{category}/{datalab[region]}_data")

    if "mono" in category:
        mainbkgs = {
            "singlemuon": ["wjets"],
            "dimuon": ["zll"],
            "gjets": ["gjets"],
            "signal": ["zjets"],
            "singleelectron": ["wjets"],
            "dielectron": ["zll"],
        }
        processes = [
            # "qcd",
            "zll",
            "gjets",
            "top",
            "diboson",
            "ewk",
            # "ww",
            # "wz",
            # "zz",
            "wjets",
            "zjets",
            "wgamma",
            "zgamma",
        ]
    else:
        mainbkgs = {
            "singlemuon": ["ewk_wjets", "qcd_wjets"],
            "dimuon": ["ewk_zll", "qcd_zll"],
            "gjets": ["ewk_gjets", "qcd_gjets"],
            "signal": ["qcd_zjets", "ewk_zjets"],
            "singleelectron": ["ewk_wjets", "qcd_wjets"],
            "dielectron": ["ewk_zll", "qcd_zll"],
        }
        processes = [
            "qcd",
            "qcd_zll",
            "ewkzll",
            "ewk_zll",
            "qcdzll",
            "ewk_gjets",
            "qcd_gjets",
            "top",
            "diboson",
            "ewk_wjets",
            "qcd_wjets",
            "qcd_zjets",
            "ewk_zjets",
        ]
    colors = {
        "diboson": "#4897D8",
        "ww": "#4897D8",
        "wz": "#4897D8",
        "zz": "#4897D8",
        "wgamma": "#4897D8",
        "zgamma": "#4897D8",
        "gjets": "#9A9EAB",
        "qcd_gjets": "#9A9EAB",
        "ewk_gjets": "#9A9EAB",
        "qcd": "#F1F1F2",
        "top": "#CF3721",
        "ewk": "#000000",
        "zll": "#9A9EAB",
        "qcd_zll": "#9A9EAB",
        "qcdzll": "#82ba34",
        "ewk_zll": "#9A9EAB",
        "ewkzll": "#b4c754",
        "wjets": "#FAAF08",
        "qcd_wjets": "#feb24c",
        "ewk_wjets": "#ffeda0",
        "zjets": "#258039",
        "ewk_zjets": "#74c476",
        "qcd_zjets": "#00441b",
        "prefit": rt.kRed + 1,
        "postfit": rt.kAzure - 4,
    }

    binLowE = []

    # Pre/Post Fit
    prefit_dir = "shapes_prefit"
    postfit_dir = "shapes_fit_b"
    h_prefit = {}
    h_postfit = {}
    h_all_prefit = f_mlfit.Get(f"{prefit_dir}/{channel}/total_background").Clone("h_all_prefit")
    h_all_postfit = f_mlfit.Get(f"{postfit_dir}/{channel}/total_background").Clone("h_all_postfit")
    h_postfit_total_sig_bkg = f_mlfit.Get(f"{postfit_dir}/{channel}/total").Clone("h_postfit_total_sig_bkg")

    h_other_prefit = None
    h_other_postfit = None
    h_prefit["total"] = f_mlfit.Get(f"{prefit_dir}/{channel}/total").Clone("h_prefit_total")
    for i in range(1, h_prefit["total"].GetNbinsX() + 2):
        binLowE.append(h_prefit["total"].GetBinLowEdge(i))

    h_stack_postfit = rt.THStack("h_stack_postfit", "h_stack_postfit")

    for process in processes:
        h_prefit[process] = f_mlfit.Get(f"{prefit_dir}/{channel}/{process}")
        if not h_prefit[process]:
            continue
        h_prefit[process] = h_prefit[process].Clone(f"h_prefit_{process}")
        h_postfit[process] = f_mlfit.Get(f"{postfit_dir}/{channel}/{process}")
        h_postfit[process] = h_postfit[process].Clone(f"h_postfit_{process}")
        if not h_postfit[process]:
            continue
        if str(h_prefit[process].Integral()) == "nan" or str(h_postfit[process].Integral()) == "nan":
            logger.critical(f"Found process with integral==Nan: {process}", exception_cls=RuntimeError)
        h_prefit[process].SetDirectory(0)
        for i in range(1, h_prefit[process].GetNbinsX() + 1):
            width = h_prefit[process].GetBinWidth(i)
            h_prefit[process].SetBinContent(i, h_prefit[process].GetBinContent(i) * width)
            h_prefit[process].SetBinError(i, h_prefit[process].GetBinError(i) * width)
            h_postfit[process].SetBinContent(i, h_postfit[process].GetBinContent(i) * width)
            h_postfit[process].SetBinError(i, h_postfit[process].GetBinError(i) * width)
        color = rt.TColor.GetColor(colors[process])
        h_prefit[process].SetLineColor(color)
        h_prefit[process].SetFillColor(color)
        if process not in mainbkgs[region]:
            if h_other_prefit is None:
                h_other_prefit = h_prefit[process].Clone("h_other_prefit")
                h_other_postfit = h_postfit[process].Clone("h_other_postfit")
                h_other_prefit.SetDirectory(0)
                h_other_postfit.SetDirectory(0)
            else:
                h_other_prefit.Add(h_prefit[process])
                h_other_postfit.Add(h_postfit[process])

        h_postfit[process].SetLineColor(1)
        h_postfit[process].SetFillColor(color)
        h_postfit[process].Scale(1, "width")

        if is_SR:
            h_stack_postfit.Add(h_postfit[process])

    if h_other_prefit is None:
        h_other_prefit = h_all_prefit.Clone("h_other_prefit")
        h_other_postfit = h_all_postfit.Clone("h_other_postfit")
        h_other_prefit.SetDirectory(0)
        h_other_postfit.SetDirectory(0)
        h_other_prefit.Scale(0)
        h_other_postfit.Scale(0)

    x_min = h_all_prefit.GetBinLowEdge(1)
    x_max = h_all_prefit.GetBinLowEdge(h_all_prefit.GetNbinsX() + 1)
    is_dnn = x_max < 10
    nameXaxis = "DNN score" if is_dnn else ("Recoil [GeV]" if "mono" in category else "m_{jj} [GeV]")
    nameYaxis = "Events / bin" if is_dnn else "Events / GeV"
    y_up_min, y_up_max = 10 if is_dnn else 0.002, (1000 if is_dnn else 100) * h_all_prefit.GetMaximum()
    CMS.SetEnergy(13.6)
    CMS.SetLumi(lumi)
    CMS.ResetAdditionalInfo()
    CMS.AppendAdditionalInfo("mono-V" if "monov" in category else ("monojet" if "mono" in category else "VBF") + " cat.")
    canv = CMS.cmsTriCanvas(
        canvName="canv",
        x_min=x_min,
        x_max=x_max,
        y_up_min=y_up_min,
        y_up_max=y_up_max,
        y_mid_min=0.7,
        y_mid_max=1.5,
        y_low_min=-3.5,
        y_low_max=3.5,
        nameXaxis=nameXaxis,
        nameYaxis_up=nameYaxis,
        nameYaxis_mid="Data / Pred.",
        nameYaxis_low="#frac{(Data-Pred.)}{#sigma}",
    )
    canv.cd(1).SetLogy(True)
    canv.cd(1)

    h_other_prefit.Scale(1, "width")

    if is_SR:
        if sb:
            CMS.cmsDraw(h_postfit_total_sig_bkg, "hist", lcolor=1, fcolor=1, fstyle=3144)
        h_stack_postfit.Draw("hist same")

    else:
        CMS.cmsDraw(h_other_prefit, "hist", lwidth=1, lcolor=1, fcolor=33)
        CMS.cmsDraw(h_all_prefit, "hist", lwidth=2, lcolor=colors["prefit"], fstyle=0)
        CMS.cmsDraw(h_all_postfit, "hist", lwidth=2, lcolor=colors["postfit"], fstyle=0)

    h_data.Scale(1, "width")
    CMS.cmsDraw(h_data, "ep", marker=20, msize=1.2, lcolor=1)

    if region == "singlemuon":
        legname = "W #rightarrow #mu#nu"
    if region == "dimuon":
        legname = "Z #rightarrow #mu#mu"
    if region == "gjets":
        legname = "#gamma + jets"
    if region == "singleelectron":
        legname = "W #rightarrow e#nu"
    if region == "dielectron":
        legname = "Z #rightarrow ee"

    n_leg_entries = (len(h_postfit) - 1) if is_SR else 6
    legend = CMS.cmsLeg(x1=0.55, y1=0.89 - (n_leg_entries) * 0.045, x2=0.89, y2=0.89, textSize=0.045)
    if is_SR:
        legend.AddEntry(h_data, "Pseudo data", "elp")
        if "mono" in category:
            legend.AddEntry(h_postfit["zjets"], "Z(#nu#nu)+jets", "f")
            legend.AddEntry(h_postfit["wjets"], "W(l#nu)+jets", "f")
            legend.AddEntry(h_postfit["diboson"], "WW/ZZ/WZ", "f")
            legend.AddEntry(h_postfit["top"], "Top quark", "f")
            # legend.AddEntry(h_postfit['gjets'], "Z(ll)+jets, #gamma+jets", "f")
            # legend.AddEntry(h_postfit["qcd"], "QCD", "f")
        else:
            # pass
            legend.AddEntry(h_postfit["qcd_zjets"], "QCD Z(#nu#nu)+jets", "f")
            legend.AddEntry(h_postfit["qcd_wjets"], "QCD W(l#nu)+jets", "f")
            legend.AddEntry(h_postfit["ewk_zjets"], "EWK Z(#nu#nu)+jets", "f")
            legend.AddEntry(h_postfit["ewk_wjets"], "EWK W(l#nu)+jets", "f")
            legend.AddEntry(h_postfit["diboson"], "WW/ZZ/WZ", "f")
            legend.AddEntry(h_postfit["top"], "Top quark", "f")
            legend.AddEntry(h_postfit["qcdzll"], "QCD Z(ll)+jets", "f")
            legend.AddEntry(h_postfit["ewkzll"], "EWK Z(ll)+jets", "f")
            # legend.AddEntry(h_postfit["gjets"], "#gamma+jets", "f") TODO
            # legend.AddEntry(h_postfit["qcd"], "QCD", "f")
        if sb:
            legend.AddEntry(h_postfit_total_sig_bkg, "S+B post-fit", "f")

    else:
        legend.AddEntry(h_data, "Data", "elp")
        legend.AddEntry(h_all_postfit, f"Post-fit ({legname})", "l")
        legend.AddEntry(h_all_prefit, f"Pre-fit ({legname})", "l")
        legend.AddEntry(h_other_prefit, "Other backgrounds", "f")

    g_ratio_pre, g_ratio_post, ratiosys = create_ratios(h_data=h_data, h_all_prefit=h_all_prefit, h_all_postfit=h_all_postfit)

    canv.cd(2)

    ref_line = rt.TLine(x_min, 1, x_max, 1)

    CMS.cmsDraw(ratiosys, "e2", msize=0, lwidth=1, lcolor=rt.kGray, fcolor=rt.kGray)
    CMS.cmsDrawLine(line=ref_line, lcolor=rt.kBlack, lstyle=rt.kDashed, lwidth=2)
    CMS.cmsDraw(g_ratio_pre, "ep", marker=20, msize=1.2, mcolor=colors["prefit"], lcolor=colors["prefit"])
    CMS.cmsDraw(g_ratio_post, "ep", marker=20, msize=1.2, mcolor=colors["postfit"], lcolor=colors["postfit"])

    legend_ratio = CMS.cmsLeg(x1=0.18, y1=0.70, x2=0.50, y2=0.92, textSize=0.14)
    legend_ratio.AddEntry(g_ratio_pre, "Pre-fit", "ple")
    legend_ratio.AddEntry(g_ratio_post, "Post-fit", "ple")
    legend_ratio.SetNColumns(2)
    legend_ratio.Draw("same")

    canv.cd(3)
    # Compute the pulls
    data_pull = h_data.Clone("pull")
    data_pull_sig = h_data.Clone("pull")

    def get_pull(hist_1: rt.TH1, hist_2: rt.TH1, hbin: int) -> float:
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/DataMCComparison
        # formula: pull = data-pred/sigma, with
        # sigma = sqrt(sigma_data^2-sigma_fit^2)
        # sigma_data = sqrt(mc_pred) -> Poisson statistical error estimated from the MC prediction
        # sigma_fit = mc_err -> mc postfit error
        # sigma = sqrt(mc_pred-mc_err^2)
        width = hist_1.GetBinWidth(hbin)
        data_pred = width * hist_1.GetBinContent(hbin)
        mc_pred = width * hist_2.GetBinContent(hbin)
        postfit_err = width * hist_2.GetBinError(hbin)
        sigma = mc_pred - postfit_err**2
        if sigma < 0:
            logger.warning(f"Bin {hbin} at x={hist_2.GetBinCenter(hbin)} with too large post fit errors.")
            sigma = mc_pred + postfit_err**2
        pull = (data_pred - mc_pred) / math.sqrt(sigma)
        return pull

    for hbin in range(1, data_pull.GetNbinsX() + 1):
        pull = get_pull(hist_1=h_data, hist_2=h_all_postfit, hbin=hbin)
        data_pull.SetBinContent(hbin, pull)
        data_pull.SetBinError(hbin, 0)
        pull = get_pull(hist_1=h_data, hist_2=h_postfit_total_sig_bkg, hbin=hbin)
        data_pull_sig.SetBinContent(hbin, pull)
        data_pull_sig.SetBinError(hbin, 0)

    data_pull_sig.SetLineColor(2)
    data_pull_sig.SetFillColor(2)
    data_pull_sig.SetFillStyle(3004)
    data_pull_sig.SetMarkerColor(2)
    CMS.cmsDraw(data_pull, "hist", mcolor=colors["postfit"], lcolor=colors["postfit"], fcolor=colors["postfit"])

    legend_pull = CMS.cmsLeg(x1=0.18, y1=0.80, x2=0.40, y2=0.92, textSize=0.11)
    legend_pull.Draw("same")
    legend_pull.AddEntry(data_pull, "Background only", "f")

    for i in range(1, 4):
        CMS.UpdatePad(canv.cd(i))

    # for extension in ["png", "pdf", "C","root"]:
    for extension in ["pdf"]:
        canv.SaveAs(f"{outdir}/prefit_postfit_{category}_{region}_{year}.{extension}")

    canv.Close()
    f_mlfit.Close()
    f_data.Close()
