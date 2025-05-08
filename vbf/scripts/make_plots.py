#!/bin/env python3
from plotter.plot_prefit_postfit import plot_prefit_postfit
from plotter.plot_data_validation import plot_data_validation
from plotter.plot_ratio import plot_ratio
from plotter.plot_diff_nuis import plot_diff_nuis


def main() -> None:
    lumi = {
        2017: 41.5,
        2018: 59.7,
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

    # years = [2017, 2018]
    # years = [2017]
    # years = [2018]
    years = ["Run3"]

    for year in years:
        ws_filename = "./root/ws_vbf.root"
        category = f"vbf_{year}"
        outdir = f"./plots/{year}/"
        fitdiag_file = f"diagnostics/fitDiagnostics_{category}.root"
        diffnuis_file = f"diagnostics/diffnuisances_{category}.root"
        common_args = {"category": category, "outdir": outdir, "lumi": lumi[year], "year": year}

        for region in regions:
            plot_prefit_postfit(region=region, ws_filename=ws_filename, fitdiag_file=fitdiag_file, **common_args)
        for proc in procs:
            plot_ratio(process=proc, model_filename="root/combined_model_vbf.root", **common_args)

        for region1, region2 in region_pairs:
            plot_data_validation(region1=region1, region2=region2, ws_filename=ws_filename, fitdiag_filename=fitdiag_file, **common_args)

        plot_diff_nuis(diffnuis_file=diffnuis_file, outdir=outdir, category=category)


if __name__ == "__main__":
    main()
