# monox_fit


## Setup combine

Start by setting up [combine v9.0.0](http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/#combine-v9-recommended-version), 
and then also set up [combineHarvester v2.0.0](https://github.com/cms-analysis/CombineHarvester/tree/v2.0.0):

```bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
REL=$(lsb_release -r | awk '{print $2}')
 
if [[ $REL == 6* ]]; then
    export SCRAM_ARCH=slc6_amd64_gcc530
elif [[ $REL == 7 ]]; then
    export SCRAM_ARCH=slc7_amd64_gcc530
fi

cmsrel CMSSW_11_3_4
cd CMSSW_11_3_4/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v9.0.0
scramv1 b clean; scramv1 b -j4

git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
cd CombineHarvester/
git fetch origin
git checkout v2.0.0
cd ../
scram b -j4
```
