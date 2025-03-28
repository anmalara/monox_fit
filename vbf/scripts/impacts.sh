#!/bin/bash

### Impacts
mkdir -p impacts_nocondor
pushd impacts_nocondor
# for YEAR in 2018 combined; do
#for YEAR in 2017; do
for YEAR in 2018; do
    mkdir ${YEAR}
    pushd ${YEAR}
    COMMON_OPTS="--parallel=4 --rMin=-5 --rMax=5 --autoRange 5 --squareDistPoiStep"

    combineTool.py -M Impacts -t -1 -d ../../cards/card_vbf_${YEAR}.root -m 125 --doInitialFit --robustFit 1 --cminDefaultMinimizerStrategy 0 ${COMMON_OPTS} | tee log_impact1.txt
    combineTool.py -M Impacts -t -1 -d ../../cards/card_vbf_${YEAR}.root -m 125 --robustFit 1 --doFits --cminDefaultMinimizerStrategy 0 ${COMMON_OPTS} | tee log_impact2.txt
    combineTool.py -M Impacts -t -1 -d ../../cards/card_vbf_${YEAR}.root -m 125 -o impacts.json --robustFit 1 --cminDefaultMinimizerStrategy 0 ${COMMON_OPTS} | tee log_impact3.txt

    popd
    plotImpacts.py -i ${YEAR}/impacts.json -o impacts_${YEAR} --blind
done
