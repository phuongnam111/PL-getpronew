#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

echo "Running payment...."
python payment-runner.py
#find /app/payment-fe -name '*.py' -exec python {} \;;

echo "All tests completed."