
### Asimov limit
mkdir -p limit
pushd limit
# for YEAR in 2017 2018; do
# for YEAR in 2017; do
# for YEAR in 2018; do
for YEAR in Run3; do
    combine -M AsymptoticLimits -t -1 -n _vbf_${YEAR} ../cards/card_vbf_${YEAR}.root --saveToys | tee log_asimov_${YEAR}.txt
    # combine -M AsymptoticLimits -t -1 -n _vbf_${YEAR} ../cards/card_vbf_${YEAR}.root --rMax=100 | tee log_asimov_${YEAR}.txt
    #combine -M AsymptoticLimits -t -1 -n _vbf_${YEAR} ../cards/card_vbf_${YEAR}.root --run blind| tee log_asimov_${YEAR}.txt
    # combine -M AsymptoticLimits -t -1 -n _vbf_nophoton_${YEAR} --setParameters mask_vbf_${YEAR}_photon=1 ../cards/card_vbf_${YEAR}.root | tee log_asimov_nophoton_${YEAR}.txt
done

#combine -M AsymptoticLimits -t -1 -n _vbf_combined ../cards/card_vbf_combined.root | tee log_asimov_combined.txt
# combine -M AsymptoticLimits -t -1 -n _vbf_nophoton_combined --setParameters mask_vbf_2017_photon,mask_vbf_2018_photon=1 ../cards/card_vbf_combined.root | tee log_asimov_nophoton_combined.txt
popd
