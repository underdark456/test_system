from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.enum_types_constants import ControlModes
from src.exceptions import InvalidOptionsException, NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.teleport import Teleport
from src.options_providers.options_provider import OptionsProvider

__author__ = 'dkudryashov'
__version__ = '0.1'
options_path = 'test_scenarios.statistics.controller'
backup_name = 'default_config.txt'

@skip
class HublessControllerDashCase(CustomTestCase):
    """"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.options = OptionsProvider.get_options(options_path)
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.uhp1_ip = cls.system_options.get('uhp1_ip')
        if cls.uhp1_ip is None:
            raise InvalidOptionsException('Controller IP address is not provided in the options')
        cls.uhp1 = UhpRequestsDriver(cls.uhp1_ip)
        ctrl_options = cls.options.get('controller1')
        ctrl_options['control'] = ControlModes.FULL
        ctrl_options['device_ip'] = cls.uhp1_ip
        cls.net = Network.create(cls.driver, 0, cls.options.get('network'))
        cls.tp = Teleport.create(cls.driver, cls.net.get_id(), cls.options.get('teleport1'))
        cls.ctrl = Controller.create(cls.driver, cls.net.get_id(), ctrl_options)
        cls.uhp1.set_nms_permission(password=cls.options.get('network').get('dev_password'))
        if not cls.ctrl.wait_up():
            raise NmsControlledModeException(f'UHP {cls.uhp1_ip} is not under NMS controlled mode')

    def set_up(self) -> None:
        pass

    def test_controller_dash_stats(self):
        uhp_cn = self.uhp1.get_stations_state().get('1').get('bdrx')
        nms_cn = self.ctrl.get_param('hub_own_cn')
        with self.subTest('hub_own_cn'):
            self.assertAlmostEqual(float(uhp_cn), float(nms_cn), delta=0.9)
        hub_tx_level = self.ctrl.get_param('hub_tx_level')
        with self.subTest('hub_tx_level'):
            self.assertEqual(self.options.get('controller1').get('tx_level'), hub_tx_level)

    def tear_down(self) -> None:
        pass

    @classmethod
    def tear_down_class(cls) -> None:
        pass