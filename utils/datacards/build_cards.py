import os
import subprocess
import argparse
from utils.workspace.flat_uncertainties import *
import CombineHarvester.CombineTools.ch as ch


class DatacardBuilder:
    def __init__(self, channel: str, year: str):
        os.makedirs("cards", exist_ok=True)
        self.ws_path = "root/combined_model_vbf.root"  # TODO: unused at the moment, needed to extract the shapes

        self.harvester = ch.CombineHarvester()

        ### Settings

        # TODO: make naming of variables consistent
        self.analysis = channel
        self.year = year
        self.eras = [year]

        ## Regions (common for all analyses)
        self.region_names = ["signal", "dimuon", "dielec", "singlemu", "singleel", "photon"]
        # put in the form (index, name) for CombineHarvester
        self.regions = [(i, f"{region}") for i, region in enumerate(self.region_names)]

        self.init_processes()

    def init_processes(self):
        ## Processes
        # TODO: might vary depending on the analysis
        self.processes = {
            "vbf": {
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
            },
            "monojet": {
                # TODO: replace with proper processes. Here: copied from vbf
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
            },
        }[self.analysis]

        # Common arguments
        common_args = {
            "mass": ["*"],
            "analysis": [self.analysis],
            "era": self.eras,
            "channel": [self.analysis],
        }

        ### Add the "Observation" entry for each region
        self.harvester.AddObservations(bin=self.regions, **common_args)

        ### Defining the processes for each region
        for region_idx, region_name in self.regions:
            proc_label = region_name.split("_")[-1]

            # Signals (effectively only for the SR)
            self.harvester.AddProcesses(
                procs=self.processes[proc_label]["signals"],
                bin=[(region_idx, region_name)],
                signal=True,
                **common_args,
            )

            # Backgrounds and models
            self.harvester.AddProcesses(
                procs=self.processes[proc_label]["backgrounds"] + self.processes[proc_label]["models"],
                bin=[(region_idx, region_name)],
                signal=False,
                **common_args,
            )

        # Manually fixing rate and observation
        self.harvester.ForEachProc(
            lambda x: x.set_rate(
                -1
                if x.process()
                not in [
                    "ewk_zll",
                    "qcd_zll",
                    "ewk_zjets",
                    "qcd_zjets",
                    "ewk_wjets",
                    "qcd_wjets",
                    "ewk_gjets",
                    "qcd_gjets",
                ]
                else 1
            )
        )
        self.harvester.ForEachObs(lambda x: x.set_rate(-1))

    def add_systematics(self, syst_dict, syst_type: str):

        ### Systematics

        for syst_name, syst_val in syst_dict.items():
            map = self.build_syst_map(syst_val)

            self.harvester.AddSyst(
                target=self.harvester,
                name=syst_name,
                type=syst_type,
                valmap=map,
            )

    def build_syst_map(self, syst_val):

        syst_map = ch.SystMap("era", "bin_id", "process")
        if "value" in syst_val:
            for region_idx, region_name in self.regions:
                syst_map(
                    ["Run3"],
                    [region_idx],
                    syst_val["processes"],
                    syst_val["value"],
                )
        else:
            for region_idx, region_name in self.regions:
                proc_label = region_name.split("_")[-1]
                if proc_label in syst_val:
                    syst_map(
                        ["Run3"],
                        [region_idx],
                        syst_val[proc_label]["processes"],
                        syst_val[proc_label]["value"],
                    )

        return syst_map

    def write_datacard(self):

        # Standardize bin names
        ch.SetStandardBinNames(self.harvester, "$CHANNEL_$ERA_$BIN")

        # Extract shapes
        # TODO: will require changes to the scripts building the workspace
        # self.harvester.cp().signals().ExtractShapes(self.ws_path, "category_vbf_$ERA:$CHANNEL_$ERA_$BIN_$PROCESS", "category_vbf_$ERA:$CHANNEL_$ERA_$BIN_$PROCESS_$SYSTEMATIC")
        # self.harvester.cp().backgrounds().ExtractShapes(self.ws_path, "category_vbf_Run3/$BIN/$PROCESS", "$BIN/$PROCESS_$SYSTEMATIC")

        # self.harvester.WriteDatacard("test.txt", "test.root")
        self.harvester.WriteDatacard(f"cards/card_{self.analysis}_{self.year}.txt")


def main():
    parser = argparse.ArgumentParser(description="Arguments for workspace creation.")
    parser.add_argument("-y", "--year", type=str, default="Run3", help="Data-taking year (e.g., '2017', '2018', 'Run3').")
    parser.add_argument("-c", "--channel", type=str, default="vbf", help="Analysis name (e.g., 'vbf', 'monojet', 'monov').")
    args = parser.parse_args()

    channel, year = args.channel, args.year
    datacard_builder = DatacardBuilder(channel, year)

    datacard_builder.add_systematics(get_lumi_uncertainties(year), "lnN")
    datacard_builder.add_systematics(get_lepton_efficiency_uncertainties(year), "lnN")
    datacard_builder.add_systematics(get_trigger_uncertainties(year), "lnN")
    datacard_builder.add_systematics(get_qcd_uncertainties(year), "lnN")
    datacard_builder.add_systematics(get_pdf_uncertainties(year), "lnN")
    datacard_builder.add_systematics(get_misc_uncertainties(year), "lnN")
    datacard_builder.add_systematics(get_jer_shape(), "shape")

    # Add all constrained nuisance parameters
    # TODO: there does not seem to be a proper way to add these using CombineHarvester
    # Could this be done in a cleaner way if changes are made to the workspace building scripts?
    for nuis_name in (
        [f"CMS_veto{year}_{l}" for l in ["t", "m", "e"]]
        + [jer for jer in get_jer_shape()]
        + [
            f"{channel}_{year}_stat_error_{region}_bin{i}"
            for region in [
                "qcd_dimuonCR",
                "qcd_dielectronCR",
                "qcd_wzCR",
                "qcd_photonCR",
                "ewkqcdzCR",
                "qcd_singlemuon",
                "qcd_singleelectron",
                "ewk_dimuonCR",
                "ewk_dielectronCR",
                "ewk_wzCR",
                "ewk_photonCR",
                "ewk_singlemuon",
                "ewk_singleelectron",
            ]
            for i in range(12)
        ]
        + [f"{ratio}_{channel}_bin{i}" for ratio in ["qcd_ewk", "qcd_photon_ewk", "ewk_ewk", "ewkphoton_ewk"] for i in range(12)]
        + [
            f"{ratio}_{production_mode}_{theory_unc}_{channel}"
            for ratio in ["ZnunuWJets", "Photon"]
            for production_mode in ["QCD", "EWK"]
            for theory_unc in ["renscale", "facscale", "pdf"]
        ]
    ):
        datacard_builder.harvester.AddDatacardLineAtEnd(f"{nuis_name} param 0.0 1")

    datacard_builder.write_datacard()

    # Manually fix path of shapes
    with open(f"cards/card_{channel}_{year}.txt") as f:
        content = f.readlines()
        idx_list = [i for i, line in enumerate(content) if line.startswith("shapes")]

        for idx in idx_list[::-1]:  # Reverse order to avoid index issues
            content.pop(idx)  # Remove the line

        current_idx = idx_list[0]

        for region, region_old in [("dielec", "Zee"), ("dimuon", "Zmm"), ("signal", "signal"), ("singleel", "Wen"), ("singlemu", "Wmn"), ("photon", "gjets")]:
            shapes_list = (
                [
                    f"shapes *                 {channel}_{year}_{region}    combined_model.root combinedws:{channel}_{year}_{region_old}_$PROCESS combinedws:vbf_{year}_{region_old}_$PROCESS_$SYSTEMATIC\n",
                    f"shapes data_obs          {channel}_{year}_{region}    combined_model.root combinedws:{channel}_{year}_{region_old}_data\n",
                ]
                if region != "photon"
                else [
                    f"shapes *                 {channel}_{year}_{region}    combined_model.root combinedws:{channel}_{year}_{region_old}_$PROCESS\n",
                    f"shapes data_obs          {channel}_{year}_{region}    combined_model.root combinedws:{channel}_{year}_{region_old}_data\n",
                ]
            )

            region_models = {
                "dielec": [("ewk_zll", "ewk_dielectron_ewk_zjets"), ("qcd_zll", "qcd_dielectron_qcd_zjets")],
                "dimuon": [("ewk_zll", "ewk_dimuon_ewk_zjets"), ("qcd_zll", "qcd_dimuon_qcd_zjets")],
                "signal": [
                    ("ewk_wjets", "ewk_wjetssignal_ewk_zjets"),
                    ("ewk_zjets", "ewkqcd_signal_qcd_zjets"),
                    ("qcd_wjets", "qcd_wjetssignal_qcd_zjets"),
                    ("qcd_zjets", "signal_qcd_zjets"),
                ],
                "singleel": [("ewk_wjets", "ewk_singleelectron_ewk_wjets"), ("qcd_wjets", "qcd_singleelectron_qcd_wjets")],
                "singlemu": [("ewk_wjets", "ewk_singlemuon_ewk_wjets"), ("qcd_wjets", "qcd_singlemuon_qcd_wjets")],
                "photon": [("ewk_gjets", "ewk_photon_ewk_zjets"), ("qcd_gjets", "qcd_photon_qcd_zjets")],
            }[region]
            shapes_list += [
                f"shapes {model}           {channel}_{year}_{region}    combined_model.root combinedws:{channel}_{year}_{model_old}_model\n"
                for model, model_old in region_models
            ]

            for l in shapes_list:
                content.insert(current_idx, l)
                current_idx += 1

    with open(f"cards/card_{channel}_{year}.txt", "w") as f:
        f.write("".join(content))

    # TODO: check that this works for monojet
    # Remove useless stat uncertainties
    # Uncertainties are removed if they do not have a variation histogram available
    # The criteria for whether a variation histogram is present are defined in make_ws.py

    # Get the list of nuisances from the ROOT file
    # rootls_cmd = ["rootls", "-1", f"root/ws_{channel}.root:category_{channel}_{year}"]
    # rootls_out = subprocess.run(rootls_cmd, stdout=subprocess.PIPE, check=True)
    # workspace_nuis = rootls_out.stdout.decode("utf-8").splitlines()

    # # Getting stat nuisances present in the datacard
    # with open(datacard_builder.card_path, "r") as file:
    #     datacard_nuis = [l.split(" ")[0] for l in file.readlines() if "shape" in l and "stat" in l.split(" ")[0]]

    # # Check if the nuisances are present in the ROOT file
    # for nuis in datacard_nuis:
    #     if f"{nuis}Up" not in workspace_nuis:
    #         # If the nuisance is not present, remove it from the datacard
    #         content = "\n".join(line for line in content.splitlines() if not line.startswith(nuis))
    #         print(f"Warning: removing nuisance {nuis} from {datacard_builder.card_path}, shape not present in ws_{channel}.root")

    # Write the modified content to the datacard file
    exit()

    # Run external tools
    subprocess.run(["text2workspace.py", datacard_builder.card_path, "--channel-masks"], check=True)
    with open(f"cards/systematics_{year}.html", "w") as outfile:
        subprocess.run(
            [
                "python3",
                os.path.join(os.environ["CMSSW_BASE"], "src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py"),
                "--all",
                "-f",
                "html",
                datacard_builder.card_path,
            ],
            check=True,
            stdout=outfile,
        )


if __name__ == "__main__":
    main()
