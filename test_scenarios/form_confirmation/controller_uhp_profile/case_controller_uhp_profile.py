from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes

options_path = 'test_scenarios.form_confirmation.controller_uhp_profile'
backup_name = 'default_config.txt'


class ControllerUhpProfileCase(CustomTestCase):
    """Make sure that UHP modem runs an appropriate profile upon setting the controller mode"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 155  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        cls.controller = test_api.get_uhp_by_model('UHP200', 'UHP200X', number=1)[0]
        cls.controller_uhp = cls.controller.get('web_driver')

    def set_up(self):
        nms_api.load_config(backup_name)
        self.net = nms_api.create('nms:0', 'network', {'name': 'test_net', 'dev_password': ''})
        self.tp = nms_api.create(self.net, 'teleport', {'name': 'test_tp'})

    def check_next_mode(self, nms_mode_value, mode_name):
        nms_api.create(self.net, 'controller', {
            'name': mode_name,
            'mode': nms_mode_value,
            'teleport': self.tp,
            'device_ip': self.controller.get('device_ip'),
            'device_vlan': self.controller.get('device_vlan'),
            'device_gateway': self.controller.get('device_gateway'),
        })
        self.controller_uhp.set_nms_permission(vlan=self.controller.get('device_vlan'), password='')
        nms_api.wait_next_tick()
        nms_api.wait_next_tick()
        uhp_profile = self.controller_uhp.get_active_profile_name()
        self.assertEqual(
            mode_name,
            uhp_profile,
            msg=f'UHP profile is {uhp_profile} upon setting controller to {mode_name}'
        )

    def test_mf_hub(self):
        """UHP runs MF hub profile upon setting NMS controller to MF hub mode"""
        self.check_next_mode(ControllerModes.MF_HUB, 'MF hub')

    def test_outroute(self):
        """UHP runs Outroute profile upon setting NMS controller to Outroute mode"""
        self.check_next_mode(ControllerModes.OUTROUTE, 'Outroute')

    def test_dama_hub(self):
        """UHP runs DAMA hub profile upon setting NMS controller to DAMA_hub mode"""
        self.check_next_mode(ControllerModes.DAMA_HUB, 'DAMA hub')

    def test_hubless_master(self):
        """UHP runs Hubless master profile upon setting NMS controller to Hubless_master mode"""
        self.check_next_mode(ControllerModes.HUBLESS_MASTER, 'Hubless master')

    def test_inroute(self):
        """UHP runs Inroute profile upon setting NMS controller to Inroute mode"""
        mf_hub = nms_api.create(
            self.net,
            'controller',
            {'name': 'mf_hub', 'mode': ControllerModes.MF_HUB, 'teleport': self.tp}
        )
        nms_api.create(self.net, 'controller', {
            'name': 'inroute',
            'mode': ControllerModes.INROUTE,
            'tx_controller': mf_hub,
            'teleport': self.tp,
            'device_ip': self.controller.get('device_ip'),
            'device_vlan': self.controller.get('device_vlan'),
            'device_gateway': self.controller.get('device_gateway'),
            'inroute': 99,
        })
        self.controller_uhp.set_nms_permission(vlan=self.controller.get('device_vlan'), password='')
        nms_api.wait_next_tick()
        nms_api.wait_next_tick()
        uhp_profile = self.controller_uhp.get_active_profile_name()
        self.assertEqual(
            'Inroute',
            uhp_profile,
            msg=f'UHP profile is {uhp_profile} upon setting controller to Inroute',
        )

    def test_dama_inroute(self):
        """UHP runs DAMA inroute profile upon setting NMS controller to DAMA_inroute mode"""
        dama_hub = nms_api.create(
            self.net,
            'controller',
            {'name': 'mf_hub', 'mode': ControllerModes.DAMA_HUB, 'teleport': self.tp})
        nms_api.create(self.net, 'controller', {
            'name': 'dama_inroute',
            'mode': ControllerModes.DAMA_INROUTE,
            'tx_controller': dama_hub,
            'teleport': self.tp,
            'device_ip': self.controller.get('device_ip'),
            'device_vlan': self.controller.get('device_vlan'),
            'device_gateway': self.controller.get('device_gateway'),
        })
        self.controller_uhp.set_nms_permission(vlan=self.controller.get('device_vlan'), password='')
        nms_api.wait_next_tick()
        nms_api.wait_next_tick()
        uhp_profile = self.controller_uhp.get_active_profile_name()
        self.assertEqual(
            'DAMA inroute',
            uhp_profile,
            msg=f'UHP profile is {uhp_profile} upon setting controller to DAMA_inroute',
        )

    def test_gateway(self):
        """UHP runs DAMA hub profile upon setting NMS controller to Gateway mode"""
        mf_hub = nms_api.create(self.net, 'controller', {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': self.tp,
            'device_ip': '127.0.0.1',
            'device_vlan': 0,
            # 'device_gateway': '127.0.0.15',  # ticket 8176 currently fixed
        })
        nms_api.create(self.net, 'controller', {
            'name': 'gateway',
            'mode': ControllerModes.GATEWAY,
            'tx_controller': mf_hub,
            'teleport': self.tp,
            'device_ip': self.controller.get('device_ip'),
            'device_vlan': self.controller.get('device_vlan'),
            'device_gateway': self.controller.get('device_gateway'),
        })
        self.controller_uhp.set_nms_permission(vlan=self.controller.get('device_vlan'), password='')
        nms_api.wait_next_tick()
        nms_api.wait_next_tick()
        uhp_profile = self.controller_uhp.get_active_profile_name()
        self.assertEqual(
            'DAMA hub',
            uhp_profile,
            msg=f'UHP profile is {uhp_profile} upon setting controller to Gateway, should be DAMA hub',
        )

    def test_mf_inroute(self):
        """UHP runs MF inroute profile upon setting NMS controller to MF_inroute mode"""
        self.check_next_mode(ControllerModes.MF_INROUTE, 'MF inroute')

    def tear_down(self):
        self.controller_uhp.set_nms_permission(password='qwerty')
