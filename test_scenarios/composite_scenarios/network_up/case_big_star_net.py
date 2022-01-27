from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, Checkbox, StationModes, RouteTypes, RouteIds

options_path = 'test_scenarios.composite_scenarios.network_up'
backup_name = 'default_config.txt'


class BigStarNetCase(CustomTestCase):
    """Star network with 20 stations UP case"""

    __author__ = 'dkudryashov'
    __version__ = '0.1'
    __execution_time__ = None  # approximate case execution time in seconds

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)
        test_options = test_api.get_options(options_path)

        controllers, stations = test_api.get_uhp_controllers_stations(1, ['UHP200X', ], 20, ['ANY', ])

        net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        tp = nms_api.create(net, 'teleport', {'name': 'test_tp', 'rx1_lo': 0, 'rx2_lo': 0, 'tx_lo': 0})
        mf_hub = nms_api.create(net, 'controller', {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
            'device_ip': controllers[0].get('device_ip'),
            'device_vlan': controllers[0].get('device_vlan'),
            'device_gateway': controllers[0].get('device_gateway'),
            'uhp_model': controllers[0].get('model'),
            'tx_on': Checkbox.ON,
            'tx_level': test_options.get('tx_level'),
            'stn_number': 21,
        })
        rx1_frq = nms_api.get_param(mf_hub, 'tx_frq')
        rx1_sr = nms_api.get_param(mf_hub, 'tx_sr')
        vno = nms_api.create(net, 'vno', {'name': 'test_vno'})

        ser = nms_api.create(net, 'service', {'name': 'local_ser', 'stn_vlan': stations[0].get('device_vlan')})
        for i in range(len(stations)):
            nms_api.create(vno, 'station', {
                'name': f'stn{i}',
                'serial': stations[i].get('serial'),
                'enable': True,
                'mode': StationModes.STAR,
                'rx_controller': mf_hub,
            })
            nms_api.create(f'station:{i}', 'route', {
                'type': RouteTypes.IP_ADDRESS,
                'service': ser,
                'ip': stations[i].get('device_ip'),
                'id': RouteIds.PRIVATE
            })
            nms_api.create(f'station:{i}', 'route', {
                'type': RouteTypes.STATIC_ROUTE,
                'service': ser,
                'ip': '0.0.0.0',
                'mask': '/0',
                'gateway': stations[i].get('device_gateway'),
                'id': RouteIds.PRIVATE
            })
            stations[i].get('web_driver').star_station(params={
                'rx1_frq': rx1_frq,
                'rx1_sr': rx1_sr,
                'tx_level': test_options.get('tx_level'),
            })

        controllers[0].get('web_driver').set_nms_permission(vlan=controllers[0].get('device_vlan'), password='')
        if not nms_api.wait_up(mf_hub, timeout=60):
            test_api.error('MF hub is not UP')
        for i in range(len(stations)):
            if not nms_api.wait_up(f'station:{i}', timeout=60):
                test_api.error(f'Station {i+1} is not UP')

    def test_big_net(self):
        """One line string describing the test method"""
        self.assertTrue(True)
