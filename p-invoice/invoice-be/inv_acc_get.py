import requests
from config import ProdConfig, Paramconfig
from inv_acc_create import configure_account
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def GetAccount():
    response_data = configure_account()    
    partner = response_data.get("partner")
    merchant_id = response_data.get("merchant_id")
    merchant_code = response_data.get("merchant_code")
    
    url = ProdConfig.invoice_account.format(partner=partner, merchant_id=merchant_id, merchant_code=merchant_code)
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': Paramconfig.apikey
    }
    print("Formatted URL:", url)

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        response_body = response.json()
        print("Invoice account infor:", response_body)
        logger.info("Get account success")
        return response_body
    else:
        print(f"INVOICE ACCOUNT: {response.status_code}")
        print("INVOICE ACCOUNT:", response.text)
        logger.info("Get account fail")
        return None

GetAccount()
