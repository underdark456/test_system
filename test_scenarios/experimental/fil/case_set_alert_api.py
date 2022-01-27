from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.nms import Nms
from src.options_providers.options_provider import OptionsProvider

options_path = ''
backup_name = ''


@skip('Probably not needed')
class SetAlertCase(CustomTestCase):
    """Not needed?"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        # cls.alert = Alert(cls.driver, 0, 0)
        cls.nms = Nms(cls.driver, 0, 0)
        # cls.backup.apply_backup(backup_name)

    def test_set_alert_76(self):
        self.nms.send_param('set_alert', 'alert:76')
        print(self.nms.get_param('set_alert'))
