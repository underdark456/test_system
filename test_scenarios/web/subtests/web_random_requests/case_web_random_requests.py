import random

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.user import User
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

__author__ = 'dkudryashov'
__version__ = '0.1'
__execution_time__ = 450  # approximate test case execution time
options_path = 'test_scenarios.web.subtests.web_random_requests'
backup_name = 'each_entity.txt'


class WebRandomRequestsCase(CustomTestCase):
    """Bombarding WEB server with random requests"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.options = OptionsProvider.get_options(options_path)

        cls.api_requests = cls.options.get('api')
        cls.web_requests = cls.options.get('web')
        cls.entities = cls.options.get('entities')

        cls.nms_address_port = cls.system_options.get(CHROME_CONNECT).get('address')

        cls.nms = Nms(cls.driver, 0, 0)

        cls.number_of_sessions = cls.options.get('number_of_sessions')
        for i in range(cls.number_of_sessions):
            User.create(cls.driver, 0, {'name': f'user-{i}', 'password': '12345'})

    def test_semi_correct_requests(self):
        """Semi correct requests via WEB"""
        valid_cookies = self.driver.get_cookies()
        for i in range(50000):
            entity = random.choice(self.entities)
            path = random.choice(self.api_requests)
            path = path.replace('{}={}', f'{entity}={random.randint(0, 100000)}')
            if path.count('{}') == 1:
                path = path.replace('{}', entity)
            path = self.modify_path(path)
            # No cookies in 50% of cases
            if random.random() > 0.5:
                cookies = valid_cookies
            else:
                cookies = ''
            with self.subTest(f'Getting {path}'):
                # GET request in 50% of cases
                if random.random() > 0.5:
                    self.driver.custom_get(path, cookies=cookies)
                # POST request in 50% of cases
                else:
                    payload = {'name': 'qwerty'}
                    self.driver.custom_post(path, payload=payload, cookies=cookies)
                # Getting NMS dashboard to make sure that the WEB server is alive
                self.assertIsNotNone(self.nms.get_param('name'))

    def send_requests(self):
        for i in range(100000):
            entity = random.choice(self.entities)
            path = random.choice(self.api_requests)
            path = path.replace('{}={}', f'{entity}={random.randint(0, 100000)}')
            if path.count('{}') == 1:
                path = path.replace('{}', entity)
            path = self.modify_path(path)
            with self.subTest(f'Getting {path}'):
                # GET request in 50% of cases
                if random.random() > 0.5:
                    self.driver.custom_get(path)
                # POST request in 50% of cases
                else:
                    payload = {'name': 'qwerty'}
                    self.driver.custom_post(path, payload=payload)
                # Getting NMS dashboard to make sure that the WEB server is alive
                self.assertIsNotNone(self.nms.get_param('name'))

    def modify_path(self, path):
        elements = path.split('/')
        for i in range(len(elements)):
            for j in range(len(elements[i])):
                # 20% chance to replace a char
                if random.random() < 0.2:
                    elements[i] = elements[i][:j] + self._get_random_char() + elements[i][j + 1:]
        random.shuffle(elements)
        return '/'.join(elements)

    @staticmethod
    def _get_random_char():
        whitespace = ' \t\n\r\v\f'
        ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
        ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ascii_letters = ascii_lowercase + ascii_uppercase
        digits = '0123456789'
        punctuation = r"""!"#$%&'()*+,-.:;<=>?@[\]^_`{|}~"""
        printable = digits + ascii_letters + punctuation + whitespace
        return printable[random.randint(0, len(printable) - 1)]

    @staticmethod
    def _generate_random_string(max_length=50):
        whitespace = ' \t\n\r\v\f'
        ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
        ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ascii_letters = ascii_lowercase + ascii_uppercase
        digits = '0123456789'
        punctuation = r"""!"#$%&'()*+,-.:;<=>?@[\]^_`{|}~"""
        printable = digits + ascii_letters + punctuation + whitespace
        random_string = ''
        for _ in range(random.randint(1, max_length+1)):
            # Keep appending random characters using chr(x)
            random_string += printable[random.randint(0, len(printable) - 1)]
        return random_string
