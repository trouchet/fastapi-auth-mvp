#!/bin/bash
clear

# Define the omitted paths
OMIT_PATHS="backend/tests/*,*/__init__.py"
SLEEP_TIME=10

while true; do
    coverage run --rcfile=.coveragerc -m pytest
    coverage report --omit="$OMIT_PATHS" --show-missing

    sleep $SLEEP_TIME
    clear
done