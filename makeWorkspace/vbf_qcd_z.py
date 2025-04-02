import ROOT  # type:ignore
from counting_experiment import Category
from model_utils import *

# TODO: utils to be used by all models
model = "qcd_zjets"


def cmodel(
    category_id: str,
    category_name: str,
    input_file: ROOT.TFile,
    output_file: ROOT.TFile,
    output_workspace: ROOT.RooWorkspace,
    diagonalizer,
    year: int,
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

    # Some setup
    target_name = "signal_qcdzjets"

    # Control MC samples
    samples_map = {
        "qcd_zmm": "Zmm_qcdzll",
        "qcd_zee": "Zee_qcdzll",
        "qcd_w": "signal_qcdwjets",
        "ewkqcd": "signal_ewkzjets",
        "qcd_photon": "gjets_qcdgjets",
    }

    # label used for channel of each transfer factor
    channel_names = {
        "qcd_zmm": "qcd_dimuon",
        "qcd_zee": "qcd_dielectron",
        "qcd_w": "qcd_wjetssignal",
        "ewkqcd": "ewkqcd_signal",
        "qcd_photon": "qcd_photon",
    }

    veto_channel_list = ["qcd_w"]
    veto_dict = {
        f"CMS_veto{year}_t": -0.01,
        f"CMS_veto{year}_m": -0.015,
        f"CMS_veto{year}_e": -0.03,
    }

    jes_jer_channel_list = ["qcd_zmm", "qcd_zee", "qcd_w", "qcd_photon"]
    model_label = "znunu"
    production_mode = "qcd"
    theory_channel_list = ["qcd_w", "qcd_photon"]

    # label used for region of each transfer factor
    region_names = {
        "qcd_zmm": "qcd_dimuonCR",
        "qcd_zee": "qcd_dielectronCR",
        "qcd_w": "qcd_wzCR",
        "qcd_photon": "qcd_photonCR",
        "ewkqcd": "ewkqcdzCR",
    }

    cat = define_model(
        category_id=category_id,
        input_file=input_file,
        output_file=output_file,
        output_workspace=output_workspace,
        convention=convention,
        model_name=model,
        year=year,
        category_name=category_name,
        diagonalizer=diagonalizer,
        samples_map=samples_map,
        channel_names=channel_names,
        veto_dict=veto_dict,
        target_name=target_name,
        veto_channel_list=veto_channel_list,
        jes_jer_channel_list=jes_jer_channel_list,
        theory_channel_list=theory_channel_list,
        jes_jer_model=model_label,
        jes_jer_production=production_mode,
        region_names=region_names,
    )

    return cat
