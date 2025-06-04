#!/bin/bash

### Asimov limit
mkdir -p limit
pushd limit
# for YEAR in 2017 2018; do
# for YEAR in 2017; do
# for YEAR in 2018; do
for YEAR in Run3; do
    combine -M AsymptoticLimits -t -1 -n _monojet_${YEAR} ../cards/card_monojet_${YEAR}.root --saveToys | tee log_asimov_${YEAR}.txt
    # combine -M AsymptoticLimits -t -1 -n _monojet_${YEAR} ../cards/card_monojet_${YEAR}.root  --setParameters 'LUMISCALE=1' --freezeParameters LUMISCALE | tee log_${YEAR}.txt &
    # combine -M AsymptoticLimits -t -1 -n _asimov_monojet_${YEAR} ../cards/card_monojet_${YEAR}.root  --setParameters 'LUMISCALE=1' --freezeParameters LUMISCALE &> log_asimov_${YEAR}.txt &
    # combine -M AsymptoticLimits -t -1 -n _monojet_${YEAR} ../cards/card_monojet_${YEAR}.root --setParameters 'LUMISCALE=1' --freezeParameters LUMISCALE | tee log_asimov_${YEAR}.txt
done
popd
