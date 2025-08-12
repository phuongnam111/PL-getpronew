import os
import requests
import json
from dotenv import load_dotenv
from config import ProdConfig, Paramconfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def syns():
    partner = os.getenv('PARTNER')
    merchant_id = os.getenv('MERCHANT_ID')
    merchant_code = os.getenv('MERCHANT_CODE')
    
    try:
        merchant_id = int(merchant_id)
    except ValueError:
        return
    if not partner or not merchant_id or not merchant_code:
        return
    
    url = ProdConfig.invoice_syncFromPartner.format(merchant_id=merchant_id, merchant_code=merchant_code, partner=partner)
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': Paramconfig.apikey
    }
    payload = {
        "merchant_id": merchant_id,
        "merchant_code": merchant_code,
        "partner": partner
    }
    print("Formatted URL:", url)
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        response_body = response.json()
        print("Sync status:", response_body)
        return response_body
    else:
        print(f"Sync status: {response.status_code}")
        print("Sync status:", response.text)
        logging.info("Call partner sync succes")
        return None

syns()
