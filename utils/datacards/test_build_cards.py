import os
import CombineHarvester.CombineTools.ch as ch

aux_path = "root/combined_model_vbf.root"

cb = ch.CombineHarvester()

### Settings

analysis = "vbf"  # TODO: pass as an argument
eras = ["Run3"]  # TODO: pass as an argument

## Regions (common for all analyses)
region_names = ["signal", "dimuon", "dielec", "singlemu", "singleel", "photon"]
# put in the form (index, name) for CombineHarvester
regions = [(i, f"{region}") for i, region in enumerate(region_names)]

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
    proc_label = region_name.split("_")[-1]
    cb.AddProcesses(
        mass=["*"],
        analysis=[analysis],
        era=eras,
        channel=[analysis],
        procs=processes[proc_label]["backgrounds"] + processes[proc_label]["models"],
        bin=[(region_idx, region_name)],
        signal=False,
    )

### Systematics
# WIP, Adapted from example in https://gitlab.cern.ch/cms-analysis/nps/common/datacard-tutorial#combine-tutorial-for-the-nps-workshop-2025
lumi_map = ch.SystMap("era", "bin_id", "process")
for region_idx, region_name in regions:
    proc_label = region_name.split("_")[-1]
    lumi_map(
        ["Run3"],
        [region_idx],
        processes[proc_label]["signals"] + processes[proc_label]["backgrounds"],
        1.015,
    )

cb.AddSyst(
    target=cb,
    name="lumi_$ERA",
    type="lnN",
    valmap=lumi_map,
)

# Standardize bin names
ch.SetStandardBinNames(cb, "$CHANNEL_$ERA_$BIN")

# Extract shapes
# TODO: will require changes to the scripts building the workspace
# cb.cp().signals().ExtractShapes(aux_path, "category_vbf_$ERA:$CHANNEL_$ERA_$BIN_$PROCESS", "category_vbf_$ERA:$CHANNEL_$ERA_$BIN_$PROCESS_$SYSTEMATIC")
# cb.cp().backgrounds().ExtractShapes(aux_path, "category_vbf_Run3/$BIN/$PROCESS", "$BIN/$PROCESS_$SYSTEMATIC")

# cb.WriteDatacard("test.txt", "test.root")
cb.WriteDatacard("test.txt")
