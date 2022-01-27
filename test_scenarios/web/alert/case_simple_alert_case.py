import time
from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.nms import Nms
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.web.alert'
backup_name = 'default_config.txt'


@skip('Test case Not ready')
class SimpleAlertCaseCase(CustomTestCase):
    """One line string describing the test case"""

    __author__ = 'dkudryashov'
    __version__ = '0.1'
    __execution_time__ = None  # approximate case execution time in seconds

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT),
            driver_id='case_simple_alert_case',
            store_driver=False
        )
        cls.backup = BackupManager()
        # cls.backup.apply_backup(backup_name)
        cls.nms = Nms(cls.driver, 0, 0)

    def test_sample(self):
        """One line string describing the test case"""
        self.nms.load()
        time.sleep(5)
        print(self.driver._is_status_error())
