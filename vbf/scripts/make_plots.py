#!/bin/env python3
from plotter.plot_prefit_postfit import plot_prefit_postfit
from plotter.plot_data_validation import plot_data_validation
from plotter.plot_ratio import plot_ratio
from plotter.plot_diff_nuis import plot_diff_nuis


def main():
    lumi = {
        # 2017: 41.5,
        # 2018: 59.7,
        "Run3": 62.5,
    }
    regions = ["singlemuon", "dimuon", "gjets", "singleelectron", "dielectron", "signal"]
    procs = ["zmm", "zee", "w", "photon", "wen", "wmn"]
    # years = [2017, 2018]
    # years = [2017]
    # years = [2018]
    years = ["Run3"]

    for year in years:
        ws_file = "./root/ws_vbf.root"
        fitdiag_file = f"diagnostics/fitDiagnostics_vbf_{year}.root"
        diffnuis_file = f"diagnostics/diffnuisances_vbf_{year}.root"
        category = f"vbf_{year}"
        outdir = f"./plots/{year}/"
        for region in regions:
            plot_prefit_postfit(region=region, category=category, ws_file=ws_file, fitdiag_file=fitdiag_file, outdir=outdir, lumi=lumi[year], year=year)
        for proc in procs:
            plot_ratio(process=proc, category=category, model_filename="root/combined_model_vbf.root", outdir=outdir, lumi=lumi[year], year=year)

        # Flavor integrated
        plot_data_validation("combined", "gjets", category, ws_file, fitdiag_file, outdir, lumi[year], year)
        plot_data_validation("combinedW", "gjets", category, ws_file, fitdiag_file, outdir, lumi[year], year)
        plot_data_validation("combined", "combinedW", category, ws_file, fitdiag_file, outdir, lumi[year], year)
        # Split by flavor
        plot_data_validation("dimuon", "singlemuon", category, ws_file, fitdiag_file, outdir, lumi[year], year)
        plot_data_validation("dielectron", "singleelectron", category, ws_file, fitdiag_file, outdir, lumi[year], year)
        plot_data_validation("singleelectron", "gjets", category, ws_file, fitdiag_file, outdir, lumi[year], year)
        plot_data_validation("singlemuon", "gjets", category, ws_file, fitdiag_file, outdir, lumi[year], year)
        plot_data_validation("dielectron", "gjets", category, ws_file, fitdiag_file, outdir, lumi[year], year)
        plot_data_validation("dimuon", "gjets", category, ws_file, fitdiag_file, outdir, lumi[year], year)
        plot_diff_nuis(diffnuis_file, outdir)


if __name__ == "__main__":
    main()
