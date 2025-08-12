import os
import asyncio
from datetime import datetime
import logging

#snapshot function
logger = logging.getLogger(__name__)

async def snapshot(page, filename=None):
    """
    Universal screenshot function for Playwright tests
    
    Args:
        page: Playwright page object
        filename (optional): Custom filename for the screenshot
        
    Returns:
        str: Path to the saved screenshot
    """
    try:
        screenshot_dir = os.getenv('SCREENSHOT_DIR', os.path.join(os.getcwd(), "snapshot"))
        logger.debug(f"Screenshot directory: {screenshot_dir}")
        
        os.makedirs(screenshot_dir, exist_ok=True)
        os.chmod(screenshot_dir, 0o777)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"error_{timestamp}.png"
        
        screenshot_path = os.path.join(screenshot_dir, filename)
        
        try:
            await page.screenshot(path=screenshot_path, full_page=True, timeout=10000)
            logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.warning(f"Retrying screenshot after error: {str(e)}")
            await asyncio.sleep(1)
            await page.screenshot(path=screenshot_path, full_page=True)
            return screenshot_path
            
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {str(e)}")
        raise

  #ui config  
class DevConfig:
    DOMAIN = 'https://lending-dev.kiotfinance.vn/mb-application-form'
    USER = 'admin'
    PASSWORD = '123'
    RETAILER_NAME = 'linhvd1'
    USERNAME = 'admin'
    PASS = '123'

class ProdConfig:
    #DOMAIN
    LANDINGPAGE = 'https://finance.kiotviet.vn'
    TESTZ18 = 'https://testz18.kiotviet.vn/man/#/login'
    RETAIL_DOMAIN ='https://linhinternalcheck.kiotviet.vn/man/#/login'
    TESTZ9 =   'https://testz9.kiotviet.vn/man/#/login'
    testkv2025='https://testkv2025.kiotviet.vn/man/#/login'
    FNB_DOMAIN ='https://fnb.kiotviet.vn/login'
    FORMLIVE ='https://lending.kiotviet.vn/application-form'
    SALON_DOMAIN ='https://salon.kiotviet.vn'
    HOTEL_DOMAIN='https://hotel.kiotviet.vn'
    #ACCOUNT USER
    ##retailshop
    testkv2025account  ='0335133195'
    retailshop  ='testz9'
    retailshop2 ='linhinternalcheck'
    retailshop3 ='testkv2025'
    retailname ='admin'
    retailname2 ='1'
    retailpass ='Kiotviet1234568'
    retailpass2 ='Kiotviet123456'

    #fnbshop
    fnbnshop ='kms'
    fnbnshop2 ='chuyendb2'
    fnbname ='0331234567'
    fnbpass ='248407'
    #bookingshop
    bookingshop ='autokms'
    bookingname ='0999999999'
    bookingpass ='591186'
    timeout=15000
    #hotelshop
    hotel_shop='autokfinance'
    hotel_name='0331234567'
    hotel_pass='999069'

# UI Selectors
class UiSelectors:
    #touchpoint enviroment
    #retail
    XP_SHOP_RT ="//input[@id='RetailerCode']"
    XP_USERNAME = '//input[@id="UserName"]'
    XP_PASSWORD = '//*[@id="Password"]'
    XP_BTNLOGIN = '//*[@id="loginForm"]/section/section[2]/span[1]'
    XP_RETAILNAME = '//*[@id="RetailerCode"]'
    XP_LOGIN_BUTTON = '//*[@id="btnLogin"]/input'
    XP_KFIN_SLIDE = '//*[@class="slick-slider kfin-slider slick-initialized"]'
    XP_VIEW = "//div[@class='kld-bg-white kld-px-4 kld-py-6 kld-rounded-2 kld-text-neutral-500 kld-relative']//div[2]//div[3]//div[2]//a"
    XP_LOAN_PROCESS="//div[@class='kv-main']//div[4]//div[2]//a[1]"
    XP_STORE_HEADER = '//p[@class="text-gray-02 leading font-bold text-xs h-[14px]"]'
    XP_RETAILER_NAME = '//input[@id="RetailerCode"]'
    XP_NEXT_SLIDE = '//*[@class="slick-arrow slick-next"]'
    SHOP_NAME = '//*[@class="css-gg4vpm"]'
    HEADER_STORE = "//span[@class='chakra-avatar css-1hf4mi7']//*[name()='svg']"
    TOUCHPOINT_CONTENT="//*[contains(text(),'Vay vốn ưu đãi dành riêng cho bạn')]"
    #banner size
    XP_KFIN_TOUCH ="//div[@class='kfin-touch-title-icon']"
    RT_XP_SKIPP='//*[@id="k-target-popup"]/div[1]/div[2]/span'
    XP_BANNER_KFIN ="//div[@class='kfin-touch-slider-item']"
    EXPECTED_WIDTH ="312"
    EXPECTED_HEIGHT="458"
    #lannding page
    XP_FINDMORE="//a[contains(text(),'Tìm hiểu thêm')]"
    IMG_KOV_LOGO ="//img[@alt='Phần mềm quản lý bán hàng KiotViet']"
    BTN_LOAN_LANDINGPAGE ="header-register-button"   
    #fnb
    XP_BTN_SKIPP ='//*[@id="k-target-popup"]/div[1]/div[2]/span'
    XP_SHOPNAME_FNB ="//input[@id='Retailer']"
    XP_FNB_LOGIN_BUTTON = '//*[@id="btn-login"]'
    XP_FNB_ACC = "//input[@id='UserName']"
    XP_FNB_PASS ="//input[@id='Password']"
    XP_SKIP_FNB = "//span[@role='presentation' and @class='k-icon k-i-close']"
    XP_LOGGED_POS ="//span[@id='loginNewSale']"
    XP_BTN_TASKBAR ="//i[@class='fa-solid fa-bars']"
    XP_MANAGER ="//span[contains(text(),'Quản lý')]"
    #salon
    SL_CLOSE_POPUP="//*[@class='info-popup-close']"
    SL_TXT_SHOP ="//input[@id='Retailer']"
    SL_TXT_USER ="//input[@id='UserName']"
    SL_TXT_PSSWRD="//input[@id='Password']"
    SL_BTN_MANAGER ="//input[@name='quan-ly']"
    SL_BTN_SALE ="//input[@id='loginNewSale']"
    SL_BTN_TASKBAR="//i[@class='far fa-bars']"
    SL_BTN_ADMIN="//span[contains(text(),'Quản lý')]"
    #landingpage    
    BRP1 = {"H": 1920, "W": 5558}
    BRP2 = {"H": 1600, "W": 5423}
    BRP3 = "1366x5443"
    BRP4 = "1280x5203"
    BRP5 = "768x4626"
    BRP6 = "375x10047"
    XP_REGISTER = "//a[@id='navbar-register-button']"
    XP_REGISTER_LD2 = "//a[@id='header-register-button']"
    XP_REGISTER_LD3 = "//a[@id='process-register-button']"
    XP_REGISTER_LD4 = "//a[@id='social-proof-register-button']"
    XP_BENEFIT = "//a[@id='loi-ich-link']"
    XP_LOANPROCESS = "//a[@id='quy-trinh-vay-link']"
    XP_PARTNER = "//a[@id='doi-tac-link']"
    XP_QA = "//a[@id='cau-hoi-thuong-gap-link']"
    XP_HEADER_TITLE = "//h1[@id='header-title']"
    XP_BENEFIT_TITLE = "//h2[@id='benefit-title']"
    XP_PROCESS_TITLE = "//h2[@id='process-title']"
    XP_PARTNER_TITLE = "//h2[@id='partner-title']"
    XP_QA_TITLE = "//div[@id='cau-hoi-thuong-gap-title']"
    XP_CUST_NEXT = "//button[@id='customer-arrow-right']//*[name()='svg']"
    XP_MENUTASKBAR = "//*[@class='lg:hidden block open-close-button']"
    XP_CUS_TITLE = "//div[@id='customer-title']"
    XP_MOREACCOUNT = "//*[@class='fas fa-arrow-right']"
    XP_SKIPP_BK = "//*[@class='info-popup-close']"

    IMG_CUS_SIZE = {"W": 108, "H": 108}
    IMG_CUSTMR = [
        "(//img)[8]",
        "(//img)[9]",
        "(//img)[10]",
        "(//img)[11]",
        "(//img)[12]"
    ]
    XP_IMG_GIRL = "hero-background-girl"
    FULLIMG_GIRL = {"W": 1032.0, "H": 935.0}
    # FULLIMG_GIRL_H = 556.0  # Commented out in original
    IMG_1920 = {"W": 883.0, "H": 800.0}
    IMG_1600 = {"W": 690.0, "H": 625.0}
    IMG_1366 = {"W": 640.0, "H": 580.0}
    IMG_1280 = {"W": 388.0, "H": 351.0}
    IMG_768 = {"W": 374.0, "H": 351.0}
    IMG_375 = {"W": 374.0, "H": 351.0}

    #paymenthub enviroment
    rt_payment_touch='//*[@id="kfin-payment-touchpoint"]/div/a'
    rt_pm_qrpay="//section[@class='container main_wrapper ng-scope']//div[1]//img[1]"
    rt_pm_title="//div[contains(@class,'kpm-text-headline-s kpm-text-neutral-base')]"
    rt_pm_video_intro="//video[contains(@class,'kpm-w-full kpm-rounded-lg')]"
    #bank register button
    pmb_vib="//button[@data-testid='VIB-register-button']"
    pmb_bidv="//button[@data-testid='BIDV-register-button']"
    pmb_vcb="//button[@data-testid='Vietcombank-register-button']"
    pmb_mb="//button[@data-testid='MB Bank-register-button']"
    pmb_bank_register_title="//div[@class='kpm-text-title-l kpm-text-text-title']"
    pmh_close_register="//div[@class='kpm-cursor-pointer']//*[name()='svg']"
    pmh_vib_confirm_policy="//label[@for='payment-hub-policy-agreement']"
    pmh_vib_confirm=register="(//*[contains(text(),'Xác nhận')])[2]"