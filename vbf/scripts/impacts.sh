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

    #combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --doInitialFit --robustFit 1 --cminDefaultMinimizerStrategy 0 ${COMMON_OPTS} | tee log_impact1.txt
    #combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --robustFit 1 --doFits --cminDefaultMinimizerStrategy 0 ${COMMON_OPTS} | tee log_impact2.txt
    #combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 -o impacts.json --robustFit 1 --cminDefaultMinimizerStrategy 0 ${COMMON_OPTS} | tee log_impact3.txt

    combineTool.py -M Impacts -t -1 -d ../../cards/card_vbf_${YEAR}.root -m 125 --doInitialFit --robustFit 1 --cminDefaultMinimizerStrategy 0 ${COMMON_OPTS} | tee log_impact1.txt
    combineTool.py -M Impacts -t -1 -d ../../cards/card_vbf_${YEAR}.root -m 125 --robustFit 1 --doFits --cminDefaultMinimizerStrategy 0 ${COMMON_OPTS} | tee log_impact2.txt
    combineTool.py -M Impacts -t -1 -d ../../cards/card_vbf_${YEAR}.root -m 125 -o impacts.json --robustFit 1 --cminDefaultMinimizerStrategy 0 ${COMMON_OPTS} | tee log_impact3.txt

    # trying to use toys
    #combineTool.py -M Impacts -t -1 -d ../../cards/card_vbf_${YEAR}.root -m 125 --doInitialFit --robustFit 1 --parallel=4 --rMin=-1 | tee log_impact1.txt
    #combine -M MultiDimFit -n _initialFit_Test --algo singles --redefineSignalPOIs r --verbose 3 --robustFit 1 --rMin=-1 -m 125 -d ../../cards/card_vbf_2017.root
    #combineTool.py -M Impacts -t -1 -d ../../cards/card_vbf_${YEAR}.root -m 125 --robustFit 1 --doFits --parallel 4 --parallel=4 --rMin=-1 | tee log_impact2.txt
    #combineTool.py -M Impacts -t -1 -d ../../cards/card_vbf_${YEAR}.root -m 125 -o impacts.json  --parallel=4 --rMin=-1 | tee log_impact3.txt

    # Trying to use with condor
    #COMMON_OPTS="--parallel=4 --rMin=-5 --rMax=5 --autoRange 5 --squareDistPoiStep"
    #combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --doInitialFit --robustFit 1 --cminDefaultMinimizerStrategy 0 ${COMMON_OPTS} || exit 1

    # Submit the hard work to condor
    #TAG=task_${YEAR}_${SIGNAL}_${RANDOM}
    #combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --robustFit 1 --doFits --job-mode condor --task-name ${TAG} --cminDefaultMinimizerStrategy 0 ${COMMON_OPTS} || exit 1

    #combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 -o impacts.json  --parallel=4 --rMin=-1 | tee log_impact3.txt popd

    # mkdir ${YEAR}_nophoton
    # pushd ${YEAR}_nophoton
    # combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --doInitialFit --robustFit 1 -t -1 --expectSignal=${SIGNAL} --parallel=4 --setParameters mask_vbf_photon=1 --rMin=-1
    # combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 --robustFit 1 --doFits --parallel 4 -t -1 --expectSignal=${SIGNAL} --parallel=4  --setParameters mask_vbf_photon=1 --rMin=-1
    # combineTool.py -M Impacts -d ../../cards/card_vbf_${YEAR}.root -m 125 -o impacts.json -t -1 --expectSignal=${SIGNAL}  --parallel=4  --setParameters mask_vbf_photon=1 --rMin=-1
    popd
    # plotImpacts.py -i ${YEAR}_nophoton/impacts.json -o impacts_${YEAR}_nophoton
    plotImpacts.py -i ${YEAR}/impacts.json -o impacts_${YEAR} --blind
done
