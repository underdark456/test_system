from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api.subtests.semi_correct_objects'
backup_name = 'default_config.txt'


class ApiAbbreviatedCase(CustomTestCase):
    """API requests with abbreviated tools or objects case"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

    def test_abbreviated_tool_method_(self):
        """Create network using abbreviated tool and method in the URL"""
        path = f'api/object/write/nms=0/new_item=network'
        reply, error, error_code = self.driver.custom_post(path, payload={'name': 'net1'})
        with self.subTest(path):
            self.assertEqual(NO_ERROR, error_code, msg=f'API request {path} unsuccessful')
        path = f'api/obj/write/nms=0/new_item=network'
        reply, error, error_code = self.driver.custom_post(path, payload={'name': 'net2'})
        with self.subTest(path):
            self.assertEqual(NO_ERROR, error_code, msg=f'API request {path} unsuccessful')
        path = f'api/obj/wri/nms=0/new_item=network'
        reply, error, error_code = self.driver.custom_post(path, payload={'name': 'net3'})
        with self.subTest(path):
            self.assertEqual(NO_ERROR, error_code, msg=f'API request {path} unsuccessful')
        path = f'ap/ob/wr/nms=0/new_item=network'
        reply, error, error_code = self.driver.custom_post(path, payload={'name': 'net4'})
        with self.subTest(path):
            self.assertEqual(NO_ERROR, error_code, msg=f'API request {path} unsuccessful')

    def test_semi_correct_entities(self):
        """Create objects using semi_correct parent and new_item names"""
        base_parent = 'ms'
        for i in range(97, 123):
            if i == 110:  # char `n`
                continue
            parent = chr(i) + base_parent
            path = f'api/object/write/{parent}=0/new_item=network'
            with self.subTest(path):
                reply, error, error_code = self.driver.custom_post(path, payload={'name': 'net'})
                self.assertNotEqual(NO_ERROR, error_code)
        base_child = 'network'
        for i in range(len(base_child)):
            correct_char = ord(base_child[i])
            for j in range(97, 123):
                if j == correct_char:
                    continue
                child = base_child[:i] + chr(j) + base_child[i:]
                path = f'api/object/write/nms=0/new_item={child}'
                with self.subTest(path):
                    reply, error, error_code = self.driver.custom_post(path, payload={'name': child})
                    self.assertNotEqual(NO_ERROR, error_code)
