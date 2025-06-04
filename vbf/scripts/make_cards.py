import os
import shutil
import subprocess
from utils.workspace.flat_uncertainties import get_lumi_uncertainties

# Ensure the cards directory exists
os.makedirs("cards", exist_ok=True)

# List of years to process
years = ["Run3"]

# Constants for each year

for year in years:
    card_path = f"cards/card_vbf_{year}.txt"
    template_path = "../../../templates/vbf_template.txt"

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
    content = content.replace("combined_model.root", "../root/combined_model_vbf.root")
    content = content.replace(f"vbf_qcd_nckw_ws_{year}.root", f"../root/vbf_qcd_nckw_ws_{year}.root")

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
