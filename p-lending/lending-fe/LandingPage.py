from config import ProdConfig, UiSelectors, snapshot
from playwright.async_api import async_playwright
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_loan_button_visible(page):
    """Checks if the loan button is visible on the page."""
    try:
        btn_loan_visible = await page.is_visible(UiSelectors.XP_REGISTER)
        if btn_loan_visible:
            logger.info("Loan button is visible")
        else:
            logger.warning("Loan button is not visible")
        return btn_loan_visible
    except Exception as e:
        logger.error(f"Failed to check loan button visibility: {e}")
        raise

async def is_lending_form_visible(page):
    """Checks if the lending form is visible."""
    try:
        return await page.is_visible(UiSelectors.XP_REGISTER)
    except Exception as e:
        logger.error(f"Failed to check lending form visibility: {e}")
        raise

async def open_lending_form(page):
    """Opens the lending form in a new window."""
    try:
        if await is_lending_form_visible(page):
            logger.info("Opening lending form")
            async with page.context.expect_page() as new_page_info:
                await page.click(UiSelectors.XP_REGISTER)
            lending_window = await new_page_info.value
            await lending_window.bring_to_front()
            await page.bring_to_front()
            logger.info("Lending form opened successfully")
            return lending_window
        
        logger.warning("Lending form not visible")
        return None
    except Exception as e:
        logger.error(f"Failed to open lending form: {e}")
        raise

async def validate_lending_form(lending_window):
    """Validates the lending form by filling and checking elements."""
    try:
        logger.info("Validating lending form")
        
        # Fill form fields
        await lending_window.fill(UiSelectors.XP_SHOP_RT, ProdConfig.retailshop3)
        await lending_window.fill(UiSelectors.XP_USERNAME, ProdConfig.testkv2025account)
        await lending_window.fill(UiSelectors.XP_PASSWORD, ProdConfig.retailpass2)
        await lending_window.click(UiSelectors.XP_LOGIN_BUTTON)
        
        # Verify elements
        await lending_window.wait_for_selector(UiSelectors.HEADER_STORE)
        assert await lending_window.is_visible(UiSelectors.HEADER_STORE), "Lending Form Store is not visible"
        assert await lending_window.is_visible(UiSelectors.SHOP_NAME), "Lending Form Header is not visible"
        
        logger.info("Lending form validated successfully")
    except Exception as e:
        logger.error(f"Failed to validate lending form: {e}")
        await snapshot(lending_window, "landingpage-error.png")
        raise

async def verify_backdrop(page, locator, expected_width, expected_height):
    """Verifies the dimensions of a backdrop element."""
    try:
        img_size = await page.locator(locator).bounding_box()
        width = img_size['width']
        height = img_size['height']
        assert width > 0
        assert width == expected_width
        assert height > 0
        assert height == expected_height
    except Exception as e:
        logger.error(f"Failed to verify backdrop dimensions: {e}")
        raise

async def verify_page_content(page):
    """Verifies various sections of the landing page."""
    try:
        await page.click(UiSelectors.XP_BENEFIT)
        await page.wait_for_selector(UiSelectors.XP_BENEFIT_TITLE)
        
        await page.click(UiSelectors.XP_LOANPROCESS)
        await page.wait_for_selector(UiSelectors.XP_PROCESS_TITLE)
        
        await page.click(UiSelectors.XP_PARTNER)
        await page.wait_for_selector(UiSelectors.XP_PARTNER_TITLE)
        
        await page.click(UiSelectors.XP_QA)
        await page.wait_for_selector(UiSelectors.XP_QA_TITLE)
        
        logger.info("Landing Page content verified successfully")
    except Exception as e:
        logger.error(f"Failed to verify page content: {e}")
        raise

async def main():
    """Main function to execute the landing page test flow."""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.goto(ProdConfig.LANDINGPAGE)
            
            # Verify page content sections
            await verify_page_content(page)
            
            # Test lending form functionality
            lending_window = await open_lending_form(page)
            if lending_window:
                await validate_lending_form(lending_window)
                logger.info("Kfin-TouchPoint from Lending - Hub")
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        raise
    finally:
        if 'browser' in locals():
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())