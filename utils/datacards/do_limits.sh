#!/bin/bash
source "$(dirname "$0")/colors.sh"

# Limit script

CHANNEL="$1"
YEAR="$2"
FOLDER="limit"

mkdir -p ${FOLDER}
pushd ${FOLDER} > /dev/null

TAG="${CHANNEL}_${YEAR}"
CARD="../cards/card_${TAG}.root"
LOGFILE="log_limit_${YEAR}.txt"
METHOD="-M AsymptoticLimits"
# METHOD="-M AsymptoticLimits -t -1"

# Uncomment the options you want to use
EXTRA_OPTS=()
EXTRA_OPTS+=(--rMin -5 --rMax 5)
# EXTRA_OPTS+=(--run blind)

cecho blue "Running AsymptoticLimits for ${TAG}"
combine ${METHOD} ${CARD} -n "_${TAG}" "${EXTRA_OPTS[@]}" | tee ${LOGFILE}

popd > /dev/null
