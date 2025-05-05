import os
import ROOT as rt  # type:ignore
import plotter.cmsstyle as CMS
from utils.generic.general import oplus
from utils.workspace.flat_uncertainties import get_flat_uncertainties
from utils.generic.logger import initialize_colorized_logger

logger = initialize_colorized_logger(log_level="INFO")


def get_label_name(region1: str, region2: str) -> str:
    """Return the formatted label for the given region comparison."""
    label_map: dict[str, str] = {
        "combined": "Z #rightarrow ll",
        "combinedW": "W #rightarrow l#nu",
        "gjets": "#gamma",
        "dielectron": "Z #rightarrow ee",
        "dimuon": "Z #rightarrow #mu#mu",
        "singleelectron": "W #rightarrow e#nu",
        "singlemuon": "W #rightarrow #mu#nu",
    }
    if region1 not in label_map:
        logger.critical(f"No label defined for {region1}", exception_cls=ValueError)
    if region2 not in label_map:
        logger.critical(f"No label defined for {region2}", exception_cls=ValueError)
    return f"{label_map[region1]} / {label_map[region2]}"


def get_regions_and_leadbg(region: str) -> tuple[list[str], str]:
    channel_map = {
        "singlemuon": "singlemu",
        "singleelectron": "singleel",
        "dimuon": "dimuon",
        "dielectron": "dielec",
        "gjets": "photon",
    }
    leadbkg_map = {
        "singlemuon": "wjets",
        "singleelectron": "wjets",
        "dimuon": "zll",
        "dielectron": "zll",
        "gjets": "gjets",
    }
    if region == "combined":
        return ["dimuon", "dielec"], "zll"
    elif region == "combinedW":
        return ["singlemu", "singleel"], "wjets"
    else:
        return [channel_map[region]], leadbkg_map[region]


def add_histograms(hists: list[rt.TH1]) -> rt.TH1:
    """Sum the histograms of a given process over multiple regions."""
    tot_hist = hists[0].Clone()
    for h in hists[1:]:
        tot_hist.Add(h)
    tot_hist.SetDirectory(0)
    return tot_hist


def get_region_label(region: str) -> str:
    label_map: dict[str, str] = {
        "singlemuon": "Wmn",
        "singleelectron": "Wen",
        "dimuon": "Zmm",
        "dielectron": "Zee",
        "gjets": "gjets",
    }
    return label_map[region]


def get_data(region1: str, region2: str, ws_filename: str, category: str) -> rt.TH1:
    """Return the data histogram ratio: region1 / region2."""
    ws_file = rt.TFile.Open(ws_filename, "READ")

    def retrieve(region: str) -> rt.TH1:
        if region == "combined":
            labels = ["dimuon", "dielectron"]
        elif region == "combinedW":
            labels = ["singlemuon", "singleelectron"]
        else:
            labels = [region]
        hists = [ws_file.Get(f"category_{category}/{get_region_label(region=r)}_data").Clone() for r in labels]
        hist = add_histograms(hists=hists)
        return hist

    ratio = retrieve(region1)
    den = retrieve(region2)
    ratio.Divide(den)
    ws_file.Close()
    return ratio


def get_mc_variations(region1: str, region2: str, ws_filename: str, category: str, syst_groups: dict[str, list[str]] = {}) -> dict[str, rt.TH1]:
    """Return the ratio of MC histograms (region1 / region2) with grouped systematics."""
    ws_file = rt.TFile.Open(ws_filename, "READ")
    subdir = ws_file.Get(f"category_{category}")
    histogram_names = [x.GetName() for x in subdir.GetListOfKeys()]
    histogram_names = [hname for hname in histogram_names if "Up" not in hname and "Down" not in hname]
    syst_names = list(set(sum(syst_groups.values(), [])))
    logger.debug(f"Systematics: {syst_names}")

    def retrieve(region: str) -> dict[str, rt.TH1]:
        if region == "combined":
            labels = ["dimuon", "dielectron"]
        elif region == "combinedW":
            labels = ["singlemuon", "singleelectron"]
        else:
            labels = [region]
        hnames = [hname for hname in histogram_names if "_data" not in hname and any(hname.startswith(get_region_label(region=r)) for r in labels)]
        logger.debug(f"Histograms: {hnames}")
        hists = [ws_file.Get(f"category_{category}/{hname}").Clone() for hname in hnames]
        syst_hists = {}
        for syst in syst_names:
            syst_hist_names = [f"category_{category}/{hname}_{syst}Up" for hname in hnames]
            logger.debug(f"Systematic: {syst}. Histograms: {syst_hist_names}")
            syst_hists[syst] = add_histograms(hists=[ws_file.Get(hname).Clone() for hname in syst_hist_names])
        nominal_hist = add_histograms(hists=hists)
        grouped_syst_hists = {syst: nominal_hist.Clone(syst) for syst in syst_groups}
        for bin in range(1, nominal_hist.GetNbinsX() + 1):
            content = nominal_hist.GetBinContent(bin)
            stat_error = nominal_hist.GetBinError(bin)
            for group_name, syst_variation in list(syst_groups.items()):
                total_error = stat_error
                for syst in syst_variation:
                    total_error = oplus(total_error, syst_hists[syst].GetBinContent(bin) - content)
                grouped_syst_hists[group_name].SetBinContent(bin, content)
                grouped_syst_hists[group_name].SetBinError(bin, total_error)
        grouped_syst_hists["Stat."] = nominal_hist
        return grouped_syst_hists

    ratio = retrieve(region1)
    den = retrieve(region2)
    for syst in ratio:
        ratio[syst].Divide(den[syst])
        ratio[syst].SetDirectory(0)
    ws_file.Close()
    return ratio


def get_prefit_histograms(region1: str, region2: str, fitdiag_filename: str, category: str) -> dict[str, rt.TH1]:
    fitdiag_file = rt.TFile.Open(fitdiag_filename, "READ")

    def get_shape(region: str, process: str) -> rt.TH1:
        """Retrieve a prefit histogram from the diagnostics file for a given region and process."""
        path = f"shapes_prefit/{category}_{region}/{process}"
        hist = fitdiag_file.Get(path)
        if not hist:
            logger.critical(f"Histogram not found at path: {path}")
        hist.SetDirectory(0)
        return hist

    h_prefit = {}
    # Read prefit histogram
    for region in [region1, region2]:
        region_list, leadbkg = get_regions_and_leadbg(region)
        h_prefit[region] = add_histograms(hists=[get_shape(region=region, process="total_background") for region in region_list])
        if "vbf" in category:
            h_prefit[f"qcd_{region}"] = add_histograms(hists=[get_shape(region, process=f"qcd_{leadbkg}") for region in region_list])
            h_prefit[f"ewk_{region}"] = add_histograms(hists=[get_shape(region, process=f"ewk_{leadbkg}") for region in region_list])

    fitdiag_file.Close()
    return h_prefit


def plot_data_validation(region1: str, region2: str, category: str, ws_filename: str, fitdiag_filename: str, outdir: str, lumi: float, year: str) -> None:
    """Compare data and MC prediction between two regions with prefit uncertainties."""
    logger.debug(f"Input parameters: {locals()}")
    os.makedirs(outdir, exist_ok=True)

    # flat_uncertainties = get_flat_uncertainties(process=process)
    # Define systematics
    syst_groups = {
        "Exp.": ["prefiring_jet", "pu", "trigger_met", "trigger_electron", "trigger_photon", "electron", "photon", "muonID", "muonISO"],
        "JECs": [
            "jer_Run3",
            "jesBBEC1_Run3",
            "jesEC2_Run3",
            "jesAbsolute_Run3",
            "jesRelativeBal",
            "jesEC2",
            "jesHF",
            "jesRelativeSample_Run3",
            "jesAbsolute",
            "jesHF_Run3",
            "jesBBEC1",
            "jesFlavorQCD",
        ],
        "Theory": ["muf", "mur", "pdf"],
    }
    syst_groups["Total"] = list(set(sum(syst_groups.values(), [])))

    # Retrieve histograms. This is to show the input to the workspace
    h_data = get_data(region1=region1, region2=region2, ws_filename=ws_filename, category=category)
    h_mc_syst_variations = get_mc_variations(region1=region1, region2=region2, ws_filename=ws_filename, category=category, syst_groups=syst_groups)

    # Compute MC ratio histogram. This is to show the total syst as seen by combine
    h_prefit = get_prefit_histograms(region1=region1, region2=region2, fitdiag_filename=fitdiag_filename, category=category)
    h_mc = h_prefit[region1].Clone()
    h_mc.Divide(h_prefit[region2])
    h_tot_error = h_mc.Clone("tot_error")

    # Canvas setup
    CMS.SetEnergy(13.6)
    CMS.SetLumi(lumi)
    CMS.ResetAdditionalInfo()
    category_label = "mono-V" if "monov" in category else ("monojet" if "mono" in category else "VBF")
    CMS.AppendAdditionalInfo(f"{category_label} cat.")

    x_min = h_mc.GetBinLowEdge(1) - h_mc.GetBinWidth(1)
    x_max = h_mc.GetBinLowEdge(h_mc.GetNbinsX() + 1) + h_mc.GetBinWidth(1)
    name_x_axis = "DNN score" if x_max < 10 else ("Recoil [GeV]" if "mono" in category else "m_{jj} [GeV]")

    canv = CMS.cmsDiCanvas(
        canvName="canv",
        x_min=x_min,
        x_max=x_max,
        y_min=0,
        y_max=2.0 * h_mc.GetMaximum(),
        r_min=0.4,
        r_max=1.6,
        nameXaxis=name_x_axis,
        nameYaxis=get_label_name(region1=region1, region2=region2),
        nameRatio="Data / Pred.",
        extraSpace=0.08,
    )

    # Upper pad: draw main distributions
    canv.cd(1)
    color_data, color_mc, color_stat_unc, color_tot_unc = rt.kBlack, rt.kRed + 1, rt.kGray, rt.kAzure + 5
    color_map = [
        ("Total", rt.kViolet + 2),
        ("Theory", rt.kRed + 1),
        ("JECs", rt.kGreen + 2),
        ("Exp.", rt.kOrange + 1),
        ("Stat.", rt.kGray + 1),
    ]

    CMS.cmsDraw(h_tot_error, "e2", msize=0, lwidth=1, lcolor=color_tot_unc, fcolor=color_tot_unc)
    for syst, color in color_map:
        CMS.cmsDraw(h_mc_syst_variations[syst], "e2", msize=0, lwidth=1, lcolor=color, fcolor=color, alpha=0.7)
    CMS.cmsDraw(h_mc, "hist", msize=0, lwidth=1, lcolor=color_mc, fstyle=0)
    CMS.cmsDraw(h_data, "Pe", marker=20, lwidth=1, lcolor=color_data)

    # Add legend
    legend = CMS.cmsLeg(x1=0.40, y1=0.89 - (len(h_mc_syst_variations) + 4) * 0.05, x2=0.70, y2=0.89, textSize=0.05)
    legend.AddEntry(h_data, "Data", "lep")
    legend.AddEntry(h_mc, "MC", "l")
    for syst, _ in list(reversed(color_map)):
        legend.AddEntry(h_mc_syst_variations[syst], f"{syst} unc.", "f")
    legend.AddEntry(h_tot_error, "Tot. unc.", "f")
    legend.Draw("same")

    # Lower pad: ratio plot
    canv.cd(2)
    ratio = h_data.Clone("ratio")
    ratio_stat = h_mc_syst_variations["Stat."].Clone("ratio_stat")
    ratio_tot = h_tot_error.Clone("ratio_tot")
    ratio.Divide(h_mc)
    ratio_stat.Divide(h_mc)
    ratio_tot.Divide(h_mc)

    ref_line = rt.TLine(x_min, 1, x_max, 1)
    CMS.cmsDraw(ratio_tot, "e2", msize=0, lwidth=1, lcolor=color_tot_unc, fcolor=color_tot_unc)
    CMS.cmsDraw(ratio_stat, "e2", msize=0, lwidth=1, lcolor=color_stat_unc, fcolor=color_stat_unc)
    CMS.cmsDrawLine(line=ref_line, lcolor=rt.kBlack, lstyle=rt.kDashed, lwidth=2)
    CMS.cmsDraw(ratio, "Pe", marker=20, lwidth=1, lcolor=color_data)

    CMS.UpdatePad(canv.cd(1))
    CMS.UpdatePad(canv.cd(2))

    # for extension in ["png", "pdf", "C","root"]:
    for extension in ["pdf"]:
        canv.SaveAs(f"{outdir}/ratio_{category}_{region1}_{region2}_{year}.{extension}")
    canv.Close()
