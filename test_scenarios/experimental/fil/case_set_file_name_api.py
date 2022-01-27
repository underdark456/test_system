from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.alert import Alert
from src.options_providers.options_provider import OptionsProvider

options_path = ''
backup_name = ''


@skip('Test case does not make sense: delete or edit!')
class WrongFileNameCase(CustomTestCase):
    """Not needed?"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        # cls.alert = Alert(cls.driver, 0, 0)
        cls.alert = Alert(cls.driver, 0, 0)

        # cls.backup.apply_backup(backup_name)

    def test_set_wrong_file_name(self):
        self.alert.send_param('priority', '1')
        self.assertEqual(self.alert.get_param('priority'), 'Medium')
