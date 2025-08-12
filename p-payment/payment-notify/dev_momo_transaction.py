# from config import DevConfig, ProdConfig, UiSelectors, snapshot, press_multiple_times
# from playwright.async_api import async_playwright
# import logging
# import asyncio
# import httpx
# import json
# import hashlib
# import uuid
# from datetime import datetime
# import sys
# import re
# import time
# import hmac
# from typing import Optional

# # Configure logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# # API Configuration
# MOMO_API_URL = "https://payment-dev.kiotfinance.vn/payment-gateway/ipn/momo/notify"
# MOMO_ACCESS_KEY = "uPGTYOQEnecosVHC"
# MOMO_SECRET_KEY = "CE9fIKTaF2InO2Gh70Qvm33JnHJ0c1CG"
# DEFAULT_TIMEOUT = 30000

# class MomoPaymentProcessor:
#     def __init__(self):
#         self.payment_req_id = None
#         self.MOMO_API_URL = "https://payment-dev.kiotfinance.vn/payment-gateway/ipn/momo/notify"
#         self.MOMO_ACCESS_KEY = "uPGTYOQEnecosVHC"
#         self.MOMO_SECRET_KEY = "CE9fIKTaF2InO2Gh70Qvm33JnHJ0c1CG"

#     async def api_gen_qr(self, response) -> Optional[str]:
#         """Extract payment_req_id from generate-qr API response and trigger MoMo notification"""
#         if 'generate-qr' in response.url:
#             try:
#                 response_body = await response.json()
#                 logger.debug(f"Raw API response: {json.dumps(response_body, indent=2)}")
                
#                 payment_req_id = response_body.get("body", {}).get("payment_req_id")
                
#                 if payment_req_id:
#                     logger.info(f"Successfully extracted payment_req_id: {payment_req_id}")
#                     self.payment_req_id = payment_req_id
#                     await self.call_notify_api(payment_req_id)
#                     return payment_req_id
#                 else:
#                     logger.error("payment_req_id not found in the response body")
#                     return None
                    
#             except Exception as e:
#                 logger.error(f"Error processing API response: {str(e)}")
#                 return None
#         return None

#     def generate_momo_signature(self, params: dict) -> str:
#         """Generate MoMo signature for the request"""
#         sorted_params = sorted(params.items())
#         message = "&".join([f"{k}={v}" for k, v in sorted_params])
#         return hmac.new(
#             self.MOMO_SECRET_KEY.encode('utf-8'),
#             message.encode('utf-8'),
#             hashlib.sha256
#         ).hexdigest()

#     async def call_notify_api(self, bill_id: str) -> bool:
#         """Call the MoMo notification API"""
#         try:
#             current_time = int(time.time() * 1000)
            
#             params = {
#                 "partnerCode": "MOMOSKSU20240119_TEST",
#                 "orderId": bill_id,
#                 "requestId": str(uuid.uuid4()),
#                 "amount": 5000,
#                 "orderInfo": "Payment for retail product",
#                 "orderType": "momo_wallet",
#                 "transId": current_time,
#                 "resultCode": 0,
#                 "message": "Thành công",
#                 "payType": "qr",
#                 "responseTime": current_time,
#                 "extraData": "",
#                 "accessKey": self.MOMO_ACCESS_KEY
#             }
            
#             params["signature"] = self.generate_momo_signature(params)
#             del params["accessKey"]
            
#             async with httpx.AsyncClient(timeout=30.0) as client:
#                 response = await client.post(
#                     self.MOMO_API_URL,
#                     headers={"Content-Type": "application/json"},
#                     json=params
#                 )
#                 response.raise_for_status()
#                 logger.info(f"MoMo notification successful for bill_id: {bill_id}")
#                 return True
                
#         except Exception as e:
#             logger.error(f"Failed to call MoMo API: {str(e)}")
#             return False

# async def api_gen_qr(self, response) -> Optional[str]:
#     """Extract payment_req_id from generate-qr API response and trigger MoMo notification"""
#     if 'generate-qr' in response.url:
#         try:
#             response_body = await response.json()
#             logger.debug(f"Raw API response: {json.dumps(response_body, indent=2)}")
            
#             # Extract payment_req_id from nested structure
#             payment_req_id = response_body.get("body", {}).get("payment_req_id")
            
#             if payment_req_id:
#                 logger.info(f"Successfully extracted payment_req_id: {payment_req_id}")
#                 self.payment_req_id = payment_req_id  # Store it in the instance
                
#                 # Immediately trigger MoMo notification
#                 await self.call_notify_api(payment_req_id)
#                 return payment_req_id
#             else:
#                 logger.error("payment_req_id not found in the response body")
#                 logger.debug(f"Full response body: {response_body}")
#                 return None
                
#         except json.JSONDecodeError:
#             response_text = await response.text()
#             logger.error(f"Failed to decode JSON response. Raw response: {response_text}")
#             return None
            
#         except Exception as e:
#             logger.error(f"Unexpected error processing API response: {str(e)}")
#             return None
#     return None
# async def login_to_sale_dashboard(page):
#     """Logs into the retail dashboard and navigates to the sale screen."""
#     try:
#         logger.info(f"Logging in as {DevConfig.retailname}...")
#         await page.wait_for_selector(UiSelectors.XP_USERNAME, state="visible", timeout=10000)
#         await page.fill(UiSelectors.XP_USERNAME, DevConfig.retailname)
#         await page.wait_for_selector(UiSelectors.XP_PASSWORD, state="visible", timeout=10000)
#         await page.fill(UiSelectors.XP_PASSWORD, DevConfig.retailpass)
#         await page.wait_for_selector(UiSelectors.RETAIL_SALE, state="visible", timeout=10000)
#         await page.click(UiSelectors.RETAIL_SALE)
#         logger.info("Login successful, navigating to sale screen.")
#     except Exception as e:
#         logger.error(f"Failed to log in to sale dashboard: {e}")
#         await snapshot(page, "notify-momo-payment-error.png")
#         raise

# async def generate_qr_process(page, momo_processor: MomoPaymentProcessor):
#     """Performs actions to generate and display the QR code with optimized retries."""
#     try:
#         max_page_retries = 3
#         payment_req_id = None
        
#         for page_attempt in range(max_page_retries):
#             try:
#                 await page.wait_for_selector(UiSelectors.XP_FAST_SALE, state="visible", timeout=10000)
#                 await page.click(UiSelectors.XP_FAST_SALE)
                
#                 try:
#                     await page.wait_for_selector(UiSelectors.BTN_SKIP_INTRO, state="visible", timeout=10000)
#                     await page.click(UiSelectors.BTN_SKIP_INTRO, force=True)
#                 except:
#                     logger.debug("Skip intro button not found, continuing")
                
#                 await page.wait_for_selector(UiSelectors.DRP_FIND_PRODUCT, state="visible", timeout=10000)
#                 await page.fill(UiSelectors.DRP_FIND_PRODUCT, ProdConfig.RETAIL_PRODUCTNAME)
#                 await asyncio.sleep(3)
#                 await press_multiple_times(page.locator(UiSelectors.DRP_FIND_PRODUCT), 'Enter', 2)
                
#                 await page.wait_for_selector(UiSelectors.RAD_WALLET, state="visible", timeout=10000)
#                 await page.click(UiSelectors.RAD_WALLET)
                
#                 # Wait for QR code to be visible
#                 await page.locator(UiSelectors.IMG_QR_CODE).wait_for(state='visible', timeout=10000)
#                 logger.info("QR code is visible, proceeding with API call.")
                
#                 # Get all captured payment_req_ids from responses
#                 responses = await page.evaluate("""() => {
#                     return window.__playwright_last_response ? 
#                         window.__playwright_last_response.map(r => {
#                             try {
#                                 return r.url.includes('generate-qr') ? JSON.parse(r.body).body.  : null;
#                             } catch {
#                                 return null;
#                             }
#                         }).filter(id => id) : [];
#                 }""")
                
#                 if responses:
#                     payment_req_id = responses[-1]
#                     logger.info(f"Using payment_req_id: {payment_req_id}")
                    
#                     # Call Momo API with payment_req_id
#                     api_result = await momo_processor.call_notify_api(payment_req_id)
#                     if api_result:
#                         logger.info("Momo API called successfully")
#                         return True
#                     else:
#                         logger.error("Failed to call Momo API")
#                 else:
#                     logger.error("No payment_req_id found in responses")
                
#                 return False
            
#             except Exception as e:
#                 logger.warning(f"Page attempt {page_attempt + 1} - Failed to complete process: {e}")
#                 if page_attempt < max_page_retries - 1:
#                     logger.debug(f"Reloading page, attempt {page_attempt + 2}")
#                     await page.reload(wait_until="networkidle", timeout=60000)
#                     await asyncio.sleep(1)
#                 else:
#                     logger.error("Failed to complete process after maximum page retries")
#                     await snapshot(page, "momo_QR_not_found_error.png")
#                     return False
        
#         return False
        
#     except Exception as e:
#         logger.error(f"Failed to generate QR code: {e}")
#         await snapshot(page, "notify-momo-payment-error.png")
#         return False

# async def verify_payment_success(page):
#     """Verify if the payment success element is visible."""
#     try:
#         await page.wait_for_selector(UiSelectors.XP_PAYMENT_SUCESS, state="visible", timeout=10000)
#         success_visible = await page.is_visible(UiSelectors.XP_PAYMENT_SUCESS)
#         if success_visible:
#             logger.info("Payment verification successful.")
#             return True
#         else:
#             logger.warning("Payment success element is not visible.")
#             return False
#     except Exception as e:
#         logger.error(f"Failed to verify payment success element: {e}")
#         await snapshot(page, "notify-momo-payment-error.png")
#         return False

# async def transaction_status(response, momo_processor: MomoPaymentProcessor):
#     """Capture the response from the transaction_status API."""
#     if re.search(r'/transaction-status\?', response.url):
#         logger.info(f"Intercepted API response for: {response.url}")
#         try:
#             response_body = await response.json()
#             logger.info(f"APIs transaction_status: {response_body}")
#         except Exception as e:
#             response_body = await response.text()
#             logger.info(f"transaction_status: {response_body}")

# async def main():
#     """Main function to execute the QR generation and verification process."""
#     momo_processor = MomoPaymentProcessor()
    
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(
#             headless=False,
#             timeout=60000,
#             args=[
#                 '--disable-gpu',
#                 '--disable-dev-shm-usage',
#                 '--disable-setuid-sandbox',
#                 '--no-sandbox'
#             ]
#         )
        
#         # Create a new context with increased timeouts
#         context = await browser.new_context(
#             java_script_enabled=True,
#         )
        
#         page = await context.new_page()
        
#         # Add response listeners with the processor instance
#         page.on('response', lambda response: momo_processor.api_gen_qr(response))
#         page.on('response', lambda response: transaction_status(response, momo_processor))
        
#         try:
#             await page.goto(
#                 DevConfig.RETAIL_DOMAIN,
#                 wait_until="networkidle",
#                 timeout=60000
#             )
            
#             await login_to_sale_dashboard(page)
#             qr_success = await generate_qr_process(page, momo_processor)
#             payment_success = await verify_payment_success(page)
            
#             if qr_success and payment_success:
#                 logger.info("Test completed successfully")
#                 sys.exit(0)
#             else:
#                 logger.error("Test failed")
#                 sys.exit(1)
                
#         except Exception as e:
#             logger.error(f"An error occurred: {e}")
#             sys.exit(1)
#         finally:
#             await context.close()
#             await browser.close()
#             logger.info("Browser closed.")

# if __name__ == "__main__":
#     asyncio.run(main())