import ROOT  # type:ignore
from counting_experiment import Category
from model_utils import *

model = "qcd_wjets"


def cmodel(
    category_id: str,
    category_name: str,
    input_file: ROOT.TFile,
    output_file: ROOT.TFile,
    output_workspace: ROOT.RooWorkspace,
    diagonalizer,
    year: str,
    variable: str,
    convention: str = "BU",
) -> Category:
    """
    Constructs a category model for QCD W+jets processes using control regions and transfer factors.

    This function:
    - Reads histograms from the input ROOT file.
    - Computes transfer factors by dividing the target signal by control regions.
    - Applies systematic uncertainties (JES/JER, and veto nuisances).
    - Adds bin-by-bin statistical uncertainties.
    - Creates and returns a `Category` object.

    Args:
        category_id (str): Unique identifier for the category.
        category_name (str): Human-readable name for the category.
        input_file (ROOT.TFile): Input ROOT file containing relevant histograms.
        output_file (ROOT.TFile): Output ROOT file for storing processed histograms.
        output_workspace (ROOT.RooWorkspace): Output workspace for RooFit objects.
        diagonalizer: Diagonalizer to pass to `Category`
        year (str): Data-taking year.
        convention (str, optional): Naming convention for transfer factors. Defaults to "BU".

    Returns:
        Category: A `Category` object encapsulating the modeled process.
    """

    model_args = {
        "model_name": model,
        # Name of the target sample in the input ROOT file.
        "target_name": "signal_qcdwjets",
        # Mapping of control sample names to their ROOT file entries.
        "samples_map": {
            "qcd_wmn": "Wmn_qcdwjets",
            "qcd_wen": "Wen_qcdwjets",
        },
        # Mapping of transfer factor labels to channel names.
        "channel_names": {
            "qcd_wmn": "qcd_singlemuon",
            "qcd_wen": "qcd_singleelectron",
        },
        # TODO: lepton veto uncertainties from sys file (ele id, ele reco, mu id, mu iso, tau id; both wmn and wen)
        # TODO: electron id and iso uncertainties from sys file (wen region only)
        # TODO: prefiring uncertainties (both wmn and wen)
        # TODO: pdf uncertainties (both wmn and wen)
        # Channels where veto uncertainties are applied.
        "veto_channel_list": ["qcd_wmn", "qcd_wen"],
        # Channels where trigger uncertainties are applied.
        "trigger_channel_list": ["qcd_wmn"],
        # Channels where JES/JER uncertainties are applied.
        "jes_jer_channel_list": ["qcd_wmn", "qcd_wen"],
        "jes_jer_process": "wlnu",
        # Channels where theory uncertainties are applied.
        "theory_channel_list": [],
        # Mapping of transfer factor labels to region names.
        "region_names": {
            "qcd_wmn": "qcd_singlemuon",
            "qcd_wen": "qcd_singleelectron",
        },
        "prefiring_channel_list": ["qcd_wmn", "qcd_wen"],
    }

    cat = define_model(
        # arguments of `cmodel`
        category_id=category_id,
        category_name=category_name,
        input_file=input_file,
        output_file=output_file,
        output_workspace=output_workspace,
        diagonalizer=diagonalizer,
        year=year,
        variable=variable,
        convention=convention,
        # model-specific arguments
        **model_args,
    )

    # Specify this is dependant on QCD (Z->nunu / W->lnu) in SR from corresponding channel in vbf_qcd_z
    cat.setDependant("qcd_zjets", "qcd_wjetssignal")
    return cat
