import random

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api_operations'
backup_name = 'each_entity.txt'  # empty config


class _AbstractCase(CustomTestCase):
    """"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path)
        )
        cls.cookies = cls.driver.get_cookies()
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

    def set_up(self) -> None:
        pass

    def tear_down(self) -> None:
        pass

    @classmethod
    def tear_down_class(cls) -> None:
        pass

    @staticmethod
    def _generate_random_string(max_length=50):
        whitespace = ' \t\n\r\v\f'
        ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
        ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ascii_letters = ascii_lowercase + ascii_uppercase
        digits = '0123456789'
        punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
        printable = digits + ascii_letters + punctuation + whitespace
        random_string = ''
        for _ in range(random.randint(1, max_length+1)):
            # Keep appending random characters using chr(x)
            random_string += printable[random.randint(0, len(printable) - 1)]
        return random_string
