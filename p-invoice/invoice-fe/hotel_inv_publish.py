from config import ProdConfig, UiSelectors,snapshot
from playwright.async_api import async_playwright
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def login_sale_dashboard(page):
    """Logs into the hotel sales dashboard."""
    try:
        logger.info("Hotel - invoice - publish invoice: %s", ProdConfig.hotelshop)
        await page.fill(UiSelectors.BTN_SALON_NAME, ProdConfig.hotelshop)
        await page.fill(UiSelectors.XP_USERNAME, ProdConfig.hotelname)
        await page.fill(UiSelectors.XP_PASSWORD, ProdConfig.hotelpass)
        await page.click(UiSelectors.HOTEL_RECEPTION)
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
        #await page.locator(UiSelectors.HOTEL_BILL).wait_for(state='visible', timeout=UiSelectors.timeout)
        await page.click(UiSelectors.HOTEL_BILL)
        await page.fill(UiSelectors.HOTEL_PRODUCT_FILLTER, ProdConfig.SALON_PRODUCT_NAME)
        await asyncio.sleep(3)
        await page.locator(UiSelectors.HOTEL_PRODUCT_FILLTER).press('Enter')
        await page.click(UiSelectors.HOTEL_INVOICE_TEMLIST, force =True)
        if not await page.is_checked(UiSelectors.HOTEL_AUO_PUBLISH):
            await page.click(UiSelectors.HOTEL_AUO_PUBLISH)
            logger.info("Auto publish selected.")
        else:
            logger.info("Auto publish don't need to select")
        await page.click(UiSelectors.HOTEL_INVOICE_TEM, force =True)
        await page.click(UiSelectors.HOTEL_PAYMENT, force =True)
        await page.click(UiSelectors.HOTEL_PAYMENT_DONE)
    except Exception as e:
        logger.error(f"Publish failed: {e}")
        await snapshot(page, "hotel-publish-invoice-error.png")
        return False
    
async def get_publish_infor(page):
    try:
        await page.locator(UiSelectors.HT_PUBLISH_STATUS).wait_for(state='visible', timeout=UiSelectors.timeout)
        logger.info("Publish completed")
        logger.info("Message title: %s", UiSelectors.HOTEL_INVOICE_TEXT)
        await asyncio.sleep(2)
    except Exception as e:
        logger.error(f"Publish failed: {e}")
        return False

async def get_publish_api(page):
    """Intercepts and logs the response from the API call to the 'e-invoice/publishEInvoice' endpoint."""
    
    async def ivnstatus(response):
        if 'api/invoices/booking/v2' in response.url:
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
            await page.goto(ProdConfig.HOTEL_DOMAIN)
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