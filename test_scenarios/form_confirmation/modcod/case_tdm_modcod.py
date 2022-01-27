import json
import os

from global_options.options import PROJECT_DIR
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, ModcodModes, ModcodModesStr, ModelTypesStr
from src.exceptions import NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.form_confirmation.modcod'
backup_name = 'default_config.txt'


class TdmModcodConfirmationCase(CustomTestCase):
    """Confirm that UHP200X gets ALL correct TDM modcod from a controller"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 570  # approximate test case execution time in seconds
    __express__ = False

    @classmethod
    def set_up_class(cls):
        uhp200x_modems = OptionsProvider.get_uhp_by_model(ModelTypesStr.UHP200X, number=1)
        cls.uhp_ip = uhp200x_modems[0].get('device_ip')
        cls.uhp = uhp200x_modems[0].get('web_driver')

        with open(
                f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_tdm_acm_cn_order{os.sep}sf_tdm_acm_cn_order_uhp200x.txt',
                'r'
        ) as file:
            cls.sf_modcods = json.load(file)
        with open(
                f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_tdm_acm_cn_order{os.sep}lf_tdm_acm_cn_order_uhp200x.txt',
                'r'
        ) as file:
            cls.lf_modcods = json.load(file)

        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)

        cls.nms = Nms(cls.driver, 0, 0)
        cls.class_logger.info(f'NMS SW version: {cls.nms.get_param("version")}')

        cls.class_logger.info(f'UHP {cls.uhp_ip} SW version: {cls.uhp.get_software_version()}')
        cls.uhp.set_nms_permission(password='indeed', vlan=uhp200x_modems[0].get('device_vlan'))

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
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{cls.tp.get_id()}',
            'device_ip': cls.uhp_ip,
            'device_vlan': uhp200x_modems[0].get('device_vlan'),
            'device_gateway': uhp200x_modems[0].get('device_gateway'),
            'uhp_model': uhp200x_modems[0].get('model'),
            'tx_on': 'ON',
            'tx_level': cls.options.get('tx_level'),
        })
        if not cls.controller.wait_not_states(['Unknown', 'Unreachable']):
            raise NmsControlledModeException(f'UHP at {cls.uhp_ip} is not under NMS control')
        cls.nms.wait_next_tick()

    def test_tdm_modcod_uhp(self):
        """Check that ALL applied TDM modcod are received by UHP200X"""
        for m in [*ModcodModes()]:
            i = [*ModcodModes()].index(str(m))
            m_str = [*ModcodModesStr()][i]
            self.controller.send_param('tx_modcod', m)
            self.nms.wait_ticks(2)
            uhp_value = self.uhp.get_tdm_tx_form().get('tx_modcod')
            self.assertEqual(
                str(m_str.lower()),
                str(uhp_value),
                msg=f'applied value={str(m_str.lower())}, uhp value={str(uhp_value)}'
            )

    def test_tx_modcod_stored_name(self):
        """Test TDM modcod NMS stored names"""
        for i in range(len([*ModcodModes()])):
            self.controller.send_param('tx_modcod', [*ModcodModes()][i])
            nms_modcod = self.controller.get_param('tx_modcod')
            with self.subTest(f'TX modcod number {i} TX modcod value {[*ModcodModesStr()][i]}'
                              f' TX modcod reply {nms_modcod}'):
                self.assertEqual([*ModcodModesStr()][i], nms_modcod)

    def test_tx_modcod_nms_uhp_equality(self):
        """Make sure that NMS and UHP tx_modcod values are the same"""
        for modcod in self.sf_modcods:
            self.controller.send_param('tx_modcod', modcod.get('value'))
            self.assertEqual(modcod.get('name'), self.controller.read_param('tx_modcod'))
        for modcod in self.lf_modcods:
            self.controller.send_param('tx_modcod', modcod.get('value'))
            self.assertEqual(modcod.get('name'), self.controller.read_param('tx_modcod'))
