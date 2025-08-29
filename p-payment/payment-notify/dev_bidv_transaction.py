from config import DevConfig, ProdConfig, UiSelectors, snapshot,press_multiple_times
from playwright.async_api import async_playwright
import logging
import asyncio
import httpx
import json
import hashlib
import uuid
from datetime import datetime
import sys
import re

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# API Configuration
BIDV_API_URL = DevConfig.BIDV_NOTI_URL
SECRET_CODE = DevConfig.BIDV_SECRET_CODE
DEFAULT_TIMEOUT = 30000  # 30 seconds timeout for most operations

async def api_genqr(response):
    """Capture the response from the generate-qr API."""
    if "generate-qr" in response.url:
        try:
            response_body = await response.json()
            logger.info(f"API GenQR Response: {json.dumps(response_body, indent=2)}")

            # Extract payment_req_id
            bill_id = response_body.get("body", {}).get("payment_req_id")
            if bill_id:
                logger.info(f"Extracted bill_id (payment_req_id): {bill_id}")
                await call_bidv_paybill_api(bill_id)
            else:
                logger.error("payment_req_id not found in the response.")
        except Exception as e:
            logger.error(f"Failed to process API response: {e}")
            logger.debug(f"Response content: {await response.text()}")

def generate_checksum(trans_id, bill_id, amount):
    """Generate checksum for the request."""
    checksum_plain = f"{SECRET_CODE}|{trans_id}|{bill_id}|{amount}"
    return hashlib.sha256(checksum_plain.encode("utf-8")).hexdigest()

async def call_bidv_paybill_api(bill_id):
    """Call the BIDV Paybill API using HTTPX."""
    try:
        # Generate dynamic values
        trans_id = str(uuid.uuid4())
        trans_date = datetime.now().strftime("%Y%m%d%H%M%S")
        customer_id = DevConfig.customer_id
        service_id = DevConfig.servcice_id
        amount = DevConfig.BIDV_AMOUNT

        # Prepare request
        payload = {
            "trans_id": trans_id,
            "trans_date": trans_date,
            "customer_id": customer_id,
            "service_id": service_id,
            "bill_id": bill_id,
            "amount": amount,
            "checksum": generate_checksum(trans_id, bill_id, amount)
        }

        logger.debug(f"API Request Payload: {json.dumps(payload, indent=2)}")

        # Make API call with timeout
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                BIDV_API_URL,
                headers={"Content-Type": "application/json"},
                json=payload
            )
            response.raise_for_status()
            
            logger.info(f"API Response [HTTP {response.status_code}]: {response.text}")
            return response.json()

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Failed to call BIDV Paybill API: {str(e)}")
        raise

async def login_to_sale_dashboard(page):
    """Logs into the retail dashboard and navigates to the sale screen."""
    try:
        logger.info(f"Logging in as {DevConfig.retailname}...")
        # Wait for and fill login form
        await page.fill(UiSelectors.XP_USERNAME, DevConfig.retailname)
        await page.fill(UiSelectors.XP_PASSWORD, DevConfig.retailpass)
        async with page.expect_navigation():
            await page.click(UiSelectors.RETAIL_SALE)
        logger.info("Login successful, attaching API listener")
        page.on("response", api_genqr)

    except Exception as e:
        logger.error(f"Login failed: {e}")
        await snapshot(page, "login-error.png")
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
                logger.warning(f"BIDV -Failed to find XP_FAST_SALE on attempt {attempt + 1}: {str(e)}")
                await snapshot(page, f"BIDV fast_sale_error_attempt_{attempt + 1}.png")
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

            # Step 6: Bank Selection (BIDV)
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
                        await page.wait_for_selector(f"text={DevConfig.BIDV}", state="visible", timeout=2000)
                        break
                    except:
                        if bank_attempt == max_bank_retries - 1:
                            logger.warning(f"Failed to select bank after {max_bank_retries} attempts")
                            raise
                        continue

                # Select BIDV bank
                await page.wait_for_selector(f"text={DevConfig.BIDV}", state="visible", timeout=5000)
                
                try:
                    await page.get_by_text(DevConfig.BIDV).click()
                except:
                    await page.get_by_text(DevConfig.BIDV).click(force=True)

                # Verify selection
                try:
                    selected_text = await page.locator("#bankAccounts").inner_text(timeout=3000)
                    if DevConfig.BIDV not in selected_text:
                        logger.warning("Bank selection verification failed, but continuing")
                except:
                    logger.debug("Bank verification skipped")

            except Exception as bank_error:
                logger.error(f"BIDV selection error on attempt {attempt + 1}: {bank_error}")
                await snapshot(page, f"BIDV_selection_error_attempt_{attempt + 1}.png")
                if attempt < max_retries - 1:
                    logger.info("Reloading page and retrying...")
                    await page.reload(wait_until="networkidle", timeout=60000)
                    continue
                else:
                    logger.error("Max retries reached for BIDV selection")
                    return False

            # If we reach this point, all steps succeeded
            logger.info("QR code generation process completed successfully")
            return True

        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
            await snapshot(page, f"notify-BIDV-payment-error_attempt_{attempt + 1}.png")
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
        await page.wait_for_selector(UiSelectors.XP_PAYMENT_SUCESS, state="visible", timeout=15000)
        success_visible = await page.is_visible(UiSelectors.XP_PAYMENT_SUCESS)
        if success_visible:
            logger.info("Payment verify successful.")
        else:
            logger.warning("Payment success element is not visible.")
    except Exception as e:
        logger.error(f"Failed to verify payment success element: {e}")
        await snapshot(page, "notify-BIDV-payment-error.png")

async def verify_payment_success(page):
    """Verify if the payment success element is visible."""
    try:
        await page.wait_for_selector(
            UiSelectors.XP_PAYMENT_SUCESS,
            state="visible",
            timeout=DEFAULT_TIMEOUT
        )
        logger.info("Payment verify successful.")
        return True
    except Exception as e:
        logger.error(f"Payment verification failed: {e}")
        await snapshot(page, "payment-BIDV-verification-error.png")
        return False

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