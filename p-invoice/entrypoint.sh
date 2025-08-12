#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

echo "Running invoice..."
python invoice-runner.py
#find /app/invoice-fe -name '*.py' -exec python {} \;

echo "All tests completed."