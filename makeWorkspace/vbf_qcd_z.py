import ROOT  # type:ignore
from typing import Any
from counting_experiment import *
from utils.jes_utils import get_jes_variations, get_jes_jer_source_file_for_tf
from W_constraints import do_stat_unc, add_variation

# Define how a control region(s) transfer is made by defining *cmodel*, the calling pattern must be unchanged!
# First define simple string which will be used for the datacard
model = "qcd_zjets"


def cmodel(category_id, category_name, input_file, output_file, output_workspace, diagonalizer, year, convention="BU"):
    """
    Constructs a category model for a given signal process using control regions and transfer factors.

    This function:
    - Retrieves histograms from the input ROOT file.
    - Computes transfer factors for various control regions.
    - Applies systematic uncertainties (scale, PDF, and EWK corrections).
    - Constructs control regions using transfer factors.
    - Adds statistical and systematic uncertainties.
    - Creates and returns a `Category` object representing the process.

    Args:
        category_id (str): Category ID.
        category_name (str): Category name.
        input_file (ROOT.TFile): Input ROOT file containing relevant histograms.
        output_file (ROOT.TFile): Output ROOT file for storing processed histograms.
        output_workspace (ROOT.RooWorkspace): Output workspace for RooFit objects.
        diagonalizer (bool): Diagonalizer to pass to `Category`
        year (int): Data-taking year.
        convention (str, optional): Naming convention for transfer factors. Defaults to "BU".

    Returns:
        Category: A `Category` object encapsulating the modeled process.

    Notes:
        - The function assumes specific naming conventions for histograms inside `input_file`.
        - Uses systematic uncertainty files for VBF processes (`sys/vbf_z_w_gjets_theory_unc_ratio_unc.root`).
        - Applies various nuisances and systematic effects to transfer factors.
        - Constructs control regions using transfer factors and stores them in the output workspace.
    """

    # Some setup
    input_tdir = input_file.Get("category_%s" % category_id)
    input_wspace = input_tdir.Get("wspace_%s" % category_id)

    # Defining the nominal transfer factors
    # Nominal MC process to model
    target = input_tdir.Get("signal_qcdzjets")
    # Control MC samples
    control_samples = {
        "qcd_zmm": input_tdir.Get("Zmm_qcdzll"),
        "qcd_zee": input_tdir.Get("Zee_qcdzll"),
        "qcd_w": input_tdir.Get("signal_qcdwjets"),
        "ewkqcd": input_tdir.Get("signal_ewkzjets"),
        "qcd_photon": input_tdir.Get("gjets_qcdgjets"),
    }

    # Compute and save a copy of the transfer factors (target divided by control)
    transfer_factors = {region: target.Clone() for region in control_samples.keys()}
    for label, sample in transfer_factors.items():
        sample.SetName(f"{label}_weights_{category_id}")
        sample.Divide(control_samples[label])

        output_file.WriteTObject(sample)

    # label used for channel of each transfer factor
    channel_names = {
        "qcd_zmm": "qcd_dimuon",
        "qcd_zee": "qcd_dielectron",
        "qcd_w": "qcd_wjetssignal",
        "ewkqcd": "qcd_photon",
        "qcd_photon": "ewkqcd_signal",
    }

    # Create a `Channel` object for each transfer factor
    CRs = {
        sample: Channel(channel_names[sample], input_wspace, output_workspace, category_id + "_" + model, transfer_factor, convention=convention)
        for sample, transfer_factor in transfer_factors.items()
    }

    add_veto_nuisances(CRs, channel_list=["qcd_w"], year=year)
    add_jes_jer_uncertainties(
        transfer_factors, CRs, channel_list=["qcd_zmm", "qcd_zee", "qcd_w", "qcd_photon"], year=year, category_id=category_id, output_file=output_file
    )
    add_theory_uncertainties(
        control_samples,
        target_sample=target,
        channel_objects=CRs,
        channel_list=["qcd_w", "qcd_photon"],
        year=year,
        category_id=category_id,
        output_file=output_file,
    )

    # label used for region of each transfer factor
    region_names = {
        "qcd_zmm": "qcd_dimuonCR",
        "qcd_zee": "qcd_dielectronCR",
        "qcd_w": "qcd_wzCR",
        "qcd_photon": "qcd_photonCR",
        "ewkqcd": "ewkqcdzCR",
    }
    # Add Bin by bin nuisances to cover statistical uncertainties
    for sample, transfer_factor in transfer_factors.items():
        do_stat_unc(transfer_factor, proc=sample, region=region_names[sample], CR=CRs[sample], cid=category_id, outfile=output_file)

    # Create and return `Category` object
    cat = Category(
        model,
        category_id,
        category_name,
        input_tdir,
        output_file,
        input_wspace,
        output_workspace,
        [target.GetBinLowEdge(b + 1) for b in range(target.GetNbinsX() + 1)],
        "mjj",
        target.GetName(),
        list(CRs.values()),
        diagonalizer,
        convention=convention,
    )
    return cat


def add_veto_nuisances(channel_objects: dict[str, Channel], channel_list: list[str], year: str) -> None:
    for channel in channel_list:
        channel_objects[channel].add_nuisance(f"CMS_veto{year}_t", -0.01)
        channel_objects[channel].add_nuisance(f"CMS_veto{year}_m", -0.015)
        channel_objects[channel].add_nuisance(f"CMS_veto{year}_e", -0.03)


def add_jes_jer_uncertainties(
    transfer_factors: dict[str, Any],
    channel_objects: dict[str, Channel],
    channel_list: list[str],
    year: str,
    category_id: str,
    output_file: ROOT.TFile,
) -> None:
    jes_region_labels = {
        "qcd_w": "wlnu",
        "qcd_zmm": "zmumu",
        "qcd_zee": "zee",
        "qcd_photon": "gjets",
    }
    # Get the JES/JER uncertainty file for transfer factors
    # Read the split uncertainties from there
    fjes = get_jes_jer_source_file_for_tf(category="vbf")
    jet_variations = get_jes_variations(fjes, year, proc="qcd")

    for sample in channel_list:
        for var in jet_variations:
            # Scale transfer factor by relative variation and write to output file
            add_variation(
                transfer_factors[sample],
                fjes,
                f"znunu_over_{jes_region_labels[sample]}{year-2000}_qcd_{var}Up",
                f"{sample}_weights_{category_id}_{var}_Up",
                output_file,
            )
            add_variation(
                transfer_factors[sample],
                fjes,
                f"znunu_over_{jes_region_labels[sample]}{year-2000}_qcd_{var}Down",
                f"{sample}_weights_{category_id}_{var}_Down",
                output_file,
            )
            # Add function (quadratic) to model the nuisance
            channel_objects[sample].add_nuisance_shape(var, output_file)


def add_theory_uncertainties(
    control_samples: dict[str, Any],
    target_sample: Any,
    channel_objects: dict[str, Channel],
    channel_list: list[str],
    year: str,
    category_id: str,
    output_file: ROOT.TFile,
) -> None:

    # Save a (renamed) copy of samples used to derive theory variations
    # Done to perfectly mirrors what is done in Z_constraints_qcd_withphoton
    spectrum_label = {
        "qcd_w": "qcd_w",
        "qcd_photon": "qcd_gjets",
    }
    spectrums = {region: control_samples[region].Clone() for region in channel_list}
    for region, sample in spectrums.items():
        sample.SetName(f"{spectrum_label[region]}_spectrum_{category_id}_")
        output_file.WriteTObject(sample)

    # File containting the theory uncertainties
    vbf_sys = r.TFile.Open("sys/vbf_z_w_gjets_theory_unc_ratio_unc.root")

    # method to add the ratios scaled by theory variation to the output file
    def add_var(num, denom, name, factor):
        new = num.Clone(name)
        new.Divide(denom)
        new.Multiply(factor)
        output_file.WriteTObject(new)

    nbins = target_sample.GetNbinsX()
    ratio_label = {
        "qcd_w": "zoverw",
        "qcd_photon": "goverz",
    }
    prefix_label = {
        "qcd_w": "z",
        "qcd_photon": "gjets",
    }
    other_labels1 = {
        "qcd_w": "ZnunuWJets",
        "qcd_photon": "Photon",
    }
    other_labels2 = {
        "qcd_w": "qcd_ewk",
        "qcd_photon": "qcd_photon_ewk",
    }

    for region in channel_list:

        denom = control_samples[region].Clone()
        denom.SetName(f"{region}_weights_denom_{category_id}")
        num = target_sample.Clone()
        num.SetName(f"{region}_weights_nom_{category_id}")

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
        add_var(num=num, denom=denom, name=f"{region}_weights_{category_id}_{other_labels1[region]}_QCD_renscale_vbf_Up", factor=variation_dict["mur_up"])
        add_var(num=num, denom=denom, name=f"{region}_weights_{category_id}_{other_labels1[region]}_QCD_renscale_vbf_Down", factor=variation_dict["mur_down"])
        add_var(num=num, denom=denom, name=f"{region}_weights_{category_id}_{other_labels1[region]}_QCD_facscale_vbf_Up", factor=variation_dict["muf_up"])
        add_var(num=num, denom=denom, name=f"{region}_weights_{category_id}_{other_labels1[region]}_QCD_facscale_vbf_Down", factor=variation_dict["muf_down"])
        # PDF Uncertainty
        add_var(num=num, denom=denom, name=f"{region}_weights_{category_id}_{other_labels1[region]}_QCD_pdf_vbf_Up", factor=variation_dict["pdf_up"])
        add_var(num=num, denom=denom, name=f"{region}_weights_{category_id}_{other_labels1[region]}_QCD_pdf_vbf_Down", factor=variation_dict["pdf_down"])

        for var in ["renscale", "facscale", "pdf"]:
            channel_objects[region].add_nuisance_shape(f"{other_labels1[region]}_QCD_{var}_vbf", output_file)

        # EWK uncertainty (decorrelated among bins)
        ratio_ewk_up = target_sample.Clone()
        ratio_ewk_up.SetName(f"{region}_weights_{category_id}_ewk_Up")
        ratio_ewk_up.Divide(denom)
        ratio_ewk_up.Multiply(variation_dict["ewk_up"])

        ratio_ewk_down = target_sample.Clone()
        ratio_ewk_down.SetName(f"{region}_weights_{category_id}_ewk_Down")
        ratio_ewk_down.Divide(denom)
        ratio_ewk_down.Multiply(variation_dict["ewk_down"])

        num.Divide(denom)

        for b in range(nbins):
            ewk_up_w = num.Clone()
            ewk_up_w.SetName("%s_weights_%s_%s_%s_bin%d_Up" % (region, category_id, other_labels2[region], re.sub("_201(\d)", "", category_id), b))
            ewk_down_w = num.Clone()
            ewk_down_w.SetName("%s_weights_%s_%s_%s_bin%d_Down" % (region, category_id, other_labels2[region], re.sub("_201(\d)", "", category_id), b))

            ewk_up_w.SetBinContent(b + 1, ratio_ewk_up.GetBinContent(b + 1))
            ewk_down_w.SetBinContent(b + 1, ratio_ewk_down.GetBinContent(b + 1))

            output_file.WriteTObject(ewk_up_w)
            output_file.WriteTObject(ewk_down_w)

            channel_objects[region].add_nuisance_shape("%s_%s_bin%d" % (other_labels2[region], re.sub("_201(\d)", "", category_id), b), output_file)
