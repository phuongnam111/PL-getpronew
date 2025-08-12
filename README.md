# KMS Kfinance Automation Test

## Installation

1. Clone the repository:
   ```bash
   git clone <git@gitlab.citigo.com.vn:kfinance/automation-test.git>
   cd kiotfinance

2. Install the dependencies:
    ```bash
   pip install -r requirements.txt

## Running

### Local Environment
    python path/to/test_file.py

### For example
    python invoice-be/-name*.py

### Docker Buid & Run

#### Build the Docker Image
    docker build -t kms-kfinance-invoice-automation .
    docker build -t kms-kfinance-payment-automation .
    docker build -t kms-kfinance-lending-automation .
    docker build -t kms-kfinance-zalo-automation .


#### Run Docker Container
    docker run --rm kms-kfinance-invoice-automation
    docker run --rm kms-kfinance-payment-automation
    docker run --rm kms-kfinance-lending-automation
    docker run --rm kms-kfinance-zalo-automation
    

#### Run Docker for Manual Execution of  Scripts
    find /app/ -name '*.py' -exec python {} \;