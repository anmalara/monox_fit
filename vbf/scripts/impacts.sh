#!/bin/bash

### Impacts
mkdir -p impacts_nocondor
pushd impacts_nocondor
for YEAR in 2018; do
    mkdir ${YEAR}
    pushd ${YEAR}
    COMMON_OPTS="-t -1 -m 125 --parallel=4 --rMin=-1 --robustFit 1 --cminDefaultMinimizerStrategy 0"
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root --doInitialFit ${COMMON_OPTS} | tee log_impact1.txt
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root --doFits ${COMMON_OPTS} | tee log_impact2.txt
    combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -o impacts.json ${COMMON_OPTS} | tee log_impact3.txt
    popd
    plotImpacts.py -i ${YEAR}/impacts.json -o impacts_${YEAR} --blind

    # mkdir ${YEAR}_nophoton
    # pushd ${YEAR}_nophoton
    # combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --doInitialFit --robustFit 1 -t -1 --expectSignal=${SIGNAL} --parallel=4 --setParameters mask_vbf_photon=1 --rMin=-1
    # combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --robustFit 1 --doFits --parallel 4 -t -1 --expectSignal=${SIGNAL} --parallel=4  --setParameters mask_vbf_photon=1 --rMin=-1
    # combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 -o impacts.json -t -1 --expectSignal=${SIGNAL}  --parallel=4  --setParameters mask_vbf_photon=1 --rMin=-1
    # popd
    # plotImpacts.py -i ${YEAR}_nophoton/impacts.json -o impacts_${YEAR}_nophoton
done