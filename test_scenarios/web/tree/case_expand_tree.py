import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.web.tree'
backup_name = 'case_database_performance.txt'


class ExpandTreeCase(CustomTestCase):
    """One line string describing the test case"""

    __author__ = 'dkudryashov'
    __version__ = '0.1'
    __execution_time__ = None  # approximate case execution time in seconds
    _wait_time_out = 3

    @classmethod
    def set_up_class(cls):
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        time.sleep(5)
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path), driver_id='case_web_expand_tree', store_driver=False
        )
        time.sleep(2)

    def test_sample(self):
        """One line string describing the test case"""
        self._wait_load_page()
        self.driver.expand_tree()

    def _wait_load_page(self):
        WebDriverWait(self.driver.driver, self._wait_time_out) \
            .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'body')))
