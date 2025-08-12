#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.
# #clear screen shots
# rm -f /app/screenshots/*.png || true
echo "Running lending..."
python lending-runner.py
#find /app/lending-fe -name '*.py' -exec python {} \;;

echo "All tests completed."