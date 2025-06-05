import os
import shutil
import subprocess
import argparse
import tempfile
from utils.workspace.flat_uncertainties import get_lumi_uncertainties


def main():
    parser = argparse.ArgumentParser(description="Arguments for workspace creation.")
    parser.add_argument("-y", "--year", type=str, default="Run3", help="Data-taking year (e.g., '2017', '2018', 'Run3').")
    parser.add_argument("-c", "--channel", type=str, default="vbf", help="Analysis name (e.g., 'vbf', 'monojet', 'monov').")
    args = parser.parse_args()

    channel, year = args.channel, args.year

    # Ensure the cards directory exists
    os.makedirs("cards", exist_ok=True)

    card_path = f"cards/card_{channel}_{year}.txt"
    template_path = f"../../../../utils/datacards/{channel}_template.txt"

    shutil.copy(template_path, card_path)

    # Read and modify the template
    with open(card_path, "r") as file:
        content = file.read()

    # Replace placeholders
    content = content.replace("@YEAR", year)
    lumi_constants = get_lumi_uncertainties(year)
    for key, value in lumi_constants.items():
        content = content.replace(key, value)

    # Replace filenames
    content = content.replace("combined_model.root", f"../root/combined_model_{channel}.root")
    content = content.replace(f"{channel}_qcd_nckw_ws_{year}.root", f"../root/{channel}_qcd_nckw_ws_{year}.root")

    # affected by mistags in loose region with ratio of -1/20
    content = content.replace("@MISTAGLOOSEW", "0.999        ")
    content = content.replace("@MISTAGLOOSEW", "0.998        ")
    content = content.replace("@MISTAGLOOSEW", "0.998        ")

    # TODO: check that this works for monojet
    # Remove useless stat uncertainties
    # Uncertainties are removed if they do not have a variation histogram available
    # The criteria for whether a variation histogram is present are defined in make_ws.py

    # Get the list of nuisances from the ROOT file
    rootls_cmd = ["rootls", "-1", f"root/ws_{channel}.root:category_{channel}_{year}"]
    rootls_out = subprocess.run(rootls_cmd, stdout=subprocess.PIPE, check=True)
    workspace_nuis = rootls_out.stdout.decode("utf-8").splitlines()

    # Getting stat nuisances present in the datacard
    with open(card_path, "r") as file:
        datacard_nuis = [l.split(" ")[0] for l in file.readlines() if "shape" in l and "stat" in l.split(" ")[0]]

    # Check if the nuisances are present in the ROOT file
    for nuis in datacard_nuis:
        if f"{nuis}Up" not in workspace_nuis:
            # If the nuisance is not present, remove it from the datacard
            content = "\n".join(line for line in content.splitlines() if not line.startswith(nuis))
            print(f"Warning: removing nuisance {nuis} from {card_path}, shape not present in ws_{channel}.root")

    # Write updated content
    with open(card_path, "w") as file:
        file.write(content)

    # Run external tools
    subprocess.run(["text2workspace.py", card_path, "--channel-masks"], check=True)
    with open(f"cards/systematics_{year}.html", "w") as outfile:
        subprocess.run(
            [
                "python3",
                os.path.join(os.environ["CMSSW_BASE"], "src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py"),
                "--all",
                "-f",
                "html",
                card_path,
            ],
            check=True,
            stdout=outfile,
        )


if __name__ == "__main__":
    main()
