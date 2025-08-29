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

#class ui selector
class DevConfig:
    DOMAIN = 'https://lending-dev.kiotfinance.vn/mb-application-form'
    USER = 'admin'
    PASSWORD = '123'
    RETAILER_NAME = 'linhvd1'
    USERNAME = 'admin'
    PASS = '123'

class ProdConfig:
    #DOMAIN
    landingpage = 'https://finance.kiotviet.vn'
    TESTZ18 = 'https://testz18.kiotviet.vn/man/#/login'
    RETAIL_DOMAIN ='https://linhinternalcheck.kiotviet.vn/man/#/login'
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
    #fnbshop
    fnbnshop ='kms'
    fnbname ='0331234567'
    fnbpass ='248407'
    #bookingshop
    bookingshop ='autokms'
    bookingname ='0999999999'
    bookingpass ='591186'
    #bookingbank
    kms_bank="VIB KMS"
    #hotel
    hotelshop='autokfinance'
    hotelname='0331234567'
    hotelpass='999069'
    #invoice account kvs
    #---misa--
    MISA_MST ='0101243150-997'
    MISA_ACC='testlivekiotviet@yopmail.com'
    MISA_PASS='12345678@Abc'
    MISA_TEMPLATE="Hóa đơn GTGT khởi tạo từ máy tính tiền DN - 1 - 1C25MAA"
    #---vnpt---
    VNPT_MST ='123456'
    VNPT_ACC='kiotvietadmin'
    VNPT_PASS='KiotViet146aA@'
    VNPT_LINK_LOGIN ='https://4200241296-999-tt78democadmin.vnpt-invoice.com.vn'
    VNPT_LINK_SEARCH='https://4200241296-999-tt78democadmin.vnpt-invoice.com.vn'
    VNPT_TEMPLATE= "Hóa đơn GTGT - 1/001 - C25MBN"
    #---viettel---
    VT_MST ='0100109106-509'
    VT_ACC='0100109106-509'
    VT_PASS='2wsxCDE#'
    VT_TEMPLATE="C25MVT - 2/22242 - C25MVT"
    #genqr prod config
    RETAIL_PRODUCTNAME='a'
    ENTER ='Enter'
    #digi invoice onboard

    #GENQR FNB
    FNB_PRODUCTNAME ="a"      
    fnb_momo_product='ích tiểu vương'
    fnb_bank="VIB 0999999"

    #GEN QR#BOOKING
    SALON_PRODUCT_NAME ='B'
    BANK ='vib'
    BANK_NUM ='123345160'
    BANK_ONER ='ABC'
    timeout =10000
    timeout1 =15
    time_to_select =5
    SALON_BANK="1925789458MSB ()'MSB Maritime"
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
    RT_XP_SKIPP='//*[@id="k-target-popup"]/div[1]/div[2]/span'
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
    RT_PUBLISH_AUTO="//span[contains(text(),'Phát hành hóa đơn điện tử ngay trên Màn hình bán h')]"
    XP_XP = 'open_fc_widget'
    XP_ADMIN = "//i[@class='hide-mobile fas fa-cog icon-btn']"
    XP_STORE_SETTING = "//div[@class='kv-setting-items-right']//span[@class='kv-setting-text'][normalize-space()='Hàng hóa']"
    XP_INV_EDIT_CONFIG = "(//a[contains(text(),'Sửa thiết lập')])[1]"
    XP_EINVOICE = '//*[contains(text(),"Kết nối hóa đơn điện tử")]'
    XP_EINVOICE_SETTING = "//ul[@class='kv-sub-setting-list']//li[2]//a[1]"
    XP_RD_VNPT = "//span[@class='kv-form-check-subtext'][normalize-space()='VNPT']"
    XP_RD_MISA = "//span[@class='kv-form-check-subtext'][normalize-space()='MISA']"
    XP_RD_VIETTEL = "//span[@class='kv-form-check-subtext'][normalize-space()='VIETTEL']"
    XP_CONECT_EINV = "//a[@class='kv-btn kv-btn-lg kv-btn-primary']"
    XP_SAVE_EINV="//a[contains(text(),'Lưu')]"
    #new retail ui
    RT_XP_CHANGE_PARTER ="//a[contains(text(),'Đổi nhà cung cấp')]"
    RT_XP_CONTINUE_CONFIG="//a[@class='kv-btn kv-btn-lg kv-btn-primary']"
    XP_BTN_SAVE_INV = '//button[@ng-click="saveEInvoiceSettingTemplate()"]'
    XP_TEMPLATE_ENV = '//*[contains(text(),"Mẫu hóa đơn điện tử")]//..//..//*[@class="k-input ng-scope"]'
    XP_BTN_CONFIRM_ENV = '//button[@class="btn-confirm btn btn-success"]'
    XP_EVN_STATUS = '//*[@id="filterMultiInvoices_wnd_title"]/..//*[contains(text(),"Thông tin đã được lưu!")]'
    XP_BTN_SALE = "//a[@class='kv-nav-link']//span[@class='ng-binding'][normalize-space()='Bán hàng']"
    BTN_SKIP_INTRO = '//a[@class="introjs-skipbutton"]'
    TXT_PRODUCT = 'a'
    DRP_FIND_PRODUCT = "//input[@id='productSearchInput']"
    BTN_CREATE_ENV = '//*[@class="print-eInvoice-wrap"]'
    BTN_ITEM_ENV = '//button[@ng-repeat="item in vm.eInvoice_ListTemplate"][1]'
    BTN_SAVE_TRANSACTION = '//*[@id="saveTransaction"]//..//*[contains(text(),"Thanh toán")]'
    BTN_DONE_ENV_TEM = '//*[@class="btn btn-primary"][text()="Xong"]'
    BTN_VIEW_DETAIL = '//*[@class="btn btn-eInvoice-detail"]'
    TXT_SUCCESS_VT = "//*[contains(text(),'Thiết lập đã được cập nhật thành công')]"
    TXT_SUCCESS_MS = "//div[@aria-label='Thiết lập đã được cập nhật thành công']"
    TXT_SUCCESS_VNPT = "//div[@aria-label='Thiết lập đã được cập nhật thành công']"
    TXT_UPDATE_DONE = '//*[contains(text(),"Cập nhật cài đặt thành công.")]'
    TXT_RT_PUBLISH_INPOS="//label[contains(text(),'Phát hành hóa đơn điện tử ngay trên Màn hình bán h')]"
    
    #invoice FNB
    FNB_PARTNER_MISA="//img[contains(@alt,'misa')]"
    FNB_PARTNER_VNPT="//img[contains(@alt,'vnt')]"
    FNB_PARTNER_VIETTEL="//img[contains(@alt,'viettel')]"
    XP_FNB_SALE="//a[@title='Thu ngân']"
    XP_BTN_SKIPP ='//*[@id="k-target-popup"]/div[1]/div[2]/span'
    XP_FNB_SETTING = "//i[@class='hide-mobile fas fa-cog']"
    XP_FNB_STORE_SETT = "//a[contains(text(),'Thiết lập cửa hàng')]"
    XP_FNB_TRANSACTION = "//span[contains(@class,'k-span ng-binding')][contains(text(),'Giao dịch')]"
    XP_FNB_INVOICE_CONFIG= "li[id='tab-electronic-invoice'] span[class='k-span ng-binding']"
    XP_FNB_EDIT_CONFIG_INV="//button[contains(text(),'Sửa thiết lập')]"
    XP_FNB_INV_PARTNER="//a[contains(text(),'Đổi nhà cung cấp')]"
    XP_INV_FB_CONTINUE="//button[contains(text(),'Tiếp tục')]"
    XP_FNB_INV_LIST_PARTNER="//div[@class='select-publisher-other']//a[1]"
    XP_FNB_INVOICE_SETTING = "(//a[@class='btn btn-default ng-binding ng-scope'][contains(text(),'Chi tiết')])[5]"
    XP_FNB_RAD_MS = "//label[normalize-space()='MISA']"
    XP_FNB_RAD_VT = "//label[normalize-space()='VIETTEL']"
    XP_FNB_RAD_VNPT = "//label[normalize-space()='VNPT']"
    XP_FNB_BTN_CONTINUE = "//button[@class='btn btn-primary ng-binding'][contains(text(),'Kết nối')]"
    XP_FNB_SAVE_TEMPLATE="//button[contains(text(),'Lưu')]"
    XP_FNB_DRPDWN_TEM="//span[@class='k-widget k-dropdown k-header ng-scope']//span[@class='k-input ng-scope']"
    XP_FNB_SAVE_TEM="a[ng-click='saveTemplate(EInvoiceSetting)']"
    XP_SAVEINVOICE = "//a[@class='btn btn-success' and @ng-click='saveTemplate(EInvoiceSetting)']"
    XP_TXT_COMPLETESET = "//div[@class='toast toast-success']"
    #XP_DRPDWN_TEMPLATE="//span[@class='k-dropdown-wrap k-state-default k-state-focused']//span[@class='k-icon k-i-arrow-s'][normalize-space()='select']"
    XP_DRPDWN_TEMLIST = "(//span[@class='k-icon k-i-arrow-s'][normalize-space()='select'])[7]"
    XP_SAVE_INV_FNB = "//a[contains(@ng-click,'saveTemplate(EInvoiceSetting)')]"
    XP_TXT_DONE_INV = "(//a[contains(text(),'Đã hiểu')])[1]"
    TXT_VALUE_INV ="//span[contains(text(),'Hóa đơn GTGT khởi tạo từ MTT xăng dầu - 1 - 1C24MA')]"
    RAD_PUBLISH_INPOS ="//span[contains(text(),'Phát hành hoá đơn điện tử ngay trên Màn hình bán h')]"
    RAD_SENT_NOTE ="//span[contains(text(),'Cho phép gửi Ghi chú món sang HĐĐT.')]"
    FNB_BTN_CONFRRM="//button[contains(text(),'Lưu')]"
    #account invoice misa:
    TXT_TAX_MISA ="//input[contains(@ng-model,'EInvoiceSetting.TaxCode')]"
    TXT_ACC_MISA ="//input[@ng-model='EInvoiceSetting.UserName']"
    TXT_PASS_MISA="//input[contains(@ng-model,'EInvoiceSetting.Password')]"
    
    TXT_TAX_VT ="//input[contains(@ng-model,'EInvoiceSetting.TaxCode')]"
    TXT_ACC_VT ="//input[@ng-model='EInvoiceSetting.UserName']"
    TXT_PASS_VT="//input[contains(@ng-model,'EInvoiceSetting.Password')]"

    #VNPT
    TXT_LINKLOGIN_VNPT ="//input[@ng-model='EInvoiceSetting.LoginUrl']"
    TXT_LINKSEARCH_VNPT="//input[@ng-model='EInvoiceSetting.EinvoiceUrlSearch']"
    TXT_TAX_VNPT="//input[contains(@ng-model,'EInvoiceSetting.TaxCode')]"
    TXT_ACC_VNPT="//input[contains(@ng-model,'EInvoiceSetting.UserName')]"
    TXT_PASS_VNPT="//input[contains(@ng-model,'EInvoiceSetting.Password')]"
    
    #invoice salon
    SALON_SETTING = "//i[@class='hide-mobile far fa-cog nav-icon-setting']"
    SALON_STORE_SETT = "//a[contains(text(),'Thiết lập cửa hàng')]"
    SALON_TRANSACTION = "//span[@class='k-span ng-binding'][contains(text(),'Giao dịch')]"
    SALON_INVOICE_SETTING = "//a[@id='EnableEInvoice']"
    SALON_RAD_MS = "//label[normalize-space()='MISA']"
    SALON_RAD_VT = "//label[normalize-space()='VIETTEL']"
    SALON_RAD_VNPT = "//label[normalize-space()='VNPT']"
    SALON_SAVEINVOICE = "//a[@ng-click='saveEInvoiceSetting(eInvoiceSetting)']"
    SALON_COMPLETED_SET = "//*[contains(text(),'Thiết lập đã được cập nhật thành công!')]"
    
    #innvoice hotel
    HOTEL_SETTING="//body/div[@class='mainWrap']/header[@class='mainHeader clearfix posR ng-scope']/section[@class='container']/section[@class='settingNav topNav posR uln flr']/ul/li[@class='setting']/a[1]"
    HOTEL_STORE="//section[@class='settingNav topNav posR uln flr']//li[4]//a[1]"
    HOTEL_TRANSACTION="li[id='tab-transaction'] span[class='k-span ng-binding']"
    HOTEL_INVOICE="//a[@id='EnableEInvoice']"
    HOTEL_MISA="//div[@class='row-padding-10 radio-custom has-pretty-child']//div[1]//div[1]//div[1]//label[1]"
    HOTEL_VIETTEL="(//label[contains(@for,'input{{item.Name}}')])[2]"
    HOTEL_VNPT="(//label[contains(@for,'input{{item.Name}}')])[3]"
    HOTEL_SAVE_INV="//a[contains(@ng-click,'saveEInvoiceSetting(eInvoiceSetting)')]"
    HOTEL_INV_STATUS="//*[contains(text(),'Thiết lập đã được cập nhật thành công!')]"
    
    #timeconfig
    TIME = 15
    TIMEstamp = 20
    timeout =10000
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
    FNB_MM_SHOWQR="(//span[@class='kfin-qr-btn-wallet kfin-text-caption-2 kfin-text-neutral-base'])[1]"
    FNB_MM_QR_CONTENT="//div[@class='kfin-popup-qr-momo-heading']"
    FNB_BTN_PAY_COUTINUE="//*[contains(text(),' Dừng tính và thanh toán ')]"
    FNB_FIND="Tìm món (F3)"
    FNB_DROPDWN_BANK="(//kv-cashier-qr-code//span)[4]"
    #CONNECT DEVICES
    CONNECT_DEVICE_LINK_TEXT="//div[@class='kfin-onboarding-mini']"
    CONNECT_DEVICE_MOMO="//div[@class='kfin-onboarding-mini-qr']"
    CONNECT_DEVICE_BUTTON="//button[@class='kfin-btn kfin-btn-primary']"

    #salon invoice
    BTN_CASHSHIER_LOG = '//*[@id="loginNewSale"]'
    BTN_SALON_CUSTOMER_LIST="//i[@class='fas fa-th-large']"
    BTN_TXT_PASS ="//input[@id='userPasswordInp']"
    XP_FIND_PRODUCT="//input[@id='cart-product-search-id']"
    BTN_SALE_SALON ="//span[normalize-space()='Bán hàng']"
    BTN_SALON_CLOSE ="//label[@for='toggleProductListTablet']//i[@class='far fa-times']"
    BTN_SALON_PAY ="//span[normalize-space()='Thanh toán']"
    RAD_SALON_BANK_TRANSFER ="label[id='bank-transfer'] span"
    BTN_SALON_SHOWQR ="span[class='kfin-qr-btn'] span"
    TXT_CONTENTQR="//div[@class='kfin-popup-qr-heading']"
    TXT_DRPDWNBANK="//div[@class='payment-qrcode-option']/kendo-dropdownlist"

    #invoice kvs publish:
    #retail
    misa_template="//button[contains(text(),'Hóa đơn GTGT khởi tạo từ máy tính tiền mẫu cơ bản 1 TS')]"
    vnpt_template="//button[contains(text(),'Hóa đơn bán hàng 2/002_C24MNB')]"
    viettel_template="//button[normalize-space()='C24TDV']"
    #variable
    RT_INV_CONFIG="//a[@id='eInvoiceConfig']"
    #misatmplate
    MS_RT_TEM_PUBLISH="//button[contains(text(),'Hóa đơn GTGT khởi tạo từ máy tính tiền mẫu cơ bản 1 TS')]"
    #vieteltmplate
    VT_RT_TEM_PUBLISH="//button[normalize-space()='C25MSN']"
    RT_INV_AUTO_PUBLISH="//span[@ng-click='vm.toggleAutoPublishEInvoice()']"
    RT_IVN_TEMPLATE="//button[contains(text(),'Hóa đơn GTGT khởi tạo từ máy tính tiền AH')]"
    RT_DONE_TEMPLATE="//a[contains(text(),'Xong')]"
    RT_PUBLISH_INV="//*[@id='saveTransaction']"
    MESSAGE_PUBLISH_DONE="//*[contains(text(),'Hóa đơn được cập nhật thành công')]"
    RT_PUBLISH_VIEW="//span[contains(text(),'Xem chi tiết')]"
    RT_STATUS_VIEW="//span[@class='eInvoice-status eInvoice-status-success']"
    RT_IVN_CONFIRM="div[class='k-widget k-window k-window-poup k-window-alert kv-window kv-close-popup k-state-focused'] button[class='btn-confirm btn btn-success']"
    RT_IVN_PL_POS="//*[contains(text(),'Phát hành hóa đơn điện tử ngay trên Màn hình bán hàng.')]"
    #VNPT template
    VNPT_RT_TEM_PUBLISH="//button[contains(text(),'Hóa đơn GTGT 1/001_C25MBN')]"
    #fnb
    FNB_TASKBAR="//i[@class='fa-solid fa-bars']"
    FNB_GENERAL_SET="li[class='menu-bar active'] ul li a span span"
    FNB_AUTO_PUBLISH="(//span[@class='toogle'])[8]"
    FNB_TEMPLATE_CHANGE="button[class='btn']"
    FNB_TEMPLATE="C23MLV - 123451/88890357 - C23MLV"
    FNB_BTN_CONFRM="button[class='btn btn-primary']"
    fnb_pay="//button[normalize-space()='Thanh toán (F9)']"
    FNB_PUBLISH_BILL="//button[@class='btn btn-lg btn-success ng-star-inserted']"
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

    #hotel
    HOTEL_AUO_PUBLISH="(//span[@class='ht-form-check-text ht-d-block'])[1]"
    HOTEL_RECEPTION="//input[@id='loginNewSale']"
    HOTEL_BILL="//i[@class='far fa-file-plus icon-btn']"
    HOTEL_PRODUCT_FILLTER="//input[@id='cart-product-search-id']"
    HOTEL_PAYMENT="//*[contains(text(),'Thanh toán')]"
    HOTEL_INVOICE_TEMLIST="//button[@title='Hoá đơn điện tử']"
    HOTEL_INVOICE_TEM="//span[normalize-space()='1/005_C24MDY']"
    HOTEL_INVOICE_TEXT="Đã phát hành hóa đơn điện tử"
    HT_PUBLISH_STATUS="//*[@class='toast-bottom-center toast-container']"
    HOTEL_PAYMENT_DONE="//button[normalize-space()='Hoàn thành']"
