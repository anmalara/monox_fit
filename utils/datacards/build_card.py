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
# processes = {
#     "signal": ["zh", "wh", "vbf", "ggh"],
#     "background": ["diboson", "top", "qcdzll", "ewkzll"],
#     "model": [f"{mode}_{proc}" for mode in ["qcd", "ewk"] for proc in ["zjets", "wjets", "gjets", "zll"]],
# }

processes = {
    "signal": {
        "signals": ["zh", "wh", "vbf", "ggh"],
        "backgrounds": ["diboson", "top", "qcdzll", "ewkzll", "ewk_wjets", "qcd_wjets", "ewk_zjets", "qcd_zjets"],
    },
    "dimuon": {
        "signals": [],
        "backgrounds": ["diboson", "top", "qcd_zll", "ewk_zll"],
    },
    "dielec": {
        "signals": [],
        "backgrounds": ["diboson", "top", "qcd_zll", "ewk_zll"],
    },
    "singlemu": {
        "signals": [],
        "backgrounds": ["diboson", "top", "qcdzll", "ewkzll", "ewk_wjets", "qcd_wjets"],
    },
    "singleel": {
        "signals": [],
        "backgrounds": ["diboson", "top", "qcdzll", "ewkzll", "ewk_wjets", "qcd_wjets"],
    },
    "photon": {
        "signals": [],
        "backgrounds": ["ewk_gjets", "qcd_gjets"],
    },
}


cb.AddObservations(
    mass=["*"],
    analysis=[analysis],
    era=eras,
    channel=[analysis],
    bin=regions,
)

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
    procs=processes["signal"]["backgrounds"],
    bin=[regions[0]],
    signal=False,
)

for region_idx, region_name in regions[1:]:
    cb.AddProcesses(
        mass=["*"],
        analysis=[analysis],
        era=eras,
        channel=[analysis],
        procs=processes[region_name.replace(f"{analysis}_", "")]["backgrounds"],
        bin=[(region_idx, region_name)],
        signal=False,
    )


# for i, region in regions:
#     cb.cp().WriteDatacard(f"{region}_{analysis}.txt", f"{region}_{analysis}.root")
cb.WriteDatacard("test.txt", "test.root")
