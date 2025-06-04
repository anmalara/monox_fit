import os
import shutil
import subprocess

# Ensure the cards directory exists
os.makedirs("cards", exist_ok=True)

# List of years to process
years = ["Run3"]

# Constants for each year
lumi_constants = {
    "2017": {
        "@LUMIXY": "1.008",
        "@LUMILS": "1.003",
        "@LUMIBBD": "1.004",
        "@LUMIDB": "1.005",
        "@LUMIBCC": "1.003",
        "@LUMIGS": "1.001",
        "@LUMI": "1.020",
    },
    "2018": {
        "@LUMIXY": "1.02",
        "@LUMILS": "1.002",
        "@LUMIBBD": "1.0",
        "@LUMIDB": "1.0",
        "@LUMIBCC": "1.02",
        "@LUMIGS": "1.00",
        "@LUMI": "1.015",
    },
    "Run3": {
        "@LUMIXY": "1.02",
        "@LUMILS": "1.002",
        "@LUMIBBD": "1.0",
        "@LUMIDB": "1.0",
        "@LUMIBCC": "1.02",
        "@LUMIGS": "1.00",
        "@LUMI": "1.015",
    },
}

for year in years:
    card_path = f"cards/card_vbf_{year}.txt"
    template_path = "../../../templates/vbf_template.txt"

    shutil.copy(template_path, card_path)

    # Read and modify the template
    with open(card_path, "r") as file:
        content = file.read()

    # Replace placeholders
    content = content.replace("@YEAR", year)
    for key, value in lumi_constants[year].items():
        if key.startswith("@"):
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
