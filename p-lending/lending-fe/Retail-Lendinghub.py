import asyncio
from playwright.async_api import async_playwright
from config import ProdConfig, UiSelectors, snapshot
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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

async def login_to_lending_hub(page, username, password):
    """Logs into the retail lending hub."""
    try:
        logger.info("Logging in with username: %s", username)
        await page.fill(UiSelectors.XP_USERNAME, username)
        await page.fill(UiSelectors.XP_PASSWORD, password)
        await page.click(UiSelectors.XP_BTNLOGIN)
        logger.info("Login successful")
    except Exception as e:
        logger.error(f"Failed to log in to lending hub: {e}")
        raise

async def click_kfin_banner(page):
    """Clicks on the KFin touchpoint banner."""
    try:
        await page.wait_for_selector(UiSelectors.XP_KFIN_TOUCH, timeout=ProdConfig.timeout)
        if await page.is_visible(UiSelectors.XP_KFIN_TOUCH):
            await page.click(UiSelectors.XP_KFIN_TOUCH)
            logger.info("Clicked KFin Touchpoint banner")
        else:
            logger.error("KFin banner is not visible")
            raise Exception("KFin banner is not visible")
    except Exception as e:
        logger.error(f"Failed to click KFin banner: {e}")
        raise

async def hover_and_click_kfin_banner(page):
    """Hovers over and clicks the KFin touchpoint banner."""
    try:
        await dismiss_popup_if_present(page, UiSelectors.XP_BTN_SKIPP)
        await page.wait_for_selector(UiSelectors.XP_KFIN_TOUCH)
        await page.hover(UiSelectors.XP_KFIN_TOUCH)
        await click_kfin_banner(page)
        logger.info("Hovered over and clicked KFin touchpoint")
    except Exception as e:
        logger.error(f"Failed to hover and click KFin banner: {e}")
        await snapshot(page, "retail-lendinghub-error.png")
        raise

async def get_loan_packaged(page):
    """Intercepts and logs the response from the API call to the 'loan-products/recommend' endpoint."""
    async def loan_list(response):
        if 'loan-products/recommend' in response.url:
            logger.info(f"Intercepted API response for: {response.url}")
            try:
                response_body = await response.json()
                logger.info(f"Loan Product: {response_body}")
            except Exception as e:
                response_body = await response.text()
                logger.error(f"Failed to parse JSON, fallback to text: {e}")
                logger.info(f"Loan Product: {response_body}")
    
    page.on('response', loan_list)

async def is_lending_form_visible(page):
    """Checks if the lending form is visible."""
    try:
        return await page.is_visible(UiSelectors.TOUCHPOINT_CONTENT)
    except Exception as e:
        logger.error(f"Failed to check lending form visibility: {e}")
        raise

async def open_lending_form(page):
    """Opens the lending form in a new window."""
    try:
        if await is_lending_form_visible(page):
            logger.info("Opening lending form")
            async with page.context.expect_page() as new_page_info:
                await page.click(UiSelectors.XP_LOAN_PROCESS)
            lending_window = await new_page_info.value
            await lending_window.bring_to_front()
            logger.info("Lending form opened successfully")
            return lending_window
        
        logger.warning("Lending form not visible")
        return None
    except Exception as e:
        logger.error(f"Failed to open lending form: {e}")
        await snapshot(page, "retail-lendinghub-error.png")
        raise

async def validate_lending_form(lending_window):
    """Validates the lending form elements."""
    try:
        logger.info("Validating lending form")
        await lending_window.wait_for_selector(UiSelectors.HEADER_STORE)
        assert await lending_window.is_visible(UiSelectors.HEADER_STORE), "Lending Form Store is not visible"
        assert await lending_window.is_visible(UiSelectors.SHOP_NAME), "Lending Form Header is not visible"
        logger.info("Lending form validated successfully")
    except Exception as e:
        logger.error(f"Failed to validate lending form: {e}")
        await snapshot(lending_window, "retail-lendinghub-error.png")
        raise

async def main():
    """Main function to execute the lending hub test flow."""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=["--headless=new",''
            '--disable-gpu','--disable-dev-shm-usage',''
            '--disable-setuid-sandbox','--no-sandbox',''
            '--single-process'])
            #browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            await get_loan_packaged(page)
            await page.goto(ProdConfig.testkv2025)
            await login_to_lending_hub(page, ProdConfig.testkv2025account, ProdConfig.retailpass2)
            await hover_and_click_kfin_banner(page)
            # Lending form operations
            lending_window = await open_lending_form(page)
            if lending_window:
                await validate_lending_form(lending_window)
                logger.info("KFin-TouchPoint from Lending - Hub")
            
            await browser.close()
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        raise
    finally:
        if 'browser' in locals():
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())