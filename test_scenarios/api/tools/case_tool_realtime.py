import ipaddress

from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, StationModes, RouteTypes, RouteIds

options_path = 'test_scenarios.form_confirmation.nat'
backup_name = 'default_config.txt'


class ApiRealtimeToolCase(CustomTestCase):
    """Get realtime data from controller and station test case (data is NOT confirmed). MF hub + star station"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.24'
    __execution_time__ = 95  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.controllers, cls.stations = test_api.get_uhp_controllers_stations(1, ['UHP200', 'UHP200X'], 1, ['ANY', ])

        test_options = test_api.get_options(options_path)
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        cls.mf_hub_uhp = cls.controllers[0].get('web_driver')
        cls.stn_uhp = cls.stations[0].get('web_driver')

        net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        tp = nms_api.create(net, 'teleport', {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0, 'sat_name': 's'})
        cls.mf_hub = nms_api.create(net, 'controller', {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
            'device_ip': cls.controllers[0].get('device_ip'),
            'device_vlan': cls.controllers[0].get('device_vlan'),
            'device_gateway': cls.controllers[0].get('device_gateway'),
            'uhp_model': cls.controllers[0].get('model'),
            'stn_number': 2040,  # setting number of stations to its maximum value to check the output of stations
            'tx_on': True,
            'tx_level': test_options.get('tx_level'),
        },
        )
        vno = nms_api.create(net, 'vno', {'name': 'test_vno'})
        cls.stn = nms_api.create(vno, 'station', {
            'name': 'stn',
            'enable': True,
            'serial': cls.stations[0].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub,
        })
        ser_loc = nms_api.create(net, 'service', {'name': 'local_ser', 'stn_vlan': cls.stations[0].get('device_vlan')})
        nms_api.create(cls.stn, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': ser_loc,
            'ip': cls.stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        nms_api.create(cls.stn, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': ser_loc,
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': cls.stations[0].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })
        cls.mf_hub_uhp.set_nms_permission(vlan=cls.controllers[0].get('device_vlan'), password='')
        cls.stn_uhp.star_station(params={
            'timeout': 100,
            'rx1_frq': nms_api.get_param(cls.mf_hub, 'tx_frq'),
            'rx1_sr': nms_api.get_param(cls.mf_hub, 'tx_sr'),
            'tx_level': test_options.get('tx_level'),
        })
        for i in range(2038):
            nms_api.create(vno, 'station', {'name': f'stn{i+1}', 'serial': 10000 + i, 'rx_controller': cls.mf_hub})

        # Adding routes to controller to check Routing Realtime output (ticket 8437 - anchor tags)
        ser = nms_api.create(
            'network:0',
            'service',
            {
                'name': 'test_ser',
                'hub_vlan': 206,
                'stn_vlan': 306,
                'ctr_normal': False,
                'ctr_gateway': False,
                'ctr_mesh': False,
                'stn_normal': False,
                'stn_gateway': False,
                'stn_mesh': False,
            }
        )
        next_route = ipaddress.IPv4Address('172.16.0.0')
        next_gateway = ipaddress.IPv4Address('192.168.0.1')
        for i in range(2, 50):
            nms_api.create(
                'controller:0',
                'route',
                {
                    'type': RouteTypes.STATIC_ROUTE,
                    'service': ser,
                    'ip': str(next_route + i * 256),
                    'gateway': str(next_gateway + i)
                }
            )

        if not nms_api.wait_up(cls.mf_hub, timeout=45):
            test_api.error('MF hub is not UP')
        if not nms_api.wait_up(cls.stn, timeout=45):
            test_api.error('Star station is not UP')

    def test_controller_realtime(self):
        """Issue all controller get realtime commands specified in frontend"""
        for key, value in nms_api._get_realtime_commands.items():
            with self.subTest(f'Controller Realtime for {value} request'):
                next_real = nms_api.get_realtime(self.mf_hub, value)
                self.assertGreater(len(next_real), 0, msg=f'Empty realtime response for {value}')
                self.assertNotEqual("No reply", next_real)
                self.assertNotEqual("Controller IP address is not defined or controller is not accessible", next_real)

    def test_station_realtime(self):
        """Issue all station get realtime commands specified in frontend"""
        for key, value in nms_api._get_realtime_commands.items():
            with self.subTest(f'Station Realtime for {value} request'):
                next_real = nms_api.get_realtime(self.stn, value)
                if value in ('show stat', 'show st rf 0', 'show st tr 0'):
                    self.assertEqual(0, len(next_real), msg=f'Non-empty reply for {value} in station')
                else:
                    self.assertGreater(len(next_real), 0, msg=f'Empty realtime response for {value}')
                self.assertNotEqual("No reply", next_real)
                self.assertNotEqual("Controller IP address is not defined or controller is not accessible", next_real)

    def test_stations(self):
        self.mf_hub = 'controller:0'
        for realtime_req in ('stations', 'stations rf', 'stations tr'):
            with self.subTest(f'Checking {realtime_req} realtime command output'):
                stations = nms_api.get_realtime(self.mf_hub, realtime_req)
                next_stn_num = 1
                for next_line in stations.strip('\r\n').split('\r\n'):
                    if next_line.startswith('Stn'):
                        continue
                    self.assertTrue(
                        next_line.startswith(str(next_stn_num)),
                        msg=f'Next line expected startswith {next_stn_num}, got {next_line}'
                    )
                    next_stn_num += 1

    def test_routing(self):
        """Getting Controller Routing Realtime to make sure that there are no anchor tags (ticket 8437)"""
        routing_table = nms_api.get_realtime(self.mf_hub, 'routing')
        self.assertEqual(
            -1,
            routing_table.lower().find('<a href='),
            msg=f'Anchor tag(s) exists in Routing Realtime output'
        )
