from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, ModelTypes, TdmaInputModes, ModelTypesStr
from src.exceptions import ObjectNotCreatedException

options_path = 'test_scenarios.form_validation.controller'
backup_name = 'default_config.txt'


class TdmaRxInputCase(CustomTestCase):
    """TDMA RX input depending on a UHP model test case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 6  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

    def test_tdma_rx_input(self):
        """Only UHP200 is suitable for setting tdma_input to RX2"""
        net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        tp = nms_api.create(net, 'teleport', {'name': 'test_tp'})
        mf_hub = nms_api.create(net, 'controller', {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp
        })

        with self.assertRaises(ObjectNotCreatedException, msg=f'MF hub, UHP model 200X, tdma_input=RX2'):
            nms_api.create(net, 'controller', {
                'name': f'mf_hub_200x',
                'mode': ControllerModes.MF_HUB,
                'teleport': tp,
                'uhp_model': ModelTypes.UHP200X,
                'tdma_input': TdmaInputModes.RX2
            })
        with self.assertRaises(ObjectNotCreatedException, msg=f'Hubless master UHP model 200, tdma_input=RX2'):
            nms_api.create(net, 'controller', {
                'name': f'hl_mas_200x',
                'mode': ControllerModes.HUBLESS_MASTER,
                'teleport': tp,
                'uhp_model': ModelTypes.UHP200X,
                'tdma_input': TdmaInputModes.RX2
            })
        with self.assertRaises(ObjectNotCreatedException, msg=f'Inroute UHP model 200, tdma_input=RX2'):
            nms_api.create(net, 'controller', {
                'name': f'inr_200x',
                'mode': ControllerModes.INROUTE,
                'teleport': tp,
                'inroute': 24,
                'uhp_model': ModelTypes.UHP200X,
                'tdma_input': TdmaInputModes.RX2
            })
        # UHP200 should be created with tdma_input=RX2
        uhp200 = nms_api.create(net, 'controller', {
            'name': f'ctrl-UHP200',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
            'uhp_model': ModelTypes.UHP200,
            'tdma_input': TdmaInputModes.RX2
        })
        self.assertEqual('ctrl-UHP200', nms_api.get_param(uhp200, 'name'))
