import ROOT  # type:ignore
from counting_experiment import Channel, Category
from vbf_qcd_z import add_veto_nuisances, add_jes_jer_uncertainties, do_stat_unc, define_transfer_factors

model = "qcd_wjets"


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
    target = input_tdir.Get("signal_qcdwjets")
    # Control MC samples
    control_samples = {
        "qcd_wmn": input_tdir.Get("Wmn_qcdwjets"),
        "qcd_wen": input_tdir.Get("Wen_qcdwjets"),
    }

    # Compute and save a copy of the transfer factors (target divided by control)
    transfer_factors = define_transfer_factors(
        control_samples=control_samples,
        category_id=category_id,
        target_sample=target,
        output_file=output_file,
    )

    # label used for channel of each transfer factor
    channel_names = {
        "qcd_wmn": "qcd_singlemuon",
        "qcd_wen": "qcd_singleelectron",
    }

    # Create a `Channel` object for each transfer factor
    CRs = {
        sample: Channel(channel_names[sample], input_wspace, output_workspace, category_id + "_" + model, transfer_factor, convention=convention)
        for sample, transfer_factor in transfer_factors.items()
    }

    add_veto_nuisances(
        CRs,
        channel_list=["qcd_wmn", "qcd_wen"],
        veto_dict={
            f"CMS_veto{year}_t": 0.01,
            f"CMS_veto{year}_m": 0.015,
            f"CMS_veto{year}_e": 0.03,
        },
    )
    add_jes_jer_uncertainties(
        transfer_factors,
        CRs,
        channel_list=["qcd_wmn", "qcd_wen"],
        year=year,
        category_id=category_id,
        output_file=output_file,
        process="wlnu",
        production_mode="qcd",
    )

    # label used for region of each transfer factor
    region_names = {
        "qcd_wmn": "qcd_singlemuon",
        "qcd_wen": "qcd_singleelectron",
    }
    # Add Bin by bin nuisances to cover statistical uncertainties
    for sample, transfer_factor in transfer_factors.items():
        do_stat_unc(transfer_factor, proc=sample, region=region_names[sample], CR=CRs[sample], cid=category_id, outfile=output_file)

    # Create `Category` object
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

    # Specify this is dependant on QCD (Z->nunu / W->lnu) in SR from corresponding channel in vbf_qcd_z
    cat.setDependant("qcd_zjets", "qcd_wjetssignal")
    return cat
