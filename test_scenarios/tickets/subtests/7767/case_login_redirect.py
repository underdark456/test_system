import time

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider

__author__ = 'dkudryashov'
__version__ = '0.1'
options_path = 'test_scenarios.tickets.subtests.7767'
backup_name = 'groups_limited_scopes.txt'


class LoginRedirectCase(CustomTestCase):
    """Ticket 7767. No redirect for Sub-VNO users after login"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.driver.logout()
        cls.options = OptionsProvider.get_options(options_path)

    def test_login_redirect(self):
        """
        Check if users who have different access privileges are able to login and are redirected to the respective areas
        """
        # Test user 'user_net_1', 'qwerty' having access to network 0
        self.driver.login('user_net_1', 'qwerty')
        # Should be redirected to network 0 dashboard
        with self.subTest('User net-1 is redirected to Network 1 dashboard'):
            self.assertTrue(self.driver.wait_for_redirect('/object/dashboard/network=0'))
        self.driver.logout()

        # TODO: probably not needed
        # Test user 'user_net_2', 'qwerty' having access to network 1
        self.driver.login('user_net_2', 'qwerty')
        # Should be redirected to network 1 dashboard
        with self.subTest('User net-2 is redirected to Network 2 dashboard'):
            self.assertTrue(self.driver.wait_for_redirect('/object/dashboard/network=1'))
        self.driver.logout()

        # Test user 'user_vno_1', 'qwerty' having access to VNO 1
        self.driver.login('user_vno_1', 'qwerty')
        # Should be redirected to vno 0 dashboard
        with self.subTest('User vno-1 is redirected to VNO 1 dashboard'):
            self.assertTrue(self.driver.wait_for_redirect('/object/dashboard/vno=0'))
        self.driver.logout()

        # TODO: probably not needed
        # Test user 'user_vno_2', 'qwerty' having access to VNO 3
        self.driver.login('user_vno_2', 'qwerty')
        # Should be redirected to vno 1 dashboard
        with self.subTest('User vno-3 is redirected to VNO 3 dashboard'):
            self.assertTrue(self.driver.wait_for_redirect('/object/dashboard/vno=2'))
        self.driver.logout()

        # Test user 'user_sub_vno_1', 'qwerty' having access to VNO 2
        self.driver.login('user_sub_vno_1', 'qwerty')
        # Should be redirected to vno 1 dashboard
        with self.subTest('User vno-2 (sub-Vno) is redirected to VNO 2 dashboard'):
            self.assertTrue(self.driver.wait_for_redirect('/object/dashboard/vno=1'))
        self.driver.logout()

        # TODO: probably not needed
        # Test user 'user_sub_vno_2', 'qwerty' having access to VNO 4
        self.driver.login('user_sub_vno_2', 'qwerty')
        # Should be redirected to vno 3 dashboard
        with self.subTest('User vno-4 (sub-Vno) is redirected to VNO 4 dashboard'):
            self.assertTrue(self.driver.wait_for_redirect('/object/dashboard/vno=3'))
        self.driver.logout()

        # Test user 'user_ctrl_1', 'qwerty' having access to ctrl-1
        self.driver.login('user_ctrl_1', 'qwerty')
        # Should be redirected to ctrl-1 dashboard
        with self.subTest('User ctrl-1 is redirected to ctrl-1 dashboard'):
            self.assertTrue(self.driver.wait_for_redirect('/object/dashboard/controller=0'))
        self.driver.logout()

        # TODO: Probably not needed
        # Test user 'user_ctrl_2', 'qwerty' having access to ctrl-2
        self.driver.login('user_ctrl_2', 'qwerty')
        # Should be redirected to ctrl-2 dashboard
        with self.subTest('User ctrl-2 is redirected to ctrl-2 dashboard'):
            self.assertTrue(self.driver.wait_for_redirect('/object/dashboard/controller=1'))
        self.driver.logout()
