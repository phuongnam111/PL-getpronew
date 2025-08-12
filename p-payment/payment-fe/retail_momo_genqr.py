from config import ProdConfig, UiSelectors,snapshot
from playwright.async_api import async_playwright
import logging
import asyncio

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
            logger.info("OBD button not found or clickable, continuing without clicking")
            
        logger.info("Login successful, navigating to sale screen.")
    except Exception as e:
        logger.error(f"Failed to log in to sale dashboard: {e}")
        raise

async def Momo_gen_qr(page):
    try:
        await asyncio.sleep(3)
        await page.fill(UiSelectors.DRP_FIND_PRODUCT, ProdConfig.RETAIL_PRODUCTNAME)
        await page.locator(UiSelectors.DRP_FIND_PRODUCT).press('Enter')
        #await page.click(UiSelectors.XP_PAY_MONEY)
        await page.click(UiSelectors.RAD_WALLET)
        #select wallet account
        await page.click(UiSelectors.WLL_DRPDOWN)
        await page.get_by_role("option", name=ProdConfig.RETAIL_WALLET).click()
        await page.locator(UiSelectors.IMG_QR_CODE).wait_for(state='visible', timeout=UiSelectors.timeout)
        assert await page.is_visible(UiSelectors.IMG_QR_CODE), "Momo QR code is visible" 
        await page.click(UiSelectors.XP_MM_SHOWQR)
        await page.locator(UiSelectors.XP_MM_QR_HEADER).wait_for(state='visible', timeout=UiSelectors.timeout)
        logger.info("Momo QR is visible.")
    except Exception as e:
        logger.error(f"Momo QR not found: {e}")
        await snapshot(page, "retail-Momo-genqr-error.png")
        raise

async def verify_device(page):
    """Verifies if the connect device link text is visible."""
    try:
        linktext_device = await page.is_visible(UiSelectors.CONNECT_DEVICE_MOMO) 
        await page.click(UiSelectors.CONNECT_DEVICE_MOMO)
        await page.locator(UiSelectors.CONNECT_DEVICE_BUTTON).wait_for(state='visible', timeout=UiSelectors.timeout)
        if linktext_device:
            logger.info("Momo Connect link text is visible.")
        else:
            logger.warning("Momo Connect link text not visible.")
        return linktext_device
    except Exception as e:
        logger.error(f"Failed to verify device link text: {e}")
        return False
    
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            page.on('response', api_genqr)
            await page.goto(ProdConfig.RETAIL_DOMAIN)
            await login_to_sale_dashboard(page)
            qr_generated = await Momo_gen_qr(page)
            device_verified = await verify_device(page)
            if qr_generated:
                device_verified = await verify_device(page)
                if verify_device and device_verified:
                    logger.info("Momo QR generation, verification, and device check successful.")
                else:
                    logger.error("Verification failed: QR code or device link text not visible.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

