#!/bin/bash
set -e
#TAG='default'
TAG='250218'
# INDIR=../input/vbf/2020-07-16_vbf_eemitigation_jerfix_circular_nohfhf_v2
# INDIR="/eos/home-h/hevard/misc/24_10_16_test_fit"
# INDIR="/eos/home-h/hevard/misc/24_10_24_test_fit"
#INDIR="/eos/home-h/hevard/misc/24_11_20_for_fit_2023/Run3Summer23"
#INDIR="/eos/home-h/hevard/misc/25_02_05_forfit"
#INDIR="/eos/home-h/hevard/misc/25_02_10_plots_for_fit/for_fit/Run3Summer22"
#INDIR="/eos/home-h/hevard/misc/25_02_10_plots_for_fit/for_fit/Run3Summer22EE"
#INDIR="/eos/home-h/hevard/misc/25_02_10_plots_for_fit/for_fit/Run3Summer23"
#INDIR="/eos/home-h/hevard/misc/25_02_10_plots_for_fit/for_fit/Run3Summer23BPix"
#INDIR="/eos/home-h/hevard/misc/25_02_10_plots_for_fit/for_fit/Run3_22_23"
INDIR="/eos/home-h/hevard/misc/25_02_18_forfit/Run3_22_23/"

INDIR="$(readlink -e $INDIR)"

OUTDIR="../vbf/$(basename $INDIR)/${TAG}/root"
mkdir -p ${OUTDIR}
OUTDIR="$(readlink -e ${OUTDIR})"

# Save some information so we can trace inputs
INFOFILE=${OUTDIR}/INFO.txt
echo "Input directory: ${INDIR}" > ${INFOFILE}
echo "--- INPUT ---" > ${INFOFILE}

INFILE=${INDIR}/legacy_limit_vbf.root   
WSFILE=${OUTDIR}/ws_vbf.root

# Save the check sum for the input
md5sum ${INFILE} >> ${INFOFILE}

# Save repo information to the info file
echo "--- REPO INFO ---" >> ${INFOFILE}
echo "Commit hash: $(git rev-parse HEAD)" >> ${INFOFILE}
echo "Branch name: $(git rev-parse --abbrev-ref HEAD)" >> ${INFOFILE}
git diff >> ${INFOFILE}

# takes mjj from input file and puts it in workspace
# applies JES variations
# -> already applied in pyRAT?
# applies Diboson variations
# -> not applied in pyRAT ?
# applies mistag variations
# -> not applied in pyrat?
# applies signal theory variations
# -> not applied in pyrat?
# makes statistical uncertainty into single nuisance
#./make_ws.py ${INFILE} --out ${WSFILE} --categories vbf_2022

# Following works:
./make_ws.py ${INFILE} --out ${WSFILE} --categories vbf_2017
# exit

# runs on ["Z_constraints_qcd_withphoton","W_constraints_qcd","Z_constraints_ewk_withphoton","W_constraints_ewk"]
#./runModel.py ${WSFILE} --categories vbf_2022 --out ${OUTDIR}/combined_model_vbf.root

# added check in convert.py,
# looking to add expectations for model  model_mu_cat_vbf_2017_ewk_zjets_bin_0 but not found in workspace
# same for qcd works fine
./runModel.py ${WSFILE} --categories vbf_2017 --out ${OUTDIR}/combined_model_vbf.root

# Split for IC
# ./runModel.py ${WSFILE} --categories vbf_2017 --out ${OUTDIR}/combined_model_vbf_forIC_2017.root --rename "mjj_MTR_2017"
# ./runModel.py ${WSFILE} --categories vbf_2018 --out ${OUTDIR}/combined_model_vbf_forIC_2018.root --rename "mjj_MTR_2018"

cp sys/vbf_qcd_nckw_ws_201*.root ${OUTDIR}

# Save the check sums for the output
echo "--- OUTPUT ---" >> ${INFOFILE}
md5sum ${OUTDIR}/*root >> ${INFOFILE}

ln -fs $(readlink -e ../vbf/templates/Makefile) ${OUTDIR}/../Makefile

exit
pushd ${OUTDIR}/..
make cards
popd

echo $(readlink -e ${OUTDIR}/..)
