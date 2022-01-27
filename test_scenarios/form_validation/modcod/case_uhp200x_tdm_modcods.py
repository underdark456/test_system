import json
import os

from global_options.options import PROJECT_DIR
from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, ModelTypes

options_path = 'test_scenarios.form_validation.modcod'
backup_name = 'default_config.txt'


class Uhp200xTdmModcodValidationCase(CustomTestCase):
    """tx_modcod for UHP200X model validation"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 6
    __express__ = True

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        # Getting lists of supported TDM modcods for UHP200X
        with open(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}modcodes_uhp_200x.txt', 'r') as file:
            modcods = json.load(file)
            cls.uhp200x_modcods = modcods.get('tx_modcod')
        net = nms_api.create('nms:0', 'network', {'name': 'net-0'})
        tp = nms_api.create(net, 'teleport', {'name': 'tp-0'})
        cls.mf_hub = nms_api.create(net, 'controller', params={
            'name': 'HM',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
            'uhp_model': ModelTypes.UHP200X,
        })

    def test_supported_unsupported(self):
        """Applying supported modcods for UHP200X"""
        for modcod in self.uhp200x_modcods:
            # should not raise ObjectNotUpdatedException
            nms_api.update(self.mf_hub, {'tx_modcod': modcod.get('value')})
