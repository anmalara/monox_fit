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
    Constructs a category model for QCD Z+jets processes using control regions and transfer factors.

    This function:
    - Reads histograms from the input ROOT file.
    - Computes transfer factors by dividing the target signal by control regions.
    - Applies systematic uncertainties (JES/JER, theory, and veto nuisances).
    - Adds bin-by-bin statistical uncertainties.
    - Creates and returns a `Category` object.

    Args:
        category_id (str): Unique identifier for the category.
        category_name (str): Human-readable name for the category.
        input_file (ROOT.TFile): Input ROOT file containing relevant histograms.
        output_file (ROOT.TFile): Output ROOT file for storing processed histograms.
        output_workspace (ROOT.RooWorkspace): Output workspace for RooFit objects.
        diagonalizer (bool): Flag for diagnostics or debugging.
        year (int): Data-taking year.
        convention (str, optional): Naming convention for transfer factors. Defaults to "BU".

    Returns:
        Category: A `Category` object encapsulating the modeled process.
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
        corrname=model,
        catid=category_id,
        cname=category_name,
        _fin=input_tdir,
        _fout=output_file,
        _wspace=input_wspace,
        _wspace_out=output_workspace,
        _bins=[target.GetBinLowEdge(b + 1) for b in range(target.GetNbinsX() + 1)],
        _varname="mjj",
        _target_datasetname=target.GetName(),
        _control_regions=list(CRs.values()),
        diag=diagonalizer,
        convention=convention,
    )
    return cat


def add_veto_nuisances(channel_objects: dict[str, Channel], channel_list: list[str], year: str) -> None:
    """
    Adds veto systematic uncertainties to the specified control regions.

    Args:
        channel_objects (dict[str, Channel]): Dictionary mapping control region names to `Channel` objects.
        channel_list (list[str]): List of control regions to apply veto uncertainties.
        year (str): Data-taking year.
    """

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
    """
    Adds JES and JER uncertainties to transfer factors.

    This function:
    - Retrieves JES/JER uncertainty variations from an external file.
    - Applies up/down variations to transfer factors.
    - Stores the modified transfer factors in the output file.
    - Adds nuisance parameters for JES/JER uncertainties to the corresponding channels.

    Args:
        transfer_factors (dict[str, Any]): Dictionary of transfer factors.
        channel_objects (dict[str, Channel]): Dictionary of `Channel` objects.
        channel_list (list[str]): List of control regions to apply JES/JER uncertainties.
        year (str): Data-taking year.
        category_id (str): Unique identifier for the category.
        output_file (ROOT.TFile): Output ROOT file for storing variations.
    """

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
    """
    Adds theoretical uncertainties (scale, PDF, and EWK corrections) to transfer factors.

    This function:
    - Saves copies of control samples used to derive theory variations.
    - Retrieves theoretical uncertainty histograms from an external file.
    - Computes and stores up/down variations for QCD scale, PDF, and EWK uncertainties.
    - Applies bin-by-bin decorrelated EWK uncertainties.
    - Adds nuisance parameters for theoretical uncertainties to the corresponding channels.

    Args:
        control_samples (dict[str, Any]): Dictionary of control region histograms.
        target_sample (Any): Histogram of the target process.
        channel_objects (dict[str, Channel]): Dictionary of `Channel` objects.
        channel_list (list[str]): List of control regions to apply theoretical uncertainties.
        year (str): Data-taking year.
        category_id (str): Unique identifier for the category.
        output_file (ROOT.TFile): Output ROOT file for storing variations.
    """

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

    # different labels to convert naming scheme between the different histogram and nuisances to read and write
    label_dict = {
        "qcd_w": ("zoverw", "z", "ZnunuWJets", "qcd_ewk"),
        "qcd_photon": ("goverz", "gjets", "Photon", "qcd_photon_ewk"),
    }

    for region in channel_list:
        ratio, denom_label, qcd_label, ewk_label = label_dict[region]

        denom = control_samples[region].Clone()
        denom.SetName(f"{region}_weights_denom_{category_id}")
        num = target_sample.Clone()
        num.SetName(f"{region}_weights_nom_{category_id}")

        for dir in [("up", "Up"), ("down", "Down")]:
            # Add QCD and PDF uncertainties
            for var in [("mur", "renscale"), ("muf", "facscale"), ("pdf", "pdf")]:
                add_var(
                    num=num,
                    denom=denom,
                    name=f"{region}_weights_{category_id}_{qcd_label}_QCD_{var[1]}_vbf_{dir[1]}",
                    factor=vbf_sys.Get(f"uncertainty_ratio_{denom_label}_qcd_mjj_unc_{ratio}_nlo_{var[0]}_{dir[0]}_{year}"),
                )

            # EWK uncertainty (decorrelated among bins)
            ratio_ewk = target_sample.Clone()
            ratio_ewk.SetName(f"{region}_weights_{category_id}_ewk_{dir[1]}")
            ratio_ewk.Divide(denom)
            ratio_ewk.Multiply(vbf_sys.Get(f"uncertainty_ratio_{denom_label}_qcd_mjj_unc_w_ewkcorr_overz_common_{dir[0]}_{year}"))

            ewk_num = num.Clone()
            ewk_num.Divide(denom)

            for b in range(nbins):
                ewk_w = ewk_num.Clone()
                ewk_w.SetName(f"{region}_weights_{category_id}_{ewk_label}_{category_id.replace(f'_{year}', '')}_bin{b}_{dir[1]}")
                ewk_w.SetBinContent(b + 1, ratio_ewk.GetBinContent(b + 1))
                output_file.WriteTObject(ewk_w)

        # Add function (quadratic) to model the nuisance
        # QCD and PDF
        for var in [("mur", "renscale"), ("muf", "facscale"), ("pdf", "pdf")]:
            channel_objects[region].add_nuisance_shape(f"{qcd_label}_QCD_{var[1]}_vbf", output_file)
        # EWK (decorrelated among bins)
        for b in range(nbins):
            channel_objects[region].add_nuisance_shape(f"{ewk_label}_{category_id.replace(f'_{year}', '')}_bin{b}", output_file)
