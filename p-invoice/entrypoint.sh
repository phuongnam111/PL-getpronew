#!/bin/bash

set -Eeuo pipefail
# #clear screen shots
# rm -f /app/screenshots/*.png || true
echo "Running invoice..."
exec python -u invoice-runner.py "$@"
echo "All tests completed."