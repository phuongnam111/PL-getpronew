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
    """    """
    now_utc = datetime.now(timezone.utc)
    desired_timezone = timezone(timedelta(hours=7))
    return now_utc.astimezone(desired_timezone).isoformat()

def generate_ref_id():
    """
    Generate a unique reference ID using UUID.
    """
    return str(uuid.uuid4())

def save_ref_id_to_env(ref_id):
    """
    Saves the generated reference ID to the `.env` file in invoice-be directory.
    """
    env_path = INVOICE_BE_DIR / '.env'
    set_key(str(env_path), 'REF_ID_BATCH', ref_id)
    logger.info(f"Saved REF_ID_BATCH to {env_path}")

def load_invoice_template_1():
    """
    Load environment variables.
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
        logger.error(f"Invalid environment variable: {e}")
        raise

def build_invoice_payload(template, config):
    """
    Build payload.
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
            "invoice_other_receivables": config.invoice_other_receivables_batch,
            "items": config.items,
            "buyer": config.buyer
        }
    }
    logger.info("Invoice payload built successfully.")
    return payload

def publish_invoice(template, config):
    """
    Publish invoice.
    """
    url = ProdConfig.invoice_publishfrompos
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': config.apikey
    }
    payload = build_invoice_payload(template, config)

    logger.info(f"Sending invoice publish request to {url} with payload: {json.dumps(payload, ensure_ascii=False)}")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info("Invoice published successfully.")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to publish invoice: {e}")
        return {"error": str(e)}

def save_response_to_env(response, template_key):
    """ save response to .env file."""
    try:
        env_path = INVOICE_BE_DIR / '.env'
        set_key(str(env_path), f'{template_key.upper()}_RESPONSE', json.dumps(response, ensure_ascii=False))
        logger.info(f"Response saved to {env_path} under key {template_key.upper()}_RESPONSE")
    except Exception as e:
        logger.error(f"Failed to save response to .env: {e}")

if __name__ == "__main__":
    logger.info("Publish invoice batch...")
    try:
        template_1 = load_invoice_template_1()
        response = publish_invoice(template_1, Paramconfig)
        print(f"Invoice publish from batch status: {response}")
        save_response_to_env(response, 'DRAFT_BATCH_IDs')
        logger.info("E-invoice publish process completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during the process: {e}")