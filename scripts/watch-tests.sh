#!/bin/bash
clear

# Define the omitted paths
OMIT_PATHS="backend/tests/*,*/__init__.py"
SLEEP_TIME_S=20
LOG_FILE="test_log.txt"  # Output filename for the test log


while true; do
    coverage run --rcfile=.coveragerc -m pytest
    coverage report --omit="$OMIT_PATHS" --show-missing &> "$LOG_FILE"

    sleep $SLEEP_TIME_S
    clear
done