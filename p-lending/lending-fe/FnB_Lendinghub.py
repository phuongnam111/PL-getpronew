from config import ProdConfig, UiSelectors,snapshot
from playwright.async_api import async_playwright
import logging
import asyncio

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def dismiss_popup_if_present(page, selector: str, timeout: int = 25000) -> bool:
    try:
        await page.wait_for_selector(selector, state="visible", timeout=timeout)
        await page.click(selector, force=True)
        logger.info(f"Popup dismissed using selector: {selector}")
        await asyncio.sleep(3)
        return True
    except Exception:
        logger.debug(f"No popup found for selector: {selector}")
        return False

async def login_to_dashboard(page):
    try:
        logger.info("Logging in with username: %s", ProdConfig.fnbnshop)
        await page.fill(UiSelectors.XP_SHOPNAME_FNB, ProdConfig.fnbnshop)
        await page.fill(UiSelectors.XP_FNB_ACC, ProdConfig.fnbname)
        await page.fill(UiSelectors.XP_FNB_PASS, ProdConfig.fnbpass)
        await page.click(UiSelectors.XP_FNB_LOGIN_BUTTON)
        logger.info("Successfully logged in to the sales dashboard.")
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise

async def fnb_touchpoint(page):
    try:
        await dismiss_popup_if_present(page, UiSelectors.XP_BTN_SKIPP)
        await page.locator(UiSelectors.XP_KFIN_TOUCH).wait_for(state='visible', timeout=ProdConfig.timeout)
        await page.click(UiSelectors.XP_KFIN_TOUCH)
        await page.keyboard.press('Escape')
        await page.locator(UiSelectors.TOUCHPOINT_CONTENT).wait_for(state='visible', timeout=ProdConfig.timeout)
        logger.info("FnB Touch Point is visible.")
    except Exception as e:
        logger.error(f"FnB Touch Point not visible.: {e}")
        await snapshot(page, "fnb-lendinghub-error.png")
        raise
    
async def get_loan_packaged(page):
    """Intercepts and logs the response from the API call to the 'loan product' endpoint."""
    async def loan_list(response):
            if 'loan-products/recommend' in response.url:
                logger.info(f"Intercepted API response for: {response.url}")
                try:
                    response_body = await response.json()  # Attempt to read the JSON body
                    logger.info(f"Loan Product: {response_body}")
                except Exception as e:
                    response_body = await response.text()  # Fallback to text if JSON fails
                    logger.error(f"Failed to parse JSON, fallback to text: {e}")
                    logger.info(f"Loan Product: {response_body}")
    
    page.on('response', loan_list)

async def main():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=["--headless=new",''
            '--disable-gpu','--disable-dev-shm-usage',''
            '--disable-setuid-sandbox','--no-sandbox',''
            '--single-process'])
            #browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await get_loan_packaged(page)
            await page.goto(ProdConfig.FNB_DOMAIN)
            await login_to_dashboard(page)
            await fnb_touchpoint(page)
            logger.info("FNB Touch-Point is visible.")
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())