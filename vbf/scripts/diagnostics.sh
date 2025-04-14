#!/bin/bash

### Fit diagnostics
mkdir -p diagnostics
pushd diagnostics
# for YEAR in 2017 2018; do
# for YEAR in 2017; do
# for YEAR in 2018; do
for YEAR in Run3; do
    combine -M FitDiagnostics \
            --saveShapes \
            --saveWithUncertainties \
            -n _vbf_${YEAR} \
            ../cards/card_vbf_${YEAR}.root | tee log_diag_${YEAR}.txt
            # --setParameters mask_vbf_${YEAR}_signal=1 \
    python3 ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
           fitDiagnostics_vbf_${YEAR}.root\
           -g diffnuisances_vbf_${YEAR}.root \
           --all
done


# Combined
# combine -M FitDiagnostics \
#        --saveShapes \
#        --saveWithUncertainties \
#        --robustFit 1 \
#        --setParameters mask_vbf_2017_signal=1,mask_vbf_2018_signal=1 \
#        -n _vbf_combined \
#        ../cards/card_vbf_combined.root

# python3 ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
#        fitDiagnostics_vbf_combined.root \
#        -g diffnuisances_vbf_combined.root
popd
