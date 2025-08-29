import logging
import json
import asyncio
from playwright.async_api import async_playwright
from config import DevConfig, ProdConfig, UiSelectors, snapshot,press_multiple_times
import httpx
import re
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def call_notify_api(payment_req_id):
    """Call the notify API using httpx."""
    url = DevConfig.ICB_NOTIFY_URL
    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "header": {
            "msgId": DevConfig.ICB_MSG_ID,
            "msgType": "1200",
            "channelId": "211701",
            "gatewayId": "G284_KiotViet",
            "providerId": "9203",
            "merchantId": "9203",
            "productId": "900000",
            "version": "1.0",
            "language": "vi",
            "timestamp": DevConfig.ICB_TIMESTAMP,
            "recordNum": "1",
            "clientIp": "1",
            "userName": "***",
            "password": "***",
            "token": "***",
            "signature": DevConfig.ICB_NOTI_SIGNATURE,
        },
        "data": {
            "records": [{
                "transId": DevConfig.ICB_TRAN_ID,
                "recordNo": "1",
                "transTime": "20250108134338",
                "phoneNo": "0985448075",
                "content": f"VietinBank:14/02/2025 10:12|TK:105003852313|GD:+1996,1999VND {payment_req_id}",
                "amount": "1020000",
                "custAcct": "105003852313",
                "recvAcctId": "",
                "preseve1": "CREDIT",
                "preseve2": "8",
            }]
        }
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            http_code = response_data.get("http_code", "unknown")
            logger.info(f"Viettin Bank Paybill API Response [HTTP {http_code}]: {response.text}")
    except httpx.RequestError as e:
        logger.error(f"Error occurred while sending request: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except json.JSONDecodeError:
        logger.warning("Failed to decode the response as JSON.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

async def api_genqr(response):
    """Capture the response from the generate-qr API."""
    if 'generate-qr' in response.url:
        try:
            response_body = await response.json()
            payment_req_id = response_body.get("body", {}).get("payment_req_id")
            if payment_req_id:
                logger.info(f"Extracted payment_req_id: {payment_req_id}")
                await call_notify_api(payment_req_id)
            else:
                logger.error("payment_req_id not found in the response.")
        except Exception as e:
            logger.warning(f"Failed to parse JSON response, fallback to text: {await response.text()}")
            logger.error(f"Error: {e}")

async def login_to_sale_dashboard(page):
    """Logs into the retail dashboard and navigates to the sale screen."""
    try:
        logger.info(f"Logging in as {DevConfig.retailname}...")
        
        # Wait for and fill username
        await page.wait_for_selector(UiSelectors.XP_USERNAME, state="visible", timeout=10000)
        await page.fill(UiSelectors.XP_USERNAME, DevConfig.retailname)
        
        # Wait for and fill password
        await page.wait_for_selector(UiSelectors.XP_PASSWORD, state="visible", timeout=10000)
        await page.fill(UiSelectors.XP_PASSWORD, DevConfig.retailpass)
        
        # Wait for and click login button
        await page.wait_for_selector(UiSelectors.RETAIL_SALE, state="visible", timeout=10000)
        await page.click(UiSelectors.RETAIL_SALE)
        
        logger.info("Login successful, navigating to sale screen.")
        page.on('response', api_genqr)
    except Exception as e:
        logger.error(f"Failed to log in to sale dashboard: {e}")
        await snapshot(page, "notify-ICB-payment-error.png")
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
                logger.warning(f"VIB - Failed to find XP_FAST_SALE on attempt {attempt + 1}: {str(e)}")
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

            # Step 6: Bank Selection (VIETTIN)
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
                        await page.wait_for_selector(f"text={DevConfig.ICB}", state="visible", timeout=2000)
                        break
                    except:
                        if bank_attempt == max_bank_retries - 1:
                            logger.error(f"Failed to select bank after {max_bank_retries} attempts")
                            raise
                        continue

                # Select ICB
                await page.wait_for_selector(f"text={DevConfig.ICB}", state="visible", timeout=5000)
                
                try:
                    await page.get_by_text(DevConfig.ICB).click()
                except:
                    await page.get_by_text(DevConfig.ICB).click(force=True)

                # Verify selection
                try:
                    selected_text = await page.locator("#bankAccounts").inner_text(timeout=3000)
                    if DevConfig.ICB not in selected_text:
                        logger.error("Bank selection verification failed, but continuing")
                except:
                    logger.debug("Bank verification skipped")

            except Exception as bank_error:
                logger.error(f"ICB selection error on attempt {attempt + 1}: {bank_error}")
                if attempt < max_retries - 1:
                    logger.info("Reloading page and retrying...")
                    await page.reload(wait_until="networkidle", timeout=60000)
                    continue
                else:
                    logger.error("Max retries reached for ICB selection")
                    return False

            logger.info("QR code generation process completed successfully")
            return True

        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
            await snapshot(page, f"notify-ICB-payment-error_attempt_{attempt + 1}.png")
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
        await snapshot(page, "notify-ICB-payment-error.png")

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