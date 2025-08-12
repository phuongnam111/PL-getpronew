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
    """Logs into the FNB sale dashboard."""
    try:
        logger.info("FNB - Banking - Generate QR code: %s", ProdConfig.fnbnshop)
        await page.fill(UiSelectors.BTN_SHOPNAME_FNB, ProdConfig.fnbnshop)
        await page.fill(UiSelectors.BTN_USERNAME_FNB, ProdConfig.fnbname)
        await page.fill(UiSelectors.BTN_PASSWRD_FNB, ProdConfig.fnbpass)
        await page.click(UiSelectors.BTN_FNB_POS)
        logger.info("FNB logged into sale screen successfully.")
    except Exception as e:
        logger.error(f"Failed to log in to FNB sale dashboard: {e}")
        raise

async def fill_prod_item(page):
    """Fills in product item details and initiates payment."""
    try:
        #await page.click(UiSelectors.XP_BTN_SKIPP)
        #await page.keyboard.press('Escape')
        await page.click(UiSelectors.BTN_SALEMODE)
        await page.click(UiSelectors.BTN_SALEMODE)
        await asyncio.sleep(ProdConfig.time_to_select)
        await page.fill(UiSelectors.DRP_PROD_SEARCH, ProdConfig.FNB_PRODUCTNAME)
        await page.press(UiSelectors.DRP_PROD_SEARCH, 'Enter')
        await page.press(UiSelectors.DRP_PROD_SEARCH, 'Enter')
        logger.info("Product item filled and payment initiated.")
    except Exception as e:
        logger.error(f"Failed to fill product item: {e}")
        raise

async def generate_qr_code(page):
    """Checks if the FNB QR code is visible."""
    try:
        await page.click(UiSelectors.fnb_pay)
        await page.click(UiSelectors.RAD_FNB_BANKTRANSFER)
        await page.wait_for_selector(UiSelectors.IMG_QR_CODE, state='visible', timeout=UiSelectors.timeout)
        await page.click(UiSelectors.BTN_SHOW_QR)
        qr_visible = await page.is_visible(UiSelectors.TXT_QR_CONTENT, timeout=UiSelectors.timeout)
        if qr_visible:
            logger.info("FNB - VietQR is visible.")
        else:
            logger.warning("FNB - VietQR is not visible.")
        return qr_visible
    except Exception as e:
        logger.error(f"Failed during FNB QR check: {e}")
        await snapshot(page, "fnb-genQR-error.png")
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
    """Main function to run all tasks."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            page.on('response', api_genqr)
            await page.goto(ProdConfig.FNB_DOMAIN)
            await login_sale_dashboard(page)
            await fill_prod_item(page)
            qr_visible = await generate_qr_code(page)
            if qr_visible:
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

if __name__ == "__main__":
    asyncio.run(main())
