import time

from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import StationModes, RouteTypes, RouteIds, Checkbox
from src.nms_entities.basic_entities.device import Device

options_path = 'test_scenarios.sr.SR_two_teleports_cases'
backup_name = 'default_config.txt'


class SrOwnCnMinCase(CustomTestCase):
    """Check teleport switching due to Low_own_CN fault"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.26'
    __review__ = 'dkudryashov'
    __execution_time__ = 400  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        controllers, stations = test_api.get_uhp_controllers_stations(2, ['UHP200', ], 1, ['ANY', ])
        test_options = test_api.get_options(options_path)

        device1_uhp = controllers[0].get('web_driver')
        device2_uhp = controllers[1].get('web_driver')
        station1_uhp = stations[0].get('web_driver')

        device1_uhp.set_nms_permission(vlan=controllers[0].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        device2_uhp.set_nms_permission(vlan=controllers[1].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        station1_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': test_options.get('tx_level')
        })
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
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
        cls.device2 = nms_api.create(sr_teleport2, 'device', test_options.get('device2'))
        nms_api.update(cls.device2, {
            'ip': controllers[1].get('device_ip'),
            'vlan': controllers[1].get('device_vlan'),
            'gateway': controllers[1].get('device_gateway'),
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

        if not nms_api.wait_up(cls.mf_hub, timeout=240):
            test_api.error('Controller MF hub is not in UP state')

        station1 = nms_api.create(vno, 'station', {
            'name': f'Station1',
            'serial': stations[0].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub
        })
        station2 = nms_api.create(vno, 'station', {
            'name': f'Station2',
            'serial': '125',
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
        nms_api.create(cls.mf_hub, 'route', {
            'type': RouteTypes.NETWORK_RX,
            'service': service_ping
        })

        nms_api.update(station1, {'enable': '1'})
        nms_api.update(station2, {'enable': '1'})

        state1 = nms_api.get_param(cls.device1, 'state')
        state2 = nms_api.get_param(cls.device2, 'state')

        states = [state1, state2]
        if not (states.count('Up') == 1 and states.count('Redundant') == 1):
            test_api.error(f'Devices\' states should be Up and Redundant, current states {state1} and {state2}')

        if not nms_api.wait_up(station1, timeout=45):
            test_api.error('Station is not Up')
        nms_api.wait_ticks(3)

    def test_sr_own_cn_min(self):
        state1 = nms_api.get_param(self.device1, 'state')
        state2 = nms_api.get_param(self.device2, 'state')
        nms_api.update(self.sr_controller, {'check_cn': Checkbox.ON, 'own_cn_min': '30'})

        time.sleep(80)
        if not nms_api.get_param(self.sr_controller, 'tp_fail_code') == 'Low_own_CN':
            test_api.fail(self, 'There is no fail code `Low_own_CN` in SR controller')
        time.sleep(20)

        if not nms_api.wait_log_message('sr_controller:0', 'Teleport reconfigured'):
            test_api.fail(self, 'There is no expected log message `Teleport reconfigured` in SR controller')

        time.sleep(60)
        state11 = nms_api.get_param(self.device1, 'state')
        state22 = nms_api.get_param(self.device2, 'state')

        # Device states have been changed
        if state1 != state22 or state2 != state11:
            test_api.fail(self, 'There was no teleport switching')

        nms_api.update(self.sr_controller, {'check_cn': Checkbox.OFF})
        # Find device with controller MF-Hub
        state_up_device, state_red_device, ip_address_a, ip_address_b = \
            self.find_active_device(self.device1, self.device2)

        time.sleep(20)
        self.ctrl_telnet = UhpTelnetDriver(ip_address_a)
        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station does not respond to ICMP echo requests!')

    def tear_down(self):
        if self.ctrl_telnet is not None:
            self.ctrl_telnet.close()

    def find_active_device(self, sr_device1, sr_device2):
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
        else:
            self.fail('Devices statuses are unexpected')

        return state_up_device, state_red_device, ip_address_a, ip_address_b
