from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes
from src.exceptions import NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.form_confirmation.modcod'
backup = 'default_config.txt'


class TdmaModcodConfirmationCase(CustomTestCase):
    """Confirm that UHP gets ALL correct TDMA modcod from a hubless controller"""

    system_options = None
    driver = None
    network = None
    teleport = None
    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 200  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        test_uhp = OptionsProvider.get_uhp_by_model('UHP200', 'UHP200X', number=1)[0]
        cls.uhp = test_uhp.get('web_driver')

        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup)

        cls.options = OptionsProvider.get_options(options_path)

        cls.nms = Nms(cls.driver, 0, 0)
        cls.class_logger.info(f'NMS SW version: {cls.nms.get_param("version")}')
        cls.class_logger.info(f'UHP {test_uhp.get("device_ip")} SW version: {cls.uhp.get_software_version()}')

        cls.net = Network.create(cls.driver, 0, params={'name': 'net-0', 'dev_password': 'indeed'})
        cls.vno = Vno.create(cls.driver, cls.net.get_id(), params={'name': 'vno-0'})
        cls.tp = Teleport.create(cls.driver, cls.net.get_id(), params={
            'name': 'tp-0',
            'sat_name': 'sat-0',
            'tx_lo': 0,
            'rx1_lo': 0,
            'rx2_lo': 0,
        })
        cls.controller = Controller.create(cls.driver, cls.net.get_id(), params={
            'name': 'HM', 
            'mode': ControllerModes.HUBLESS_MASTER, 
            'teleport': f'teleport:{cls.tp.get_id()}',
            'device_ip': test_uhp.get('device_ip'),
            'device_vlan': test_uhp.get('device_vlan'),
            'device_gateway': test_uhp.get('device_gateway'),
            'uhp_model': test_uhp.get('model'),
            'tx_on': 'ON',
            'tx_level': cls.options.get('tx_level'),
        })
        cls.uhp.set_nms_permission(password='indeed')
        if not cls.controller.wait_not_states(['Unknown', 'Unreachable', ]):
            raise NmsControlledModeException(f'UHP1 {cls.system_options.get("uhp1_ip_address")} '
                                             f'is not under NMS control')

    def test_tdma_modcod_uhp(self):
        """Check that ALL applied TDMA modcod are received by UHP"""

        self.controller.send_param('slot_length', 6)  # default slot length triggers BPSK slot too long in UHP
        for key, value in self.options.get('modcod').items():
            self.controller.send_param('tdma_mc', value)
            self.nms.wait_ticks(2)
            uhp_value = self.uhp.get_tdma_rf_form().get('tdma_mc')
            with self.subTest(key):
                self.assertEqual(self.controller.get_param('tdma_mc').lower(), uhp_value)

    def test_tdma_modcod_stored_name(self):
        """TDMA modcod NMS stored names"""
        for key, value in self.options.get('modcod').items():
            self.controller.send_param('tdma_mc', value)
            nms_modcod = self.controller.get_param('tdma_mc')
            with self.subTest(f'TX modcod number {value} TX modcod value {key} TX modcod reply {nms_modcod}'):
                self.assertEqual(key, nms_modcod)
