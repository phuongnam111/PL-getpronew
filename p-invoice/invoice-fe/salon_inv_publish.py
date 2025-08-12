from config import ProdConfig, UiSelectors,snapshot
from playwright.async_api import async_playwright
import logging
import asyncio
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def login_sale_dashboard(page):
    """Logs into the salon sales dashboard."""
    try:
        logger.info("Salon - invoice - publish from pos: %s", ProdConfig.bookingshop)
        await page.fill(UiSelectors.BTN_SALON_NAME, ProdConfig.bookingshop)
        await page.fill(UiSelectors.XP_USERNAME, ProdConfig.bookingname)
        await page.fill(UiSelectors.XP_PASSWORD, ProdConfig.bookingpass)
        await page.click(UiSelectors.BTN_CASHSHIER_LOG)
        logger.info("Login successful, navigated to the sales screen.")
    except Exception as e:
        logger.error(f"Failed to log in to the sales dashboard: {e}")
        raise

async def publish_invoice(page):
    """Invoice publish from POS with print dialog handling"""
    try:
        await page.add_init_script("""
            window.print = function() {
                console.log('Print dialog suppressed');
                return true;
            };
        """)
        await page.click(UiSelectors.BTN_SALE_SALON)
        await page.fill(UiSelectors.XP_FIND_PRODUCT, ProdConfig.SALON_PRODUCT_NAME)
        await page.locator(UiSelectors.XP_FIND_PRODUCT).press('Enter')
        await page.click(UiSelectors.SL_INVOICE_TEMLIST, force=True)
        await page.click(UiSelectors.SL_AUTO_PUBLISH, force=True)
        await page.click(UiSelectors.BTN_SALON_PAY)
        await page.locator(UiSelectors.SL_INVOICE_PUBLISH).wait_for(state='visible', timeout=UiSelectors.timeout)
        await page.click(UiSelectors.SL_INVOICE_PUBLISH)
    except Exception as e:
        logger.error(f"Publish failed: {e}")
        return False

async def get_publish_infor(page):
    try:
        await page.locator(UiSelectors.SL_PUBLISH_STATUS).wait_for(state='visible', timeout=UiSelectors.timeout)
        logger.info("Publish completed")
        logger.info("Message title: %s", UiSelectors.Salon_INVOICE_TEXT)
    except Exception as e:
        logger.error(f"Publish failed: {e}")
        await snapshot(page, "salon-publish-invoice-error.png")
        return False
    
async def get_publish_api(page):
    """Intercepts and logs the response from the API call to the 'e-invoice/publishEInvoice' endpoint."""
    
    async def ivnstatus(response):
        if 'api/invoices/booking' in response.url:
            logger.info(f"Intercepted API response for: {response.url}")
            try:
                response_body = await response.json()
                logger.info(f"Publish status: {response_body}")
            except Exception as e:
                response_body = await response.text()
                logger.error(f"Failed to parse JSON, fallback to text: {e}")
                logger.info(f"Publish status: {response_body}")
    
    page.on('response', ivnstatus)

async def main():
    """Main function to run the script."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await get_publish_api(page)
        try:
            await page.goto(ProdConfig.SALON_DOMAIN)
            await login_sale_dashboard(page)
            await publish_invoice(page)
            await get_publish_infor(page)
        except Exception as e:
            logger.error(f"Error during execution: {e}")
        finally:
            await browser.close()
            logger.info("Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())
