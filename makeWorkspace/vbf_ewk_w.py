from counting_experiment import Channel, Category
from vbf_qcd_z import add_veto_nuisances, add_jes_jer_uncertainties, do_stat_unc

model = "ewk_wjets"


def cmodel(category_id, category_name, input_file, output_file, output_workspace, diagonalizer, year, convention="BU"):
    """
    Constructs a category model for EWK W+jets processes using control regions and transfer factors.

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
    target = input_tdir.Get("signal_ewkwjets")
    # Control MC samples
    control_samples = {
        "ewk_wmn": input_tdir.Get("Wmn_ewkwjets"),
        "ewk_wen": input_tdir.Get("Wen_ewkwjets"),
    }

    # Compute and save a copy of the transfer factors (target divided by control)
    transfer_factors = {region: target.Clone() for region in control_samples.keys()}
    for label, sample in transfer_factors.items():
        sample.SetName(f"{label}_weights_{category_id}")
        sample.Divide(control_samples[label])

        output_file.WriteTObject(sample)

    # label used for channel of each transfer factor
    channel_names = {
        "ewk_wmn": "ewk_singlemuon",
        "ewk_wen": "ewk_singleelectron",
    }

    # Create a `Channel` object for each transfer factor
    CRs = {
        sample: Channel(channel_names[sample], input_wspace, output_workspace, category_id + "_" + model, transfer_factor, convention=convention)
        for sample, transfer_factor in transfer_factors.items()
    }

    add_veto_nuisances(
        CRs,
        channel_list=["ewk_wmn", "ewk_wen"],
        veto_dict={
            f"CMS_veto{year}_t": 0.01,
            f"CMS_veto{year}_m": 0.02,
            f"CMS_veto{year}_e": 0.03,
        },
    )
    add_jes_jer_uncertainties(
        transfer_factors,
        CRs,
        channel_list=["ewk_wmn", "ewk_wen"],
        year=year,
        category_id=category_id,
        output_file=output_file,
        model_label="wlnu",
        process="ewk",
    )

    # label used for region of each transfer factor
    region_names = {
        "ewk_wmn": "ewk_singlemuon",
        "ewk_wen": "ewk_singleelectron",
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

    # Specify this is dependant on EWK (Z->nunu / W->lnu) in SR from corresponding channel in vbf_ewk_z
    cat.setDependant("ewk_zjets", "ewk_wjetssignal")
    return cat
