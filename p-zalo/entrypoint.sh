#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

echo "Running zalo..."
python zalo-runner.py

echo "All tests completed."