# import json
# import requests
# import logging
# import os
# from dotenv import load_dotenv, set_key
# from config import ProdConfig, Paramconfig
# from datetime import datetime, timezone, timedelta
# import uuid
# from pathlib import Path

# # Set up paths and load environment variables
# INVOICE_BE_DIR = Path(__file__).parent
# env_path = INVOICE_BE_DIR / '.env'
# load_dotenv(env_path)

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def generate_ref_id():
#     return str(uuid.uuid4())

# def get_current_datetime_iso():
#     now_utc = datetime.now(timezone.utc)
#     desired_timezone = timezone(timedelta(hours=7))
#     now_with_timezone = now_utc.astimezone(desired_timezone)
#     return now_with_timezone.isoformat()

# def load_invoice_template_2():
#     return {
#         "merchant_id": int(os.getenv('MERCHANT_ID')),
#         "merchant_code": os.getenv('MERCHANT_CODE'),
#         "partner": os.getenv('PARTNER'),
#         "invoice_template_id": os.getenv('TEMPLATE_2_INVOICE_TEMPLATE_ID'),
#         "invoice_serial": os.getenv('TEMPLATE_2_INVOICE_SERIAL'), 
#         "invoice_template_no": os.getenv('TEMPLATE_2_INVOICE_TEMPLATE_NO')
#     }

# def invoice_publish_from_pos(template, config):
#     ref_id = generate_ref_id()
#     payload = {
#         "merchant_id": template["merchant_id"],
#         "merchant_code": template["merchant_code"],
#         "partner": template["partner"],
#         "invoice": {
#             "code": config.code,
#             "tax_reduction_config": False,
#             "ref_id": ref_id, 
#             "invoice_serial": template["invoice_serial"], 
#             "invoice_name": config.invoice_name,
#             "invoice_template_id": template["invoice_template_id"],  
#             "invoice_template_no": template["invoice_template_no"],
#             "invoice_datetime": get_current_datetime_iso(),
#             "currency_code": config.currency_code,
#             "exchange_rate": config.exchange_rate,
#             "invoice_note": config.invoice_note,
#             "payment_method_names": config.payment_method_names,
#             "invoice_discount": config.invoice_discount,
#             "invoice_other_receivables": config.invoice_other_receivables,
#             "items": config.items,
#             "buyer": config.buyer
#         }
#     }
#     return payload, ref_id

# def publish_invoice(template, config):
#     url = ProdConfig.invoice_publishfrompos
#     headers = {
#         'Content-Type': 'application/json',
#         'X-API-KEY': config.apikey
#     }
#     payload, ref_id = invoice_publish_from_pos(template, config)
#     response = requests.post(url, headers=headers, json=payload)
#     return response.json(), ref_id

# def save_response_to_env(response, ref_id, template_key):
#     # Save both the full response and the REF_ID_POS2
#     set_key(env_path, f'{template_key.upper()}_RESPONSE', json.dumps(response, ensure_ascii=False))
#     set_key(env_path, 'REF_ID_POS2', ref_id)
#     logger.info(f"Saved REF_ID_POS2: {ref_id} to .env file")

# if __name__ == "__main__":
#     template_2 = load_invoice_template_2()
#     response, ref_id = publish_invoice(template_2, Paramconfig)
#     print(f"Invoice publish from pos status: {response}")
#     logger.info("Invoice publish from POS successful for template_2")
#     save_response_to_env(response, ref_id, 'template_2')
#     print("E-invoice publish success for template_2")
#     print(f"Generated REF_ID_POS2: {ref_id}")