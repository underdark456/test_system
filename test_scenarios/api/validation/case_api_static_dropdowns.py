from src.backup_manager.backup_manager import BackupManager
from src.constants import NEW_OBJECT_ID
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes
from src.exceptions import ObjectNotCreatedException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.teleport import Teleport
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

options_path = 'test_scenarios.api.validation'
backup_name = 'default_config.txt'


class ApiStaticDropdownsCase(CustomTestCase):
    """API static dropdowns requests options"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = 6
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, API_CONNECT)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

    def test_number_of_options(self):
        """Check if value equals to the number of options can be assigned to a static dropdown"""
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})
        ctrl = Controller(self.driver, net.get_id(), NEW_OBJECT_ID, {
            'name': 'test_ctrl',
            'mode': len([*ControllerModes()]),
            'teleport': f'teleport:{tp.get_id()}'
        })
        self.assertRaises(ObjectNotCreatedException, ctrl.save)
