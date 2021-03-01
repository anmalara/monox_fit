TAG=${1}
SUBTAG=${2}
SUBSUBTAG=default
cd /afs/cern.ch/work/a/aalbert/public/2020-03-09_limit/monox_fit/combine_vj/
JDIR=$(readlink -e ../monojet/${TAG}/${SUBTAG}/)
VDIR=$(readlink -e ../monov/${TAG}/${SUBTAG}/)

WDIR=./${TAG}/${SUBTAG}_${SUBSUBTAG}/
mkdir -p $WDIR
pushd $WDIR

mkdir -p root
cp $JDIR/root/*.root ./root
cp $VDIR/root/*.root ./root

mkdir -p cards
for YEAR in 2017 2018 combined; do
    COMBINED="./cards/card_monojet_monov_nominal_${YEAR}.txt"
    combineCards.py $JDIR/cards/card_monojet_${YEAR}.txt $VDIR/cards/card_nominal_monov_${YEAR}.txt > ${COMBINED}

    # Get rid of channel prefixes + fix white space
    sed -i 's/ch\(1\|2\)_/    /g' ${COMBINED}
    sed -i 's/^bin    /bin/g' ${COMBINED}

    # Fix input file names
    sed -i '/combined_model_/ s|[^ ]*\(combined_model_.*.root\)|root/\1|g' ${COMBINED}
    sed -i '/_qcd_ws/ s|[^ ]*\(mono[^ ]*_qcd_ws.root\)|root/\1|g' ${COMBINED}

    text2workspace.py ${COMBINED} --channel-masks & 

    # ### DEBUG
    # # individual channels
    # INDIVIDUAL="./cards/card_monojet_${YEAR}.txt"
    # combineCards.py ${COMBINED} --xc 'monov.*' > ${INDIVIDUAL}
    # sed -i 's/ch\(1\|2\)_/    /g' ${INDIVIDUAL}
    # sed -i 's/^bin    /bin/g' ${INDIVIDUAL}
    # sed -i '/combined_model_/ s|[^ ]*\(combined_model_.*.root\)|root/\1|g' ${INDIVIDUAL}
    # sed -i '/_qcd_ws/ s|[^ ]*\(mono[^ ]*_qcd_ws.root\)|root/\1|g' ${INDIVIDUAL}
    # text2workspace.py ${INDIVIDUAL} --channel-masks &
done
popd
ln -fs $(readlink -e scripts/Makefile) ${WDIR}/Makefile
