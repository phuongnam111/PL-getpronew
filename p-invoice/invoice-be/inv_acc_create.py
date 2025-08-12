import requests
import json
from config import ProdConfig, Paramconfig
import logging
from dotenv import set_key, load_dotenv
from requests.exceptions import RequestException
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

INVOICE_BE_DIR = Path(__file__).parent
env_path = INVOICE_BE_DIR / '.env'
load_dotenv(env_path)

def configure_account():
    """
    API created invoice account from kvs to partner.
    """
    url = ProdConfig.invoice_host
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': Paramconfig.apikey
    }
    data = {
        "merchant_id": Paramconfig.merchant_id,
        "merchant_code": Paramconfig.merchant_code,
        "partner": Paramconfig.partner,
        "username": Paramconfig.username,
        "password": Paramconfig.password,
        "tax_code": Paramconfig.tax_code,
        "login_url": Paramconfig.login_url
    }

    try:
        logger.info("Sending PUT request to configure account.")
        response = requests.put(url, headers=headers, json=data)

        if response.status_code == 200:
            logger.info("Request successful.")
            response_data = response.json()
            save_to_env_file(response_data)
            return response_data
        else:
            logger.error(f"Request failed with status code: {response.status_code}")
            logger.error(f"Response body: {response.text}")
    except RequestException as e:
        logger.exception(f"An error occurred while making the request: {e}")
    return None

def save_to_env_file(response_data):
    """
    Created env file in the same directory as this script.
    """
    logger.info(f"Saving response data to .env file at: {env_path}")
    
    try:
        env_path.parent.mkdir(parents=True, exist_ok=True)
        
        set_key(str(env_path), "PARTNER", response_data.get('partner', ''))
        set_key(str(env_path), "MERCHANT_ID", str(response_data.get('merchant_id', '')))
        set_key(str(env_path), "MERCHANT_CODE", response_data.get('merchant_code', ''))
        logger.info(f"Data successfully saved to {env_path}")
    except Exception as e:
        logger.exception(f"Failed to save data to {env_path}: {e}")

def main():
    """
    Response logged.
    """
    response_data = configure_account()
    if response_data:
        logger.info("Account configuration successful.")
        logger.info(f"Partner: {response_data.get('partner', 'N/A')}")
        logger.info(f"Merchant ID: {response_data.get('merchant_id', 'N/A')}")
        logger.info(f"Merchant Code: {response_data.get('merchant_code', 'N/A')}")
        logger.info(f"Username: {response_data.get('username', 'N/A')}")
        logger.info(f"Tax Code: {response_data.get('tax_code', 'N/A')}")
        logger.info(f"Login URL: {response_data.get('login_url', 'N/A')}")
    else:
        logger.error("Account configuration failed.")

if __name__ == "__main__":
    main()