import time

from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import StationModes, RouteTypes, CheckboxStr, RouteIds, Checkbox
from src.nms_entities.basic_entities.device import Device

options_path = 'test_scenarios.sr.SR_two_teleports_cases'
backup_name = 'default_config.txt'


class SrMaxSwFailsCase(CustomTestCase):
    """Check teleport switching due max_sw_fails fault"""

    __author__ = 'vpetuhova'
    __version__ = '0.1'
    __review__ = 'dkudryashov'
    __execution_time__ = None  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        controllers, stations = test_api.get_uhp_controllers_stations(4, ['UHP200', ], 2, ['ANY', ])
        test_options = test_api.get_options(options_path)

        device1_uhp = controllers[0].get('web_driver')
        device2_uhp = controllers[1].get('web_driver')
        device3_uhp = controllers[2].get('web_driver')
        device4_uhp = controllers[3].get('web_driver')
        station1_uhp = stations[0].get('web_driver')
        station2_uhp = stations[1].get('web_driver')

        device1_uhp.set_nms_permission(vlan=controllers[0].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        device2_uhp.set_nms_permission(vlan=controllers[1].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        device3_uhp.set_nms_permission(vlan=controllers[2].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        device4_uhp.set_nms_permission(vlan=controllers[3].get('device_vlan'),
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
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        # Setting NMS requests timeout to 10 seconds
        nms_api.set_timeout(10)
        nms_api.load_config(backup_name)

        network = nms_api.create('nms:0', 'network', test_options.get('network'))
        nms_api.create(network, 'teleport', test_options.get('teleport1'))
        nms_api.create(network, 'teleport', test_options.get('teleport2'))
        nms_api.create(network, 'sr_license', test_options.get('lic_hub'))
        vno = nms_api.create(network, 'vno', {'name': 'vno_test'})
        cls.mf_hub = nms_api.create(network, 'controller', test_options.get('mf_hub'))
        cls.sr_controller = nms_api.create(network, 'sr_controller', test_options.get('sr_controller'))
        sr_teleport1 = nms_api.create(cls.sr_controller, 'sr_teleport', test_options.get('sr_teleport1'))
        sr_teleport2 = nms_api.create(cls.sr_controller, 'sr_teleport', test_options.get('sr_teleport2'))
        cls.device1 = nms_api.create(sr_teleport1, 'device', test_options.get('device1'))
        nms_api.update(cls.device1, {
            'ip': controllers[0].get('device_ip'),
            'vlan': controllers[0].get('device_vlan'),
            'gateway': controllers[0].get('device_gateway'),
        })
        cls.device2 = nms_api.create(sr_teleport1, 'device', test_options.get('device2'))
        nms_api.update(cls.device2, {
            'ip': controllers[1].get('device_ip'),
            'vlan': controllers[1].get('device_vlan'),
            'gateway': controllers[1].get('device_gateway'),
        })
        cls.device3 = nms_api.create(sr_teleport2, 'device', test_options.get('device3'))
        nms_api.update(cls.device3, {
            'ip': controllers[2].get('device_ip'),
            'vlan': controllers[2].get('device_vlan'),
            'gateway': controllers[2].get('device_gateway'),
        })
        cls.device4 = nms_api.create(sr_teleport2, 'device', test_options.get('device4'))
        nms_api.update(cls.device4, {
            'ip': controllers[3].get('device_ip'),
            'vlan': controllers[3].get('device_vlan'),
            'gateway': controllers[3].get('device_gateway')
        })
        nms_api.update(cls.mf_hub, {
            'binding': '2',
            'sr_controller': cls.sr_controller,
            'sr_priority': '0',
            'dyn_license': '1',
            'license_group': '1',
            'tx_level': test_options.get('tx_level'),
        })
        nms_api.update(cls.sr_controller, {'enable': '1'})

        if not nms_api.wait_up(cls.mf_hub, timeout=300):
            test_api.error('Controller MF hub is not in UP state')

        station1 = nms_api.create(vno, 'station', {
            'name': f'Station1',
            'serial': stations[0].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub
        })
        station2 = nms_api.create(vno, 'station', {
            'name': f'Station2',
            'serial': stations[1].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub
        })

        service_local = nms_api.create(network, 'service', {
            'name': 'Local',
            'stn_vlan': stations[0].get('device_vlan')
        })

        nms_api.create(station1, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_local,
            'ip': stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })

        nms_api.create(station1, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_local,
            'ip': '0.0.0.0',
            'gateway': stations[0].get('device_gateway'),
            'mask': '/0',
            'id': RouteIds.PRIVATE,
        })
        nms_api.create(station2, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_local,
            'ip': stations[1].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })

        nms_api.create(station2, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_local,
            'ip': '0.0.0.0',
            'gateway': stations[1].get('device_gateway'),
            'mask': '/0',
            'id': RouteIds.PRIVATE,
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
        nms_api.create(cls.mf_hub, 'route', {
            'type': RouteTypes.NETWORK_RX,
            'service': service_ping
        })

        nms_api.update(station1, {'enable': Checkbox.ON})
        nms_api.update(station2, {'enable': Checkbox.ON})

        states = [
            nms_api.get_param(cls.device1, 'state'),
            nms_api.get_param(cls.device2, 'state'),
            nms_api.get_param(cls.device3, 'state'),
            nms_api.get_param(cls.device4, 'state'),
        ]
        if states.count('Up') != 1 or states.count('Redundant') != 3:
            test_api.error(f'Devices\' states are unexpected: {states[0]}, {states[1]}, {states[2]}, {states[3]},')

        if not nms_api.wait_up(station1) or not nms_api.wait_up(station2):
            test_api.error('One of the stations or both is not Up')
        nms_api.wait_ticks(3)

    def test_sr_max_sw_fails(self):

        nms_api.update(
            self.sr_controller,
            {'check_ctr': CheckboxStr.OFF, 'check_sw_fails': CheckboxStr.ON, 'max_sw_fails': '3'}
        )

        # Find device with controller MF-Hub and the second device in teleport
        state_up_device, state_red_device, ip_address_a, ip_address_b = \
            self.find_active_device(self.device1, self.device2, self.device3, self.device4)

        device_request_a = UhpRequestsDriver(ip_address_a)
        device_request_b = UhpRequestsDriver(ip_address_b)

        device_request_b.set_nms_permission(vlan=nms_api.get_param('device:0', 'vlan'), monitoring=True, control=False,
                                            password=nms_api.get_param('network:0', 'dev_password'))

        device_request_a.reboot()
        time.sleep(10)
        device_request_a.set_nms_permission(vlan=nms_api.get_param('device:0', 'vlan'), monitoring=True, control=False,
                                            password=nms_api.get_param('network:0', 'dev_password'))

        # Wait 3 fail switches
        for i in range(3):
            if not nms_api.wait_log_message('sr_controller:0', 'Teleport reconfigured'):
                test_api.fail(self, 'There is no expected log message `Teleport reconfigured`')

        time.sleep(10)
        if not nms_api.get_param(self.sr_controller, 'tp_fail_code') == 'Failed_switches':
            test_api.fail(self, 'There is no fail code `Failed_switches` on teleport')

        # Wait controller Up
        if not nms_api.wait_up(self.mf_hub, timeout=240):
            test_api.fail(self, 'Controller MF hub is not in UP state')

        # Find device with controller MF-Hub and the second device in teleport
        state_up_device, state_red_device, ip_address_a, ip_address_b = \
            self.find_active_device(self.device1, self.device2, self.device3, self.device4)

        if not nms_api.wait_up('station:0') or not nms_api.wait_up('station:1'):
            test_api.error('One of the stations is not Up after switching to another SR teleport')

        # Ping stations
        self.ctrl_telnet = UhpTelnetDriver(ip_address_a)
        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station1 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.3.1', vlan=206):
            self.fail(f'Station2 does not respond to ICMP echo requests!')

    def tear_down(self):
        if self.ctrl_telnet is not None:
            self.ctrl_telnet.close()

    def find_active_device(self, sr_device1, sr_device2, sr_device3, sr_devices4):
        # find active device
        if nms_api.get_param(sr_device1, 'state') == Device.UP:
            ip_address_a = nms_api.get_param(sr_device1, 'ip')
            ip_address_b = nms_api.get_param(sr_device2, 'ip')
            state_up_device = sr_device1
            state_red_device = sr_device2
        elif nms_api.get_param(sr_device2, 'state') == Device.UP:
            ip_address_a = nms_api.get_param(sr_device2, 'ip')
            ip_address_b = nms_api.get_param(sr_device1, 'ip')
            state_up_device = sr_device2
            state_red_device = sr_device1
        elif nms_api.get_param(sr_device3, 'state') == Device.UP:
            ip_address_a = nms_api.get_param(sr_device3, 'ip')
            ip_address_b = nms_api.get_param(sr_devices4, 'ip')
            state_up_device = sr_device3
            state_red_device = sr_devices4
        elif nms_api.get_param(sr_devices4, 'state') == Device.UP:
            ip_address_a = nms_api.get_param(sr_devices4, 'ip')
            ip_address_b = nms_api.get_param(sr_device3, 'ip')
            state_up_device = sr_devices4
            state_red_device = sr_devices4
        else:
            self.fail('Devices statuses are unexpected')

        return state_up_device, state_red_device, ip_address_a, ip_address_b
