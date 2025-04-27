#!/bin/bash

### Impacts
mkdir -p impacts_nocondor
pushd impacts_nocondor
# for YEAR in 2018 combined; do
#for YEAR in 2017; do
# for YEAR in 2018; do
for YEAR in Run3; do
    mkdir ${YEAR}
    pushd ${YEAR}
    COMMON_OPTS="-t -1 -m 125 --parallel=4 --rMin=-5 --rMax=5 --robustFit 1 --cminDefaultMinimizerStrategy 0 --autoRange 5 --squareDistPoiStep"
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root --doInitialFit ${COMMON_OPTS} | tee log_impact1.txt
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root --doFits ${COMMON_OPTS} | tee log_impact2.txt
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -o impacts.json ${COMMON_OPTS} | tee log_impact3.txt
    popd
    plotImpacts.py -i ${YEAR}/impacts.json -o impacts_${YEAR} --blind
done
