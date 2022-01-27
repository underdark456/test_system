from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes
from src.exceptions import ObjectNotUpdatedException

options_path = 'test_scenarios.form_validation.controller'
backup_name = 'default_config.txt'


class FrameLengthCase(CustomTestCase):
    """TDMA frame length must be multiple of 4"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.22'
    __execution_time__ = 5
    __express__ = True

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)
        net = nms_api.create('nms:0', 'network', {'name': 'net'})
        tp = nms_api.create(net, 'teleport', {'name': 'tp'})
        cls.mf_hub = nms_api.create(net, 'controller', {
            'name': 'mf_hub',
            'teleport': tp,
            'mode': ControllerModes.MF_HUB
        })

    def test_frame_length(self):
        """TDMA frame_length divisible by 4 should be applied, the rest should not"""
        for i in range(16, 253):
            if i % 4 == 0:
                try:
                    nms_api.update(self.mf_hub, {'frame_length': i})
                except ObjectNotUpdatedException:
                    self.fail(f'frame_length={i} is not applied')
            else:
                with self.assertRaises(ObjectNotUpdatedException, msg=f'frame_length={i} applied'):
                    nms_api.update(self.mf_hub, {'frame_length': i})
