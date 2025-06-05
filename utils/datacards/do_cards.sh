#!/bin/bash

# Create cards directory

CHANNEL="$1"
YEARS=("Run3")

mkdir -p cards

# Template and target naming
TEMPLATE="../../../../utils/datacards/${CHANNEL}_template.txt"

# -----------------------------------------------------------------------------
# Year-specific luminosity factors
# -----------------------------------------------------------------------------
declare -A LUMI_2017=(
    [LUMIXY]=1.008 [LUMILS]=1.003 [LUMIBBD]=1.004 [LUMIDB]=1.005
    [LUMIBCC]=1.003 [LUMIGS]=1.001 [LUMI]=1.020
)
declare -A LUMI_2018=(
    [LUMIXY]=1.02 [LUMILS]=1.002 [LUMIBBD]=1.0 [LUMIDB]=1.0
    [LUMIBCC]=1.02 [LUMIGS]=1.00 [LUMI]=1.015
)
declare -A LUMI_Run3=(
    [LUMIXY]=1.02 [LUMILS]=1.002 [LUMIBBD]=1.0 [LUMIDB]=1.0
    [LUMIBCC]=1.02 [LUMIGS]=1.00 [LUMI]=1.015
)


for YEAR in "${YEARS[@]}"; do
    TAG="${CHANNEL}_${YEAR}"
    CARD="cards/card_${TAG}.txt"
    cp ${TEMPLATE} ${CARD}
    sed -i "s|@YEAR|${YEAR}|g" ${CARD}

    # Inject correct luminosities
    LUMI_VAR="LUMI_${YEAR}[@]"
    for VAR in LUMIXY LUMILS LUMIBBD LUMIDB LUMIBCC LUMIGS LUMI; do
        VALUE="${!LUMI_VAR%% *}"
        VALUE="$(eval echo \${LUMI_${YEAR}[${VAR}]})"
        sed -i "s|@${VAR}|${VALUE}|g" ${CARD}
    done
    
    # Year-specific edits
    if [[ "${YEAR}" == "2018" || "${YEAR}" == "Run3" ]]; then
        sed -i "/prefir/d" ${CARD}
    fi

    # affected by mistags in loose region with ratio of -1/20
    sed -i "s|@MISTAGLOOSEW|0.999        |g" ${CARD}
    sed -i "s|@MISTAGLOOSEZ|0.998        |g" ${CARD}
    sed -i "s|@MISTAGLOOSEG|0.998        |g" ${CARD}

    # Fix input file references
    sed -i "s|combined_model.root|../root/combined_model_${CHANNEL}.root|g" ${CARD}
    sed -i "s|${CHANNEL}_qcd_ws.root|../root/${CHANNEL}_qcd_ws.root|g" ${CARD}

    # Remove useless stat uncertainties
    # Uncertainties are removed if they do not have a variation histogram available
    # The criteria for whether a variation histogram is present are defined in make_ws.py
    TMPFILE="$(mktemp)"
    rootls -1 root/ws_${CHANNEL}.root:category_${TAG} > ${TMPFILE}
    for NUIS in $(grep shape ${CARD} | awk '{print $1}' | grep stat); do
      if [ $(grep -c ${NUIS}Up ${TMPFILE}) -eq 0 ]; then
         sed -i "/^${NUIS} .*/d" ${CARD}
         echo "Warning: removing nuisance ${NUIS} from ${CARD}, shape not present in ws_${TAG}.root"
      fi
    done
    rm ${TMPFILE}

    text2workspace.py ${CARD} --channel-masks
    python3 ${CMSSW_BASE}/src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py --all -f html ${CARD} > cards/systematics_${YEAR}.html
done