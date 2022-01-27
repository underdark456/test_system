import json
import os

from global_options.options import PROJECT_DIR
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.abstract_http_driver import API
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, ModelTypesStr
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.teleport import Teleport
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.web.controller'
backup_name = 'default_config.txt'


class WebModelModcodCase(CustomTestCase):
    """All valid modcodes for UHP-200 and UHP-200X as well as invalid for UHP-200 case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __express__ = True
    __execution_time = 520

    @classmethod
    def set_up_class(cls):
        cls.web_driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT),
            driver_id='case_web_model_modcod',
            store_driver=False
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.net = Network.create(cls.web_driver, 0, {'name': 'test_net'})
        cls.tp = Teleport.create(cls.web_driver, cls.net.get_id(), {'name': 'test_tp'})
        cls.ctrl = Controller.create(cls.web_driver, cls.net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{cls.tp.get_id()}',
            # 'own_cn_high': 50,
        })
        with open(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}modcodes_uhp_200.txt', 'r') as file:
            cls.uhp200_modcod = json.load(file).get('tx_modcod')
        with open(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}modcodes_uhp_200x.txt', 'r') as file:
            cls.uhp200x_modcod = json.load(file).get('tx_modcod')

    def test_model_uhp200(self):
        """Valid and invalid modcodes for UHP model 200 test"""
        self.ctrl.send_param('uhp_model', ModelTypesStr.UHP200)
        valid_modcod = self.uhp200_modcod

        invalid_modcod = []
        for modcod in self.uhp200x_modcod:
            if modcod not in valid_modcod:
                invalid_modcod.append(modcod)

        for modcod in valid_modcod:
            modcod_value = modcod.get('value')
            modcod_name = modcod.get('name')
            with self.subTest(f'UHP200 valid modcod {modcod_name}'):
                self.ctrl.send_param('tx_modcod', modcod_value)
                if self.web_driver.get_type() == API:
                    self.assertEqual(modcod_name, self.ctrl.get_param('tx_modcod'))
                else:
                    self.assertEqual(str(modcod_value), str(self.ctrl.get_param('tx_modcod')))
        for modcod in invalid_modcod:
            modcod_value = modcod.get('value')
            modcod_name = modcod.get('name')
            with self.subTest(f'UHP200 invalid modcod {modcod_name}'):
                self.ctrl.send_param('tx_modcod', modcod_value)
                if self.web_driver.get_type() == API:
                    self.assertNotEqual(modcod_name, self.ctrl.get_param('tx_modcod'))
                else:
                    self.assertNotEqual(str(modcod_value), str(self.ctrl.get_param('tx_modcod')))

    def test_model_uhp200x(self):
        """Valid modcodes for UHP model 200X test"""
        self.ctrl.send_param('uhp_model', ModelTypesStr.UHP200X)
        for modcod in self.uhp200x_modcod:
            modcod_value = modcod.get('value')
            modcod_name = modcod.get('name')
            with self.subTest(modcod_name):
                self.ctrl.send_param('tx_modcod', modcod_value)
                if self.web_driver.get_type() == API:
                    self.assertEqual(modcod_name, self.ctrl.get_param('tx_modcod'))
                else:
                    self.assertEqual(str(modcod_value), str(self.ctrl.get_param('tx_modcod')))

