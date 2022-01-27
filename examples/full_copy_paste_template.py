from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider

options_path = ''
backup_name = ''


# Rename `TemplateCase`
class TemplateCase(CustomTestCase):

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

    def set_up(self) -> None:
        pass

    # tests

    def tear_down(self) -> None:
        pass

    @classmethod
    def tear_down_class(cls) -> None:
        pass
