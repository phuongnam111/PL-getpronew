#!/bin/bash

set -Eeuo pipefail
# #clear screen shots
# rm -f /app/screenshots/*.png || true
echo "Running payment..."
exec python -u payment-runner.py "$@"
echo "All tests completed."
#find /app/lending-fe -name '*.py' -exec python {} \;;