import ipaddress
import random
from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, StationModes, RouteTypes, RouteIds

options_path = 'test_scenarios.form_confirmation.rip_router'
backup_name = 'default_config.txt'


class RipRouterMaxNumberCase(CustomTestCase):
    """Max number of RIP routers in MF hub confirmation"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 80  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.controllers, cls.stations = test_api.get_uhp_controllers_stations(1, ['UHP200', 'UHP200X'], 1, ['ANY', ])
        options = test_api.get_options(options_path)

        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        tp = nms_api.create(net, 'teleport', {'name': 'test_tp', 'rx1_lo': 0, 'rx2_lo': 0, 'tx_lo': 0})
        cls.mf_hub = nms_api.create(net, 'controller', {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
            'device_ip': cls.controllers[0].get('device_ip'),
            'device_vlan': cls.controllers[0].get('device_vlan'),
            'device_gateway': cls.controllers[0].get('device_gateway'),
            'uhp_model': cls.controllers[0].get('model'),
            'tx_on': True,
            'tx_level': options.get('tx_level'),
            'hub_tts_mode': True,
            'tts_value': 0,
        })
        stn_service = nms_api.create(net, 'service', {
            'name': 'stn_service',
            'stn_vlan': cls.stations[0].get('device_vlan'),
        })
        vno = nms_api.create(net, 'vno', {'name': 'test_vno'})
        cls.stn = nms_api.create(vno, 'station', {
            'name': 'test_stn',
            'enable': True,
            'serial': cls.stations[0].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub,
        })
        nms_api.create(cls.stn, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': stn_service,
            'ip': cls.stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        nms_api.create(cls.stn, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': stn_service,
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': cls.stations[0].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })

        cls.mf_hub_uhp = cls.controllers[0].get('web_driver')
        cls.stn_uhp = cls.stations[0].get('web_driver')
        cls.mf_hub_uhp.set_nms_permission(
            vlan=cls.controllers[0].get('device_vlan'),
            password=nms_api.get_param(net, 'dev_password')
        )
        cls.stn_uhp.star_station(params={
            'rx1_frq': nms_api.get_param(cls.mf_hub, 'rx1_frq'),
            'rx1_sr': nms_api.get_param(cls.mf_hub, 'rx1_sr'),
            'tx_level': options.get('tx_level'),
        })
        if not nms_api.wait_up(cls.mf_hub, timeout=60):
            test_api.error('MF hub is not in UP state')
        if not nms_api.wait_up(cls.stn, timeout=60):
            test_api.error('Station is not in UP state')

    def test_mf_hub_rip_router(self):
        next_hop = ipaddress.IPv4Address('172.16.0.1')
        for i in range(1, 257):
            ser = nms_api.create('network:0', 'service', {
                'name': f'ser{i}',
                'hub_vlan': i,
                'stn_vlan': 1000 + i,
            })
            nms_api.create('controller:0', 'rip_router', {
                'service': ser,
                'rip_next_hop': str(next_hop),
                'lan_rx': random.randint(0, 1),
                'lan_default': random.randint(0, 1),
                'sat_rx': random.randint(0, 1),
                'sat_default': random.randint(0, 1),
                'announce': random.randint(0, 1),
            })
            next_hop += 1
        nms_api.wait_ticks(3)
        uhp_values = self.mf_hub_uhp.get_ip_routing_static().get('rip_router')
        self.assertEqual(256, len(uhp_values))
