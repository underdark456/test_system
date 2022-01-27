from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.network import Network
from src.options_providers.options_provider import OptionsProvider
from test_scenarios.form_validation.abstract_case import _AbstractCase

backup_name = 'default_config.txt'
options_path = 'test_scenarios.form_validation.subtests.network'


@skip('There is a data types validation test. This one is not needed?')
class NetworkValidationCase(_AbstractCase):
    """Not needed? Network creation page validation"""

    @classmethod
    def set_up_class(cls):
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        cls._init_params(cls.options)
        cls._object = Network.create(cls._driver, 0, {'name': 'Network_name'})
        Alert.create(cls._driver, 0, {'name': 'alert_name', 'popup': True})

    def test_settings(self):
        """Network settings section validation test"""
        self.test_values = self.test_values.get('settings')
        self.valid_values = self.valid_values.get('settings')
        super()._test_validate_fields()

    def test_additional_setup(self):
        """Network additional setup section validation test"""
        self.test_values = self.test_values.get('additional_setup')
        self.valid_values = self.valid_values.get('additional_setup')
        super()._test_validate_fields()

    def test_beams(self):
        """Network satellite beams section validation test"""
        self.test_values = self.test_values.get('beams')
        self.valid_values = self.valid_values.get('beams')
        super()._test_validate_fields()
