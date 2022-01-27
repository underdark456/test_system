import random
import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException, \
    StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.web.web_broken_links'
backup_name = 'case_web_broken_links.txt'


class WebFastClicksJsCase(CustomTestCase):
    """WEB fast clicks on NMS elements (max duration 10 minutes)"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.22'
    __execution_time__ = 600  # approximate case execution time in seconds
    _wait_time_out = 3

    @classmethod
    def set_up_class(cls):
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        time.sleep(3)
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path), driver_id='case_web_fast_clicks_js', store_driver=False
        )
        time.sleep(2)
        cls.nms_ip_port = OptionsProvider.get_system_options(options_path).get('nms_ip').lstrip('http://').rstrip('/')
        cls.clicked_links = set()  # store links that have been visited
        cls.has_unvisited_links = set()

    def test_fast_clicks(self):
        """Clicking on random web elements within 10 minutes with no delays between clicks"""
        self._wait_load_page()
        self.driver.expand_tree()
        st_time = time.perf_counter()
        previous_previous_href = None
        previous_href = None
        while time.perf_counter() - st_time < 600:
            elements = self._get_elements_by(By.TAG_NAME, 'a')
            try:
                el = random.choice(elements)
                href = el.get_attribute('href')
                if el.text in ('HTTP', 'WWW', 'Telnet'):  # WWW and Telnet has no href - no clicking on external links
                    continue
                if el.text == 'Return to NMS' or el.get_attribute('class') == 'errorpage__link':
                    self.fail(f'Error page upon clicking {previous_href} at {previous_previous_href}')
                if href is not None and href.find('dbeditor') != -1:
                    continue
                previous_previous_href = previous_href
                previous_href = href
                el.click()
                if not self._is_tree_expanded():
                    self.driver.expand_tree()
            except ElementNotInteractableException:
                continue
            except StaleElementReferenceException:
                continue

    def _get_elements_by(self, by, search, timeout=None):
        if timeout is None:
            timeout = self._wait_time_out
        try:
            return WebDriverWait(self.driver.driver, timeout) \
                .until(expected_conditions.presence_of_all_elements_located((by, search)))
        except NoSuchElementException:
            return None
        except TimeoutException:
            return None

    def _wait_load_page(self):
        WebDriverWait(self.driver.driver, self._wait_time_out) \
            .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'body')))

    def _is_tree_expanded(self):
        """Return 0 if tree is not expanded"""
        for i in range(3):
            try:
                networks_a = self.driver.driver.find_element_by_id('unl:0')
                parent_div = networks_a.find_element_by_xpath('./../..')
                return len(parent_div.find_elements_by_class_name('tree__btn')) - 1
            except NoSuchElementException:
                time.sleep(0.1)
        return False
