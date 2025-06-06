import os
import CombineHarvester.CombineTools.ch as ch

# aux_path = "./root/combined_model_vbf.root"
aux_path = os.path.join(str(os.getenv("CMSSW_BASE")), "src/auxiliaries/shapes/")

cb = ch.CombineHarvester()
# categories = ch.Categories(
#     {
#         {1, "vbf_signal"},
#         {2, "vbf_dimuon"},
#         {3, "vbf_dielec"},
#         {4, "vbf_singlemu"},
#         {5, "vbf_singleel"},
#         {6, "vbf_photon"},
#     }
# )

analysis = "vbf"
eras = ["Run3"]
region_names = ["signal", "dimuon", "dielec", "singlemu", "singleel", "photon"]
processes = {
    "signal": ["zh", "wh", "vbf", "ggh"],
    "background": ["diboson", "top", "qcdzll", "ewkzll"],
    "model": [f"{mode}_{proc}" for mode in ["qcd", "ewk"] for proc in ["zjets", "wjets", "gjets", "zll"]],
}

regions = [(i, f"{analysis}_{region}") for i, region in enumerate(region_names)]

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
    procs=processes["signal"],
    bin=[regions[0]],
    signal=True,
)


# for i, region in regions:
#     cb.cp().WriteDatacard(f"{region}_{analysis}.txt", f"{region}_{analysis}.root")
cb.WriteDatacard("test.txt", "test.root")
