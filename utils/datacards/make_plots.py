#!/bin/env python3

import argparse
from plotter.plot_prefit_postfit import plot_prefit_postfit
from plotter.plot_data_validation import plot_data_validation
from plotter.plot_ratio import plot_ratio
from plotter.plot_diff_nuis import plot_diff_nuis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate standard plots for a given analysis channel.")
    parser.add_argument("--channel", required=True, help="Analysis channel name (e.g. vbf, monojet)")
    parser.add_argument("--year", default="Run3", choices=["2017", "2018", "Run3"], help="Dataset year (default: Run3)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    lumi = {
        "2017": 41.5,
        "2018": 59.7,
        "Run3": 62.5,
    }

    regions = ["singlemuon", "dimuon", "gjets", "singleelectron", "dielectron", "signal"]
    procs = ["zmm", "zee", "w", "photon", "wen", "wmn"]
    region_pairs = [
        # Flavor integrated
        ("combined", "gjets"),
        ("combinedW", "gjets"),
        ("combined", "combinedW"),
        # Split by flavor
        ("dimuon", "singlemuon"),
        ("dielectron", "singleelectron"),
        ("singleelectron", "gjets"),
        ("singlemuon", "gjets"),
        ("dielectron", "gjets"),
        ("dimuon", "gjets"),
    ]

    year = args.year
    channel = args.channel
    category = f"{channel}_{year}"
    outdir = f"./plots/{year}/"
    ws_filename = f"./root/ws_{channel}.root"
    fitdiag_file = f"diagnostics/fitDiagnostics_{category}.root"
    diffnuis_file = f"diagnostics/diffnuisances_{category}.root"
    model_filename = f"root/combined_model_{channel}.root"

    common_args = {"category": category, "outdir": outdir, "lumi": lumi[year], "year": year}

    for region in regions:
        plot_prefit_postfit(region=region, ws_filename=ws_filename, fitdiag_file=fitdiag_file, **common_args)

    for proc in procs:
        plot_ratio(process=proc, model_filename=model_filename, **common_args)

    for region1, region2 in region_pairs:
        plot_data_validation(region1=region1, region2=region2, ws_filename=ws_filename, fitdiag_filename=fitdiag_file, **common_args)

    plot_diff_nuis(diffnuis_file=diffnuis_file, outdir=outdir, category=category)


if __name__ == "__main__":
    main()
