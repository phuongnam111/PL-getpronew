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
    """Get current datetime in ISO format with +7 timezone"""
    now_utc = datetime.now(timezone.utc)
    desired_timezone = timezone(timedelta(hours=7))
    return now_utc.astimezone(desired_timezone).isoformat()

def generate_ref_id():
    """Generate a unique reference ID using UUID."""
    return str(uuid.uuid4())

def save_ref_id_to_env(ref_id):
    """Saves the generated reference ID to the `.env` file in invoice-be directory."""
    set_key(str(env_path), 'REF_ID_BATCH', ref_id)
    logger.info(f"Saved REF_ID_BATCH to {env_path}")

def load_invoice_template_1():
    """Load environment variables."""
    try:
        return {
            "merchant_id": int(os.getenv('MERCHANT_ID', Paramconfig.merchant_id)),
            "merchant_code": os.getenv('MERCHANT_CODE', Paramconfig.merchant_code),
            "partner": os.getenv('PARTNER', Paramconfig.partner),
            "invoice_template_id": os.getenv('TEMPLATE_1_INVOICE_TEMPLATE_ID', Paramconfig.invoice_template_id),
            "invoice_serial": os.getenv('TEMPLATE_1_INVOICE_SERIAL', Paramconfig.invoice_serial),
            "invoice_template_no": os.getenv('TEMPLATE_1_INVOICE_TEMPLATE_NO', Paramconfig.invoice_template_no)
        }
    except ValueError as e:
        logger.error(f"Invalid environment variable: {e}")
        raise

def build_invoice_payload(template, config):
    """Build payload with correct structure."""
    ref_id = generate_ref_id()
    invoices = []
    for i in range(1, 2):
        invoice = {
            "code": config.code,
            "tax_reduction_config": False,
            "ref_id": f"{ref_id}{i}",
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
        invoices.append(invoice)

    payload = {
        "merchant_id": template["merchant_id"],
        "merchant_code": template["merchant_code"],
        "partner": template["partner"],
        "invoices": invoices
    }
    
    logger.info("Invoice payload built successfully.")
    logger.debug(f"Payload content: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    return payload


def publish_invoice(template, config):
    """Publish invoice."""
    url = ProdConfig.invoice_publish_bath
    headers = {
        'Content-Type': 'application/json',
        'X-API-KEY': config.apikey
    }
    payload = build_invoice_payload(template, config)

    logger.info(f"Sending invoice publish request to {url}")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info("Invoice published successfully.")
        
        response_data = response.json()
        if isinstance(response_data, list):
            invoice_ref_ids = [invoice.get('invoice_ref_id', '') for invoice in response_data]
            set_key(str(env_path), 'REF_ID_BATCH', ','.join(filter(None, invoice_ref_ids)))
        
        return response_data
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err} - Response: {response.text}")
        return {"error": f"HTTP error: {http_err}", "response": response.text}
    except requests.RequestException as e:
        logger.error(f"Failed to publish invoice: {e}")
        return {"error": str(e)}

def save_response_to_env(response, template_key):
    """Save the API response and extract invoice_ref_ids to .env"""
    try:
        set_key(str(env_path), f'{template_key.upper()}_RESPONSE', json.dumps(response, ensure_ascii=False))
        
        if isinstance(response, list):
            invoice_ref_ids = [invoice.get('invoice_ref_id', '') for invoice in response]
            # Save as comma-separated string
            set_key(str(env_path), 'REF_ID_BATCH', ','.join(filter(None, invoice_ref_ids)))
            logger.info(f"Saved {len(invoice_ref_ids)} invoice_ref_ids to REF_ID_BATCH")
        
        logger.info(f"Response saved to {env_path} under key {template_key.upper()}_RESPONSE")
    except Exception as e:
        logger.error(f"Failed to save response to .env: {e}")

if __name__ == "__main__":
    logger.info("Publish invoice batch...")
    try:
        template_1 = load_invoice_template_1()
        response = publish_invoice(template_1, Paramconfig)
        print(f"Invoice publish from batch status: {response}")
        save_response_to_env(response, 'ref_id_batch')
        logger.info("E-invoice publish process completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during the process: {e}")