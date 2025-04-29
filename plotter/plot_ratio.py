import os
import ROOT as rt  # type: ignore
import numpy as np
from collections import defaultdict
from utils.generic.logger import initialize_colorized_logger
import plotter.cmsstyle as CMS

logger = initialize_colorized_logger(log_level="INFO")


def oplus(*args: float) -> float:
    """Compute the quadrature sum of an arbitrary number of inputs."""
    return np.sqrt(np.sum(np.array(args) ** 2))


def plot_ratio(process: str, category: str, model_filename: str, outdir: str, lumi: float, year: str) -> None:
    """Plot transfer factors and their systematic uncertainties as ratio plots."""
    logger.debug(f"Input parameters: {locals()}")

    os.makedirs(outdir, exist_ok=True)

    is_mono_category = "mono" in category
    production_modes = [""] if is_mono_category else ["qcd", "ewk"]
    tag = "" if is_mono_category else "vbf"

    model_file = rt.TFile.Open(model_filename, "READ")

    process_config = {
        "zmm": {"model": "z", "label": "Z(#mu#mu)", "addsys": oplus(0.02, 0.02, 0.02)},
        "zee": {"model": "z", "label": "Z(ee)", "addsys": oplus(0.05, 0.02, 0.01)},
        "photon": {"model": "z", "label": "#gamma", "addsys": 0.01},
        "w": {"model": "z", "label": "Z/W", "addsys": 0},
        "wen": {"model": "w", "label": "W(e#nu)", "addsys": oplus(0.025, 0.01, 0.01)},
        "wmn": {"model": "w", "label": "W(#mu#nu)", "addsys": oplus(0.01, 0.01, 0.01)},
    }
    config = process_config[process]

    for mode in production_modes:
        dirname = f"{tag}_{mode}_{config['model']}_category_{category}"
        base_name = f"{mode}_{process}_weights_{category}"
        label = f"R_{{{mode}}}^{{{config['label']}}}"
        ratio = model_file.Get(f"{dirname}/{base_name}")
        subdir = model_file.Get(dirname)

        # Collect systematics
        unc_dict = defaultdict(lambda: defaultdict(float))
        for key in subdir.GetListOfKeys():
            name = key.GetName()
            if "TH1" not in key.GetClassName():
                continue
            if base_name not in name or "Up" not in name:
                continue

            up_hist = model_file.Get(f"{dirname}/{name}")
            if "stat_error" in name:
                syst = "stat"
            elif any(word in name for word in ["trig", "prefiring", "veto", "eff", "jes", "jer", "photon_scale"]):
                syst = "exp"
            elif any(word in name for word in ["cross", "QCD_pdf", "QCD_renscale", "QCD_facscale"]):
                syst = "qcd"
            elif any(word in name for word in ["ewk", "EWK_renscale", "EWK_facscale", "EWK_pdf"]):
                syst = "ewk"
            else:
                logger.critical(f"Unrecognized variation: {name}", exception_cls=ValueError)

            logger.debug(f"Processing systematic '{syst}' for histogram '{name}'")

            for b in range(1, ratio.GetNbinsX() + 1):
                diff = up_hist.GetBinContent(b) - ratio.GetBinContent(b)
                unc_dict[syst][b] = oplus(unc_dict[syst][b], diff)

        # Build uncertainty bands
        bands = {
            "ewk": ratio.Clone("band_ewk"),
            "ewk_qcd": ratio.Clone("band_ewk_qcd"),
            "total": ratio.Clone("band_total"),
        }

        for b in range(1, ratio.GetNbinsX() + 1):
            stat = unc_dict["stat"][b]
            ewk = oplus(stat, unc_dict["ewk"][b])
            qcd = oplus(ewk, unc_dict["qcd"][b])
            tot = oplus(qcd, unc_dict["exp"][b], config["addsys"] * ratio.GetBinContent(b))
            bands["ewk"].SetBinError(b, ewk)
            bands["ewk_qcd"].SetBinError(b, qcd)
            bands["total"].SetBinError(b, tot)

        CMS.SetEnergy(13.6)
        CMS.SetLumi(lumi)
        CMS.ResetAdditionalInfo()
        CMS.AppendAdditionalInfo("mono-V" if "monov" in category else ("monojet" if "mono" in category else "VBF") + " cat.")

        x_min = ratio.GetBinLowEdge(1) - ratio.GetBinWidth(1)
        x_max = ratio.GetBinLowEdge(ratio.GetNbinsX() + 1) + ratio.GetBinWidth(1)
        y_min = 0.5 * ratio.GetMinimum()
        y_max = 2.0 * ratio.GetMaximum()
        nameXaxis = "DNN score" if x_max < 10 else ("Recoil [GeV]" if "mono" in category else "m_{jj} [GeV]")

        canv = CMS.cmsCanvas(
            canvName="canv",
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            nameXaxis=nameXaxis,
            nameYaxis=label,
            square=True,
            extraSpace=0.025,
            yTitOffset=1.15,
        )

        CMS.cmsDraw(bands["total"], "e2", fcolor=rt.TColor.GetColor(CMS.petroff_6[2]))
        CMS.cmsDraw(bands["ewk_qcd"], "e2", fcolor=rt.TColor.GetColor(CMS.petroff_6[1]))
        CMS.cmsDraw(bands["ewk"], "e2", fcolor=rt.TColor.GetColor(CMS.petroff_6[0]))
        CMS.cmsDraw(ratio, "", marker=20, lcolor=1, lwidth=2)

        legend = CMS.cmsLeg(x1=0.40, y1=0.89 - 5 * 0.045, x2=0.89, y2=0.89, textSize=0.045)
        legend.AddEntry(ratio, "Transfer factor", "lpe")
        legend.AddEntry(bands["ewk"], "#oplus ewk", "f")
        legend.AddEntry(bands["ewk_qcd"], "#oplus qcd", "f")
        legend.AddEntry(bands["total"], "#oplus exp.", "f")
        legend.Draw("same")

        CMS.UpdatePad(canv)

        # for extension in ["png", "pdf", "C","root"]:
        for extension in ["pdf"]:
            canv.SaveAs(f"{outdir}/rfactor_{category}_{mode}_{process}_{year}.{extension}")
        canv.Close()
    model_file.Close()
