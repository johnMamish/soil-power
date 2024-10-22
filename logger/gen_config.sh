#!/bin/bash

# Read and output the content of config.py.template
cat config.py.template > config.py

# Append each command-line argument to the config.py file
for arg in "$@"; do
    echo "TASKS += [$arg]" >> config.py
done

