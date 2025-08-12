from config import ProdConfig, UiSelectors,snapshot
from playwright.async_api import async_playwright
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def api_genqr(response):
    """Capture the response from the generate-qr API."""
    if 'generate-qr' in response.url:
        logger.info(f"Intercepted API response for: {response.url}")
        try:
            response_body = await response.json()  # Attempt to read the JSON body
            logger.info(f"APIs GenQR: {response_body}")
        except Exception as e:
            response_body = await response.text()  # Fallback to text if JSON fails
            logger.info(f"APIs GenQR: {response_body}")

async def login_sale_dashboard(page):
    """Logs into the salon sales dashboard."""
    try:
        logger.info("Salon - Banking - Generate QR code: %s", ProdConfig.bookingshop)
        await page.fill(UiSelectors.BTN_SALON_NAME, ProdConfig.bookingshop)
        await page.fill(UiSelectors.XP_USERNAME, ProdConfig.bookingname)
        await page.fill(UiSelectors.XP_PASSWORD, ProdConfig.bookingpass)
        await page.click(UiSelectors.BTN_CASHSHIER_LOG)
        logger.info("Login successful, navigated to the sales screen.")
    except Exception as e:
        logger.error(f"Failed to log in to the sales dashboard: {e}")
        raise

async def generate_qr_code(page):
    """Generates a QR code for a salon sale."""
    try:
        await page.click(UiSelectors.BTN_SALE_SALON)
        await page.fill(UiSelectors.XP_FIND_PRODUCT, ProdConfig.SALON_PRODUCT_NAME)
        await page.locator(UiSelectors.XP_FIND_PRODUCT).press('Enter')
        await page.click(UiSelectors.BTN_SALON_PAY)
        await page.click(UiSelectors.RAD_SALON_BANK_TRANSFER)
        # await page.click(UiSelectors.TXT_DRPDWNBANK)
        # await page.get_by_role("option", name=ProdConfig.kms_bank).click()
        await page.click(UiSelectors.BTN_SALON_SHOWQR)
        await page.click(UiSelectors.BTN_SALON_SHOWQR)
        is_visible = await page.is_visible(UiSelectors.TXT_CONTENTQR)
        if is_visible:
            logger.info("Salon-QR is visible.")
        else:
            logger.warning("QR not found.")
        
        return is_visible
    except Exception as e:
        await snapshot(page, "salon-genqr-error.png")
        logger.error(f"Failed to generate QR code: {e}")
        raise

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
    """Main function to run the script."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            page.on('response', api_genqr)
            await page.goto(ProdConfig.SALON_DOMAIN)
            await login_sale_dashboard(page)
            qr_visible = await generate_qr_code(page)
            if qr_visible:
                qr_verified = await verify_qr(page)
                device_verified = await verify_device(page)
                if qr_verified and device_verified:
                      logger.info("QR generation, verification, and device check successful.")
            else:
                 logger.error("Verification failed: QR code or device link text not visible.")
        except Exception as e:
            logger.error(f"Error during execution: {e}")
        finally:
            await browser.close()
            logger.info("Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())