import time
from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, StationModes

options_path = 'test_scenarios.experimental.dk'
backup_name = 'default_config.txt'


class MfChannelsCase(CustomTestCase):
    """MF hub + 3 MF inroute 16 channels UP"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.22'
    __execution_time__ = 1150
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.number_of_controllers = 4
        controllers = test_api.get_uhp_by_model('UHP200', number=cls.number_of_controllers)

        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        options = test_api.get_options(options_path)

        net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        tp = nms_api.create(net, 'teleport', {'name': 'test_tp', 'rx1_lo': 0, 'rx2_lo': 0, 'tx_lo': 0})
        cls.mf_hub = nms_api.create(net, 'controller', {
            'name': f'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'uhp_model': controllers[0].get('model'),
            'teleport': tp,
            'device_ip': controllers[0].get('device_ip'),
            'device_vlan': controllers[0].get('device_vlan'),
            'device_gateway': controllers[0].get('device_gateway'),
            'tx_on': True,
            'tx_level': (46 if options.get('tx_level') + 15 > 46 else options.get('tx_level') + 15),
            'stn_number': 20,
            'no_stn_check': True,
            'net_id': 24
        })
        for i in range(cls.number_of_controllers - 1):
            nms_api.create(net, 'controller', {
                'name': f'mf_inr{i + 1}',
                'mode': ControllerModes.MF_INROUTE,
                'uhp_model': controllers[i + 1].get('model'),
                'teleport': tp,
                'device_ip': controllers[i + 1].get('device_ip'),
                'device_vlan': controllers[i + 1].get('device_vlan'),
                'device_gateway': controllers[i + 1].get('device_gateway'),
                'net_id': 24,
            })
        vno = nms_api.create(net, 'vno', {'name': 'test_vno'})
        # Adding dummy ON stations
        for i in range(20):
            nms_api.create(vno, 'station', {
                'name': f'dummy_enabled{i+1}',
                'serial': 30000 + i,
                'enable': True,
                'mode': StationModes.STAR,
                'rx_controller': cls.mf_hub
            })

        for i in range(cls.number_of_controllers):
            controllers[i].get('web_driver').set_nms_permission(
                vlan=controllers[i].get('device_vlan'),
                password=nms_api.get_param(net, 'dev_password')
            )
        if not nms_api.wait_up(cls.mf_hub, timeout=60):
            test_api.error('MF hub is not UP')

    def test_mf_channels(self):
        """Adding MF channels one by one. Making sure MF hub and appropriate number of MF inroutes are Up"""
        for i in range(2, self.number_of_controllers * 4 + 1):
            self.info(f'{i} MF channels awaiting network Up')
            params = {f'mf{j}_en': (True if j <= i else False) for j in range(1, 17)}
            nms_api.update(self.mf_hub, params)
            if not nms_api.wait_not_state(self.mf_hub, 'Up'):
                test_api.fail(self, 'MF hub stayed Up after changing the number of MF channels')
            if not nms_api.wait_up(self.mf_hub, timeout=60):
                test_api.fail(self, 'MF hub is not UP')
            time.sleep(30)
            mf_inroute_states = [
                nms_api.get_param(f'controller:{j}', 'state') for j in range(1, self.number_of_controllers)
            ]
            if 9 > i > 4:
                self.assertEqual(1, mf_inroute_states.count('Up'), msg=f'1 MF inroute should be Up')
            elif 13 > i > 8:
                self.assertEqual(2, mf_inroute_states.count('Up'), msg=f'2 MF inroutes should be Up')
            elif i > 12:
                self.assertEqual(3, mf_inroute_states.count('Up'), msg=f'3 MF inroutes should be Up')
            self.assertEqual(i, nms_api.get_param(self.mf_hub, 'mf_channels'))
