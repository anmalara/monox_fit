import ROOT  # type:ignore
from typing import Any
from counting_experiment import Category, Channel
from utils.jes_utils import get_jes_variations, get_jes_jer_source_file_for_tf


def define_model(
    category_id: str,
    input_file: ROOT.TFile,
    samples_map: dict[str, str],
    output_file: ROOT.TFile,
    output_workspace: ROOT.RooWorkspace,
    convention: str,
    channel_names: dict[str, str],
    model_name: str,
    veto_dict: dict[str, float],
    year: int,
    target_name: str,
    veto_channel_list: list[str],
    jes_jer_channel_list: list[str],
    theory_channel_list: list[str],
    jes_jer_process: str,
    region_names: dict[str, str],
    category_name: str,
    diagonalizer: Any,
):

    # Some setup
    input_tdir = input_file.Get(f"category_{category_id}")
    input_wspace = input_tdir.Get(f"wspace_{category_id}")

    # Defining the nominal transfer factors
    # Nominal MC process to model
    target = input_tdir.Get(target_name)
    # Control MC samples
    control_samples = fetch_control_samples(input_tdir=input_tdir, samples_map=samples_map)

    # Compute and save a copy of the transfer factors (target divided by control)
    transfer_factors = define_transfer_factors(
        control_samples=control_samples,
        category_id=category_id,
        target_sample=target,
        output_file=output_file,
    )

    # label used for channel of each transfer factor

    # Create a `Channel` object for each transfer factor
    CRs = define_channels(
        transfer_factors=transfer_factors,
        category_id=category_id,
        input_wspace=input_wspace,
        output_workspace=output_workspace,
        convention=convention,
        channel_names=channel_names,
        model_name=model_name,
    )

    add_veto_nuisances(
        channel_objects=CRs,
        channel_list=veto_channel_list,
        veto_dict=veto_dict,
    )
    add_jes_jer_uncertainties(
        transfer_factors=transfer_factors,
        channel_objects=CRs,
        channel_list=jes_jer_channel_list,
        year=year,
        category_id=category_id,
        output_file=output_file,
        process=jes_jer_process,
        production_mode=model_name.split("_")[0],
    )
    add_theory_uncertainties(
        control_samples=control_samples,
        target_sample=target,
        channel_objects=CRs,
        channel_list=theory_channel_list,
        year=year,
        category_id=category_id,
        output_file=output_file,
    )

    # Add Bin by bin nuisances to cover statistical uncertainties
    for sample, transfer_factor in transfer_factors.items():
        do_stat_unc(transfer_factor, proc=sample, region=region_names[sample], CR=CRs[sample], cid=category_id, outfile=output_file)

    # Extract the bin edges of the distribution
    bin_edges = [target.GetBinLowEdge(b + 1) for b in range(target.GetNbinsX() + 1)]

    # Create and return `Category` object
    return Category(
        corrname=model_name,
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


def fetch_control_samples(
    input_tdir: ROOT.TDirectoryFile,
    samples_map: dict[str, str],
) -> dict[str : ROOT.TH1]:
    """
    Fetch all needed control MC samples used by the model.

    Args:
        input_tdir (ROOT.TDirectoryFile): Directory where samples are stored
        samples_map (dict[str, str]): Dictionnary mapping the name of the region / transfer factor to the name of the MC sample in the directory.
    """

    return {region_name: input_tdir.Get(sample_name) for region_name, sample_name in samples_map.items()}


def define_transfer_factors(
    control_samples: dict[str : ROOT.TH1],
    category_id: str,
    target_sample: ROOT.TH1,
    output_file: ROOT.TFile,
) -> dict[str : ROOT.TH1]:
    """
    Compute the transfer factors for each MC sample.

    Args:
        control_samples (dict[str, ROOT.TH1]): Dictionary mapping transfer factors labels to their control MC sample.
        category_id (str): Unique identifier for the category.
        target_sample (Any): Histogram of the target process.
        output_file (ROOT.TFile): Output ROOT file for a copy of the transfer factors.
    """
    transfer_factors = {}
    for label, sample in control_samples.items():
        factor = target_sample.Clone(f"{label}_weights_{category_id}")
        factor.Divide(sample)
        # transfer_factors[label] = factor
        transfer_factors.update({label: factor})
        output_file.WriteTObject(factor)
    return transfer_factors


def define_channels(
    transfer_factors: dict[str, ROOT.TH1],
    category_id: str,
    model_name: str,
    input_wspace: ROOT.RooWorkspace,
    output_workspace: ROOT.RooWorkspace,
    convention: str,
    channel_names: dict[str, str],
) -> dict[str, Channel]:
    """
    Stores transfer factors in Channel objects.

    Args:
        transfer_factors (dict[str, ROOT.TH1]): Dictionary mapping transfer factors labels to their distributions.
        category_id (str): Unique identifier for the category.
        model_name (str): Unique identifier for the model.
        input_wspace (ROOT.RooWorkspace): The input ROOT workspace containing the model parameters.
        output_workspace (ROOT.RooWorkspace): The output ROOT workspace used for importing variables and functions.
        convention (str): A string defining the naming convention used for systematic uncertainties ("IC" or "BU").
        channel_names (dict[str, str]): Dictionary mapping transfer factors labels to the name of their channels.
    """
    return {
        sample: Channel(
            cname=channel_names[sample],
            wspace=input_wspace,
            wspace_out=output_workspace,
            catid=category_id + "_" + model_name,
            scalefactors=transfer_factor,
            convention=convention,
        )
        for sample, transfer_factor in transfer_factors.items()
    }


def add_veto_nuisances(channel_objects: dict[str, Channel], channel_list: list[str], veto_dict: dict[str, float]) -> None:
    """
    Adds veto systematic uncertainties to the specified control regions.

    Args:
        channel_objects (dict[str, Channel]): Dictionary mapping control region names to `Channel` objects.
        channel_list (list[str]): List of control regions to apply veto uncertainties.
        veto_dict (dict[str, float]): Dictionnary mapping the name of the nuissance to add and its value.
    """

    for channel in channel_list:
        for veto_name, veto_value in veto_dict.items():
            channel_objects[channel].add_nuisance(veto_name, veto_value)


def add_jes_jer_uncertainties(
    transfer_factors: dict[str, Any],
    channel_objects: dict[str, Channel],
    channel_list: list[str],
    year: str,
    category_id: str,
    output_file: ROOT.TFile,
    process: str,
    production_mode: str,
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
        process (str): Label indicating the process being modeled, either "znunu" or "wlnu".
        production_mode (str): Label indicating the if the production_mode is strong or electroweak, either "qcd" or "ewk".
    """

    jes_region_labels = {
        "qcd_w": "wlnu",
        "qcd_zmm": "zmumu",
        "qcd_zee": "zee",
        "qcd_photon": "gjets",
        "qcd_wmn": "wmunu",
        "qcd_wen": "wenu",
        "ewk_w": "wlnu",
        "ewk_zmm": "zmumu",
        "ewk_zee": "zee",
        "ewk_photon": "gjets",
        "ewk_wmn": "wmunu",
        "ewk_wen": "wenu",
    }
    # Get the JES/JER uncertainty file for transfer factors
    # Read the split uncertainties from there
    fjes = get_jes_jer_source_file_for_tf(category="vbf")
    jet_variations = get_jes_variations(fjes, year, proc=production_mode)

    for sample in channel_list:
        for var in jet_variations:
            for var_direction in ["Up", "Down"]:
                # Scale transfer factor by relative variation and write to output file
                add_variation(
                    nominal=transfer_factors[sample],
                    unc_file=fjes,
                    unc_name=f"{process}_over_{jes_region_labels[sample]}{year-2000}_{production_mode}_{var}{var_direction}",
                    new_name=f"{sample}_weights_{category_id}_{var}_{var_direction}",
                    outfile=output_file,
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
    production_mode: str = "qcd",
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
        production_mode (str): Label indicating the if the production_mode is strong or electroweak, either "qcd" or "ewk".
    """

    # Save a (renamed) copy of samples used to derive theory variations
    # Done to perfectly mirrors what is done in Z_constraints_qcd_withphoton
    spectrum_label = {
        "qcd_w": "qcd_w",
        "qcd_photon": "qcd_gjets",
        "ewk_w": "ewk_w",
        "ewk_photon": "ewk_photon",
    }
    # TODO: also write Z->nunu spectrum
    spectrums = {region: control_samples[region].Clone() for region in channel_list}
    for region, sample in spectrums.items():
        sample.SetName(f"{spectrum_label[region]}_spectrum_{category_id}_")
        output_file.WriteTObject(sample)

    # File containting the theory uncertainties
    vbf_sys = ROOT.TFile.Open("sys/vbf_z_w_gjets_theory_unc_ratio_unc.root")

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
        "ewk_w": ("zoverw", "z", "ZnunuWJets", "ewk_ewk"),
        "ewk_photon": ("goverz", "gjets", "Photon", "ewkphoton_ewk"),
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
                # TODO: try to use add_variation
                add_var(
                    num=num,
                    denom=denom,
                    name=f"{region}_weights_{category_id}_{qcd_label}_{production_mode.upper()}_{var[1]}_vbf_{dir[1]}",
                    factor=vbf_sys.Get(f"uncertainty_ratio_{denom_label}_{production_mode}_mjj_unc_{ratio}_nlo_{var[0]}_{dir[0]}_{year}"),
                )

            # EWK uncertainty (decorrelated among bins)
            ratio_ewk = target_sample.Clone()
            ratio_ewk.SetName(f"{region}_weights_{category_id}_ewk_{dir[1]}")
            # todo: try
            # ratio_ewk = target_sample.Clone(f"{region}_weights_{category_id}_ewk_{dir[1]}")
            ratio_ewk.Divide(denom)
            ratio_ewk.Multiply(vbf_sys.Get(f"uncertainty_ratio_{denom_label}_{production_mode}_mjj_unc_w_ewkcorr_overz_common_{dir[0]}_{year}"))

            ewk_num = num.Clone()
            ewk_num.Divide(denom)

            for b in range(nbins):
                ewk_w = ewk_num.Clone()
                ewk_w.SetName(f"{region}_weights_{category_id}_{ewk_label}_{category_id.replace(f'_{year}', '')}_bin{b}_{dir[1]}")
                ewk_w.SetBinContent(b + 1, ratio_ewk.GetBinContent(b + 1))
                output_file.WriteTObject(ewk_w)

        # TODO: merge with previous loop?
        # Add function (quadratic) to model the nuisance
        # QCD and PDF
        for var in [("mur", "renscale"), ("muf", "facscale"), ("pdf", "pdf")]:
            channel_objects[region].add_nuisance_shape(f"{qcd_label}_{production_mode.upper()}_{var[1]}_vbf", output_file)
        # EWK (decorrelated among bins)
        for b in range(nbins):
            channel_objects[region].add_nuisance_shape(f"{ewk_label}_{category_id.replace(f'_{year}', '')}_bin{b}", output_file)


def do_stat_unc(histogram, proc, cid, region, CR, outfile, functype="lognorm"):
    """Add stat. unc. variations to the workspace"""

    # Add one variation per bin
    for b in range(1, histogram.GetNbinsX() + 1):
        err = histogram.GetBinError(b)
        content = histogram.GetBinContent(b)

        # Safety
        if (content <= 0) or (err / content < 0.001):
            # TODO: raise error and exit
            continue

        # Careful: The bin count "b" in this loop starts at 1
        # In the combine model, we want it to start from 0!
        up = histogram.Clone(f"{proc}_weights_{cid}_{cid}_stat_error_{region}_bin{b-1}_Up")
        down = histogram.Clone(f"{proc}_weights_{cid}_{cid}_stat_error_{region}_bin{b-1}_Down")
        up.SetBinContent(b, content + err)
        down.SetBinContent(b, content - err)
        outfile.WriteTObject(up)
        outfile.WriteTObject(down)

        print("Adding an error -- ", up.GetName(), err)
        CR.add_nuisance_shape(f"{cid}_stat_error_{region}_bin{b-1}", outfile, functype=functype)


# Ported from W_constraints, WIP
def add_variation(nominal, unc_file, unc_name, new_name, outfile, invert=False, scale=1):
    factor = unc_file.Get(unc_name)
    add_variation_from_histogram(nominal=nominal, factor=factor, new_name=new_name, outfile=outfile, invert=invert, scale=scale)


def add_variation_from_histogram(nominal, factor, new_name, outfile, invert=False, scale=1):
    variation = nominal.Clone(new_name)
    if factor.GetNbinsX() == 1:

        factor_value = factor.GetBinContent(1)
        if factor_value > 1:
            factor_value = 1 + (factor_value - 1) * scale
        else:
            factor_value = 1 - (1 - factor_value) * scale

        if invert:
            variation.Scale(1 / factor_value)
        else:
            variation.Scale(factor_value)

    else:
        scaled_factor = scale_variation_histogram(factor, scale)
        if invert:
            assert variation.Divide(scaled_factor)
        else:
            assert variation.Multiply(scaled_factor)
    outfile.WriteTObject(variation)


def scale_variation_histogram(histogram, scale):
    scaled = histogram.Clone(histogram.GetName())
    for i in range(1, scaled.GetNbinsX() + 1):
        content = scaled.GetBinContent(i)
        if content > 1:
            new_content = 1 + (content - 1) * scale
        else:
            new_content = 1 - (1 - content) * scale
        scaled.SetBinContent(i, new_content)
    return scaled
