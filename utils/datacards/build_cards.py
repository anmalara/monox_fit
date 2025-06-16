import os
import subprocess
import argparse
from utils.workspace.flat_uncertainties import *
import CombineHarvester.CombineTools.ch as ch


class DatacardBuilder:
    def __init__(self, channel: str, year: str):
        self.ws_path = "root/combined_model_vbf.root"  # TODO: unused at the moment, needed to extract the shapes

        self.harvester = ch.CombineHarvester()

        ### Settings

        # TODO: make naming of variables consistent
        self.analysis = channel
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
        # TODO: could be refactored?
        # defining processes as keys, with values being list of regions + if they are signal or background

        ## SR
        # signal processes
        self.harvester.AddProcesses(
            procs=self.processes["signal"]["signals"],
            bin=[self.regions[0]],
            signal=True,
            **common_args,
        )

        # background processes (MC yields + models)
        self.harvester.AddProcesses(
            procs=self.processes["signal"]["backgrounds"] + self.processes["signal"]["models"],
            bin=[self.regions[0]],
            signal=False,
            **common_args,
        )

        ## CRs, only has background processes (MC yields + models)
        for region_idx, region_name in self.regions[1:]:
            proc_label = region_name.split("_")[-1]
            self.harvester.AddProcesses(
                procs=self.processes[proc_label]["backgrounds"] + self.processes[proc_label]["models"],
                bin=[(region_idx, region_name)],
                signal=False,
                **common_args,
            )

    def add_systematics(self):

        ### Systematics
        lumi_map = ch.SystMap("era", "bin_id", "process")
        for region_idx, region_name in self.regions:
            proc_label = region_name.split("_")[-1]
            lumi_map(
                ["Run3"],
                [region_idx],
                self.processes[proc_label]["signals"] + self.processes[proc_label]["backgrounds"],
                1.015,
            )

        self.harvester.AddSyst(
            target=self.harvester,
            name="lumi_$ERA",
            type="lnN",
            valmap=lumi_map,
        )

    def write_datacard(self):

        # Standardize bin names
        ch.SetStandardBinNames(self.harvester, "$CHANNEL_$ERA_$BIN")

        # Extract shapes
        # TODO: will require changes to the scripts building the workspace
        # self.harvester.cp().signals().ExtractShapes(self.ws_path, "category_vbf_$ERA:$CHANNEL_$ERA_$BIN_$PROCESS", "category_vbf_$ERA:$CHANNEL_$ERA_$BIN_$PROCESS_$SYSTEMATIC")
        # self.harvester.cp().backgrounds().ExtractShapes(self.ws_path, "category_vbf_Run3/$BIN/$PROCESS", "$BIN/$PROCESS_$SYSTEMATIC")

        # self.harvester.WriteDatacard("test.txt", "test.root")
        self.harvester.WriteDatacard("test.txt")


def main():
    parser = argparse.ArgumentParser(description="Arguments for workspace creation.")
    parser.add_argument("-y", "--year", type=str, default="Run3", help="Data-taking year (e.g., '2017', '2018', 'Run3').")
    parser.add_argument("-c", "--channel", type=str, default="vbf", help="Analysis name (e.g., 'vbf', 'monojet', 'monov').")
    args = parser.parse_args()

    channel, year = args.channel, args.year
    datacard_builder = DatacardBuilder(channel, year)

    datacard_builder.add_systematics()
    datacard_builder.write_datacard()

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
