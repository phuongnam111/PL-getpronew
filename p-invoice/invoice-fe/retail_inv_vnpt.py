from config import ProdConfig, UiSelectors,snapshot
from playwright.async_api import async_playwright
import logging
import asyncio

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def dismiss_popup_if_present(page, selector: str, timeout: int = 15000) -> bool:
    try:
        await page.wait_for_selector(selector, state="visible", timeout=timeout)
        await page.click(selector, force=True)
        logger.info(f"Popup dismissed using selector: {selector}")
        # Wait briefly to ensure the popup is fully closed
        await asyncio.sleep(0.5)
        return True
    except Exception:
        logger.debug(f"No popup found for selector: {selector}")
        return False

logger = logging.getLogger(__name__)

async def login_to_system(page):
    try:
        logger.info("Retail invoice setting template partner = VNPT: %s", ProdConfig.retailname2)
        await page.fill(UiSelectors.XP_USERNAME, ProdConfig.retailname2)
        await page.fill(UiSelectors.XP_PASSWORD, ProdConfig.retailpass)
        await page.click(UiSelectors.XP_BTNLOGIN, force=True)
        await page.wait_for_selector(UiSelectors.XP_ADMIN)
        logger.info("Login successful, admin selector found")
    except Exception as e:
        logger.error(f"Failed to log in to the system: {e}")
        return False

async def navigate_to_einvoice_settings(page):
    try:
        await dismiss_popup_if_present(page, UiSelectors.XP_BTN_SKIPP)
        await page.click(UiSelectors.XP_ADMIN)
        await page.click(UiSelectors.XP_STORE_SETTING)
        await page.wait_for_selector(UiSelectors.XP_EINVOICE_SETTING)
        await page.click(UiSelectors.XP_EINVOICE_SETTING)
        #scroll to element
        element = page.locator(UiSelectors.XP_INV_EDIT_CONFIG)
        await element.scroll_into_view_if_needed()
        await element.click()
        #change partner
        await page.click(UiSelectors.RT_XP_CHANGE_PARTER)
        await page.click(UiSelectors.XP_FNB_RAD_VNPT)
        await page.click(UiSelectors.RT_XP_CONTINUE_CONFIG)
        logger.info("Navigated to e-invoice settings")
    except Exception as e:
        logger.error(f"Failed to navigate to e-invoice settings: {e}")
        await snapshot(page, "retail-viettel-setting-tab-error.png")
        return False
    
async def select_and_save_vnpt_template(page):
    try:
        checkbox = page.locator(UiSelectors.RT_PUBLISH_AUTO)
        if "ng-empty" in (await checkbox.get_attribute("class") or ""):
            logger.info("Turning on checkbox")
            await page.click(UiSelectors.TXT_RT_PUBLISH_INPOS)

        await page.click(UiSelectors.XP_CONECT_EINV)
        await asyncio.sleep(5)
        #await page.is_visible(UiSelectors.XP_SAVE_EINV)
        await page.click(UiSelectors.XP_SAVE_EINV)
   
    except Exception as e:
        logger.info(f"Primary save failed: {e}")
        try:
            await asyncio.sleep(ProdConfig.time_to_select)
            await page.click(UiSelectors.XP_BTN_SAVE_INV)
        except Exception as e2:
            logger.info(f"Fallback save failed: {e2}")
            await snapshot(page, "retail-viettel-select_tem-error.png")
        return False
    
async def verify_einvoice_setting_status(page):
    try:
        if await page.is_visible(UiSelectors.TXT_SUCCESS_VNPT):
            logger.info("RETAIL - VNPT - E-Invoice Setting Template Successfully Updated")
            return True
        else:
            logger.warning("RETAIL - VNPT Failed to update the E-Invoice Setting Template")
            return False
    except Exception as e:
        logger.error(f"Failed to verify e-invoice setting status: {e}")
        return False
    
# Publish invoice partner = VNPT
async def publish_invoice(page):
    """Invoice publish from POS with print dialog handling"""
    try:
        await page.add_init_script("""
            window.print = function() {
                console.log('Print dialog suppressed');
                return true;
            };
        """)
        logger.info("Navigated to sale dashboard and publish invoice = MISA")
        await page.click(UiSelectors.XP_BTN_SALE)
        await page.click(UiSelectors.BTN_SKIP_INTRO, force=True)
        await asyncio.sleep(3)
        await page.fill(UiSelectors.DRP_FIND_PRODUCT, ProdConfig.RETAIL_PRODUCTNAME)
        await page.locator(UiSelectors.DRP_FIND_PRODUCT).press('Enter')
        await page.click(UiSelectors.RT_INV_CONFIG)
        await page.click(UiSelectors.RT_INV_AUTO_PUBLISH)
        await page.click(UiSelectors.VNPT_RT_TEM_PUBLISH)
        await page.keyboard.press('F9')
        logger.info("Invoice published without print dialog")
        
    except Exception as e:
        logger.error(f"Failed to publish invoice: {e}")
        await snapshot(page, "retail-VNPT-publish-error.png")
        return False

async def get_publish_infor(page):
    try:
        await page.locator(UiSelectors.MESSAGE_PUBLISH_DONE).wait_for(state='visible', timeout=UiSelectors.timeout)
        logger.info("Publish completed")
        logger.info("Message title: %s", UiSelectors.Salon_INVOICE_TEXT)
        await asyncio.sleep(3)
    except Exception as e:
        logger.error(f"Publish information retrieval failed: {e}")
        return False

async def get_publish_api(page):
    """invoice publish response"""
    
    async def ivnstatus(response):
        if 'api-sale1.kiotviet.vn/api/invoices' in response.url:
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
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await get_publish_api(page)
            await page.goto(ProdConfig.RETAIL_DOMAIN)
            await login_to_system(page)
            await navigate_to_einvoice_settings(page)
            await select_and_save_vnpt_template(page)
            await verify_einvoice_setting_status(page)
            await publish_invoice(page)
            await get_publish_infor(page)
            await browser.close()
            logger.info("Completed")
    except Exception as e:
        logger.error(f"An error occurred in the main function: {e}")

if __name__ == "__main__":
    asyncio.run(main())
