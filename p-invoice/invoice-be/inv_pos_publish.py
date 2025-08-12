import json
import requests
import logging
import os
from pathlib import Path
from dotenv import load_dotenv, set_key
from config import ProdConfig, Paramconfig
from datetime import datetime, timezone, timedelta
import uuid

INVOICE_BE_DIR = Path(__file__).parent

env_path = INVOICE_BE_DIR / '.env'
load_dotenv(env_path)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_current_datetime_iso():
    """
    Returns the current datetime in ISO 8601 format with a specified timezone (UTC+7).
    """
    now_utc = datetime.now(timezone.utc)
    desired_timezone = timezone(timedelta(hours=7))
    now_with_timezone = now_utc.astimezone(desired_timezone)
    return now_with_timezone.isoformat()

def generate_ref_id():
    """
    Generates a unique reference ID using UUID4.
    """
    return str(uuid.uuid4())

def save_ref_id_to_env(ref_id):
    """
    Saves the generated reference ID to the `.env` file in invoice-be directory.
    """
    env_path = INVOICE_BE_DIR / '.env'
    set_key(str(env_path), 'REF_ID_POS', ref_id)
    logger.info(f"Saved REF_ID_POS to {env_path}")

def load_invoice_template_1():
    """
    Loads invoice template 1 details from environment variables.
    """
    try:
        return {
            "merchant_id": int(os.getenv('MERCHANT_ID', 0)),
            "merchant_code": os.getenv('MERCHANT_CODE', 'N/A'),
            "partner": os.getenv('PARTNER', 'N/A'),
            "invoice_template_id": os.getenv('TEMPLATE_1_INVOICE_TEMPLATE_ID', 'N/A'),
            "invoice_serial": os.getenv('TEMPLATE_1_INVOICE_SERIAL', 'N/A'),
            "invoice_template_no": os.getenv('TEMPLATE_1_INVOICE_TEMPLATE_NO', 'N/A')
        }
    except ValueError as e:
        logger.error(f"Error loading invoice template: {e}")
        return None

def invoice_publish_from_pos(template, config):
    """
    Constructs the payload for the invoice publish request.
    """
    ref_id = generate_ref_id()
    save_ref_id_to_env(ref_id)

    payload = {
        "merchant_id": template["merchant_id"],
        "merchant_code": template["merchant_code"],
        "partner": template["partner"],
        "invoice": {
            "code": config.code,
            "tax_reduction_config": False,
            "ref_id": ref_id,
            "invoice_serial": template["invoice_serial"],
            "invoice_name": config.invoice_name,
            "invoice_template_id": template["invoice_template_id"],
            "invoice_template_no": template["invoice_template_no"],
            "invoice_datetime": get_current_datetime_iso(),
            "currency_code": config.currency_code,
            "exchange_rate": config.exchange_rate,
            "invoice_note": config.invoice_note,
            "payment_method_names": config.payment_method_names,
            "invoice_discount": config.invoice_discount,
            "invoice_other_receivables": config.invoice_other_receivables,
            "items": config.items,
            "buyer": config.buyer
        }
    }
    logger.debug(f"Payload constructed: {json.dumps(payload, ensure_ascii=False)}")
    return payload

def publish_invoice(template, config):
    """
    POST invoice publish request.
    """
    url = ProdConfig.invoice_publishfrompos
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': config.apikey
    }

    payload = invoice_publish_from_pos(template, config)
    try:
        logger.info(f"Sending invoice publish request to URL: {url}")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info("Invoice publish request successful.")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error during invoice publish request: {e}")
        return {"error": str(e)}

def save_response_to_env(response, template_key):
    """
    Save response to .env file in invoice-be directory.
    """
    try:
        env_path = INVOICE_BE_DIR / '.env'
        set_key(str(env_path), f'{template_key.upper()}_RESPONSE', json.dumps(response, ensure_ascii=False))
        logger.info(f"Response for {template_key} saved to {env_path}")
    except Exception as e:
        logger.error(f"Failed to save response to .env: {e}")

def main():
    """
    Main function to execute invoice publishing.
    """
    logger.info("Starting invoice publish process...")
    template_1 = load_invoice_template_1()

    if not template_1:
        logger.error("Failed to load template 1. Exiting.")
        return

    response = publish_invoice(template_1, Paramconfig)

    if response and not response.get('error'):
        logger.info(f"Invoice publish response: {response}")
        save_response_to_env(response, 'template_1')
        print("E-invoice publish success for template_1")
    else:
        logger.error(f"Invoice publish failed for template_1. Error: {response.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()