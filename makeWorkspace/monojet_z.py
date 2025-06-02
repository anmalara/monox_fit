import ROOT  # type:ignore
from counting_experiment import Category
from model_utils import *

model = "zjets"


def cmodel(
    category_id: str,
    category_name: str,
    input_file: ROOT.TFile,
    output_file: ROOT.TFile,
    output_workspace: ROOT.RooWorkspace,
    diagonalizer,
    year: int,
    variable: str,
    convention: str = "BU",
) -> Category:
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
        diagonalizer: Diagonalizer to pass to `Category`
        year (int): Data-taking year.
        convention (str, optional): Naming convention for transfer factors. Defaults to "BU".

    Returns:
        Category: A `Category` object encapsulating the modeled process.
    """

    model_args = {
        "model_name": model,
        # Name of the target sample in the input ROOT file.
        "target_name": "signal_zjets",
        # Mapping of control sample names to their ROOT file entries.
        "samples_map": {
            "zmm": "Zmm_qcdzll",
            "zee": "Zee_qcdzll",
            "w": "signal_qcdwjets",
            "photon": "gjets_qcdgjets",
        },
        # Mapping of transfer factor labels to channel names.
        "channel_names": {
            "zmm": "dimuon",
            "zee": "dielectron",
            "w": "wjetssignal",
            "photon": "photon",
        },
        # TODO: trigger uncertainties
        # TODO: We want to correlate experimental uncertainties between the loose and tight regions.
        # TODO: Take the square of the uncertainty because we are going from zero to two leptons
        # Channels where veto uncertainties are applied.
        "veto_channel_list": ["w"],
        "veto_dict": {
            f"CMS_veto{year}_t": -0.01,
            f"CMS_veto{year}_m": -0.015,
            f"CMS_veto{year}_e": -0.03,
        },
        # Channels where JES/JER uncertainties are applied.
        "jes_jer_channel_list": ["zmm", "zee", "w", "photon"],
        "jes_jer_process": "znunu",
        # Channels where theory uncertainties are applied.
        "theory_channel_list": ["w", "photon"],
        # Mapping of transfer factor labels to region names.
        "region_names": {
            "zmm": "dimuonCR",
            "zee": "dielectronCR",
            "w": "wzCR",
            "photon": "photonCR",
        },
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

    return cat
