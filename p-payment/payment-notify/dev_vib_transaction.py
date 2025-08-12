import logging
import asyncio
from playwright.async_api import async_playwright
from config import DevConfig, ProdConfig, UiSelectors, snapshot,press_multiple_times
import httpx
from datetime import datetime
import random
import string
import re
import sys


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_random_payment_id(length=8):
    """Generate random payment ID"""
    return ''.join(random.choices(string.digits, k=length))

def generate_random_uuid(length=8):
    """Generate random uuid"""
    return ''.join(random.choices(string.digits, k=length))

async def get_vib_signed_data(payment_req_id):
    """Get signed data"""
    url = DevConfig.VIB_SIGN_DATA
    headers = {
        "Content-Type": "application/json"
    }
    # (remove "KOVQR " to get the service_request_id)
    service_request_id = payment_req_id.replace("KOVQR ", "").strip() if payment_req_id else ""

    # Validate the extracted ID is 6 characters
    if len(service_request_id) != 6:
        logger.warning(f"Invalid service_request_id length: {service_request_id}")
        return None, None
    
    # Generate uuid and payment_id
    payment_id = generate_random_payment_id()
    uuid = generate_random_uuid()
    
    payload = {
        "payment_code": "VIB",
        "amount": DevConfig.VIB_PRODUCT_AMOUNT,
        "transaction_time": int(datetime.now().timestamp() * 1000),
        "content": f"{payment_req_id}",
        "service_request_id": service_request_id,
        "payment_id": payment_id,
        "uuid": uuid,
        "partner_code": "VIETQR",
        "payment_account_number": DevConfig.VIB_ACCOUNT_NUMBER,
        "seq_no_source": "TRANHIST"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.debug(f"Get sign data payload: {payload}")
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            signed_data = response.text
            logger.info("Successfully retrieved VIB signed data")
            return signed_data, payload
    except Exception as e:
        logger.error(f"Error getting VIB signed data: {str(e)}")
        logger.error(f"Response content: {e.response.text if hasattr(e, 'response') else 'No response'}")
        return None, None

async def call_vib_transaction_notify(signed_data, payload):
    """VIB transaction-notify API"""
    url = DevConfig.VIB_TRANSACTION_NOTIFY    
    headers = {
        "Authorization": DevConfig.VIB_TOKEN_AUTORIZED,
        "signed-data": signed_data,
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.debug(f"VIB transaction-notify: {payload}")
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"VIB Transaction Notify Response: {response_data}")
            return True
    except httpx.RequestError as e:
        logger.error(f"Request error occurred: {str(e)}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
    return False

async def api_genqr(response):
    """get payment_req_id from response"""
    if 'generate-qr' in response.url:
        try:
            response_body = await response.json()
            payment_req_id = response_body.get("body", {}).get("payment_req_id")
            if payment_req_id:
                logger.info(f"Extracted payment_req_id: {payment_req_id}")
                
                # Get VIB signed data
                signed_data, payload = await get_vib_signed_data(payment_req_id)
                if not signed_data:
                    logger.error("Failed to get VIB signed data, cannot proceed with transaction notify")
                    return
                
                # Call VIB transaction notify API
                await call_vib_transaction_notify(signed_data, payload)
            else:
                logger.error("payment_req_id not found in the response.")
        except Exception as e:
            logger.warning(f"Failed to parse JSON response, fallback to text: {await response.text()}")
            logger.error(f"Error: {str(e)}")

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
        await snapshot(page, "notify-VIB-payment-error.png")
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
                if attempt < max_retries - 1:
                    logger.info("Reloading page and retrying...")
                    await page.reload(wait_until="networkidle", timeout=60000)
                    continue
                else:
                    logger.error("Max retries reached for choosing payment method")
                    raise

            # Step 6: Bank Selection (VIB)
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
                        await page.wait_for_selector(f"text={DevConfig.VIB}", state="visible", timeout=2000)
                        break
                    except:
                        if bank_attempt == max_bank_retries - 1:
                            logger.warning(f"Failed to select bank after {max_bank_retries} attempts")
                            raise
                        continue

                # Select VIB
                await page.wait_for_selector(f"text={DevConfig.VIB}", state="visible", timeout=5000)
                
                try:
                    await page.get_by_text(DevConfig.VIB).click()
                except:
                    await page.get_by_text(DevConfig.VIB).click(force=True)

                # Verify selection
                try:
                    selected_text = await page.locator("#bankAccounts").inner_text(timeout=3000)
                    if DevConfig.VIB not in selected_text:
                        logger.warning("Bank selection verification failed, but continuing")
                except:
                    logger.debug("Bank verification skipped")

            except Exception as bank_error:
                logger.error(f"VIB selection error on attempt {attempt + 1}: {bank_error}")
                if attempt < max_retries - 1:
                    logger.info("Reloading page and retrying...")
                    await page.reload(wait_until="networkidle", timeout=60000)
                    continue
                else:
                    logger.error("Max retries reached for VIB selection")
                    return False
                
            logger.info("QR code generation process completed successfully")
            return True

        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
            await snapshot(page, f"notify-VIB-payment-error_attempt_{attempt + 1}.png")
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
        await snapshot(page, "notify-VIB-payment-error.png")

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