import logging
import asyncio
from playwright.async_api import async_playwright
from config import DevConfig, ProdConfig, UiSelectors, snapshot,press_multiple_times
import httpx
from datetime import datetime, timezone
import random
import string
import re
import json
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
def generate_random_trans_sequence(length=6):
    """Generate random transaction sequence"""
    return int(''.join(random.choices(string.digits, k=length)))

def generate_msg_id():
    """Generate message ID"""
    return '-'.join([''.join(random.choices(string.digits, k=4)) for _ in range(4)])

def get_current_timestamp():
    """Get current timestamp in ISO format with timezone"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

# API Functions
async def get_encrypted_payload(payment_req_id):
    """Get encrypted payload"""
    url = DevConfig.VCB_ENCRYPT_API_URL
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "postingTime": get_current_timestamp(),
        "postingType": "NOTIFY VCB",
        "tokenString": DevConfig.VCB_TOKEN_STRING,
        "transAmount": DevConfig.VCB_TRANS_AMOUNT,
        "transReferenceNo": payment_req_id,
        "transRemark": DevConfig.VCB_TRANS_REMARK,
        "transSequence": generate_random_trans_sequence(),
        "transTeller": DevConfig.VCB_TRANS_TELLER
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.debug(f"Requesting encrypted payload: {json.dumps(payload, indent=2)}")
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            encrypted_data = response.text.strip('"')
            logger.debug(f"Received encrypted payload: {encrypted_data[:50]}...")
            return encrypted_data
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        logger.error(f"Error getting encrypted payload: {str(e)}")
    return None

async def call_advice_event_posting(encrypted_payload):
    """Call Advice Event Posting API with retry mechanism"""
    url = DevConfig.VCB_ADVICE_EVENT_POSTING_URL
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "header": {
            "appId": "KIOTVIET",
            "isEncrypt": True,
            "msgID": generate_msg_id(),
            "msgName": "AdviceEventPosting",
            "requestTime": get_current_timestamp()
        },
        "payload": encrypted_payload,
        "signature": DevConfig.VCB_SIGNATURE
    }

    max_retries = 2
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.debug(f"Attempt {attempt + 1}: Sending advice event")
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                
                response_data = response.json()
                logger.debug(f"API Response: {json.dumps(response_data, indent=2)}")
                
                # Validate response
                if response_data.get("header", {}).get("resCode") == "0":
                    logger.info("Payment notification successful")
                    return True
                else:
                    error_msg = response_data.get("header", {}).get("resMessage", "Unknown error")
                    logger.error(f"API returned error: {error_msg}")
                    if attempt == max_retries - 1:
                        return False
                    
            await asyncio.sleep(2 ** attempt)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            if attempt == max_retries - 1:
                return False
        except json.JSONDecodeError:
            logger.error("Invalid JSON response")
            if attempt == max_retries - 1:
                return False
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                return False
    return False

# Payment Processing
async def api_genqr(response):
    """Handle QR generation response and process payment"""
    if 'generate-qr' in response.url:
        try:
            response_body = await response.json()
            payment_req_id = response_body.get("body", {}).get("payment_req_id")
            
            if not payment_req_id:
                logger.error("payment_req_id not found in response")
                return
            
            logger.info(f"Extracted payment_req_id: {payment_req_id}")
            
            #Get encrypted payload
            encrypted_payload = await get_encrypted_payload(payment_req_id)
            if not encrypted_payload:
                logger.error("Failed to get encrypted payload")
                return
            
            #call payment notification
            success = await call_advice_event_posting(encrypted_payload)
            if not success:
                logger.error("Payment notification failed after retries")
                return
            #await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Error processing QR response: {str(e)}")

#payment processing from website
async def login_to_sale_dashboard(page):
    """Logs into the retail dashboard and navigates to the sale screen."""
    try:
        logger.info(f"Logging in as {DevConfig.retailname}...")
        await page.fill(UiSelectors.XP_USERNAME, DevConfig.retailname)
        await page.fill(UiSelectors.XP_PASSWORD, DevConfig.retailpass)
        await page.click(UiSelectors.RETAIL_SALE)
        logger.info("Login successful, navigating to sale screen.")
        page.on('response', api_genqr)
    except Exception as e:
        logger.error(f"Failed to log in to sale dashboard: {e}")
        await snapshot(page, "notify-MBB-payment-error.png")
        raise

async def generate_qr_process(page, max_retries=3):
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries} to generate QR code")

            # Step 1: Click on Fast Sale
            try:
                await page.wait_for_selector(UiSelectors.XP_FAST_SALE, state="visible", timeout=10000)
                await page.click(UiSelectors.XP_FAST_SALE)
            except Exception as e:
                logger.warning(f"Failed to find XP_FAST_SALE on attempt {attempt + 1}: {str(e)}")
                await snapshot(page, f"fast_sale_error_attempt_{attempt + 1}.png")
                if attempt < max_retries - 1:
                    logger.info("Reloading page and retrying...")
                    await page.reload(wait_until="networkidle", timeout=60000)
                    continue
                else:
                    logger.error("Max retries reached for XP_FAST_SALE")
                    raise

            # Step 2: Skip intro if present
            try:
                await page.wait_for_selector(UiSelectors.BTN_SKIP_INTRO, state="visible", timeout=10000)
                await page.click(UiSelectors.BTN_SKIP_INTRO, force=True)
            except:
                logger.debug("Skip intro button not found, continuing")

            # Step 3: Fill product name and press Enter
            try:
                await page.wait_for_selector(UiSelectors.DRP_FIND_PRODUCT, state="visible", timeout=10000)
                await page.fill(UiSelectors.DRP_FIND_PRODUCT, ProdConfig.RETAIL_PRODUCTNAME)
                await asyncio.sleep(3)
                await press_multiple_times(page.locator(UiSelectors.DRP_FIND_PRODUCT), 'Enter', 2)
            except Exception as e:
                logger.warning(f"Failed to interact with DRP_FIND_PRODUCT on attempt {attempt + 1}: {str(e)}")
                await snapshot(page, f"find_product_error_attempt_{attempt + 1}.png")
                if attempt < max_retries - 1:
                    logger.info("Reloading page and retrying...")
                    await page.reload(wait_until="networkidle", timeout=60000)
                    continue
                else:
                    logger.error("Max retries reached for find_product")
                    raise

            # Step 4: Click Pay Money
            try:
                await page.wait_for_selector(UiSelectors.XP_PAY_MONEY, state="visible", timeout=10000)
                await page.click(UiSelectors.XP_PAY_MONEY)
            except Exception as e:
                logger.warning(f"Failed to find XP_PAY_MONEY on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info("Reloading page and retrying...")
                    await page.reload(wait_until="networkidle", timeout=60000)
                    continue
                else:
                    logger.error("Max retries reached for choosing payment method")
                    raise

            # Step 5: Click Bank Transfer
            try:
                await page.wait_for_selector(UiSelectors.RAD_BANK_TRANSFER, state="visible", timeout=10000)
                await page.click(UiSelectors.RAD_BANK_TRANSFER)
            except Exception as e:
                logger.warning(f"Failed to find RAD_BANK_TRANSFER on attempt {attempt + 1}: {str(e)}")
                await snapshot(page, f"bank_transfer_error_attempt_{attempt + 1}.png")
                if attempt < max_retries - 1:
                    logger.info("Reloading page and retrying...")
                    await page.reload(wait_until="networkidle", timeout=60000)
                    continue
                else:
                    logger.error("Max retries reached for choosing payment method")
                    raise

            # Step 6: Bank Selection (vietcombank)
            try:
                # Wait for bank accounts dropdown to be enabled
                await page.wait_for_function("""() => {
                    const dropdown = document.querySelector('#bankAccounts');
                    return dropdown && !dropdown.disabled;
                }""", timeout=8000)

                # Retry clicking the dropdown to select the bank
                max_bank_retries = 5
                for bank_attempt in range(max_bank_retries):
                    try:
                        await page.locator("#bankAccounts").get_by_text("select").click(delay=100)
                        await page.wait_for_selector(f"text={DevConfig.VCB}", state="visible", timeout=2000)
                        break
                    except:
                        if bank_attempt == max_bank_retries - 1:
                            logger.warning(f"Failed to select bank after {max_bank_retries} attempts")
                            raise
                        continue

                # Select VIETCOMBANK   
                await page.wait_for_selector(f"text={DevConfig.VCB}", state="visible", timeout=5000)
                
                try:
                    await page.get_by_text(DevConfig.VCB).click()
                except:
                    await page.get_by_text(DevConfig.VCB).click(force=True)

                # Verify selection
                try:
                    selected_text = await page.locator("#bankAccounts").inner_text(timeout=3000)
                    if DevConfig.VCB not in selected_text:
                        logger.warning("Bank selection verification failed, but continuing")
                except:
                    logger.debug("Bank verification skipped")

            except Exception as bank_error:
                logger.error(f"VCB selection error on attempt {attempt + 1}: {bank_error}")
                await snapshot(page, f"VCB_selection_error_attempt_{attempt + 1}.png")
                if attempt < max_retries - 1:
                    logger.info("Reloading page and retrying...")
                    await page.reload(wait_until="networkidle", timeout=60000)
                    continue
                else:
                    logger.error("Max retries reached for VCB selection")
                    return False

            # If we reach this point, all steps succeeded
            logger.info("QR code generation process completed successfully")
            return True

        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
            await snapshot(page, f"notify-VCB-payment-error_attempt_{attempt + 1}.png")
            if attempt < max_retries - 1:
                logger.info("Reloading page and retrying...")
                await page.reload(wait_until="networkidle", timeout=60000)
                continue
            else:
                logger.error("Max retries reached, failing the process")
                return False

    return False

async def verify_payment_success(page):
    """Verify if the payment success element is visible."""
    try:
        await page.wait_for_selector(UiSelectors.XP_PAYMENT_SUCESS, state="visible", timeout=25000)
        success_visible = await page.is_visible(UiSelectors.XP_PAYMENT_SUCESS)
        if success_visible:
            logger.info("Payment verify successful.")
        else:
            logger.warning("Payment success element is not visible.")
    except Exception as e:
        logger.error(f"Failed to verify payment success element: {e}")
        await snapshot(page, "notify-VCB-payment-error.png")

#get api transactions_status
async def transaction_status(response):
    """Capture the response from the transaction_status API."""
    if re.search(r'/transaction-status\?', response.url):
        logger.info(f"Intercepted API response for: {response.url}")
        try:
            response_body = await response.json()  # Attempt to read the JSON body
            logger.info(f"APIs transaction_status: {response_body}")
        except Exception as e:
            response_body = await response.text()  # Fallback to text if JSON fails
            logger.info(f"transaction_status: {response_body}")

async def main():
    """Main function to execute the QR generation and verification process."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            timeout=60000,
            args=[
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-setuid-sandbox',
                '--no-sandbox'
            ]
        )        
        context = await browser.new_context(
            java_script_enabled=True,
        )
        
        page = await context.new_page()
        page.on('response', transaction_status)
        
        try:
            await page.goto(DevConfig.RETAIL_DOMAIN)
            await login_to_sale_dashboard(page)
            success = await generate_qr_process(page)
            await verify_payment_success(page)
            if success and await page.is_visible(UiSelectors.XP_PAYMENT_SUCESS):
                logger.info("Test completed successfully")
                sys.exit(0)
            else:
                logger.error("Test failed: Payment verification unsuccessful")
                sys.exit(1)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            sys.exit(1)
        finally:
            await context.close()
            await browser.close()
            page.remove_listener('response', transaction_status)
            logger.info("Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())