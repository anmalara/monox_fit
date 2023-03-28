# monox_fit


## Setup combine

Start by setting up [combine in CMSSW 8](http://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/#slc6cc7-release-cmssw_8_1_x), 
and then also set up [combineHarvester](http://cms-analysis.github.io/CombineHarvester/index.html):

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
