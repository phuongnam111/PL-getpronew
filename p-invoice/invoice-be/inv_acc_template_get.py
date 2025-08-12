import os
import requests
import random
from dotenv import load_dotenv, set_key
import logging
from config import ProdConfig, Paramconfig
from pathlib import Path

INVOICE_BE_DIR = Path(__file__).parent
env_path = INVOICE_BE_DIR / '.env'
load_dotenv(env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_template():
    partner = os.getenv("PARTNER")
    merchant_id = os.getenv("MERCHANT_ID")
    merchant_code = os.getenv("MERCHANT_CODE")

    if not partner or not merchant_id or not merchant_code:
        print("Error: Missing required environment variables (merchant id,merchant_code,parter).")
        return None, None, None, None

    url = ProdConfig.invoice_gettemplate.format(partner=partner, merchant_id=merchant_id, merchant_code=merchant_code)
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': Paramconfig.apikey
    }
    print("Formatted URL:", url)

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        response_body = response.json()
        print("invoice account info:", response_body)
        return partner, merchant_id, merchant_code, response_body
    else:
        print(f"E-INVOICE TEMPLATE FROM PARTNER: {response.status_code}")
        print("E-INVOICE TEMPLATE FROM PARTNER:", response.text)
        return None, None, None, None

def select_template(response_data):
    templates = response_data.get("data", [])
    
    template_1 = [template for template in templates if template['invoice_serial'].startswith('1C25M')]
    template_2 = [template for template in templates if template['invoice_serial'].startswith('2C25M')]

    template_with_tax = random.choice(template_1) if template_1 else None
    template_without_tax = random.choice(template_2) if template_2 else None

    return template_with_tax, template_without_tax

def save_selected_templates(template_1, template_2):
    env_path = INVOICE_BE_DIR / '.env'
    
    set_key(env_path, 'TEMPLATE_1_INVOICE_TEMPLATE_ID', template_1["invoice_template_id"])
    set_key(env_path, 'TEMPLATE_1_INVOICE_SERIAL', template_1["invoice_serial"])
    set_key(env_path, 'TEMPLATE_1_INVOICE_TEMPLATE_NO', template_1["invoice_template_no"])
    
    set_key(env_path, 'TEMPLATE_2_INVOICE_TEMPLATE_ID', template_2["invoice_template_id"])
    set_key(env_path, 'TEMPLATE_2_INVOICE_SERIAL', template_2["invoice_serial"])
    set_key(env_path, 'TEMPLATE_2_INVOICE_TEMPLATE_NO', template_2["invoice_template_no"])

def save_template_fields(partner, merchant_id, merchant_code, template_1, template_2):
    env_path = INVOICE_BE_DIR / '.env'
    
    set_key(env_path, 'PARTNER', partner)
    set_key(env_path, 'MERCHANT_ID', merchant_id)
    set_key(env_path, 'MERCHANT_CODE', merchant_code)

    set_key(env_path, 'TEMPLATE_1_INVOICE_TEMPLATE_ID', template_1["invoice_template_id"])
    set_key(env_path, 'TEMPLATE_1_INVOICE_SERIAL', template_1["invoice_serial"])
    set_key(env_path, 'TEMPLATE_1_INVOICE_TEMPLATE_NO', template_1["invoice_template_no"])
    
    set_key(env_path, 'TEMPLATE_2_INVOICE_TEMPLATE_ID', template_2["invoice_template_id"])
    set_key(env_path, 'TEMPLATE_2_INVOICE_SERIAL', template_2["invoice_serial"])
    set_key(env_path, 'TEMPLATE_2_INVOICE_TEMPLATE_NO', template_2["invoice_template_no"])

partner, merchant_id, merchant_code, response_data = get_template()

if response_data:
    template_1, template_2 = select_template(response_data)
    if template_1 and template_2:
        save_selected_templates(template_1, template_2)
        save_template_fields(partner, merchant_id, merchant_code, template_1, template_2)
        print(f"Selected template 1: {template_1}")
        print(f"Selected template 2: {template_2}")
        logger.info("Get template success")
    else:
        print("Could not find suitable templates!")