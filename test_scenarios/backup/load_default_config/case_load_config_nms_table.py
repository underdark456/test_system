from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import AlertModes, Licensing, LicensingStr, AlertModesStr, MapSource, MapSourceStr
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.nms import Nms
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.backup.load_default_config'
backup_name = 'default_config.txt'


class LoadNmsConfigNmsTableCase(CustomTestCase):
    """Loading a config having NMS table params should replace current NMS table params"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = 25  # approximate test case execution time in seconds
    __express__ = True
    backup = None

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        Alert.create(cls.driver, 0, {'name': 'test_alert', 'popup': True})

        cls.nms = Nms(cls.driver, 0, 0)
        cls.nms.send_params({
            'name': 'new_name',
            'config_descr': 'new_descr',
            'redundancy': True,
            'idle_time': 234,
            'down_time': 432,
            'licensing': Licensing.LOCAL_KEY,
            'in_key1': 11111,
            'in_key2': 22222,
            'weather_api_key': 'qwerty',
            'map_source': MapSource.USER,
            'map_url_template': 'http://none.ru',
            'alert_mode': AlertModes.SPECIFY,
            'set_alert': 'alert:0'
        })
        cls.backup.create_backup('temporary_nms_table_config.txt')

    def check_param(self, value, param):
        nms_value = self.nms.read_param(param)
        self.assertEqual(
            value,
            nms_value,
            msg=f'NMS {param} expected value={value}, actual value={nms_value}'
        )

    def test_load_config(self):
        """Config should populate NMS table with its values"""
        self.backup.apply_backup(backup_name)
        self.backup.apply_backup('temporary_nms_table_config.txt')
        self.check_param('new_name', 'name')
        self.check_param('new_descr', 'config_descr')
        self.check_param('ON ', 'redundancy')
        self.check_param(234, 'idle_time')
        self.check_param(432, 'down_time')
        self.check_param(LicensingStr.LOCAL_KEY, 'licensing')
        self.check_param(11111, 'in_key1')
        self.check_param(22222, 'in_key2')
        self.check_param('qwerty', 'weather_api_key')
        self.check_param(MapSourceStr.USER, 'map_source')
        self.check_param('http://none.ru', 'map_url_template')
        self.check_param(AlertModesStr.SPECIFY, 'alert_mode')
        self.check_param('alert:0 test_alert', 'set_alert')

    @classmethod
    def tear_down_class(cls):
        cls.backup.apply_backup(backup_name)
