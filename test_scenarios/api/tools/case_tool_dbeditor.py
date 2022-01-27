from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.api.tools'
backup_name = 'default_config.txt'
_wait_time_out = 3


class ApiToolDbeditorCase(CustomTestCase):
    """API dbeditor tool using Selenium WEB driver"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 770  # approximate test case execution time in seconds
    __express__ = False

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.web_driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.dbe = OptionsProvider.get_options(options_path).get('dbeditor')

    def test_tables_info(self):
        """Check availability of Tables info page"""
        path = f'api/dbeditor/LD/nms=0'
        self.web_driver.driver.get(self.web_driver.address + path)
        self._wait_load_page()
        hrefs = self.web_driver.driver.find_elements_by_tag_name('a')
        for href in hrefs:
            if href.get_attribute('href') == self.web_driver.address + 'api/dbeditor/TL/access=0':
                break
        else:
            self.fail(f'Cannot get Tables info page')

    def test_tables(self):
        """Check availability of Tables page"""
        path = f'api/dbeditor/LN/nms=0'
        self.web_driver.driver.get(self.web_driver.address + path)
        self._wait_load_page()
        hrefs = self.web_driver.driver.find_elements_by_tag_name('a')
        for href in hrefs:
            if href.get_attribute('href') == self.web_driver.address + 'api/dbeditor/TL/access=0':
                break
        else:
            self.fail(f'Cannot get Tables info page')

    def test_dbeditor_tool(self):
        """Get all dbeditor tables and rows (step 15) from access to vno. Test pages availability"""
        for table, data in self.dbe.items():
            # buf event has 2097216 rows - skipping
            if table == 'buf_event':
                continue
            else:
                # Getting `Table info` for the current table in a loop (step 15)
                for i in range(0, data.get('rows') + 20, 15):
                    if i > data.get('rows'):
                        break
                    path = f'api/dbeditor/TL/{table}={i}'
                    self.web_driver.driver.get(self.web_driver.address + path)
                    self._wait_load_page()
                    hrefs = self.web_driver.driver.find_elements_by_tag_name('a')
                    for href in hrefs:
                        if href.get_attribute('href') == self.web_driver.address + path:
                            break
                    else:
                        self.fail(f'{path} probably invalid')

    def test_vars_info(self):
        """Checking Vars info page for all the tables"""
        for table, data in self.dbe.items():
            path = f'api/dbeditor/TF/{table}=0'
            self.web_driver.driver.get(self.web_driver.address + path)
            self._wait_load_page()
            hrefs = self.web_driver.driver.find_elements_by_tag_name('a')
            for href in hrefs:
                if href.get_attribute('href') == self.web_driver.address + path:
                    break
            else:
                self.fail(f'{path} probably invalid')

    def _wait_load_page(self):
        WebDriverWait(self.web_driver.driver, _wait_time_out) \
            .until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, 'body')))
