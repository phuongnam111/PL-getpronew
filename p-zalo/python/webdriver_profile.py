import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_webdrive(browser: str, profile_dir: str):
    """Create the driver following specific conditions

        Descriptions: The first version is not including the desired capabilities
        only focus in create a new webdrive following a profile specification
    """
    if browser.lower() == "chrome":
        chrome_service = ChromeService(ChromeDriverManager().install())
        drive = _init_chrome(service=chrome_service ,user_data_dir=profile_dir)

    elif browser.lower() == "firefox":
        firefox_service = FirefoxService(GeckoDriverManager().install())
        drive = _init_firefox(service=firefox_service, user_data_dir=profile_dir)

    return drive


def _init_chrome(service, user_data_dir: str, profile: str = ""): #C:/Users/giang.th2/AppData/Local/Google/Chrome/User Data/Profile 3
    """Create the drive following a chrome profile"""
    chrome_options = ChromeOptions()
    if user_data_dir:
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        chrome_options.add_argument(f"--profile-directory={profile}")
        drive = webdriver.Chrome(service=service, options=chrome_options)
    return drive


def _init_firefox(service, user_data_dir: str):
    """Create the drive Following a firefox profile"""
    firefox_options = FirefoxOptions()
    if user_data_dir:
        firefox_options.add_argument("-profile")
        firefox_options.add_argument(user_data_dir)
        print(service)
        drive = webdriver.Firefox(service=service, options=firefox_options)
    return drive

def connect_zalo_by_url(url_connect: str, profile_dir: str):
    driver = create_webdrive("firefox", profile_dir)
    # Print("Giang Giang 123")
    driver.get(url_connect)
    checkbox_element = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//label[text()='Đồng ý cho phép ứng dụng quản lý Official Account']")))
    checkbox_element.click()
    submit_btn =   driver.find_element(By.XPATH, "//a[text()='Cho phép']")
    submit_btn.click()
    time.sleep(5)
    driver.close()

def get_chromedriver_path():
    driver_path = GeckoDriverManager().install()
    print(driver_path)
    return  driver_path