#!/bin/sh

# export WEBPAGES_DIR="ANALYST/"
export WEBPAGES_DIR="DEV/"
export PARTIAL_INDEX_DIR="partial_indexes/"

# SPECIFY FLAG --no-test TO SKIP UNIT TESTS BEFORE LAUNCH
if [ "$1" = "--no-test" ]; then
    (exit 0)
else
    ./test.sh
fi

if [ $? -ne 0 ]; then
    exit 1
else
    .venv/bin/python3 main.py
fi

if [ $? -eq 0 ]; then
    echo "Index vs base size comparison:"
    du -sh "$PARTIAL_INDEX_DIR" "$WEBPAGES_DIR"
fi