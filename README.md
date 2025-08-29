### KMS KFinance Automation Tests

Automated test suites for KFinance services.

## Requirements

- Python 3.10+
- Git
- Docker

## Installation

### 1) Clone the repository
```bash
git clone git@gitlab.citigo.com.vn:kfinance/automation-test.git
cd automation-test
```

### 2) (Recommended) Create a virtual environment and install dependencies
```bash
python -m venv .venv
# Windows PowerShell
. .\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

- Create a `.env` file at the repository root (or set environment variables in your shell/CI).
- Common values include: service base URLs, tokens, test accounts, and endpoints for Invoice/Payment/Lending/Zalo.

Example `.env` (adjust to your environment):
```bash
ENV=dev
API_BASE_URL=https://api.example.com
AUTH_TOKEN=your_token_here
```

## Running Tests (Local)

- Run a specific test file:
```bash
python path/to/test_file.py
```

- Example for an Invoice backend test file:
```bash
python invoice-be/example_test.py
```

- If your project uses pytest (recommended):
```bash
python -m pytest -q
python -m pytest invoice-be -q
python -m pytest -k "payment and smoke" -q
```

## Docker

### Build images
Build per-module images (update Dockerfiles if your project uses multiple Dockerfiles):
```bash
docker build -t kms-kfinance-invoice-automation  -f Dockerfile.invoice  .
docker build -t kms-kfinance-payment-automation  -f Dockerfile.payment  .
docker build -t kms-kfinance-lending-automation  -f Dockerfile.lending  .
docker build -t kms-kfinance-zalo-automation     -f Dockerfile.zalo     .
```

If you use a single Dockerfile with build args:
```bash
docker build -t kms-kfinance-invoice-automation --build-arg MODULE=invoice .
```

### Run containers (tests auto-run on start)
```bash
docker run --rm kms-kfinance-invoice-automation
docker run --rm kms-kfinance-payment-automation
docker run --rm kms-kfinance-lending-automation
docker run --rm kms-kfinance-zalo-automation
```

### Run a container for manual execution
Enter the container and run Python commands as needed:
```bash
docker run --rm -it kms-kfinance-payment-automation sh
# Inside the container
find /app -name '*.py' -print
python /app/path/to/test_file.py
```

Or run a single command at container start:
```bash
docker run --rm kms-kfinance-payment-automation sh -lc "find /app -name '*.py' -print -exec python {} \;"
```

## Project structure (example)

```
automation-test/
  invoice-be/
  p-payment/
    payment-notify/
      config.py
      dev_bidv_transaction.py
  lending/
  zalo/
  requirements.txt
  Dockerfile.invoice
  Dockerfile.payment
  Dockerfile.lending
  Dockerfile.zalo
```

## Troubleshooting

- Dependency issues: upgrade pip and reinstall requirements.
- Import errors: run commands from the repo root and check `PYTHONPATH`.
- Docker build failures: verify Dockerfile paths and build context.
- Configuration/env issues: verify `.env` or CI secrets.