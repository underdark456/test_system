from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.exceptions import ObjectNotFoundException
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.api.tools'
backup_name = 'each_entity.txt'


class ApiDashboardToolCase(CustomTestCase):
    """Dashboard tool test case"""

    __author__ = 'dkudryashov'
    __version__ = '0.1'
    __execution_time__ = 25  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.web_driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.options = OptionsProvider.get_options(options_path)

    def test_dashboard(self):
        """Dashboard get for objects supported and not supported the tool"""
        path_api = PathsManager._API_OBJECT_DASHBOARD
        path_web = PathsManager._OBJECT_DASHBOARD
        for obj_name in self.options.get('valid_dashboard_objects'):
            with self.subTest(f'Valid dashboard {obj_name} API'):
                reply, error, error_code = self.driver.custom_get(path_api.format(obj_name, 0))
                self.assertEqual(
                    NO_ERROR,
                    error_code,
                    msg=f'{obj_name} dashboard error_code {error_code}, expected {NO_ERROR}'
                )
                self.assertEqual(
                    '',
                    error,
                    msg=f'{obj_name} dashboard error {error}, expected empty error message'
                )
                self.assertEqual(
                    dict,
                    type(reply),
                    msg=f'{obj_name} dashboard reply type {type(reply)}, expected dictionary'
                )
            with self.subTest(f'Valid dashboard {obj_name} web form'):
                self.web_driver.load_data(path_web.format(obj_name, 0))
                self.assertEqual(
                    -1,
                    self.web_driver.driver.page_source.find('No dashboard for this object'),
                    msg=f'{path_web.format(obj_name, 0)} No dashboard for this object message on screen'
                )

        for obj_name in self.options.get('invalid_dashboard_objects'):
            with self.subTest(f'Invalid dashboard {obj_name} API'):
                reply, error, error_code = self.driver.custom_get(path_api.format(obj_name, 0))
                self.assertEqual(
                    NO_ERROR,
                    error_code,
                    msg=f'{obj_name} dashboard error_code {error_code}, expected {NO_ERROR}'
                )
                self.assertEqual(
                    '',
                    error,
                    msg=f'{obj_name} dashboard error {error}, expected empty error message'
                )
                self.assertEqual(
                    dict,
                    type(reply),
                    msg=f'{obj_name} dashboard reply type {type(reply)}, expected dictionary'
                )
            # Loading page of non-existing object dashboard should trigger 404 or No dashboard for this object message
            with self.subTest(f'Invalid dashboard {obj_name} web form'):
                try:
                    self.web_driver.load_data(path_web.format(obj_name, 0))
                    self.assertNotEqual(
                        -1,
                        self.web_driver.driver.page_source.find('No dashboard for this object'),
                        msg=f'{path_web.format(obj_name, 0)} is not 404 or No dashboard for this object message'
                    )
                except ObjectNotFoundException:
                    pass

