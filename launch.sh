#!/bin/sh

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

du -sh index.shelve ANALYST/