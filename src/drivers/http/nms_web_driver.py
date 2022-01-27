import atexit
import re
import time

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException, \
    ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from global_options.options import SCREENSHOT_DIR
from src.class_logger import class_logger_decorator
from src.constants import NOT_FOUND_PAGE, WEB_ERROR_SELECTOR, WEB_LOGIN_PATH, WEB_LOGIN_BUTTON, WEB_APPLY_BUTTON, \
    WEB_FIELD_ERROR_SELECTOR, WEB_LOGOUT_BUTTON, WEB_ADD_DEVICE_BUTTON, WEB_SYNC_ADD_BUTTON
from src.drivers.abstract_http_driver import AbstractHttpDriver, DRIVER_NAMES
from src.exceptions import NoSuchParamException, ObjectNotFoundException, \
    ObjectNotCreatedException, NotImplementedException, ObjectNotDeletedException
from src.options_providers.options_provider import OptionsProvider

_ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
_wait_time_out = 0.5


@class_logger_decorator
class NmsWebDriver(AbstractHttpDriver):

    def __init__(self, driver_type, webdriver):
        self._type = driver_type
        self._path = None
        self._current_path = None
        self.address = None

        self.sender_selector = WEB_APPLY_BUTTON
        self.driver = webdriver
        self._username = None
        self._password = None
        atexit.register(self.close)

    def get_type(self):
        return self._type

    def get_driver_name(self):
        return DRIVER_NAMES.get(self._type, None)

    def get_current_path(self):
        """
        Get the current path SET for the NmsWebDriver instance
        """
        return self._current_path

    def get_current_url(self):
        """
        Get the current url of the selenium web driver. Can be used to handle redirects
        """
        return self.driver.current_url

    def wait_for_redirect(self, url: str, timeout=3):
        """
        Wait for the expected url to load.

        :param str url: the expected partial url
        :param int timeout: number of seconds to wait for the expected url
        """
        while timeout > 0:
            if self.get_current_url().find(url) != -1:
                return True
            timeout -= 0.2
            time.sleep(0.2)
        return False

    def load_data(self, path=None):
        if path is None:
            path = self._path
        self._current_path = path
        full_address = self.address + path
        self.driver.get(full_address)
        WebDriverWait(self.driver, _wait_time_out).until(
            expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'body'))
        )
        url = self.driver.current_url
        if -1 != url.find(NOT_FOUND_PAGE):
            raise ObjectNotFoundException(full_address)

    def get_value(self, element_id):
        element = self._get_element_by(By.ID, element_id)
        if element:
            if 'checkbox' == element.get_attribute('type'):
                return element.is_selected()
            value = element.get_attribute("value")
            if value is None:
                value = element.text
            return value

    def search_id_by_name(self, search: dict):
        try:
            element = self._get_element_by(By.XPATH, search.get('web'))
            if element:
                return element.get_attribute("href")
        except TimeoutException:
            return None

    def set_value(self, element_id, element_value):
        element = self._get_element_by(By.ID, element_id)
        if element:
            for i in range(0, 3):
                try:
                    ActionChains(self.driver).move_to_element(element).perform()
                    self._set_elements_value(element, element_value)
                    break
                # Since ver.4.0.0.9 checkboxes are represented by invisible element
                except ElementNotInteractableException:
                    self._set_elements_value(element, element_value)
                    break
                except StaleElementReferenceException:
                    element = self._get_element_by(By.ID, element_id)
        else:
            raise NoSuchElementException(element_id)

    def send_value(self, element_id, element_value, sender_selector=None):
        self.set_value(element_id, element_value)
        self.send_data(sender_selector)

    def create_object(self, sender_selector=None):
        _url = self.driver.current_url
        self.send_data(sender_selector)
        err = self._get_element_by(By.CSS_SELECTOR, WEB_ERROR_SELECTOR)

        if err is not None and '' != err.text.strip():
            raise ObjectNotCreatedException(err.text)

        # Make sure that after sending the data browser url is changed #
        try:
            WebDriverWait(self.driver, 3).until(expected_conditions.url_changes(_url))
        except TimeoutException:
            raise ObjectNotCreatedException('URL has not been changed (no redirection) upon applying')

        obj_id = self._get_object_id_from_url()
        self._current_path = None
        if obj_id.isdigit():
            return int(obj_id)
        else:
            raise ObjectNotCreatedException('Can not parse object id')

    def delete_object(self, sender_selector=None):
        self.send_data(sender_selector)
        err = self._get_element_by(By.CSS_SELECTOR, WEB_ERROR_SELECTOR)
        if err is not None and '' != err.text.strip():
            raise ObjectNotDeletedException(err.text)

    def send_data(self, sender_selector=None):
        if sender_selector is None:
            sender_selector = self.sender_selector
        btn = self._get_element_by(By.CSS_SELECTOR, sender_selector)
        if btn:
            btn.click()
            self._current_path = None
        else:
            raise ObjectNotFoundException(f'Cannot locate {sender_selector} button')
        WebDriverWait(self.driver, _wait_time_out, ignored_exceptions=_ignored_exceptions) \
            .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'body')))
        # # Change current path to None only if a redirect happened
        # if urlparse(self.driver.current_url).path.lstrip('/') != self._current_path:
        #     self._current_path = None

    def has_param_error(self, element_id):
        elem = self._get_element_by(By.ID, element_id, 0.5)
        ActionChains(self.driver).move_to_element(elem).perform()
        err = self._get_element_by(By.ID, WEB_FIELD_ERROR_SELECTOR.format(element_id))
        if err is None:
            err = self._try_parse_global_error(element_id)
        return err is not None

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except ImportError:
                pass

    def set_path(self, path):
        self._path = path

    def _get_element_by(self, by, search, timeout=None):
        if timeout is None:
            timeout = _wait_time_out
        try:
            return WebDriverWait(self.driver, timeout, ignored_exceptions=_ignored_exceptions) \
                .until(expected_conditions.presence_of_element_located((by, search)))
        except NoSuchElementException:
            return None
        except TimeoutException:
            return None

    def _get_elements_by(self, by, search, timeout=None):
        if timeout is None:
            timeout = _wait_time_out
        try:
            return WebDriverWait(self.driver, timeout) \
                .until(expected_conditions.presence_of_all_elements_located((by, search)))
        except NoSuchElementException:
            return None
        except TimeoutException:
            return None

    @staticmethod
    def _set_elements_value(element, value):
        if float == type(value):
            value = str(value)
        if "select" == element.tag_name:
            select = Select(element)
            try:
                select.select_by_value(str(value))
            except NoSuchElementException:
                # API allows to set params by either their names or by the index number
                # To let some tests be driver independent WEB driver lets set by value or by visible text
                try:
                    select.select_by_visible_text(str(value))
                except NoSuchElementException:
                    err = F"param {element.get_attribute('id')} with {value}"
                    raise NoSuchParamException(err)
        elif "checkbox" == element.get_attribute("type"):
            # Since NMS 4.0.0.9 checkboxes are represented by invisible input
            checked = element.get_attribute('checked')
            if bool(value) != bool(checked):
                # Getting parent DIV which is clicked
                parent_div = element.find_element_by_xpath('..')
                parent_div.click()
        # Input element
        else:
            element.click()
            element.send_keys(Keys.CONTROL + "a")
            element.send_keys(Keys.DELETE)
            # Clear does not work since ver.4.0.0.9
            # element.clear()
            element.send_keys(value)

    def _get_object_id_from_url(self):
        WebDriverWait(self.driver, _wait_time_out, ignored_exceptions=_ignored_exceptions) \
            .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'body')))
        err = self._get_element_by(By.CSS_SELECTOR, WEB_ERROR_SELECTOR)
        if err and '' != err.text:
            raise ObjectNotCreatedException(err.text)
        return self.driver.current_url.split('/')[-1].split('=')[1]

    def login(self, user, password, timeout=3):
        self.driver.get(self.address + WEB_LOGIN_PATH)
        self.set_value('username', user)
        self.set_value('password', password)
        self.send_data(WEB_LOGIN_BUTTON)
        while timeout > 0:
            if self.get_current_url().find('login') == -1:
                self._current_path = None
                self._username = user
                self._password = password
                return True
            timeout -= 0.2
            time.sleep(0.2)
        self._current_path = None
        return False

    def logout(self):
        logout_btn = self._get_element_by(By.ID, WEB_LOGOUT_BUTTON)
        if logout_btn:
            logout_btn.click()
        self._current_path = None
        self._username = None
        self._password = None

    def _try_parse_global_error(self, element_id):
        has_error = None
        global_error = self._get_element_by(By.CSS_SELECTOR, 'div.errors')
        if global_error and global_error.text.find(element_id) != -1:
            has_error = True
        return has_error

    def _is_status_error(self):
        status_error = self._get_element_by(By.CSS_SELECTOR, 'div.status.status--bad')
        if status_error:
            return True
        return False

    def get_realtime(self, command):
        raise NotImplementedException('Method is not implemented through Selenium WEB driver')

    def custom_get(self, path, cookies=None, headers=None):
        raise NotImplementedException('Method is not implemented through Selenium WEB driver')

    def custom_post(self, path, cookies=None, payload=None, headers=None):
        raise NotImplementedException('Method is not implemented through Selenium WEB driver')

    def screenshot(self, screenshot_name):
        res = self.driver.save_screenshot(OptionsProvider.get_system_options('global_options').get(SCREENSHOT_DIR)
                                          + screenshot_name)
        return res

    def get_nms_version(self):
        tags = self.driver.find_elements_by_tag_name('div')
        for tag in tags:
            version = re.search(r'[0-9]+.[0-9]+.[0-9]+.[0-9]+', tag.text)
            if version is not None:
                return version.group()

    def expand_tree(self, delay=None):
        """
        Expand all NMS tree elements

        :param int delay: delay in seconds between trying to expand next element
        """
        # expand networks
        networks = self._get_element_by(By.CLASS_NAME, 'tree__btn', timeout=3)
        networks.click()
        time.sleep(0.1)
        clicked = set()
        # expand the rest
        while True:
            if delay is not None:
                time.sleep(delay)
            networks = self.driver.find_element_by_class_name('tree__btn')
            elements = networks.find_elements_by_xpath('//span[@class="tree__btn"]')
            for el in elements:
                try:
                    div_tag = el.find_element_by_xpath('./..')
                    a_tag = div_tag.find_element_by_tag_name('a')
                    _obj = a_tag.get_attribute('href')
                    if _obj not in clicked:
                        el.click()
                        clicked.add(_obj)
                        break
                except StaleElementReferenceException:
                    continue
            else:
                break

    def add_device(self):
        # TODO: get rid of multiple buttons by id search when issue is fixed
        add_device_btn = self._get_elements_by(By.CSS_SELECTOR, WEB_ADD_DEVICE_BUTTON)
        add_device_btn[-1].click()

    def sync_add(self):
        # TODO: get rid of multiple buttons by id search when issue is fixed
        add_device_btn = self._get_elements_by(By.CSS_SELECTOR, WEB_SYNC_ADD_BUTTON)
        add_device_btn[-1].click()

    def _is_url_changed(self, old_url):
        print(self.driver.current_url)
        return old_url != self.driver.current_url
