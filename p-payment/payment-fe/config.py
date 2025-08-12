import os
import asyncio
from datetime import datetime
import logging
from functools import wraps

logger = logging.getLogger(__name__)

async def snapshot(page, filename=None):
    """
    Universal screenshot function for Playwright tests
    
    Args:
        page: Playwright page object
        filename (optional): Custom filename for the screenshot
        
    Returns:
        str: Path to the saved screenshot or None if failed
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

class DevConfig:
    RETAIL_DOMAIN = 'https://linhvd1.kvpos.com/man/#/login'
    #ACCOUNT USER
    #retailshop
    retailshop ='linhvd1'
    retailname ='admin'
    retailpass ='Kiotviet123456'
    #value
    ICB="VietinBank - 105003852313Customer Title"
    BIDV="BIDV - 8894711552Nguyễn Thị Thu"
    # UI Selectors
class Dev_UiSelectors:
    XP_PAYMENT_SUCESS ="//img[@alt='kpay qrcode success']"


class ProdConfig:
    #DOMAIN
    landingpage = 'https://finance.kiotviet.vn'
    TESTZ18 = 'https://testz18.kiotviet.vn/man/#/login'
    RETAIL_DOMAIN ='https://linhinternalcheck.kiotviet.vn/man/#/login'
    RETAIL_DOMAIN2 ='https://testz9.kiotviet.vn/man/#/login'
    TESTZ9 =   'https://testz9.kiotviet.vn/man/#/login'
    FNB_DOMAIN ='https://fnb.kiotviet.vn/login'
    FORMLIVE ='https://lending.kiotviet.vn/application-form'
    SALON_DOMAIN ='https://salon.kiotviet.vn'
    HOTEL_DOMAIN='https://hotel.kiotviet.vn'
    
    #ACCOUNT USER
    #retailshop
    retailshop   ='testz9'
    retailname ='admin'
    retailname2 ='1'
    retailpass ='Kiotviet1234568'
    retailpass2 ='Kiotviet123456'
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
    RETAIL_BANK="VIB - 029273641 Phuong Nam"
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
     #invoice retail
    XP_XP = 'open_fc_widget'
    XP_ADMIN = '//*[@class="kv-nav-link hide-mobile"]'
    XP_BTN_CONFIRM_ENV = '//button[@class="btn-confirm btn btn-success"]'
    XP_BTN_SALE = "//a[@class='kv-nav-link']//span[@class='ng-binding'][normalize-space()='Bán hàng']"
    TXT_PRODUCT = 'a'
    DRP_FIND_PRODUCT = "//input[@id='productSearchInput']"
    BTN_CREATE_ENV = '//*[@class="print-eInvoice-wrap"]'
    BTN_ITEM_ENV = '//button[@ng-repeat="item in vm.eInvoice_ListTemplate"][1]'
    BTN_SAVE_TRANSACTION = '//*[@id="saveTransaction"]//..//*[contains(text(),"Thanh toán")]'
    BTN_DONE_ENV_TEM = '//*[@class="btn btn-primary"][text()="Xong"]'
    BTN_VIEW_DETAIL = '//*[@class="btn btn-eInvoice-detail"]'
    TXT_SUCCESS_VT = '//*[contains(text(),"Kết nối thành công với VIETTEL")]'
    TXT_SUCCESS_MS = "//div[@class='toast-message']"
    TXT_SUCCESS_VNPT = '//*[contains(text(),"Kết nối thành công với VNPT")]'
    TXT_UPDATE_DONE = '//*[contains(text(),"Cập nhật cài đặt thành công.")]'
    XP_TXT_INVOICE_TEM  ='/html/body/div[14]/div[2]/kv-e-invoice-setting-template/div/section/div[1]/div/div/span[2]/span/span[1]'
  
    # QR Generation Environment
    #retail
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
    FNB_MM_SHOWQR='//*[@id="k-payment"]/div/div/span[1]/span'
    FNB_MM_QR_CONTENT="//div[@class='kfin-popup-qr-heading']"
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

    #salon genQR
    BTN_CASHSHIER_LOG = '//*[@id="loginNewSale"]'
    BTN_SALON_CUSTOMER_LIST="//i[@class='fas fa-th-large']"
    BTN_TXT_PASS ="//input[@id='userPasswordInp']"
    XP_FIND_PRODUCT="//input[@id='cart-product-search-id']"
    BTN_SALE_SALON ="//span[normalize-space()='Bán hàng']"
    BTN_SALON_CLOSE ="//label[@for='toggleProductListTablet']//i[@class='far fa-times']"
    BTN_SALON_PAY ="//*[contains(text(),' Thanh toán ')]"
    RAD_SALON_BANK_TRANSFER ="//span[contains(text(),'Chuyển khoản')]"
    BTN_SALON_SHOWQR ="span[class='kfin-qr-btn'] span"
    TXT_CONTENTQR="//div[@class='kfin-popup-qr-heading']"
    TXT_DRPDWNBANK="//div[@class='payment-qrcode-option']/kendo-dropdownlist"
    SL_DRPDOWN_BANK='//span[contains(@class, "k-dropdown-wrap")]//span[contains(@class, "k-select")]'
    SL_BANK_LIST="//ul[contains(@class, 'k-list')]"
    #HOTEL_GENQR
    HOTEL_RECEPTION="//input[@id='loginNewSale']"
    HOTEL_BILL="//i[@class='far fa-file-plus icon-btn']"
    HOTEL_PRODUCT_FILLTER="//input[@id='cart-product-search-id']"
    HOTEL_PAYMENT="//*[contains(text(),'Thanh toán')]"
    SL_CLOSE_QR="//span[@class='vodal-close']"

     #digi invoice onboarding
    RETAIL_TRANSACTION_NOTIFY="(//span[contains(text(),'Nhận thông báo giao dịch?')])[1]"
    DIGI_ONBOARD="//h3[contains(text(),'Kích hoạt dịch vụ Digi Invoice')]"
    DIGI_ACTIVE="//h3[contains(text(),'Kích hoạt dịch vụ Digi Invoice')]"
    DIGI_ACTIVE_TITLE="//h3[contains(text(),'Kích hoạt dịch vụ Digi Invoice')]"
    DIGI_ACTIVE_CONFIRM="//*[@class='kfin-btn kfin-btn-primary']"
    #diginvoice fnb onboarding
    FNB_BANK_TYPE="//div[@class='filter-report-new']//li[2]//div[1]//a[1]"
    FNB_BANK_TRANSFER="//i[@id='bank-transfer']"
    #momo enviroment
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
    RT_SKIP_OBD="//div[@class='kf-icon kf-icon--s ']//*[name()='svg']"

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
    #qr momo
    XP_MM_SHOWQR='//*[@id="k-payment"]/div/div/span[1]/span'
    XP_MM_QR_HEADER="//div[@class='kfin-popup-qr-heading']"

    #fnb momo
    #REMOVE
    FNB_CASHBOOK="//body/div[@class='mainWrap']/header[@class='mainHeader clearfix posR ng-scope']/nav[@class='mainNav w100 fll uln off-menu']/section[@class='container']/ul[@class='menu']/li[8]/a[1]"
    fnb_cashbook="//a[@ng-href='/kms/#/CashFlow/']"
    FNB_RAD_WALLET="//div[contains(@class,'filter-report-new')]//li[3]//div[1]//a[1]"
    FNB_DRPDWN_WALL="//span[contains(text(),'--Chọn--')]"
    fnb_momo_account="- MoMo - python"
    FNB_EDIT_WALLET="//a[contains(@class,'editBox btn-icon')]//i[contains(@class,'far fa-pen')]"
    FNB_DEL_BSS_ACC="//button[contains(text(),'Xóa kết nối')]"
    FNB_CFRM_DELETE="//button[@class='kfin-btn kfin-btn-error kfin-btn-ver-2']"
    FBN_WALLET_EDIT="//a[@title='Sửa tài khoản']//i[@class='far fa-pen']"
    FNB_USER_DEL="//a[@class='btn btn-danger ng-binding'][normalize-space()='Xóa']"
    FNB_BTN_CNFRM="//button[contains(text(),'Đồng ý')]"

    #add WALLET
    FNB_ADD_WALLET="//i[@class='far fa-plus-circle']"
    FNB_WALL_NUM="//input[@placeholder='Nhập số ví hoặc số tài khoản ngân hàng']"
    FNB_WALL_NAME="//input[@ng-model='eWallet.Name']"
    FNB_WALL_NOTE="//textarea[@placeholder='Ghi chú']"
    FNB_SAVE_WALLET="//a[@ng-click='saveEwallet()']"
    FNB_BSN_CONNECT="//a[contains(text(),'Kết nối')]"
    FNB_MOMO_TITLE="//div[@class='kfin-gray-01 kfin-headline-2-D']"
    FNB_MOMO_CODE="(//input[@id='input-17'])[1]"
    FNB_MM_PARTNER_CODE="Nhập Partner code"
    FNB_MM_STORE_CODE="Mã cửa hàng MoMo"
    FNB_MOMO_MESSAGE="//div[contains(text(),'Kết nối thành công')]"

    #invoice kvs publish:
    #retail
    misa_template="//button[contains(text(),'Hóa đơn GTGT khởi tạo từ máy tính tiền AH')]"
    vnpt_template="//button[contains(text(),'Hóa đơn bán hàng 2/002_C24MNB')]"
    viettel_template="//button[normalize-space()='C24MVV']"
    #variable
    RT_INV_CONFIG="//a[@id='eInvoiceConfig']"
    RT_INV_AUTO_PUBLISH="//span[@ng-click='vm.toggleAutoPublishEInvoice()']"
    RT_IVN_TEMPLATE="//button[contains(text(),'Hóa đơn GTGT khởi tạo từ máy tính tiền AH')]"
    RT_DONE_TEMPLATE="//a[contains(text(),'Xong')]"
    RT_PUBLISH_INV="//button[@id='saveTransaction']"
    MESSAGE_PUBLISH_DONE="//*[contains(text(),'Hóa đơn được cập nhật thành công')]"
    RT_PUBLISH_VIEW="//span[contains(text(),'Xem chi tiết')]"
    RT_STATUS_VIEW="//span[@class='eInvoice-status eInvoice-status-success']"
    RT_IVN_CONFIRM="div[class='k-widget k-window k-window-poup k-window-alert kv-window kv-close-popup k-state-focused'] button[class='btn-confirm btn btn-success']"
    #fnb
    FNB_TASKBAR="//i[@class='fa-solid fa-bars']"
    FNB_GENERAL_SET="li[class='menu-bar active'] ul li a span span"
    FNB_AUTO_PUBLISH="//div[@class='form-group']//div//div[@class='form-output']//span[@class='toogle active']"
    FNB_TEMPLATE_CHANGE="button[class='btn']"
    FNB_TEMPLATE="C23MLV - 123451/88890357 - C23MLV"
    FNB_BTN_CONFRM="button[class='btn btn-primary']"
    fnb_pay="//*[contains(text(),'Thanh toán (F9)')]"
    FNB_PUBLISH_BILL="//button[@class='btn btn-lg btn-success']"
    FNB_MESSAGE_PUBLISH="//body/div[@class='overlay-container']/div[@id='toast-container']/div[1]"
    FNB_PUBLISH_STATUS="//*[contains(text(),'Giao dịch được cập nhật thành công')]"
    FNB_INVOICE_TEXT="Đã phát hành hóa đơn điện tử"
    #salon
    SL_INVOICE_TEMLIST="//i[@class='far fa-file-invoice']"
    SL_AUTO_PUBLISH="//label[@for='customSwitch1']"
    SL_INVOICE_TEMPLATE="//span[contains(text(),'Hóa đơn GTGT 1/001_K22THP')]"
    SL_INVOICE_PUBLISH="//button[normalize-space()='HOÀN THÀNH']"
    SL_PUBLISH_STATUS="//div[starts-with(@aria-label, 'Thanh toán thành công hóa đơn')]"
    Salon_INVOICE_TEXT="Đã phát hành hóa đơn điện tử"
