#!/bin/sh

export TESTING=true

echo "Running unit tests from directory /unittests"

.venv/bin/python3 -m unittest discover ./unittests
