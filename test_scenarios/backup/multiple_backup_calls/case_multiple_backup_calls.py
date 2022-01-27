import time

from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.nms import Nms
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.operations_with_backups.subtests.multiple_backup_calls'
backup_name = 'default_config.txt'


class MultipleBackupCallsCase(CustomTestCase):
    """Call same backup multiple times case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 4800  # approximate test case execution time in seconds

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.nms = Nms(cls.driver, 0, 0)
        cls.backup = BackupManager()

    def test_multiple_backup_calls(self):
        """Backup call multiple times"""
        # The test continues on at the assertion fault.
        # Caution: each backup applying on average takes 10 seconds. Therefore, the test lasts several minutes.
        backup_calls = 1000
        counter = 0
        counter2 = 0
        for i in range(backup_calls):
            with self.subTest(f'Backup load number {i + 1}'):
                try:
                    self.backup.apply_backup('case_database_performance.txt')
                except ValueError:
                    counter += 1
                time.sleep(5)
                self.nms.wait_next_tick()
                _, _, error_code = self.driver.custom_get('api/object/dashboard/nms=0')
                if error_code != NO_ERROR:
                    counter2 += 1
                self.assertEqual(
                    NO_ERROR,
                    error_code,
                    f'Error {error_code} at getting dashboard after backup apply number {i}'
                )
        self.assertEqual(0, counter, f'{counter} out of {backup_calls} backup calls are failed')
        self.assertEqual(0, counter2, f'{counter2} time(s) getting NMS dashboard failed after loading backup')
