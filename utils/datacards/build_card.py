import os
import CombineHarvester.CombineTools.ch as ch

# aux_path = "./root/combined_model_vbf.root"
aux_path = os.path.join(str(os.getenv("CMSSW_BASE")), "src/auxiliaries/shapes/")

cb = ch.CombineHarvester()

### Settings

analysis = "vbf"  # TODO: pass as an argument
eras = ["Run3"]  # TODO: pass as an argument

## Regions (common for all analyses)
region_names = ["signal", "dimuon", "dielec", "singlemu", "singleel", "photon"]
# put in the form (index, name) for CombineHarvester
regions = [(i, f"{analysis}_{region}") for i, region in enumerate(region_names)]

## Processes (might depend on the analysis)
processes = {
    "signal": {
        "signals": ["zh", "wh", "vbf", "ggh"],
        "backgrounds": ["diboson", "top", "qcdzll", "ewkzll"],
        "models": ["ewk_wjets", "qcd_wjets", "ewk_zjets", "qcd_zjets"],
    },
    "dimuon": {
        "signals": [],
        "backgrounds": ["diboson", "top"],
        "models": ["qcd_zll", "ewk_zll"],
    },
    "dielec": {
        "signals": [],
        "backgrounds": ["diboson", "top"],
        "models": ["qcd_zll", "ewk_zll"],
    },
    "singlemu": {
        "signals": [],
        "backgrounds": ["diboson", "top", "qcdzll", "ewkzll"],
        "models": ["ewk_wjets", "qcd_wjets"],
    },
    "singleel": {
        "signals": [],
        "backgrounds": ["diboson", "top", "qcdzll", "ewkzll"],
        "models": ["ewk_wjets", "qcd_wjets"],
    },
    "photon": {
        "signals": [],
        "backgrounds": [],
        "models": ["ewk_gjets", "qcd_gjets"],
    },
}


### Defining the regions
cb.AddObservations(
    mass=["*"],
    analysis=[analysis],
    era=eras,
    channel=[analysis],
    bin=regions,
)

### Defining the processes for each region
## SR
cb.AddProcesses(
    mass=["*"],
    analysis=[analysis],
    era=eras,
    channel=[analysis],
    procs=processes["signal"]["signals"],
    bin=[regions[0]],
    signal=True,
)

cb.AddProcesses(
    mass=["*"],
    analysis=[analysis],
    era=eras,
    channel=[analysis],
    procs=processes["signal"]["backgrounds"] + processes["signal"]["models"],
    bin=[regions[0]],
    signal=False,
)

## CRs
for region_idx, region_name in regions[1:]:
    cb.AddProcesses(
        mass=["*"],
        analysis=[analysis],
        era=eras,
        channel=[analysis],
        procs=processes[region_name.replace(f"{analysis}_", "")]["backgrounds"] + processes[region_name.replace(f"{analysis}_", "")]["models"],
        bin=[(region_idx, region_name)],
        signal=False,
    )

### Systematics
# WIP, Adapted from example in https://gitlab.cern.ch/cms-analysis/nps/common/datacard-tutorial#combine-tutorial-for-the-nps-workshop-2025
# cb.AddSyst(
#     target=cb,
#     name="lumi_$ERA",
#     type="lnN",
#     valmap=ch.SystMap("era")(["2016"], 1.010)(["2017"], 1.020)(["2018"], 1.015)(["Run3"], 1.015),
# )

#   cb.cp()
#       .AddSyst(cb,
#         "CMS_scale_j_$ERA", "lnN", SystMap<era, bin_id, process>::init
#         ({"8TeV"}, {1},     {"ggH"},        1.04)
#         ({"8TeV"}, {1},     {"qqH"},        0.99)
#         ({"8TeV"}, {2},     {"ggH"},        1.10)
#         ({"8TeV"}, {2},     {"qqH"},        1.04)
#         ({"8TeV"}, {2},     {"TT"},         1.05));

# import pdb

# pdb.set_trace()
# test_list = [(["Run3"], [region_idx], processes[region_name.replace(f"{analysis}_", "")]["backgrounds"], 1.015) for region_idx, region_name in regions]
test_tuple2 = tuple((["Run3"], [region_idx], processes[region_name.replace(f"{analysis}_", "")]["backgrounds"], 1.015) for region_idx, region_name in regions)
# test_tuple = (
#     (["Run3"], [0], processes["signal"]["backgrounds"], 1.015),
#     (["Run3"], [1], processes["signal"]["backgrounds"], 1.015),
#     (["Run3"], [2], processes["signal"]["backgrounds"], 1.015),
#     (["Run3"], [3], processes["signal"]["backgrounds"], 1.015),
#     (["Run3"], [4], processes["signal"]["backgrounds"], 1.015),
#     (["Run3"], [5], processes["signal"]["backgrounds"], 1.015),
# )

lumi_map = ch.SystMap("era", "bin_id", "process")
for region_idx, region_name in regions:
    lumi_map(
        ["Run3"],
        [region_idx],
        processes[region_name.replace(f"{analysis}_", "")]["signals"] + processes[region_name.replace(f"{analysis}_", "")]["backgrounds"],
        1.015,
    )

cb.AddSyst(
    target=cb,
    name="lumi_$ERA",
    type="lnN",
    valmap=lumi_map,
)
# valmap = (ch.SystMap("era")(["2016"], 1.010)(["2017"], 1.020)(["2018"], 1.015)(["Run3"], 1.015),)

# Models should not get lumi uncertainty

cb.WriteDatacard("test.txt", "test.root")
