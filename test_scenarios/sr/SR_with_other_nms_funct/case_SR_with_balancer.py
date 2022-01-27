from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import StationModes, RouteTypes, CheckboxStr

options_path = 'test_scenarios.sr.SR_with_other_nms_funct'
backup_name = 'default_config.txt'


class SrWithBalancerCase(CustomTestCase):
    """The test to check that SR works with Balancer"""

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        controllers, stations = test_api.get_uhp_controllers_stations(3, ['UHP200'], 3, ['ANY', ])
        test_options = test_api.get_options(options_path)

        device1_uhp = controllers[0].get('web_driver')
        device2_uhp = controllers[1].get('web_driver')
        device3_uhp = controllers[2].get('web_driver')
        station1_uhp = stations[0].get('web_driver')
        station2_uhp = stations[1].get('web_driver')
        station3_uhp = stations[2].get('web_driver')

        device1_uhp.set_nms_permission(vlan=controllers[0].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        device2_uhp.set_nms_permission(vlan=controllers[1].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        device3_uhp.set_nms_permission(vlan=controllers[2].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        station1_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': test_options.get('tx_level')
        })
        station2_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': test_options.get('tx_level')
        })
        station3_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': test_options.get('tx_level')
        })
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        network = nms_api.create('nms:0', 'network', test_options.get('network'))
        nms_api.create(network, 'teleport', test_options.get('teleport1'))
        nms_api.create(network, 'sr_license', test_options.get('lic_hub'))
        vno = nms_api.create(network, 'vno', {'name': 'vno_test'})
        cls.mf_hub = nms_api.create(network, 'controller', test_options.get('mf_hub'))
        cls.inroute = nms_api.create(network, 'controller', test_options.get('inroute'))
        cls.sr_controller = nms_api.create(network, 'sr_controller', test_options.get('sr_controller'))
        sr_teleport1 = nms_api.create(cls.sr_controller, 'sr_teleport', test_options.get('sr_teleport1'))
        cls.device1 = nms_api.create(sr_teleport1, 'device', test_options.get('device1'))
        nms_api.update(cls.device1, {
            'ip': controllers[0].get('device_ip'),
            'vlan': controllers[0].get('device_vlan'),
            'gateway': controllers[0].get('device_gateway')
        })
        cls.device2 = nms_api.create(sr_teleport1, 'device', test_options.get('device2'))
        nms_api.update(cls.device2, {
            'ip': controllers[1].get('device_ip'),
            'vlan': controllers[1].get('device_vlan'),
            'gateway': controllers[1].get('device_gateway')
        })
        cls.device3 = nms_api.create(sr_teleport1, 'device', test_options.get('device3'))
        nms_api.update(cls.device3, {
            'ip': controllers[2].get('device_ip'),
            'vlan': controllers[2].get('device_vlan'),
            'gateway': controllers[2].get('device_gateway')
        })
        nms_api.update(cls.mf_hub, {
            'binding': '2',
            'sr_controller': cls.sr_controller,
            'sr_priority': '0',
            'dyn_license': '1',
            'license_group': '1'
        }
                       )
        nms_api.update(cls.inroute, {
            'binding': '2',
            'sr_controller': cls.sr_controller,
            'sr_priority': '2',
            'dyn_license': '1',
            'license_group': '2'
        }
                       )
        nms_api.update(cls.sr_controller, {'enable': '1'})

        station1 = nms_api.create(vno, 'station', {
            'name': f'Station1',
            'serial': stations[0].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub
        }
                                  )
        station2 = nms_api.create(vno, 'station', {
            'name': f'Station2',
            'serial': stations[1].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub
        })
        station3 = nms_api.create(vno, 'station', {
            'name': f'Station3',
            'serial': stations[2].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.inroute
        })

        service_local = nms_api.create(network, 'service', {
            'name': 'Local',
            'stn_vlan': controllers[0].get('device_vlan')
        })

        nms_api.create(station1, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_local,
            'ip': stations[0].get('device_ip'),
            'id': '3'
        })

        nms_api.create(station1, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_local,
            'ip': '0.0.0.0',
            'gateway': stations[0].get('device_gateway'),
            'mask': '/0',
            'id': '3'
        })
        nms_api.create(station2, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_local,
            'ip': stations[1].get('device_ip'),
            'id': '3'
        })

        nms_api.create(station2, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_local,
            'ip': '0.0.0.0',
            'gateway': stations[1].get('device_gateway'),
            'mask': '/0',
            'id': '3'
        })
        nms_api.create(station3, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_local,
            'ip': stations[2].get('device_ip'),
            'id': '3'
        })

        nms_api.create(station3, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_local,
            'ip': '0.0.0.0',
            'gateway': stations[2].get('device_gateway'),
            'mask': '/0',
            'id': '3'
        })

        # create routing to check stations availability
        service_ping = nms_api.create(network, 'service', test_options.get('service_ping'))

        nms_api.create(cls.mf_hub, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.1.1'
        })
        nms_api.create(station1, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.2.1'
        })
        nms_api.create(station2, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.3.1'
        })
        nms_api.create(station3, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.4.1'
        })
        nms_api.create(cls.mf_hub, 'route', {
            'type': RouteTypes.NETWORK_RX,
            'service': service_ping
        })
        nms_api.create(cls.inroute, 'route', {
            'type': RouteTypes.NETWORK_RX,
            'service': service_ping
        })
        nms_api.create(cls.inroute, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.1.2'
        })
        nms_api.create(cls.inroute, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_ping,
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': '192.168.1.1'
        })

        nms_api.update(station1, {'enable': '1'})
        nms_api.update(station2, {'enable': '1'})
        nms_api.update(station3, {'enable': '1'})

        if not nms_api.wait_up(cls.mf_hub, timeout=240):
            test_api.error('Controller MF hub is not in UP state')

        state1 = nms_api.get_param(cls.device1, 'state')
        state2 = nms_api.get_param(cls.device2, 'state')
        state3 = nms_api.get_param(cls.device3, 'state')

        if not nms_api.wait_up(station1) or not nms_api.wait_up(station2) or not nms_api.wait_up(station3):
            test_api.error('One of the stations is not Up')

        if not (state1 == 'Up' and state2 == 'Up' and state3 == 'Redundant') \
                and not (state1 == 'Redundant' and state2 == 'Up' and state3 == 'Up') \
                and not (state1 == 'Up' and state2 == 'Redundant' and state3 == 'Up'):
            test_api.error('Controllers are not in UP state')

    def test_sr_with_balancer(self):

        nms_api.create('network:0', 'bal_controller',
                       {'name': 'balancer', 'enable': CheckboxStr.ON, 'free_down': CheckboxStr.ON})
        nms_api.update(self.mf_hub, {'bal_enable': CheckboxStr.ON,
                                     'bal_controller': 'bal_controller:0',
                                     'max_load': '1000'})
        nms_api.update(self.inroute, {'bal_enable': CheckboxStr.ON,
                                      'bal_controller': 'bal_controller:0'})

        ip_station_hub = nms_api.get_param('route:0', 'ip')
        ip_station_inroute = nms_api.get_param('route:4', 'ip')

        station_1_request = UhpRequestsDriver(ip_station_hub)
        station_3_request = UhpRequestsDriver(ip_station_inroute)

        station_1_request.traffic_generator({'enabled': 1, 'vlan': 3006,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 500, 'pps_to': 500,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        station_3_request.traffic_generator({'enabled': 1, 'vlan': 3006,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 500, 'pps_to': 500,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        # Find device with controller Inroute
        controller1 = 'controller:0 test_ctrl'
        controller2 = 'controller:1 test_ctrl_Inr'
        state_up_device, ip_address_A = \
            self.find_active_device(self.device1, self.device2, self.device3, controller2)

        device_request_inr = UhpRequestsDriver(ip_address_A)

        # Change password on device with Inroute
        device_request_inr.set_nms_permission(vlan=nms_api.get_param('device:0', 'vlan'), password='hjhjfull')

        if not nms_api.wait_log_message('sr_controller:0', 'Teleport reconfigured'):
            test_api.fail(self, 'There are no expected log messages')

        # Wait controller Inroute Up
        if not nms_api.wait_up(self.inroute, timeout=240):
            test_api.fail(self, 'Controller Inroute is not in UP state after switching')

        # Check rx controller on station
        if not nms_api.get_param('station:2', 'rx_controller') == 'controller:1 test_ctrl_Inr':
            test_api.fail(self, 'Station switched by balancer')

        state1 = nms_api.get_param(self.device1, 'state')
        state2 = nms_api.get_param(self.device2, 'state')
        state3 = nms_api.get_param(self.device3, 'state')

        if not (state1 == 'Up' and state2 == 'Unreachable' and state3 == 'Up') \
                and not (state1 == 'Up' and state2 == 'Up' and state3 == 'Unreachable') \
                and not (state1 == 'Unreachable' and state2 == 'Up' and state3 == 'Up'):
            test_api.fail(self, 'Devices states are unexpected')

        # Find device with controller MF-Hub
        hub_up_device, ip_address_hub = \
            self.find_active_device(self.device1, self.device2, self.device3, controller1)

        # Ping stations on Hub
        ctrl_telnet = UhpTelnetDriver(ip_address_hub)

        # Set right password for device
        device_request_inr.set_nms_permission(vlan=nms_api.get_param('device:0', 'vlan'), monitoring=True, control=True,
                                              password=nms_api.get_param('network:0', 'dev_password'))

        if not nms_api.wait_up('station:2', timeout=60):
            test_api.fail(self, 'Station on Inroute is not in Up state')

        if not ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station1 does not respond to ICMP echo requests!')
        if not ctrl_telnet.ping(ip_address='192.168.3.1', vlan=206):
            self.fail(f'Station2 does not respond to ICMP echo requests!')
        if not ctrl_telnet.ping(ip_address='192.168.4.1', vlan=206):
            self.fail(f'Station3 does not respond to ICMP echo requests!')

    def find_active_device(self, sr_device1, sr_device2, sr_device3, controller):
        # find active device
        if nms_api.get_param(sr_device1, 'state') == 'Up' \
                and nms_api.get_param(sr_device1, 'controller') == controller:
            ip_address_A = nms_api.get_param(sr_device1, 'ip')
            state_up_device = sr_device1
        elif nms_api.get_param(sr_device2, 'state') == 'Up' \
                and nms_api.get_param(sr_device2, 'controller') == controller:
            ip_address_A = nms_api.get_param(sr_device2, 'ip')
            state_up_device = sr_device2
        elif nms_api.get_param(sr_device3, 'state') == 'Up' \
                and nms_api.get_param(sr_device3, 'controller') == controller:
            ip_address_A = nms_api.get_param(sr_device3, 'ip')
            state_up_device = sr_device3
        else:
            self.fail('Devices statuses are unexpected')

        return state_up_device, ip_address_A
