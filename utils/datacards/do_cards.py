import os
import shutil
import subprocess
import argparse
from utils.workspace.flat_uncertainties import get_lumi_uncertainties


class DatacardBuilder:
    def __init__(self, channel: str, year: str):
        self.channel = channel
        self.year = year
        self.card_path = f"cards/card_{channel}_{year}.txt"
        self.template_path = f"../../../../utils/datacards/{channel}_template.txt"

        # minimum number of spaces between fields in the datacard
        self.min_spaces = 2

        # Content of the datacard, to be modified later
        self.raw_content = ""
        self.header = ""
        self.shapes = ""
        self.channels = ""
        self.processes = ""
        self.nuisances = ""

        # Ensure the cards directory exists
        os.makedirs("cards", exist_ok=True)
        # Touch the card file to ensure it exists
        # open(self.card_path, "a").close()

        self.read_template()

    def read_template(self):
        """Read the template file and store its content."""
        with open(self.template_path, "r") as file:
            self.raw_content = file.read()

        self.update_parts()

    def update_parts(self):
        """Split the raw content into its individual parts."""
        parts = [l.strip("-") for l in self.raw_content.split("---") if l != ""]
        self.header, self.shapes, self.channels, self.processes, self.nuisances = parts

    def update_raw_content(self):
        """Reconstruct the raw content from the individual parts."""
        self.raw_content = "---".join([self.header, self.shapes, self.channels, self.processes, self.nuisances])

    def bulk_replace(self, replacements: dict):
        """Replace multiple placeholders in the raw content."""
        # Ensure the raw content is up-to-date
        self.update_raw_content()

        for placeholder, value in replacements.items():
            self.raw_content = self.raw_content.replace(placeholder, value)

        # Propagate changes to the individual parts
        self.update_parts()

    def nuisance_replace(self, replacements: dict):
        """Replace nuisance parameters in the nuisances section."""
        # Ensure the parts are up-to-date
        self.update_parts()

        # Extract lines
        shapes_lines = [
            l
            for l in self.nuisances.splitlines()
            # remove empty lines
            if (l.strip() != "")
            # is a shape nuisance
            and ([field for field in l.split(" ") if field.strip() != ""][1] == "shape")
        ]
        lnN_lines = [
            l
            for l in self.nuisances.splitlines()
            # remove empty lines
            if (l.strip() != "")
            # is a lnN nuisance
            and ([field for field in l.split(" ") if field.strip() != ""][1] == "lnN")
        ]
        other_nuisance_lines = [
            l
            for l in self.nuisances.splitlines()
            # remove empty lines
            if (l.strip() != "")
            # is not a shape or lnN nuisance
            and ([field for field in l.split(" ") if field.strip() != ""][1] not in ["shape", "lnN"])
        ]

        # Extract each column for the lnN nuisances
        lnN_fields = [l.split() for l in lnN_lines if l.strip() != ""]
        ref_proc = [field.split("_")[-1] for field in self.processes.splitlines()[1].split() if field.strip() != ""][1:]

        for nuisance, value in replacements.items():
            if type(value) is dict:
                pass
            else:
                lnN_fields = [[field.replace(nuisance, value) for field in line] for line in lnN_fields]

        new_lnN_lines = "\n".join([" ".join(line_fields) for line_fields in lnN_fields])
        shapes_lines = "\n".join(shapes_lines)
        other_nuisance_lines = "\n".join(other_nuisance_lines)
        self.nuisances = f"\n{shapes_lines}\n{new_lnN_lines}\n{other_nuisance_lines}"
        # Propagate changes to raw content
        self.update_raw_content()

    def fix_formating(self):
        self.update_parts()

        # channels
        channel_lines = [l for l in self.channels.splitlines() if l.strip() != ""]
        # length of the longuest field, accross all lines
        max_length = max(len(l.strip()) for line in channel_lines for l in line.split())

        # add spaces to the end of each field to make them all the same length
        channel_fields = [[l.strip() + " " * (max_length - len(l.strip()) + self.min_spaces) for l in line.split()] for line in channel_lines]
        new_channel_lines = "\n".join(["".join(line_fields) for line_fields in channel_fields])
        self.channels = f"\n{new_channel_lines}\n"

        # Processes, tied with shape and lnN nuisances
        process_lines = [l for l in self.processes.splitlines() if l.strip() != ""]
        shapes_and_lnN_lines = [
            l for l in self.nuisances.splitlines() if (l.strip() != "") and ([field for field in l.split(" ") if field.strip() != ""][1] in ["shape", "lnN"])
        ]
        other_nuisance_lines = [
            l
            for l in self.nuisances.splitlines()
            if (l.strip() != "") and ([field for field in l.split(" ") if field.strip() != ""][1] not in ["shape", "lnN"])
        ]
        # length of the longuest field, accross all lines
        max_process_length = max(len(l.strip()) for line in process_lines for l in line.split())
        max_nuisance_length = max(len(l.strip()) for line in shapes_and_lnN_lines for l in line.split())
        max_length = max(max_process_length, max_nuisance_length)

        # add spaces to the end of each field to make them all the same length
        process_fields = [[l.strip() + " " * (max_length - len(l.strip()) + self.min_spaces) for l in line.split()] for line in process_lines]
        for line_fields in process_fields:
            line_fields.insert(1, " " * (max_length + self.min_spaces))
        shapes_and_lnN_fields = [[l.strip() + " " * (max_length - len(l.strip()) + self.min_spaces) for l in line.split()] for line in shapes_and_lnN_lines]
        new_process_lines = "\n".join(["".join(line_fields) for line_fields in process_fields])
        self.processes = f"\n{new_process_lines}\n"

        new_shapes_and_lnN_lines = "\n".join(["".join(line_fields) for line_fields in shapes_and_lnN_fields])
        other_nuisance_lines = "\n".join(other_nuisance_lines)
        self.nuisances = f"\n{new_shapes_and_lnN_lines}\n{other_nuisance_lines}"

        self.update_raw_content()

    def write_datacard(self):
        """Write the datacard content to the specified file."""
        self.fix_formating()
        with open(self.card_path, "w") as file:
            file.write(self.raw_content)


def main():
    parser = argparse.ArgumentParser(description="Arguments for workspace creation.")
    parser.add_argument("-y", "--year", type=str, default="Run3", help="Data-taking year (e.g., '2017', '2018', 'Run3').")
    parser.add_argument("-c", "--channel", type=str, default="vbf", help="Analysis name (e.g., 'vbf', 'monojet', 'monov').")
    args = parser.parse_args()

    channel, year = args.channel, args.year
    datacard_builder = DatacardBuilder(channel, year)

    datacard_builder.bulk_replace(
        {
            "@YEAR": year,
            # Replace filenames
            "combined_model.root": f"../root/combined_model_{channel}.root",
            f"{channel}_qcd_nckw_ws_{year}.root": f"../root/{channel}_qcd_nckw_ws_{year}.root",
        }
    )

    datacard_builder.nuisance_replace(
        {
            # affected by mistags in loose region with ratio of -1/20
            "@MISTAGLOOSEW": "0.999",
            "@MISTAGLOOSEW": "0.998",
            "@MISTAGLOOSEW": "0.998",
            **get_lumi_uncertainties(year),
        }
    )

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
    datacard_builder.write_datacard()
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
