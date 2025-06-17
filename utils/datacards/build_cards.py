#!/usr/bin/env python3
import os
import subprocess
import argparse
from utils.workspace.flat_uncertainties import *
import CombineHarvester.CombineTools.ch as ch  # type: ignore


class DatacardBuilder:
    def __init__(self, channel: str, year: str):
        ### Settings
        self.analysis = channel
        self.year = year
        self.eras = [year]
        self.ws_path = f"../root/combined_model_{self.analysis}.root"
        self.card_path = f"cards/card_{self.analysis}_{self.year}.txt"

        self.harvester = ch.CombineHarvester()

        os.makedirs("cards", exist_ok=True)

        ## Regions (common for all analyses)
        self.region_names = ["signal", "dimuon", "dielec", "singlemu", "singleel", "photon"]
        # put in the form (index, name) for CombineHarvester
        self.regions = [(idx, region) for idx, region in enumerate(self.region_names)]

        self.processes = get_processes(self.analysis)
        self.model_names = list(set([model for region in self.region_names for model in self.processes[region]["models"]]))
        self.init_processes()

    def init_processes(self):
        # Common arguments
        common_args = {
            "mass": ["*"],
            "analysis": [self.analysis],
            "era": self.eras,
            "channel": [self.analysis],
        }

        ### Add the "Observation" entry for each region
        self.harvester.AddObservations(bin=self.regions, **common_args)
        # Set observation to -1 for all regions
        self.harvester.ForEachObs(lambda x: x.set_rate(-1))

        ### Defining the processes for each region
        for region_idx, region_name in self.regions:

            # Signals (effectively only for the SR)
            self.harvester.AddProcesses(
                procs=self.processes[region_name]["signals"],
                bin=[(region_idx, region_name)],
                signal=True,
                **common_args,
            )

            # Backgrounds and models
            self.harvester.AddProcesses(
                procs=self.processes[region_name]["models"] + self.processes[region_name]["backgrounds"],
                bin=[(region_idx, region_name)],
                signal=False,
                **common_args,
            )

        # Set rates to -1 for all processes except models
        self.harvester.ForEachProc(lambda x: x.set_rate(1 if x.process() in self.model_names else -1))

    def add_systematics(self, syst_dict, syst_type: str):
        """Add a shape or lnN systematic uncertainty to the card."""
        for syst_name, syst_val in syst_dict.items():
            valmap = self.build_syst_map(syst_val)

            self.harvester.AddSyst(
                target=self.harvester,
                name=syst_name,
                type=syst_type,
                valmap=valmap,
            )

    def build_syst_map(self, syst_val):
        """Convert a dictionary containting the value of the systematic for each region and process it applies to into a SystMap."""
        syst_map = ch.SystMap("era", "bin_id", "process")

        for region_idx, region_name in self.regions:
            # If "value" is present, the same value is applied accross all regions
            if "value" in syst_val:
                syst_map(
                    [self.year],
                    [region_idx],
                    syst_val["processes"],
                    syst_val["value"],
                )
            # Otherwise, value is specified for each region
            elif region_name in syst_val:
                syst_map(
                    [self.year],
                    [region_idx],
                    syst_val[region_name]["processes"],
                    syst_val[region_name]["value"],
                )

        return syst_map

    def add_nuisances(self, nuisances: list[str]) -> None:
        for nuisance in nuisances:
            self.harvester.AddDatacardLineAtEnd(f"{nuisance} param 0.0 1")

    def write_datacard(self):

        # Standardize bin names
        ch.SetStandardBinNames(self.harvester, "$CHANNEL_$ERA_$BIN")

        # Extract shapes
        # TODO: will require changes to the scripts building the workspace
        # self.harvester.cp().signals().ExtractShapes(self.ws_path, "category_vbf_$ERA:$CHANNEL_$ERA_$BIN_$PROCESS", "category_vbf_$ERA:$CHANNEL_$ERA_$BIN_$PROCESS_$SYSTEMATIC")
        # self.harvester.cp().backgrounds().ExtractShapes(self.ws_path, "category_vbf_Run3/$BIN/$PROCESS", "$BIN/$PROCESS_$SYSTEMATIC")

        self.harvester.WriteDatacard(self.card_path)

    def insert_shape_lines(self):
        # Manually fix path of shapes
        # as the correct path of the shapes cannot currently be read by CombineHarvester
        with open(self.card_path) as f:
            card_lines = f.readlines()

        # Find the index of the lines containing the placeholder path of the shapes, remove them
        idx_list = [i for i, line in enumerate(card_lines) if line.startswith("shapes")]

        for idx in reversed(idx_list):  # Reverse order to avoid index issues
            card_lines.pop(idx)

        # Start inserting new lines from where the first shape line was found
        current_idx = idx_list[0] if idx_list else len(card_lines)

        region_label_map = get_region_label_map()

        region_model_map = get_region_model_map()

        def format_line(process: str, region: str, hname: str, workspace: str = "combinedws", systematics: bool = False) -> str:
            """Format a line for the datacard shapes block."""

            def pad(word: str, width: int = 15) -> str:
                return word + " " * max(1, width - len(word))

            shape_expr = f"{self.analysis}_{self.year}_{hname}"
            if not "data" in hname and not "model" in hname:
                shape_expr += "_$PROCESS"
            channel = f"{self.analysis}_{self.year}_{region}"
            line = f"shapes {pad(word=process, width=10)} {pad(word=channel, width=20)} {self.ws_path} {workspace}:{shape_expr}"
            if systematics:
                line += f" {workspace}:{shape_expr}_$SYSTEMATIC"
            line += "\n"
            return line

        for region, region_old in region_label_map:
            shapes_list = [
                format_line(process="*", region=region, hname=region_old, systematics=True),
                format_line(process="data_obs", region=region, hname=f"{region_old}_data"),
            ]

            shapes_list += [format_line(process=model, region=region, hname=f"{model_old}_model") for model, model_old in region_model_map[region]]

            for l in shapes_list:
                card_lines.insert(current_idx, l)
                current_idx += 1

        # Write modified content to the datacard
        with open(self.card_path, "w") as f:
            f.writelines(card_lines)

    def add_comments_to_datacard(self, comments):
        with open(self.card_path, "r") as f:
            lines = f.readlines()

        with open(self.card_path, "w") as f:
            for comment in comments:
                f.write(f"# {comment}\n")
            f.writelines(lines)


def main():
    parser = argparse.ArgumentParser(description="Arguments for workspace creation.")
    parser.add_argument("-y", "--year", type=str, default="Run3", help="Data-taking year (e.g., '2017', '2018', 'Run3').")
    parser.add_argument("-c", "--channel", type=str, default="vbf", help="Analysis name (e.g., 'vbf', 'monojet', 'monov').")
    args = parser.parse_args()

    channel, year = args.channel, args.year
    builder = DatacardBuilder(channel=channel, year=year)

    builder.add_systematics(syst_dict=get_lumi_uncertainties(year=year), syst_type="lnN")
    builder.add_systematics(syst_dict=get_lepton_efficiency_uncertainties(year=year), syst_type="lnN")
    builder.add_systematics(syst_dict=get_trigger_uncertainties(year=year), syst_type="lnN")
    builder.add_systematics(syst_dict=get_qcd_uncertainties(year=year), syst_type="lnN")
    builder.add_systematics(syst_dict=get_pdf_uncertainties(year=year), syst_type="lnN")
    builder.add_systematics(syst_dict=get_misc_uncertainties(year=year), syst_type="lnN")
    builder.add_systematics(syst_dict=get_jer_shape(), syst_type="shape")

    # Add constrained nuisance parameters
    # TODO: there does not seem to be a proper way to add these using CombineHarvester
    # Could this be done in a cleaner way if changes are made to the workspace building scripts?
    nuis_list = (
        [f"CMS_veto{year}_{l}" for l in ["t", "m", "e"]]
        + [jer.replace("$ERA", year) for jer in get_jer_shape()]
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
    )

    builder.add_nuisances(nuisances=nuis_list)

    builder.write_datacard()

    builder.insert_shape_lines()

    comments = [
        "This datacard was generated using CombineHarvester",
        f"Analysis: {channel}, era: {year}",
    ]
    builder.add_comments_to_datacard(comments=comments)

    # TODO: check that this works for monojet
    # Remove useless stat uncertainties
    # Uncertainties are removed if they do not have a variation histogram available
    # The criteria for whether a variation histogram is present are defined in make_ws.py

    # Get the list of nuisances from the ROOT file
    # rootls_cmd = ["rootls", "-1", f"root/ws_{channel}.root:category_{channel}_{year}"]
    # rootls_out = subprocess.run(rootls_cmd, stdout=subprocess.PIPE, check=True)
    # workspace_nuis = rootls_out.stdout.decode("utf-8").splitlines()

    # # Getting stat nuisances present in the datacard
    # with open(builder.card_path, "r") as file:
    #     datacard_nuis = [l.split(" ")[0] for l in file.readlines() if "shape" in l and "stat" in l.split(" ")[0]]

    # # Check if the nuisances are present in the ROOT file
    # for nuis in datacard_nuis:
    #     if f"{nuis}Up" not in workspace_nuis:
    #         # If the nuisance is not present, remove it from the datacard
    #         content = "\n".join(line for line in content.splitlines() if not line.startswith(nuis))
    #         print(f"Warning: removing nuisance {nuis} from {builder.card_path}, shape not present in ws_{channel}.root")

    # Write the modified content to the datacard file

    # Run external tools
    subprocess.run(["text2workspace.py", builder.card_path, "--channel-masks"], check=True)
    with open(f"cards/systematics_{year}.html", "w") as outfile:
        subprocess.run(
            [
                "python3",
                os.path.join(os.environ["CMSSW_BASE"], "src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py"),
                "--all",
                "-f",
                "html",
                builder.card_path,
            ],
            check=True,
            stdout=outfile,
        )


if __name__ == "__main__":
    main()
