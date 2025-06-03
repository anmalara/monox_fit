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
            --cminDefaultMinimizerStrategy 0 \
            -n _monojet_${YEAR} \
            ../cards/card_monojet_${YEAR}.root | tee diag_${YEAR}.log &&
    python3 ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
           fitDiagnostics_monojet_${YEAR}.root\
           -g diffnuisances_monojet_${YEAR}.root \
           --all
        #    --skipFitS
done
#     combine -M FitDiagnostics \
#             --saveShapes \
#             --saveWithUncertainties \
#             --robustFit 1 \
#             -n _monojet_unblind_${YEAR} \
#             ../cards/card_monojet_${YEAR}.root \
#             --cminDefaultMinimizerStrategy 0 \
#             | tee diag_unblind_${YEAR}.log &&
#     python3 ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py \
#            fitDiagnostics_monojet_unblind_${YEAR}.root \
#            -g diffnuisances_monojet_unblind_${YEAR}.root \
#            --skipFitS &

popd
