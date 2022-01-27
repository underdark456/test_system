from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api.response_size'
backup_name = '32768_stations_1_vno.txt'


class MapResponseSizeCase(CustomTestCase):
    """API 32768 stations in map request"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = 5  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

    def test_number_of_stations_in_map_response(self):
        """One line string describing the test case"""
        path = 'api/map/both/vno=0'
        payload = {'marker_mode': 'num_state'}
        reply, error, error_code = self.driver.custom_post(path, payload=payload)
        self.assertEqual(NO_ERROR, error_code)
        self.assertEqual(32768, len(reply.get('list')))
