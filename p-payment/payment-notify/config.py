import os
import asyncio
from datetime import datetime
import logging
from functools import wraps

logger = logging.getLogger(__name__)

async def snapshot(page, filename=None):
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
        return None

def with_error_snapshot(func):
    """
    Decorator that automatically captures a screenshot when an error occurs in the decorated function.
    """
    @wraps(func)
    async def wrapper(page, *args, **kwargs):
        try:
            return await func(page, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            await snapshot(page, f"error_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            raise
    return wrapper

#press any case
async def press_multiple_times(locator, key, times, delay=2):
    for _ in range(times):
        await locator.press(key)
        if delay > 0:
            await asyncio.sleep(delay)

#config ui
class DevConfig:
    RETAIL_DOMAIN = 'https://linhvd1.kvpos.com/man/#/login'
    #ACCOUNT USER
    #retailshop
    sale_amount='5000'
    retailshop ='linhvd1'
    retailname ='admin'
    retailpass ='Kiotviet123456'
    #value # BIDV NOTI
    ICB="VietinBank - 105003852313Customer Title"
    BIDV="BIDV - 8894711552Nguyễn Thị Thu"
    BIDV_NOTI_URL="https://payment-private-dev.kiotfinance.vn/open-api/ipn/bidv/paybill"
    BIDV_SECRET_CODE="BIDV_KIOTVIET@123"
    customer_id="3365V32"
    BIDV_AMOUNT=50000
    servcice_id="199999"

     #value # ICB NOTI
    ICB_NOTIFY_URL="https://payment-private-dev.kiotfinance.vn/open-api/ipn/vietinbank/notify/sendNotify"
    ICB_NOTI_SIGNATURE="AznkEqs8nfuf/JCMmhVji/xTc4gTIAO/Xs4NLREYxR8ADgCgAZsqvrRXZUJ2CzHR/t0ce+trNcHI2aeRcr1pk2ZwtYBrs2NpFC1WddNjr+axlUEMCgZL65GPR16xzwWz6EYjexop+JI1uMjxaKkAnUKU6AaayH+RX8EXs1NTf0HZkzIV7dXjmg/TgJsOAO7QsFtaPfZlwPycIERqY7GbLjpo2c25UDqV8Yb7hMaL7wxOYyXMUDptKCYmqjmCEsPSqotrMX2NwOuefxXLJk8+JcQc4jSSUrn4Euio1YwH2PS1ut55qZbTF/AU+nLlHPWqpkeKxUbo82MQx5TUAdrRxg=="
    ICB_MSG_ID="dd04b05c-fc61-4a78-99cf-d47b57957c18"
    ICB_TRAN_ID="ICBNOTIFYTESTAUTO"
    ICB_TIMESTAMP="20250108134338"
   
    #value MB NOTI
    MBB="MB - 9341729203828KIOTVIET"
    MB_NOTI_URL="https://payment-private-dev.kiotfinance.vn/open-api/ipn/mbb/api/transaction-sync"
    MB_NOTI_GET_TOKEN="https://payment-private-dev.kiotfinance.vn/open-api/ipn/mbb/api/token_generate"
    MB_AUTORIZED="Basic bWJiYW5rOjRHMzdAUTVPcTUmZg=="
    MB_AMOUNT=50000

    #value VIB NOTI
    VIB_SIGN_DATA="https://dev-kms.citigo.net/tools/sign/VIB"
    VIB_TRANSACTION_NOTIFY="https://payment-private-dev.kiotfinance.vn/payment-integrator/api/v2.0.0/transaction-notify"
    VIB_TOKEN_AUTORIZED="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjM2MDAwMDAwMDAwMDAsImlkIjoiMSIsIm5hbWUiOiJ2aWIiLCJyb2xlIjoidXNlciJ9.X9POpcWhXpFp4nSYlMtORPik7hYRAbVTLzA7jlGp2aE"
    VIB="VIB - 000009KMS"
    VIB_ACCOUNT_NUMBER='000009'
    VIB_PRODUCT_AMOUNT=50000

    #value VCB NOTI
    VCB="vietcombank - 0000000011121123"
    VCB_ENCRYPT_API_URL = "https://dev-kms.citigo.net/tools/aes/ctr/encrypt"
    VCB_ADVICE_EVENT_POSTING_URL = "https://payment-private-dev.kiotfinance.vn/open-api/ipn/vcb/api/v1/PartnerApi/AdviceEventPosting"
    VCB_TOKEN_STRING = "C534BD63CBAA1DFF702E4638436A138F-7319"
    VCB_TRANS_AMOUNT = 50000
    VCB_TRANS_REMARK = "84561"
    VCB_TRANS_TELLER = 10293721
    VCB_SIGNATURE = "signature by automation"

    #value VPB NOTI
    VPB_X_request="123"
    VPB="VPBank - 421371172Nguyen Van Hung Anh"
    VPB_ENCRYPT_API_URL = "https://dev-kms.citigo.net/tools/vp/noti/encrypt"
    VPB_NOTIFY_URL = "https://payment-private-dev.kiotfinance.vn/open-api/ipn/vpb/api/notification"
    VPB_linkId='11000011'
    VPB_amount='60000'
    VPB_transactionId='00019999'
    VPB_transactionDate='2025-02-12 03:03:03'
    VPB_AUTHORIZED="Basic dnBiYW5rOnRBNExnVlE5d2UzOFpiS0RSeE4xWXE2cEM1bVg="

    #value momo- noti
    MOMO='MoMo - 123456'
    MOMO_NOTIFY_URL='https://payment-dev.kiotfinance.vn/payment-gateway/ipn/momo/notify'
    MOMO_PARTNER_CODE="MOMOSKSU20240119_TEST"
    MOMO_REQUEST_ID='711a3e80-b9f4-4ccb-b0fa-6cab9268de69'
    MOMO_TRANS_ID=1747389789970
    MOMO_AMOUNT=5000
    MOMO_ORDER_INFO='AUTOMATION'
    MOMO_ODER_TYPE='momo_wallet'
    MOMO_MESSAGE='Thành công'
    MOMO_PAYMENT_TYPE='qr'
    MOMO_SIGNATURE='5ed6e57a25e6aa86f556ec5c3a468cdda5cb01f3f1ce2f215c68659a2da62b6b'
    MOMO_ACCES_KEY= 'uPGTYOQEnecosVHC'
    MOMO_SECRET_KEY= 'CE9fIKTaF2InO2Gh70Qvm33JnHJ0c1CG'
    

    # UI Selectors
class Dev_UiSelectors:
    XP_PAYMENT_SUCESS ="//img[@alt='kpay qrcode success']"

class ProdConfig:
    #DOMAIN
    landingpage = 'https://finance.kiotviet.vn'
    TESTZ18 = 'https://testz18.kiotviet.vn/man/#/login'
    RETAIL_DOMAIN ='https://linhinternalcheck.kiotviet.vn/man/#/login'
    TESTZ9 = 'https://testz9.kiotviet.vn/man/#/login'
    FNB_DOMAIN ='https://fnb.kiotviet.vn/login'
    FORMLIVE ='https://lending.kiotviet.vn/application-form'
    SALON_DOMAIN ='https://salon.kiotviet.vn'
    HOTEL_DOMAIN='https://hotel.kiotviet.vn'
        
    #ACCOUNT USER
    #retailshop
    retailshop   ='testz9'
    retailname ='admin'
    retailname2 ='1'
    retailpass ='Kiotviet1234567'
    #fnbshop
    #fnbnshop ='testfnbz16a'
    fnbnshop ='kms'
    fnbname ='0331234567'
    fnbpass ='248407'
    fnb_momo_shop ='chuyendb2'
    #fnb momoshop
    fnb_momo_acc='admin'
    fnb_momo_pass='44'
    # fnbname ='admin'
    # fnbpass ='4321'
    #bookingshop
    bookingshop ='autokms'
    bookingname ='0999999999'
    bookingpass ='591186'
    kms_bank="VIB KMS"
    hotelshop='autokfinance'
    hotelname='0331234567'
    hotelpass='999069'
    #invoice account kvs
    #---misa--
    MISA_MST ='0101243150-997'
    MISA_ACC='testlivekiotviet@yopmail.com'
    MISA_PASS='12345678@Abc'
    MISA_TEMPLATE="Hóa đơn GTGT khởi tạo từ máy tính tiền - MTT - 1 - 1C24MBH"
    #---vnpt---
    VNPT_MST ='123456'
    VNPT_ACC='kiotvietadmin'
    VNPT_PASS='123456aA@'
    VNPT_LINK_LOGIN ='https://4200241296-999-tt78democadmin.vnpt-invoice.com.vn'
    VNPT_LINK_SEARCH='https://4200241296-999'
    VNPT_TEMPLATE= "Hóa đơn bán hàng - 2/002 - C24MNB"
    #---viettel---
    VT_MST ='0100109106-509'
    VT_ACC='0100109106-509'
    VT_PASS='2wsxCDE#'
    VT_TEMPLATE="C24MGH - 5/2030 - C24MGH"
    #genqr prod config
    RETAIL_PRODUCTNAME='a'
    ENTER ='Enter'
    RETAIL_WALLET="MoMo - 09020209 KMS"
    #digi invoice onboard

    #GENQR FNB
    FNB_PRODUCTNAME ="a"      
    fnb_bank="VIB 029273641"

    #GEN QR#BOOKING
    SALON_PRODUCT_NAME ='B'
    BANK ='vib'
    BANK_NUM ='123345160'
    BANK_ONER ='ABC'
    timeout =10000
    timeout1 =15
    time_to_select =20
    SALON_BANK=" VIB - 099999 - KMS "
    #momo
    #retail
    MM_PRTNR_CODE='MOMOXRKK20240118'
    MM_BRANCH='cuahang1'
    MM_BANK_NUM="09020209"
    MM_BANK_NAME="KMS"
    MM_NOTE="TEST"
    #fnb momo
    fnb_momo_wall_num="123456"
    fnb_momo_wall_name="python"
    fnb_momo_Wall_note="test"


# UI Selectors
class UiSelectors:
    DRP_FIND_PRODUCT = "//input[@id='productSearchInput']"
    XP_PAYMENT_SUCESS ="//img[@alt='kpay qrcode success']"
    XP_FAST_SALE='//*[@id="PaymentTabId"]/span/span/span'
    XP_BTN_SKIPP ='//*[@id="k-target-popup"]/div[1]/div[2]/div/div[1]/div/div/div[1]/div/div'
    XP_USERNAME = '//input[@id="UserName"]'
    XP_PASSWORD = '//*[@id="Password"]'
    XP_BTNLOGIN = '//*[@id="loginForm"]/section/section[2]/span[1]'
    XP_BTN_SALON_LOGIN = "//*[@class='loginBtn']"
    XP_RETAILNAME = '//*[@id="RetailerCode"]'
    XP_LOGIN_BUTTON = '//*[@id="btnLogin"]/input'
    XP_FNB_LOGIN_BUTTON = '//*[@id="btn-login"]'
    XP_KFIN_BANNER = '//*[@class="kfifn-name"]'
    XP_KFIN_TOUCH_TITLE_ICON = '//div[@class="kfin-touch-title-icon"]'
    XP_KFIN_SLIDE = '//*[@class="slick-slider kfin-slider slick-initialized"]'
    XP_LOAN = '(//a[@class="kfin-touch-btn" and @data-testid="touch-action-button"])'
    XP_STORE_HEADER = '//p[@class="text-gray-02 leading font-bold text-xs h-[14px]"]'
    XP_RETAILER_NAME = '//input[@id="RetailerCode"]'
    XP_FNB_ACC = '//*[@id="Retailer"]'
    XP_BOOKING_ACC = '//*[@id="Retailer"]'
    XP_SKIP_FNB = "(//div[contains(@class, 'k-window-actions')]//span[contains(@class, 'k-i-close')])[2]"
    XP_NEXT_SLIDE = '//*[@class="slick-arrow slick-next"]'
    XP_DI_ADD = '(//button[@class="kfin-touch-btn" and @data-testid="touch-action-button"])[2]'
    XP_CLOSE_DI = '//*[@class="kfin-btn kfin-btn-outline"]'
    XP_HEADER_LDF = '//*[@class="css-gg4vpm"]'
    XP_STORE_LDF = '//*[@class="chakra-avatar css-1hf4mi7"]'
    XP_WALLET = '//span[@class="ng-binding" and contains(text(), "Sổ quỹ")]'
    XP_BANK = '//a[text()="Ngân hàng"]'
    XP_ADD_BANK = '//*[@id="btnLogin"]/input'
    XP_BANK_LIST = '//*[@class="v-icon__svg"]'
    XP_BANK_TYPE = '(//input[@type="text" and @autocomplete="off"])[1]'
    XP_VIB_BANK = '//div[contains(@class, "v-list-item__title") and contains(., "VIB - TMCP Quốc tế Việt Nam")]'
    XP_BANK_NUMBER = '//input[@placeholder="Số tài khoản" and @type="text"]'
    XP_BANK_NAME_OWNER = '//input[@placeholder="Nhập tên chủ tài khoản" and @type="text"]'
    XP_NOTE = '//input[@placeholder="Ghi chú" and @type="text"]'
    XP_SAVE_BANK = '//*[@class="kfin-btn kfin-btn-primary"]'
    XP_CONFIRM = '//button[@class="btn-confirm btn btn-success"]'
    XP_CANCEL = '//*[@class="kfin-btn-cancel"]'
    XP_BTN_FIND_MORE = '//*[@class="kfin-touch-btn-text"]'
    BTN_SALON_NAME = '//*[@id="Retailer"]'

    # Einvoice Environment Selectors  
    # QR Generation Environment
    #retail
    RETAIL_BTN_AMOUNT="//input[@id='payingAmtInvoice']"
    RETAIL_SALE ="//input[@id='loginNewSaleOld']"
    BTN_SKIP_INTRO = '//a[@class="introjs-skipbutton"]'
    BTN_SALE_FAST = "//span[contains(text(),'Bán nhanh')]"
    RAD_BANK_TRANSFER = "//*[@id='bank-transfer']"
    RAD_BANK_MONEY="//span[contains(text(),'Tiền mặt')]"
    FNB_DRPDWN_BANK="(//span[@class='k-icon k-i-arrow-s'])[5]"
    FNB_CLOSE_PAY="//div[@class='cashier-payment']//i[@class='fal fa-times']"
    IMG_QR_CODE = "//img[@alt='kpay qrcode']"
    IMG_QR_URL = '//*[@class="k-pay-checkout-qrcode"]'
    BTN_SHOW_QR = "span[class='kfin-print-qr'] span[class='kfin-qr-btn'] span"
    TXT_QR_CONTENT = '//*[@class="kfin-popup-qr-heading"]'
    POPUP_QR = '//*[@class="kfin-popup-display-qr theme-retail"]'
    BTN_CLOSE_QR = '//*[@id="k-finance-widget-popup"]/div/div[2]/span'
    TXT_INPUT_BANK = '//*[@id="bankAccountDropdown-list"]/span/input'
    BTN_DRPDWN_BANK = '//*[@id="bankAccounts"]/div[2]/span/span/span[2]/span'
    XP_BANK_VALUE = '//*[@id="bankAccountDropdown"]/option[2]'
    XP_PAY_MONEY ="//span[@class='text-check']//span[contains(text(),'Tiền mặt')]"
    XP_ADD_PRODUCT="//a[@class='btn-icon btn-icon-default']//i[@class='far fa-plus']"
    RT_SKIP_DIGI="//*[@class='kfin-btn-cancel']"

    # FNB QR Generation Environment
    BTN_FNB_POS ="//span[@id='loginNewSale']"
    BTN_SHOPNAME_FNB ="//input[@id='Retailer']"
    BTN_USERNAME_FNB="//input[@id='UserName']"
    BTN_PASSWRD_FNB="//input[@id='Password']"
    TXT_UNDERSTAND = "//button[contains(text(),'Đã hiểu')]"
    POPUP_FNB_QR = '//*[@class="kfin-popup-display-qr theme-FnB"]'
    TXT_QR_CONTENT_FNB = '//*[@class="kfin-popup-qr-heading"]'    
    DRP_PROD_SEARCH ="//input[@id='productSearchInput']"
    BTN_SALEMODE="//i[@class='fas fa-bolt-lightning']"
    XP_ITEM_ACTIVE  ="//kv-cashier-cart-item[@class='row-list row-list-active active']"
    BTN_FNB_PAY="//button[@class='btn btn-success']"
    RAD_FNB_BANKTRANSFER ="//span[contains(text(),'Chuyển khoản')]"
    FNB_RAD_QR_MM="//span[normalize-space()='Ví']"
    FNB_MM_SHOWQR="//span[@class='kfin-qr-btn-wallet kfin-qr-btn-border kfin-text-caption-2 kfin-text-neutral-base']"
    FNB_MM_QR_CONTENT="//div[@class='kfin-popup-qr-momo-heading']"
    FNB_BTN_PAY_COUTINUE="//*[contains(text(),' Dừng tính và thanh toán ')]"
    FNB_FIND="Tìm món (F3)"
    FNB_DROPDWN_BANK="(//kv-cashier-qr-code//span)[4]"
    #CONNECT DEVICES    
    CONNECT_DEVICE_LINK_TEXT="//div[@class='kfin-onboarding-mini']"
    CONNECT_DEVICE_MOMO="//div[@class='kfin-onboarding-mini-qr']"
    CONNECT_DEVICE_BUTTON="//button[@class='kfin-btn kfin-btn-primary']"

    #timeconfig
    TIME = 15
    TIMEstamp = 20
    timeout =100000

    #retail
    BTN_SALE ="//a[@class='kv-nav-link']//span[@class='ng-binding'][normalize-space()='Bán hàng']"
    momo_account ="MoMo KMS"
    BTN_CASH_BOOK ="(//span[@class='ng-binding'][contains(text(),'Sổ quỹ')])[1]"
    WALLET_CASH_BOOK="//article[@class='boxLeft uln']//li[3]//div[1]//a[1]"
    WALLET_DROPDOWN_LIST='//*[@id="ddlBankAccount"]/span/span/span[2]'
    WALLET_EDIT="//a[@title='Sửa ví điện tử']//i[@class='far fa-pen']"
    WLL_BTN_DELETE_BSS="//button[contains(text(),'Xóa kết nối')]"
    WLL_BSS_DLT_CNFRM="//button[@class='kfin-btn kfin-btn-error kfin-btn-ver-2']"
    WLL_DELE_BTN="a[class='btn btn-danger ng-binding']"
    WLL_DELE_CNFRM="//button[contains(text(),'Đồng ý')]"
    TXT_MM_DELETE_SCSS="//div[@class='toast-message']"
    WLL_DRPDOWN="//span[@class='k-widget k-dropdown k-header dropdown-control dropdown-control-lg']//span[@class='k-dropdown-wrap k-state-default']"

    RAD_WALLET ="//payment-invoice-component//label[4]//input"
    BTN_ADD_WALLET="button[class='btn btn-icon-no-action btn-add-wallet'] span span"
    TXT_WALLET_BANK ="//input[@placeholder='Nhập số tài khoản']"
    TXT_WALLET_NAME="//input[@placeholder='Nhập tên chủ tài khoản']"
    TXT_WALLET_NOTE="//textarea[@placeholder='Nhập ghi chú']"
    BTN_SAVE_WALLET="a[id='saveWalletBtn'] span span"
    POPUP_ADD_WALLET="//div[@class='kfin-gray-01 kfin-headline-2-D']"
    BTN_CONNECT_WALLET="//button[contains(text(),'Kết nối')]"
    TXT_MOMO_BUSINESS="//div[@class='kfin-text-primary-500 kfin-cursor-pointer kfin-items-center']"
    BTN_CONNECT_MOMO_BUSS="//div[@class='kfin-text-primary-500 kfin-cursor-pointer kfin-items-center']"
    TXT_MOMO_PARTNER_CODE ="//input[@id='input-17']"
    TXT_MOMO_BRANCH="//input[@id='input-22']"
    RAD_MM_CONFRM="//div[@class='kfin-mr-1 kfin-items-center kfin-justify-center kfin-h-6 kfin-w-6']//*[name()='svg']"
    BTN_MM_CONNECT ="//button[contains(text(),'Kết nối')]"
    MESSAGE_MM_BSN="//div[contains(text(),'Kết nối ví điện tử doanh nghiệp thành công')]"
    IMG_MM_QR="img[alt='kpay qrcode']"
    RAD_DOPRDOWN_BTN="//span[@class='k-widget k-dropdown k-header dropdown-control dropdown-control-lg']"
    #qr momo
    XP_MM_SHOWQR="//span[@class='kfin-ml-1']"
    XP_MM_QR_HEADER="//div[@class='kfin-popup-qr-momo-heading']"
