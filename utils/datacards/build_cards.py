#!/usr/bin/env python3
import os
import subprocess
import argparse
from typing import Any
from collections.abc import Callable

import CombineHarvester.CombineTools.ch as ch  # type: ignore
from utils.workspace.flat_uncertainties import *


class DatacardBuilder:
    """Datacard builder using CombineHarvester for a given analysis and year."""

    def __init__(self, channel: str, year: str):
        self.analysis: str = channel
        self.year: str = year
        self.ws_path: str = f"../root/combined_model_{self.analysis}.root"
        self.card_path: str = f"cards/card_{self.analysis}_{self.year}.txt"

        self.harvester = ch.CombineHarvester()
        os.makedirs("cards", exist_ok=True)

        ## Regions (common for all analyses)
        self.region_names = ["signal", "dimuon", "dielec", "singlemu", "singleel", "photon"]
        # put in the form (index, name) for CombineHarvester
        self.regions = [(idx, region) for idx, region in enumerate(self.region_names)]
        self.model_names = list(set([model for region in self.region_names for model in get_processes(analysis=self.analysis, region=region, type="models")]))

        self.init_processes()

    def init_processes(self) -> None:
        """Initialize observations and processes in CombineHarvester."""
        common_args = {"mass": ["*"], "analysis": [self.analysis], "era": [self.year], "channel": [self.analysis]}

        self.harvester.AddObservations(bin=self.regions, **common_args)
        # Set observation to -1 for all regions
        self.harvester.ForEachObs(lambda x: x.set_rate(-1))

        for region_idx, region_name in self.regions:
            signal_procs = get_processes(analysis=self.analysis, region=region_name, type="signals")
            self.harvester.AddProcesses(procs=signal_procs, bin=[(region_idx, region_name)], signal=True, **common_args)

            model_procs = get_processes(analysis=self.analysis, region=region_name, type="models")
            bkg_procs = get_processes(analysis=self.analysis, region=region_name, type="backgrounds")
            self.harvester.AddProcesses(procs=model_procs + bkg_procs, bin=[(region_idx, region_name)], signal=False, **common_args)

        # Set rates to -1 for all processes except models
        self.harvester.ForEachProc(lambda x: x.set_rate(1 if x.process() in self.model_names else -1))

    def add_all_systematics(self) -> None:
        """Add lnN and shape systematics and custom nuisance parameters."""
        lnN_funcs: list[Callable[[str, str], dict[str, Any]]] = [
            get_lumi_uncertainties,
            get_lepton_efficiency_uncertainties,
            get_trigger_uncertainties,
            get_qcd_uncertainties,
            get_pdf_uncertainties,
            get_misc_uncertainties,
        ]
        for func in lnN_funcs:
            self.add_systematics(syst_func=func, syst_type="lnN")

        self.add_systematics(syst_func=get_jec_shape, syst_type="shape")

        # Add constrained nuisance parameters
        nbins = 12  # TODO
        nuisances = get_lepton_veto_list(year=self.year, analysis=self.analysis)
        nuisances += list(get_jec_shape(year=self.year, analysis=self.analysis).keys())
        nuisances += get_stat_unc_list(year=self.year, analysis=self.analysis, nbins=nbins)
        nuisances += get_theory_unc_list(year=self.year, analysis=self.analysis)

        self.add_nuisances(nuisances=nuisances)

    def add_systematics(self, syst_func: Callable[[str, str], dict[str, Any]], syst_type: str) -> None:
        """Add a lnN or shape systematic uncertainty to the card."""
        syst_dict = syst_func(year=self.year, analysis=self.analysis)
        for name, val in syst_dict.items():
            valmap = self.build_syst_map(syst_val=val)
            self.harvester.AddSyst(target=self.harvester, name=name, type=syst_type, valmap=valmap)

    def build_syst_map(self, syst_val: dict[str, Any]) -> ch.SystMap:
        """Build a SystMap from the provided value map of the systematic for each region and process it applies to."""
        syst_map = ch.SystMap("era", "bin_id", "process")
        for region_idx, region_name in self.regions:
            entry = syst_val
            if region_name in entry:
                # Apply a region-specific value
                entry = entry[region_name]
            if "value" in entry:
                syst_map([self.year], [region_idx], entry["processes"], entry["value"])
        return syst_map

    def add_nuisances(self, nuisances: list[str]) -> None:
        """Add flat nuisance parameters as Gaussian priors."""
        for nuisance in nuisances:
            self.harvester.AddDatacardLineAtEnd(f"{nuisance} param 0.0 1.0")

    def write_datacard(self) -> None:
        """Write the datacard and insert shape lines."""
        ch.SetStandardBinNames(self.harvester, "$CHANNEL_$ERA_$BIN")
        self.harvester.WriteDatacard(self.card_path)
        self.align_datacard_columns()
        self.insert_shape_lines()

    def align_datacard_columns(self) -> None:
        """Align columns in the datacard using custom spacing rules."""
        with open(self.card_path, "r") as f:
            lines = f.readlines()

        def should_align_line(line: str) -> bool:
            return any(key in line for key in ["bin ", "observation ", "process ", "rate ", "lnN ", "shape "])

        def format_line(line: str) -> str:
            tokens = line.strip().split()
            if len(tokens) <= 1:
                raise ValueError(f"Found poorly formatted line: {line!r}")

            # Uniform padding for all tokens
            header = tokens[0]
            formatted = ""

            if "lnN" in line or "shape" in line:
                formatted += header.ljust(35) + tokens[1].ljust(6)
                rest = tokens[2:]
            elif "observation" == header or ("bin" == header and not "bin             " in line):
                formatted += header.ljust(15)
                rest = tokens[1:]
            else:
                formatted += header.ljust(41)
                rest = tokens[1:]

            for token in rest:
                formatted += token.ljust(20)

            return formatted.rstrip() + "\n"

        aligned_lines = [format_line(line) if should_align_line(line) else line for line in lines]

        with open(self.card_path, "w") as f:
            f.writelines(aligned_lines)

    def insert_shape_lines(self) -> None:
        """Insert custom shape lines for histograms."""
        # Manually add path of shapes as the correct path of the shapes cannot currently be read by CombineHarvester
        with open(self.card_path) as f:
            lines = f.readlines()

        # Find the index of the lines containing the placeholder path of the shapes, remove them
        shape_idx = [i for i, l in enumerate(lines) if l.startswith("shapes")]

        for idx in reversed(shape_idx):  # Reverse order to avoid index issues
            lines.pop(idx)

        region_label_map = get_region_label_map()
        region_model_map = get_region_model_map()

        def format_line(process: str, region: str, hname: str, systematics: bool = False, workspace: str = "combinedws") -> str:
            """Format a line for the datacard shapes block."""

            def pad(word: str, width: int = 15) -> str:
                return word + " " * max(1, width - len(word))

            shape_expr = f"{self.analysis}_{self.year}_{hname}"
            if "data" not in hname and "model" not in hname:
                shape_expr += "_$PROCESS"
            channel = f"{self.analysis}_{self.year}_{region}"
            line = f"shapes {pad(word=process, width=10)} {pad(word=channel, width=20)} {self.ws_path} {workspace}:{shape_expr}"
            if systematics:
                line += f" {workspace}:{shape_expr}_$SYSTEMATIC"
            line += "\n"
            return line

        # Start inserting new lines from where the first shape line was found
        insert_at = shape_idx[0] if shape_idx else len(lines)
        for region, region_old in region_label_map:
            shapes_list = [
                format_line(process="*", region=region, hname=region_old, systematics=True),
                format_line(process="data_obs", region=region, hname=f"{region_old}_data"),
            ]

            shapes_list += [format_line(process=model, region=region, hname=f"{model_old}_model") for model, model_old in region_model_map[region]]

            for shape in shapes_list:
                lines.insert(insert_at, shape)
                insert_at += 1

        # Write modified content to the datacard
        with open(self.card_path, "w") as f:
            f.writelines(lines)

    def add_comments_to_datacard(self, comments: list[str]) -> None:
        """Prepend comments to the datacard."""
        with open(self.card_path, "r") as f:
            lines = f.readlines()

        with open(self.card_path, "w") as f:
            for comment in comments:
                f.write(f"# {comment}\n")
            f.writelines(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Datacard generator for CombineHarvester.")
    parser.add_argument("-y", "--year", type=str, default="Run3", help="Data-taking year (e.g., '2017', '2018', 'Run3').")
    parser.add_argument("-c", "--channel", type=str, default="vbf", help="Analysis channel name (e.g., 'vbf', 'monojet', 'monov').")
    args = parser.parse_args()

    channel, year = args.channel, args.year
    builder = DatacardBuilder(channel=channel, year=year)
    builder.add_all_systematics()
    builder.write_datacard()

    comments = ["This datacard was generated using CombineHarvester", f"Analysis: {channel}, era: {year}"]
    builder.add_comments_to_datacard(comments=comments)

    # Run external tools
    subprocess.run(["text2workspace.py", builder.card_path, "--channel-masks"], check=True)
    script = os.path.join(os.environ["CMSSW_BASE"], "src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py")
    with open(f"cards/systematics_{year}.html", "w") as outfile:
        subprocess.run(["python3", script, "--all", "-f", "html", builder.card_path], check=True, stdout=outfile)


if __name__ == "__main__":
    main()
