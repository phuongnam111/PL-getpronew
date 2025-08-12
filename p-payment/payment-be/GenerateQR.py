import requests
import json
from config import ProdConfig, Paramconfig
import logging
from dotenv import set_key, load_dotenv
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_qr_code():
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

    # Log request
    logger.info(f"Sending request to {url}")
    logger.info(f"Request headers: {headers}")
    logger.info(f"Request body: {data}")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raises HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to generate QR Code: {e}")
        return None

    if response.status_code == 200:
        try:
            response_data = response.json()
            logger.info(f"Response data: {response_data}")
            return response_data
        except ValueError:
            logger.error(f"Failed to parse JSON response: {response.text}")
            return None
    else:
        logger.error(f"Failed to generate QR Code with status: {response.status_code}")
        logger.error(f"Response body: {response.text}")
        return None

def gen_qr(response_data):
    env_file = load_dotenv('.env')
    body = response_data.get('body', {})

    # save to. evn
    set_key(env_file, "IMAGE", body.get('image', ''))
    set_key(env_file, "TRANSACTION_ID", str(body.get('transaction_id', '')))
    set_key(env_file, "QR_STRING", body.get('qr_string', ''))
    set_key(env_file, "KOV_CODE", body.get('kov_code', ''))
    set_key(env_file, "PAYMENT_REQ_ID", body.get('payment_req_id', ''))

response_data = generate_qr_code()
    #created .dot evn file 
if response_data: 
    env_path = os.path.join(os.getcwd(), 'payment-be', '.env') 
    load_dotenv(env_path)

    print(f"IMAGE: {os.getenv('IMAGE')}")
    print(f"TRANSACTION_ID: {os.getenv('TRANSACTION_ID')}")
    print(f"QR_STRING: {os.getenv('QR_STRING')}")
    print(f"KOV_CODE: {os.getenv('KOV_CODE')}")
    print(f"PAYMENT_REQ_ID: {os.getenv('PAYMENT_REQ_ID')}")

    logger.info("QR code generated successfully")
else:
    logger.error("Failed to generate QR code")
