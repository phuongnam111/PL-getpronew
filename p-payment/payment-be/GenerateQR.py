import requests
import json
import logging
import os
from dotenv import set_key, load_dotenv
from config import ProdConfig, Paramconfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_qr_code():
    """Generate QR code via API call"""
    url = ProdConfig.generate_qr_url
    headers = {
        'Authorization': Paramconfig.authorization.strip(),
        'x-api-key': Paramconfig.apikey,
        'Content-Type': 'application/json'
    }
    data = {
        "payment_id": Paramconfig.payment_id,
        "payment_code": Paramconfig.payment_code,
        "amount": Paramconfig.amount,
        "uuid": Paramconfig.uuid,
        "merchant_code": Paramconfig.merchant_code,
        "merchant_id": Paramconfig.merchant_id,
        "content": Paramconfig.content
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to generate QR code: {e}")
        return None


def save_to_env(response_data):
    """Save response data to .env file"""
    try:
        # env be
        env_file_path = os.path.join(os.path.dirname(__file__), '.env')
        
        body = response_data.get('body', {})
        env_vars = {
            "IMAGE": body.get('image', ''),
            "TRANSACTION_ID": str(body.get('transaction_id', '')),
            "QR_STRING": body.get('qr_string', ''),
            "KOV_CODE": body.get('kov_code', ''),
            "PAYMENT_REQ_ID": body.get('payment_req_id', '')
        }
        
        for key, value in env_vars.items():
            set_key(env_file_path, key, value)
        
        logger.info(f"Saved to {env_file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save to .env: {e}")
        return False


def print_results():
    """Print environment variables"""
    env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_file_path)
    vars_to_print = ['IMAGE', 'TRANSACTION_ID', 'QR_STRING', 'KOV_CODE', 'PAYMENT_REQ_ID']
    
    for var in vars_to_print:
        print(f"{var}: {os.getenv(var, 'Not set')}")


if __name__ == "__main__":
    # Generate QR code
    response = generate_qr_code()
    
    if response and save_to_env(response):
        print_results()
        logger.info("QR code generated successfully")
    else:
        logger.error("Failed to generate QR code")
