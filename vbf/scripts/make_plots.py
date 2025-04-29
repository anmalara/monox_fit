#!/bin/env python3
import sys
import os

from plotter.plot_PreFitPostFit import plot_prefit_postfit
from plotter.plot_datavalidation import dataValidation
from plotter.plot_ratio import plot_ratio
from plotter.plot_diffnuis import plot_nuis

lumi = {
    # 2017: 41.5,
    # 2018: 59.7,
    # Temporary: replacing 2017 lumi value with that of 22+23 lumi
    2017: 62.5,
    2018: 62.5,
    "Run3": 62.5,
}
regions = ["singlemuon", "dimuon", "gjets", "singleelectron", "dielectron", "signal"]
procs = ["zmm", "zee", "w", "photon", "wen", "wmn"]

### Years fit separately
# for year in [2017, 2018]:
# for year in [2017]:
# for year in [2018]:
for year in ["Run3"]:
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
    dataValidation("combined", "gjets", category, ws_file, fitdiag_file, outdir, lumi[year], year)
    dataValidation("combinedW", "gjets", category, ws_file, fitdiag_file, outdir, lumi[year], year)
    dataValidation("combined", "combinedW", category, ws_file, fitdiag_file, outdir, lumi[year], year)
    # Split by flavor
    dataValidation("dimuon", "singlemuon", category, ws_file, fitdiag_file, outdir, lumi[year], year)
    dataValidation("dielectron", "singleelectron", category, ws_file, fitdiag_file, outdir, lumi[year], year)
    dataValidation("singleelectron", "gjets", category, ws_file, fitdiag_file, outdir, lumi[year], year)
    dataValidation("singlemuon", "gjets", category, ws_file, fitdiag_file, outdir, lumi[year], year)
    dataValidation("dielectron", "gjets", category, ws_file, fitdiag_file, outdir, lumi[year], year)
    dataValidation("dimuon", "gjets", category, ws_file, fitdiag_file, outdir, lumi[year], year)
    plot_nuis(diffnuis_file, outdir)


### Years fit together
# outdir = "plots/combined"
# diffnuis_file = "diagnostics/diffnuisances_vbf_combined.root"
# plot_nuis(diffnuis_file, outdir)

# for year in [2017,2018]:
# for year in [2017]:
#     ws_file = "root/ws_vbf.root"
#     fitdiag_file = f"diagnostics/fitDiagnostics_vbf_combined.root"
#     category = f"vbf_{year}"
#     outdir = f"./plots/combined_{year}/"
#     for region in regions:
#         plotPreFitPostFit(region, category, ws_file, fitdiag_file, outdir, lumi[year], year)
