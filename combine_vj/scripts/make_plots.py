#!/bin/env python
import os
import sys
sys.path.append(os.path.abspath("../../../plotter"))
from plot_PreFitPostFit import plotPreFitPostFit
from plot_datavalidation import dataValidation
from plot_ratio import plot_ratio
from plot_diffnuis import plot_nuis
lumi ={
    2017 : 41.5,
    2018: 59.8
}
regions = ['singlemuon','dimuon','gjets','singleelectron','dielectron','signal']
procs = ['zmm','zee','w_weights','photon','wen','wmn']

### Years fit separately
for year in [2018]:
    ws_file = "root/ws_monojet.root"
    fitdiag_file = 'diagnostics/fitDiagnostics_monojet_monov_{year}.root'.format(year=year)
    diffnuis_file = 'diagnostics/diffnuisances_monojet_monov_combined_{year}.root'.format(year=year)
    category='monojet_{year}'.format(year=year)
    outdir = './plots/{year}/'.format(year=year)
    for region in regions:
        plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, lumi[year], year)
    for proc in procs:
        plot_ratio(proc, category, 'root/combined_model_monojet.root'.format(year=year), outdir, lumi[year],year)

    # Flavor integrated
    dataValidation("combined",  "gjets",    category, ws_file, fitdiag_file, outdir,lumi[year],year)
    dataValidation("combinedW", "gjets",    category, ws_file, fitdiag_file, outdir,lumi[year],year)
    dataValidation("combined",  "combinedW",category, ws_file, fitdiag_file, outdir,lumi[year],year)
    # Split by flavor
    dataValidation("dimuon",        "singlemuon",    category, ws_file, fitdiag_file, outdir,lumi[year],year)
    dataValidation("dielectron",    "singleelectron",category, ws_file, fitdiag_file, outdir,lumi[year],year)
    dataValidation("singleelectron","gjets",         category, ws_file, fitdiag_file, outdir,lumi[year],year)
    dataValidation("singlemuon",    "gjets",         category, ws_file, fitdiag_file, outdir,lumi[year],year)
    dataValidation("dielectron",    "gjets",         category, ws_file, fitdiag_file, outdir,lumi[year],year)
    dataValidation("dimuon",        "gjets",         category, ws_file, fitdiag_file, outdir,lumi[year],year)

    # plot_nuis(diffnuis_file, outdir)


### Years fit together
outdir="plots/combined"
diffnuis_file = 'diagnostics/diffnuisances_monojet_monov_combined_combined.root'
plot_nuis(diffnuis_file, outdir)

ws_file = "root/ws_monojet.root"
for year in [2018]:
    fitdiag_file = 'diagnostics/fitDiagnostics_monojet_monov_combined.root'.format(year=year)
    category='monojet_{year}'.format(year=year)
    outdir = './plots/combined_{year}/'.format(year=year)
    for region in regions:
        plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, lumi[year], year)

for wp in ['tight','loose']:
    ### Years fit separately
    ws_file="root/ws_monov_nominal_{WP}.root".format(WP=wp)
    model_file = "root/combined_model_monov_nominal_{WP}.root".format(WP=wp)
    for year in [2018]:
        category='monov{WP}_{YEAR}'.format(WP=wp,YEAR=year)
        filler = {
            "year" : year,
            "category" : category
        }
        fitdiag_file = 'diagnostics/fitDiagnostics_monojet_monov_{year}.root'.format(**filler)

        outdir = './plots/{year}/'.format(**filler)
        for region in regions:
            plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, lumi[year], year)
        for proc in procs:
            plot_ratio(proc, category, model_file, outdir, lumi[year], year)

        # Flavor integrated
        dataValidation("combined",  "gjets",    category, ws_file, fitdiag_file, outdir,lumi[year],year)
        dataValidation("combinedW", "gjets",    category, ws_file, fitdiag_file, outdir,lumi[year],year)
        dataValidation("combined",  "combinedW",category, ws_file, fitdiag_file, outdir,lumi[year],year)
        # Split by flavor
        dataValidation("dimuon",        "singlemuon",    category, ws_file, fitdiag_file, outdir,lumi[year],year)
        dataValidation("dielectron",    "singleelectron",category, ws_file, fitdiag_file, outdir,lumi[year],year)
        dataValidation("singleelectron","gjets",         category, ws_file, fitdiag_file, outdir,lumi[year],year)
        dataValidation("singlemuon",    "gjets",         category, ws_file, fitdiag_file, outdir,lumi[year],year)
        dataValidation("dielectron",    "gjets",         category, ws_file, fitdiag_file, outdir,lumi[year],year)
        dataValidation("dimuon",        "gjets",         category, ws_file, fitdiag_file, outdir,lumi[year],year)


    ### Years fit together
    filler = {
        "WP" : wp,
        "category" : "monov{WP}".format(WP=wp),
    }
    ws_file="root/ws_monov_nominal_{WP}.root".format(**filler)
    fitdiag_file = 'diagnostics/fitDiagnostics_monojet_monov_combined.root'
    model_file = "root/combined_model_monov_nominal_{WP}.root".format(**filler)

    for year in [2018]:
        filler["YEAR"]=year
        outdir = './plots/combined_{YEAR}/'.format(**filler)
        category = 'monov{WP}_{YEAR}'.format(**filler)
        for region in regions:
            plotPreFitPostFit(region,     category,ws_file, fitdiag_file, outdir, lumi[year], year)
        for proc in procs:
            plot_ratio(proc, category, model_file, outdir, lumi[year], year)


