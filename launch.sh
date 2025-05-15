#!/bin/sh

export WEBPAGES_DIR="ANALYST/"
# export WEBPAGES="DEV/"

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

echo "Index vs base size comparison:"
du -sh index.shelve "$WEBPAGES_DIR"