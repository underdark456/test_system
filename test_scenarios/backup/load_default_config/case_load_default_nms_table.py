from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import AlertModes, Licensing, LicensingStr, MapSource, MapSourceStr
from src.nms_entities.basic_entities.nms import Nms
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.backup.load_default_config'
backup_name = 'case_database_performance.txt'


class LoadDefaultConfigNmsTableCase(CustomTestCase):
    """Default config should replace all NMS table params with default values"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = 12  # approximate test case execution time in seconds
    __express__ = True
    nms = None

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

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

    def check_param(self, old_value, param):
        self.assertNotEqual(
            old_value,
            self.nms.read_param(param),
            msg=f'Old NMS {param} is in place after loading default'
        )

    def test_load_default_config(self):
        """Default config should replace all NMS table parameters"""
        self.backup.apply_backup('default_config.txt')
        self.check_param('new_name', 'name')
        self.check_param('new_descr', 'config_descr')
        self.check_param('ON ', 'redundancy')
        self.check_param(11111, 'in_key1')
        self.check_param(22222, 'in_key2')
        self.check_param('qwerty', 'weather_api_key')
        self.assertIsNone(self.nms.read_param('idle_time'))
        self.assertIsNone(self.nms.read_param('down_time'))
        self.check_param('Specify', 'alert_mode')
        self.assertIsNone(self.nms.read_param('set_alert'))
        self.check_param(MapSourceStr.USER, 'map_source')
        self.check_param('http://none.ru', 'map_url_template')
        self.check_param(LicensingStr.LOCAL_KEY, 'licensing')

    @classmethod
    def tear_down_class(cls):
        pass
        if cls.nms is not None:
            # NMS ver.4.0.0.20 leaves licensing untouched
            cls.nms.send_param('licensing', Licensing.DEMO_MODE)
