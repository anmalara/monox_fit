#!/usr/bin/env python3

import os
import glob
import shutil
import hashlib
from typing import Optional
from datetime import date
from utils.generic.file_utils import execute_command
from utils.generic.logger import initialize_colorized_logger
from scripts.make_workspace import create_workspace


def compute_md5(file_path: str) -> str:
    """Compute the MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def collect_md5_checksums(file_paths: list[str]) -> list[str]:
    """Return lines with MD5 checksums for given file paths."""
    return [f"{compute_md5(file)}  {os.path.basename(file)}" for file in file_paths]


def collect_git_info() -> list[str]:
    """Return lines with Git commit, branch, and diff information."""
    return [
        "--- REPO INFO ---",
        "Commit hash: " + os.popen("git rev-parse HEAD").read().strip(),
        "Branch name: " + os.popen("git rev-parse --abbrev-ref HEAD").read().strip(),
        os.popen("git diff").read(),
    ]


def run_model_generation(workspace_file: str, output_filename: str, category: str) -> None:
    """Run the model generation script."""
    execute_command(f"./runModel.py {workspace_file} --category {category} --out {output_filename}", description="Generate model")


def copy_systematic_files(destination_dir: str, analysis: str) -> None:
    """Copy systematic .root files to the output directory."""
    for file_path in glob.glob(f"sys/{analysis}_qcd_nckw_ws_201*.root"):
        shutil.copy(file_path, destination_dir)


def create_makefile_symlink(output_dir: str, analysis: str) -> None:
    """Create or update symlink to the Makefile in the parent of the output directory."""
    makefile_source = os.path.realpath(f"../{analysis}/templates/Makefile")
    makefile_link = os.path.join(os.path.dirname(output_dir), "Makefile")
    if os.path.exists(makefile_link) or os.path.islink(makefile_link):
        os.remove(makefile_link)
    os.symlink(makefile_source, makefile_link)


def generate_info_lines(input_dir: str, input_filename: str, output_dir: str) -> list[str]:
    """Gather and return all lines for INFO.txt."""
    lines = [
        f"Input directory: {input_dir}",
        "--- INPUT ---",
        *collect_md5_checksums([input_filename]),
        *collect_git_info(),
        "--- OUTPUT ---",
        *collect_md5_checksums([os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith(".root")]),
    ]
    return lines


def run_workspace_pipeline(input_dir: str, analysis: str, year: str, tag: str, variable: str, root_folder: Optional[str] = None) -> None:
    """Run the full pipeline for a given category and date tag."""
    input_dir = os.path.realpath(input_dir)
    category = f"{analysis}_{year}"
    output_dir = os.path.realpath(os.path.join(os.getenv("FIT_FRAMEWORK_PATH", ""), analysis, year, tag, "root"))
    os.makedirs(output_dir, exist_ok=True)

    input_filename = os.path.join(input_dir, f"limit_{analysis}.root")
    workspace_file = os.path.join(output_dir, f"ws_{analysis}.root")
    combined_model_file = os.path.join(output_dir, f"combined_model_{analysis}.root")
    info_file = os.path.join(output_dir, "INFO.txt")

    logger.info(f"Creating workspace for category '{category}'...")
    create_workspace(input_filename=input_filename, output_filename=workspace_file, category=category, variable=variable, root_folder=root_folder)

    logger.info("Running model generation...")
    # run_model_generation(workspace_file, combined_model_file, category)

    logger.info("Finalizing...")
    # copy_systematic_files(output_dir, analysis)

    with open(info_file, "w") as f:
        info_lines = generate_info_lines(input_dir, input_filename, output_dir)
        f.write("\n".join(info_lines) + "\n")

    logger.info("Creating Makefile symlink and running make...")
    # create_makefile_symlink(output_dir,analysis)
    # execute_command("make cards", description="Build datacards")

    logger.info(f"Done! Output path: {os.path.dirname(output_dir)}")


def main() -> None:
    """Main function to generate workspace and datacards."""
    input_dir = "/ada_mnt/ada/user/anmalara/WorkingArea/pyRAT/hinvisible/plots/for_fit/Run3/"
    analysis = "vbf"
    year = "2017"
    variable = "mjj"
    tag = date.today().strftime("%Y_%m_%d")
    # tag = "year_month_day"
    run_workspace_pipeline(input_dir=input_dir, analysis=analysis, year=year, tag=tag, variable=variable)


if __name__ == "__main__":
    log_level = "INFO"
    # log_level = "DEBUG"
    logger = initialize_colorized_logger(log_level=log_level)
    main()
