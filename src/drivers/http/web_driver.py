from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from src.drivers.abstract_http_driver import CHROME, FIREFOX
from src.drivers.http.nms_web_driver import NmsWebDriver
from src.exceptions import DriverInitException


class WebDriver(object):

    @classmethod
    def create_driver(cls, driver_options=None):
        driver_type = driver_options.get("type")
        if driver_options is not None:
            driver = None
            if CHROME == driver_type:
                driver = WebDriver._create_chrome_driver(driver_type, driver_options)
            elif FIREFOX == driver_options.get("type"):
                driver = WebDriver._create_firefox_driver(driver_type, driver_options)
            if driver is None:
                raise DriverInitException
            if driver_options.get('auto_login'):
                driver.login(driver_options.get('username'), driver_options.get('password'))
            return driver
        else:
            raise DriverInitException('empty options')

    @classmethod
    def _create_chrome_driver(cls, driver_type, driver_options):
        chrome_options = Options()
        if 'no_gui' in driver_options and driver_options['no_gui']:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")  # linux only
            _headless = True
        else:
            _headless = False
        driver = NmsWebDriver(driver_type, webdriver.Chrome(
            executable_path=driver_options.get("driver_path"),
            options=chrome_options
        ))
        driver.address = driver_options.get('address')
        window_size = driver_options.get('window_size', None)
        if window_size is not None and isinstance(window_size, tuple) and len(window_size) == 2 and \
                isinstance(window_size[0], int) and isinstance(window_size[1], int):
            driver.driver.set_window_size(window_size[0], window_size[1])
        elif 'maximize_window' in driver_options and driver_options['maximize_window']:
            if _headless:  # Cannot auto maximize window in headless mode, setting to full hd
                driver.driver.set_window_size(1920, 1080)
            else:
                driver.driver.maximize_window()
        return driver

    @classmethod
    def _create_firefox_driver(cls, driver_type, driver_options):
        firefox_options = FirefoxOptions()
        if 'no_gui' in driver_options and driver_options['no_gui']:
            firefox_options.headless = True
            _headless = True
        else:
            _headless = False
        driver = NmsWebDriver(driver_type, webdriver.Firefox(
            options=firefox_options
        ))
        driver.address = driver_options.get('address')
        window_size = driver_options.get('window_size', None)
        if window_size is not None and isinstance(window_size, tuple) and len(window_size) == 2 and \
                isinstance(window_size[0], int) and isinstance(window_size[1], int):
            driver.driver.set_window_size(window_size[0], window_size[1])
        elif 'maximize_window' in driver_options and driver_options['maximize_window']:
            if _headless:  # Cannot auto maximize window in headless mode, setting to full hd
                driver.driver.set_window_size(1920, 1080)
            else:
                driver.driver.maximize_window()
        return driver
