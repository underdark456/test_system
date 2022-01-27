from selenium.webdriver.common.by import By
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.web.investigator'
backup_name = 'groups_limited_scopes.txt'


class WebInvestigatorUsersCase(CustomTestCase):
    """WEB Investigator users with limited scope access to the tool"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __execution_time__ = 35  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT),
            driver_id='case_web_investigator_users',
            store_driver=False
        )
        cls.options = OptionsProvider.get_options(options_path)
        cls.inv_search_title_class = 'investigator__search-title'
        cls.inv_search_input_class = 'investigator__search-input'
        cls.error_page_error_class = 'errorpage__error'
        cls.error_page_title_class = 'errorpage__title'
        cls.error_page_message_class = 'errorpage__message'

    def set_up(self):
        self.driver.logout()

    def test_user_net1(self):
        """User of network 1 can access Investigator"""
        self.next_user('user_net_1', 'qwerty')

    def test_user_net2(self):
        """User of network 1 can access Investigator"""
        self.next_user('user_net_2', 'qwerty')

    def test_user_vno1(self):
        """User of VNO 1 can access Investigator"""
        self.next_user('user_vno_1', 'qwerty')

    def test_user_vno2(self):
        """User of VNO 2 can access Investigator"""
        self.next_user('user_vno_2', 'qwerty')

    def test_user_sub_vno1(self):
        """User of Sub VNO 2 can access Investigator"""
        self.next_user('user_sub_vno_1', 'qwerty')

    def test_user_sub_vno2(self):
        """User of Sub VNO 2 can access Investigator"""
        self.next_user('user_sub_vno_2', 'qwerty')

    def test_user_ctrl1(self):
        """User of Controller 1 can access Investigator"""
        self.next_user('user_ctrl_1', 'qwerty')

    def test_user_ctrl2(self):
        """User of Controller 2 can access Investigator"""
        self.next_user('user_ctrl_2', 'qwerty')

    def next_user(self, username, password):
        self.driver.login(username, password)
        self.driver.load_data(PathsManager.nms_investigator(self.driver.get_type(), 0))
        self.check_expected_elements()

    def check_expected_elements(self):
        self.assertIsNotNone(
            self.driver._get_element_by(By.CLASS_NAME, self.inv_search_title_class),
            msg=f'Cannot locate Investigator search title by class name'
        )
        self.assertIsNotNone(
            self.driver._get_element_by(By.CLASS_NAME, self.inv_search_input_class),
            msg=f'Cannot locate Investigator search input by class name'
        )
        self.assertIsNone(
            self.driver._get_element_by(By.CLASS_NAME, self.error_page_error_class, timeout=0.5),
            msg=f'Investigator error element is located'
        )
        self.assertIsNone(
            self.driver._get_element_by(By.CLASS_NAME, self.error_page_title_class, timeout=0.5),
            msg=f'Investigator error title element is located'
        )
        self.assertIsNone(
            self.driver._get_element_by(By.CLASS_NAME, self.error_page_message_class, timeout=0.5),
            msg=f'Investigator error message is located'
        )
