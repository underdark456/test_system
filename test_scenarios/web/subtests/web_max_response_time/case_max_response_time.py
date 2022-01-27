import time
from threading import Thread
from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.abstract_http_driver import API, AbstractHttpDriver
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

options_path = 'test_scenarios.web.subtests.web_max_response_time'
backup_name = 'case_web_max_response_time.txt'


@skip('Not ready')
class WebMaxResponseTimeCase(CustomTestCase):
    """! Not ready. Maximum response time to some time consuming requests"""

    __author__ = 'dkudryashov'
    __version__ = '0.1'

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.nms_address_port = cls.system_options.get(API_CONNECT).get('address')

    def set_up(self) -> None:
        pass

    def test_response_time(self):
        drivers = []
        threads = []
        for i in range(1, 511):
            username = f'user-{i}'
            driver = DriversProvider.get_driver_instance(
                {
                    'type': API,
                    'address': self.nms_address_port,
                    'username': username,
                    'password': '12345',
                    'auto_login': True,
                }
            )
            drivers.append(driver)

            path = f'api/realtime/get/controller={i-1}'
            post = {"command": "show int eth", "control": i-1}

            threads.append(Thread(
                target=self.send_request,
                args=(driver, path, post)
            ))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def send_request(self, driver: AbstractHttpDriver, path: str, post=None):
        st_time = time.perf_counter()
        if post is None:
            reply, error, error_code = driver.custom_get(path)
        else:
            reply, error, error_code = driver.custom_post(path, payload=post)
        resp_time = time.perf_counter() - st_time
        self.assertEqual(NO_ERROR, error_code)
        print(resp_time)
        print(reply)
