from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR, API_LOGOUT_PATH
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api.random_requests'
backup_name = 'default_config.txt'


@skip('Does not make sense. Delete?')
class ApiLogoutCase(CustomTestCase):
    """One line string describing the test case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = None  # approximate case execution time in seconds

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(), driver_id='case_api_logout', store_driver=False
        )
        cls.backup = BackupManager()

    def test_sample(self):
        """One line string describing the test case"""
        reply, error, error_code, status = self.driver.custom_get(API_LOGOUT_PATH, http_status_code=True)
        self.assertEqual('OK', status, msg=f'Http status code {status}, expected OK')
        self.assertEqual(NO_ERROR, error_code)
        self.assertEqual('', reply)
        self.assertEqual('', error)
