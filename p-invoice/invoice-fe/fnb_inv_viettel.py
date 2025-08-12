from config import ProdConfig, UiSelectors,snapshot
from playwright.async_api import async_playwright
import logging
import asyncio

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def dismiss_popup_if_present(page, selector: str, timeout: int = 5000) -> bool:
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

async def login_to_system(page):
    try:
        logger.info("FNB invoice setting template partner = Viettel: %s", ProdConfig.fnbnshop)
        await page.fill(UiSelectors.XP_FNB_ACC, ProdConfig.fnbnshop)
        await page.fill(UiSelectors.XP_USERNAME, ProdConfig.fnbname)
        await page.fill(UiSelectors.XP_PASSWORD, ProdConfig.fnbpass)
        await page.click(UiSelectors.XP_FNB_LOGIN_BUTTON, force=True)
        logger.info("Login successful")
    except Exception as e:
        logger.error(f"Failed to log in: {e}")
        await snapshot(page, "fnb-viettel-login-error.png")

async def navigate_to_einvoice_settings(page):
    try:
        await dismiss_popup_if_present(page, UiSelectors.XP_BTN_SKIPP)
        await page.wait_for_selector(UiSelectors.XP_FNB_SETTING, state="visible", timeout=10000)
        await page.click(UiSelectors.XP_FNB_SETTING)
        logger.info("Clicked on FNB Settings")

        await page.wait_for_selector(UiSelectors.XP_FNB_STORE_SETT, state="visible", timeout=10000)
        await page.click(UiSelectors.XP_FNB_STORE_SETT)
        await dismiss_popup_if_present(page, UiSelectors.XP_BTN_SKIPP)
        logger.info("Clicked on Store Settings successfully")
        await asyncio.sleep(2)

        await page.wait_for_selector(UiSelectors.XP_FNB_INVOICE_CONFIG, state="visible", timeout=10000)
        await page.click(UiSelectors.XP_FNB_INVOICE_CONFIG)
        await dismiss_popup_if_present(page, UiSelectors.XP_BTN_SKIPP)

        await page.wait_for_selector(UiSelectors.XP_FNB_EDIT_CONFIG_INV, state="visible", timeout=10000)
        await page.click(UiSelectors.XP_FNB_EDIT_CONFIG_INV, force=True)

        await page.wait_for_selector(UiSelectors.XP_FNB_INV_PARTNER, state="visible", timeout=10000)
        await page.click(UiSelectors.XP_FNB_INV_PARTNER)

        await page.wait_for_selector(UiSelectors.XP_FNB_INV_LIST_PARTNER, state="visible", timeout=10000)
        await page.click(UiSelectors.XP_FNB_INV_LIST_PARTNER)

        logger.info("Navigated to e-invoice settings")
    except Exception as e:
        logger.error(f"Failed to navigate to e-invoice settings: {e}")
        await snapshot(page, "fnb-viettel-setting-tab-error.png")

async def select_and_save_viettel_template(page):
    try:
        await dismiss_popup_if_present(page, UiSelectors.XP_BTN_SKIPP)
        #CONFIG ACCOUNT INVOICE; PARTNER =viettel
        await page.wait_for_selector(UiSelectors.FNB_PARTNER_VIETTEL, state="visible", timeout=10000)
        await page.click(UiSelectors.FNB_PARTNER_VIETTEL)
        await page.click(UiSelectors.XP_INV_FB_CONTINUE)
        #account fill
        await page.fill(UiSelectors.TXT_TAX_VT, ProdConfig.VT_MST)
        await page.fill(UiSelectors.TXT_ACC_VT, ProdConfig.VT_ACC)
        await page.fill(UiSelectors.TXT_PASS_VT, ProdConfig.VT_PASS)

        if not await page.is_checked(UiSelectors.RAD_PUBLISH_INPOS):
            await page.click(UiSelectors.RAD_PUBLISH_INPOS)
            logger.info("Auto publish selected.")
        else:
            logger.info("Auto publish don't need to select")
        await page.wait_for_selector(UiSelectors.XP_FNB_BTN_CONTINUE)
        await page.click(UiSelectors.XP_FNB_BTN_CONTINUE)
        #SAVE
        await page.click(UiSelectors.XP_FNB_SAVE_TEMPLATE,  timeout=UiSelectors.timeout)
        await page.click(UiSelectors.TXT_UNDERSTAND,  timeout=UiSelectors.timeout)
        await page.wait_for_selector(UiSelectors.XP_TXT_COMPLETESET, timeout=UiSelectors.timeout)
        logger.info("MISA template settings completed")
    except Exception as e:
        logger.error(f"Failed to select and save MISA template: {e}")
        await snapshot(page, "fnb-viettel-select-template-error.png")

async def verify_einvoice_setting_status(page):
    try:
        if await page.is_visible(UiSelectors.XP_TXT_COMPLETESET):
            logger.info("E-Invoice Setting Template Successfully Updated")
            return True
        else:
            logger.error("Failed to update the E-Invoice Setting Template")
            return False
    except Exception as e:
        logger.error(f"Error verifying e-invoice setting status: {e}")
        return False

#VIETTEL PUBLISH INVOICE
async def publish_invoice(page):
    """Invoice publish from POS with print dialog handling."""
    try:
        await page.add_init_script("""
            window.print = function() {
                console.log('Print dialog suppressed');
                return true;
            };
        """)
        await page.click(UiSelectors.XP_FNB_SALE)
        await asyncio.sleep(ProdConfig.time_to_select)
        await page.click(UiSelectors.FNB_TASKBAR)
        await page.click(UiSelectors.FNB_GENERAL_SET)
        await page.click(UiSelectors.FNB_TEMPLATE_CHANGE)
        await page.get_by_role("option", name=ProdConfig.VT_TEMPLATE).click()
        await page.click(UiSelectors.FNB_AUTO_PUBLISH)
        await page.wait_for_selector(
            UiSelectors.FNB_BTN_CONFRRM, 
            state="visible", 
            timeout=10000
        )
        await page.click(UiSelectors.FNB_BTN_CONFRRM)
        
        # Add product to cart
        await page.click(UiSelectors.BTN_SALEMODE)
        await page.click(UiSelectors.BTN_SALEMODE)
        await asyncio.sleep(ProdConfig.time_to_select)
        await page.fill(UiSelectors.DRP_PROD_SEARCH, ProdConfig.FNB_PRODUCTNAME)
        await page.press(UiSelectors.DRP_PROD_SEARCH, 'Enter')
        await page.press(UiSelectors.DRP_PROD_SEARCH, 'Enter')
        await asyncio.sleep(3)
        
        # Publish
        await page.locator(UiSelectors.fnb_pay).wait_for(
            state='visible', 
            timeout=UiSelectors.timeout
        )
        await page.click(UiSelectors.fnb_pay)
        await page.click(UiSelectors.FNB_PUBLISH_BILL)
        logger.info("FnB Publish succeeded.")
    except Exception as e:
        logger.error(f"FNB - Fail to publish invoice: {e}")
        await snapshot(page, "fnb-viettel-publish-error.png")
        raise

async def get_publish_infor(page):
    try:
        await page.locator(UiSelectors.FNB_MESSAGE_PUBLISH).wait_for(state='visible', timeout=UiSelectors.timeout)
        logger.info("Publish completed")
        logger.info("Message title: %s", UiSelectors.FNB_INVOICE_TEXT)
        await asyncio.sleep(3)
    except Exception as e:
        logger.error(f"Publish failed: {e}")
        await snapshot(page, "fnb-viettel-publish-error.png")
        return False

async def get_publish_api(page):
    """Get publish infor"""
    
    async def ivnstatus(response):
        if 'api/invoices/new-fnb' in response.url:
            logger.info(f"Intercepted API response for: {response.url}")
            try:
                response_body = await response.json()
                logger.info(f"Publish status: {response_body}")
            except Exception as e:
                response_body = await response.text()
                logger.error(f"Failed to parse JSON, fallback to text: {e}")
                logger.info(f"Publish status (text): {response_body}")
    
    page.on('response', ivnstatus)

async def main():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=["--headless=new",''
            '--disable-gpu','--disable-dev-shm-usage',''
            '--disable-setuid-sandbox','--no-sandbox',''
            '--single-process'])
            #browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await get_publish_api(page)
            await page.goto(ProdConfig.FNB_DOMAIN)
            await login_to_system(page)
            await navigate_to_einvoice_settings(page)
            await select_and_save_viettel_template(page)
            await verify_einvoice_setting_status(page)
            await publish_invoice(page)
            await get_publish_infor(page)
            logger.info("Process completed")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
    finally:
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
