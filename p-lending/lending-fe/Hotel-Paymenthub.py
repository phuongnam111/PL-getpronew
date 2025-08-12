from config import ProdConfig, UiSelectors,snapshot
from playwright.async_api import async_playwright
import logging
import asyncio

# Configure logging
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
        logger.info("Logging in with username: %s", ProdConfig.hotel_shop)
        await page.fill(UiSelectors.SL_TXT_SHOP, ProdConfig.hotel_shop)
        await page.fill(UiSelectors.SL_TXT_USER, ProdConfig.hotel_name)
        await page.fill(UiSelectors.SL_TXT_PSSWRD, ProdConfig.hotel_pass)
        await page.click(UiSelectors.SL_BTN_MANAGER)
        logger.info("Successfully logged in to the sales dashboard.")
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise

async def payment_screen(page):
    try:
        await dismiss_popup_if_present(page, UiSelectors.XP_BTN_SKIPP)
        #touchpoint
        await page.keyboard.press('Escape')
        await page.locator(UiSelectors.rt_payment_touch).wait_for(state='visible', timeout=ProdConfig.timeout)
        await page.click(UiSelectors.rt_payment_touch)
    except Exception as e:
        logger.error(f"Payment Touch-Point not visible.: {e}")
        await snapshot(page, "hotel-paymenthub-error.png")
        raise

async def verify_payment_hub(page):
    try:
        await asyncio.sleep(5)
        is_visible = await page.is_visible(UiSelectors.rt_pm_title)
        await page.is_visible(UiSelectors.rt_pm_video_intro)
        if is_visible:
            logger.info("Payment-hub screen is enable.")
        else:
            logger.warning("payment-hub screen not found.")
    except Exception as e:
        logger.error(f"Payment-hub screen not visible.: {e}")
        raise

async def get_registers(page):
    """Intercepts and logs the response from the API call to the 'registers' endpoint."""
    async def register_list(response):
        if 'merchants/registers' in response.url:
            logger.info(f"Intercepted API response for: {response.url}")
            try:
                response_body = await response.json()  # Attempt to read the JSON body
                logger.info(f"Register account list: {response_body}")
            except Exception as e:
                response_body = await response.text()  # Fallback to text if JSON fails
                logger.info(f"Register account list: {response_body}")
    
    page.on('response', register_list)

#verify register bank title list
async def verify_bank_register(page, bank_selector, close_selector, register_title_selector):
    try:
        await page.keyboard.press('Escape')
        await page.click(bank_selector)
        await page.is_visible(register_title_selector)
        await page.click(close_selector)
    except Exception as e:
        logger.error(f"Payment-hub register not visible for {bank_selector}: {e}")
        raise

async def verify_all_banks(page):
    """Verify register tittle all bank services."""
    bank_selectors = {
        "VIB": UiSelectors.pmb_vib,
        "BIDV": UiSelectors.pmb_bidv,
        "VCB": UiSelectors.pmb_vcb,
        "MB": UiSelectors.pmb_mb,
    }
    
    for bank_name, bank_selector in bank_selectors.items():
        try:
            await verify_bank_register(page, bank_selector, UiSelectors.pmh_close_register, UiSelectors.pmb_bank_register_title)
            logger.info(f"{bank_name} register verified successfully.")
        except Exception as e:
            logger.error(f"Failed to verify {bank_name} register: {e}")
            await snapshot(page, "hotel-paymenthub-error.png")

async def main():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=["--headless=new",''
            '--disable-gpu','--disable-dev-shm-usage',''
            '--disable-setuid-sandbox','--no-sandbox',''
            '--single-process'])
            page = await browser.new_page()
            await page.goto(ProdConfig.HOTEL_DOMAIN)
            await login_to_dashboard(page)
            await payment_screen(page)
            await get_registers(page)
            await verify_payment_hub(page)
            await verify_all_banks(page)
            logger.info("Payment-Hub is enable.")
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())