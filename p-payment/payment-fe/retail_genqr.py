from config import ProdConfig, UiSelectors,snapshot
from playwright.async_api import async_playwright
import logging
import asyncio
import pathlib

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCRIPT_DIR = pathlib.Path(__file__).parent

async def api_genqr(response):
    """Capture the response from the generate-qr API."""
    if 'generate-qr' in response.url:
        logger.info(f"Intercepted API response for: {response.url}")
        try:
            response_body = await response.json()
            logger.info(f"API GenQR Response: {response_body}")
        except Exception as e:
            response_body = await response.text()
            logger.warning(f"Failed to parse JSON response, fallback to text: {response_body}")
            logger.error(f"Error: {e}")

async def login_to_sale_dashboard(page):
    """Logs into the retail dashboard and navigates to the sale screen."""
    try:
        logger.info("Retail - Banking - Generate QR code: %s", ProdConfig.retailname2)
        await page.fill(UiSelectors.XP_USERNAME, ProdConfig.retailname2)
        await page.fill(UiSelectors.XP_PASSWORD, ProdConfig.retailpass)
        await page.click(UiSelectors.RETAIL_SALE)
        await page.click(UiSelectors.BTN_SKIP_INTRO, force=True)
        #verify onboarding if enable
        try:
            await page.click(UiSelectors.RT_SKIP_OBD, force=True, timeout=5000)
            logger.info("Clicked on skip On boarding button")
        except Exception as e:
            logger.info("On boarding button not found or clickable, continuing without clicking")
            
        logger.info("Login successful, navigating to sale screen.")
    except Exception as e:
        logger.error(f"Failed to log in to sale dashboard: {e}")
        raise

async def generate_qr_process(page):
    """Performs actions to generate and display the QR code."""
    try:
        await asyncio.sleep(3)
        await page.fill(UiSelectors.DRP_FIND_PRODUCT, ProdConfig.RETAIL_PRODUCTNAME)
        await page.locator(UiSelectors.DRP_FIND_PRODUCT).press('Enter')
        await page.click(UiSelectors.XP_PAY_MONEY)
        await page.locator(UiSelectors.RAD_BANK_TRANSFER).wait_for(state='visible', timeout=UiSelectors.timeout)
        await page.click(UiSelectors.RAD_BANK_TRANSFER)
        await page.click(UiSelectors.WLL_DRPDOWN)
        await page.get_by_role("option", name=ProdConfig.RETAIL_BANK).click()
        await page.locator(UiSelectors.IMG_QR_CODE).wait_for(state='visible', timeout=UiSelectors.timeout)
        await page.click(UiSelectors.BTN_SHOW_QR)
        qr_visible = await page.is_visible(UiSelectors.TXT_QR_CONTENT, timeout=UiSelectors.timeout)
        if qr_visible:
            logger.info("Retail - VietQR is visible.")
        else:
            logger.warning("Retail - VietQR is not visible.")
        return qr_visible
    except Exception as e:
        logger.error(f"Failed to generate QR code: {e}")
        return False

async def verify_qr(page):
    """Verifies if the QR code is visible."""
    try:
        qr_visible = await page.is_visible(UiSelectors.TXT_QR_CONTENT)
        if qr_visible:
            logger.info("Viet QR is visible.")
        else:
            logger.warning("QR not found.")
        return qr_visible
    except Exception as e:
        logger.error(f"Failed to verify QR code: {e}")
        await snapshot(page, "retail-genqr-error.png")
        return False

async def verify_device(page):
    """Verifies if the connect device link text is visible."""
    try:
        linktext_device = await page.is_visible(UiSelectors.CONNECT_DEVICE_LINK_TEXT)
        if linktext_device:
            await page.click(UiSelectors.CONNECT_DEVICE_LINK_TEXT)
            await page.locator(UiSelectors.CONNECT_DEVICE_BUTTON).wait_for(state='visible', timeout=UiSelectors.timeout)
            logger.info("Connect link text is visible.")
        else:
            logger.warning("Connect link text not visible.")
        return linktext_device
    except Exception as e:
        logger.error(f"Failed to verify device link text: {e}")
        return False

async def main():
    """Main function to execute the QR generation and verification process."""
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        try:
            page.on('response', api_genqr)
            await page.goto(ProdConfig.RETAIL_DOMAIN)
            await login_to_sale_dashboard(page)
            qr_generated = await generate_qr_process(page)
            if qr_generated:
                qr_verified = await verify_qr(page)
                device_verified = await verify_device(page)
                if qr_verified and device_verified:
                    logger.info("QR generation, verification, and device check successful.")
                else:
                    logger.error("Verification failed: QR code or device link text not visible.")
            else:
                logger.error("Failed to generate QR code.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            await browser.close()
            logger.info("Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())