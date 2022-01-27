import time

from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import StationModes, RouteTypes, RouteIds

options_path = 'test_scenarios.sr.SR_one_teleport_cases'
backup_name = 'default_config.txt'


class SrSamePriorityCase(CustomTestCase):
    """Check that controllers with the same priorities do not switch"""

    __author__ = 'Valentina Petuhova'
    __version__ = '4.0.0.21'
    __execution_time__ = 130  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        devices, stations = test_api.get_uhp_controllers_stations(2, ['UHP200', ], 2, ['ANY', ])
        cls.test_options = test_api.get_options(options_path)

        device1_uhp = devices[0].get('web_driver')
        device2_uhp = devices[1].get('web_driver')
        station1_uhp = stations[0].get('web_driver')
        station2_uhp = stations[1].get('web_driver')

        device1_uhp.set_nms_permission(vlan=devices[0].get('device_vlan'),
                                       password=cls.test_options.get('network').get('dev_password'))
        device2_uhp.set_nms_permission(vlan=devices[1].get('device_vlan'),
                                       password=cls.test_options.get('network').get('dev_password'))
        station1_uhp.star_station(params={
            'rx1_sr': cls.test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': cls.test_options.get('mf_hub').get('tx_frq'),
            'tx_level': cls.test_options.get('stations_tx_lvl')
        })
        station2_uhp.star_station(params={
            'rx1_sr': cls.test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': cls.test_options.get('mf_hub').get('tx_frq'),
            'tx_level': cls.test_options.get('stations_tx_lvl')
        })
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        network = nms_api.create('nms:0', 'network', cls.test_options.get('network'))
        nms_api.create(network, 'teleport', cls.test_options.get('teleport'))
        nms_api.create(network, 'sr_license', cls.test_options.get('lic_hub'))
        nms_api.create(network, 'sr_license', cls.test_options.get('lic_inr'))
        vno = nms_api.create(network, 'vno', {'name': 'vno_test'})
        cls.mf_hub = nms_api.create(network, 'controller', cls.test_options.get('mf_hub'))
        cls.inroute = nms_api.create(network, 'controller', cls.test_options.get('inroute'))
        sr_controller = nms_api.create(network, 'sr_controller', cls.test_options.get('sr_controller'))
        sr_teleport = nms_api.create(sr_controller, 'sr_teleport', cls.test_options.get('sr_teleport'))
        cls.device1 = nms_api.create(sr_teleport, 'device', cls.test_options.get('device1'))
        nms_api.update(cls.device1, {
            'ip': devices[0].get('device_ip'),
            'gateway': devices[0].get('device_gateway'),
            'vlan': devices[0].get('device_vlan'),
        })
        cls.device2 = nms_api.create(sr_teleport, 'device', cls.test_options.get('device2'))
        nms_api.update(cls.device2, {
            'ip': devices[1].get('device_ip'),
            'gateway': devices[1].get('device_gateway'),
            'vlan': devices[1].get('device_vlan'),
        })
        nms_api.update(cls.mf_hub, {
            'binding': '2',
            'sr_controller': sr_controller,
            'sr_priority': '0',
            'dyn_license': '1',
            'license_group': '1',
            'tx_level': cls.test_options.get('tx_level')
        }
                       )
        nms_api.update(cls.inroute, {
            'binding': '2',
            'sr_controller': sr_controller,
            'sr_priority': '0',
            'dyn_license': '1',
            'license_group': '2'
        }
                       )
        nms_api.update(sr_controller, {'enable': '1'})

        if not nms_api.wait_up(cls.inroute, timeout=240):
            test_api.error('Controller is not in UP state')

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
            'rx_controller': cls.inroute
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
        service_ping = nms_api.create(network, 'service', cls.test_options.get('service_ping'))

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

        state1 = nms_api.get_param(cls.device1, 'state')
        state2 = nms_api.get_param(cls.device2, 'state')

        if not (state1 == 'Up' and state2 == 'Up'):
            test_api.error('Devices states are not expected, should be both Up')

        if not nms_api.wait_up(station1) or not nms_api.wait_up(station2):
            test_api.error('One of the stations is not Up')

        nms_api.wait_ticks(3)

    def test_sr_same_priority(self):
        controller1 = nms_api.get_param(self.device1, 'controller')
        controller2 = nms_api.get_param(self.device2, 'controller')
        nms_api.update(self.mf_hub, {
            'sr_priority': '5',
        })
        nms_api.update(self.inroute, {
            'sr_priority': '5',
        })
        state_up_device, state_red_device, ip_address_A, ip_address_B = \
            self.find_active_device(self.device1, self.device2)

        ctrl_request_A = UhpRequestsDriver(ip_address_A)
        ctrl_request_A.set_modulator_on_off(tx_on=False)

        time.sleep(120)
        controller11 = nms_api.get_param(self.device1, 'controller')
        controller22 = nms_api.get_param(self.device2, 'controller')
        state1 = nms_api.get_param(self.device1, 'state')
        state2 = nms_api.get_param(self.device2, 'state')

        if not (controller1 == controller11 and controller2 == controller22) or not (
                state1 == 'Down' and state2 == 'Down'):
            test_api.fail(self, 'Switching with the same priority controllers after setting modulator OFF in MF hub')

        ctrl_request_A.set_modulator_on_off(tx_on=True, tx_level=self.test_options.get('tx_level'))
        time.sleep(60)

        controller13 = nms_api.get_param(self.device1, 'controller')
        controller23 = nms_api.get_param(self.device2, 'controller')
        state1 = nms_api.get_param(self.device1, 'state')
        state2 = nms_api.get_param(self.device2, 'state')

        if not (controller1 == controller13 and controller2 == controller23) or not (
                state1 == 'Up' and state2 == 'Up'):
            test_api.fail(self, 'Switching with the same priority controllers after setting modulator ON in MF hub')

        self.ctrl_telnet = UhpTelnetDriver(ip_address_A)
        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.3.1', vlan=206):
            self.fail(f'Station does not respond to ICMP echo requests!')

    def tear_down(self):
        if self.ctrl_telnet is not None:
            self.ctrl_telnet.close()

    def find_active_device(self, sr_device1, sr_device2):
        # find active device
        if nms_api.get_param(sr_device1, 'state') == 'Up' \
                and nms_api.get_param(sr_device1, 'controller') == 'controller:0 test_ctrl':
            ip_address_A = nms_api.get_param(sr_device1, 'ip')
            ip_address_B = nms_api.get_param(sr_device2, 'ip')
            state_up_device = sr_device1
            state_red_device = sr_device2
        elif nms_api.get_param(sr_device2, 'state') == 'Up' \
                and nms_api.get_param(sr_device2, 'controller') == 'controller:0 test_ctrl':
            ip_address_A = nms_api.get_param(sr_device2, 'ip')
            ip_address_B = nms_api.get_param(sr_device1, 'ip')
            state_up_device = sr_device2
            state_red_device = sr_device1
        else:
            self.fail('Devices statuses are unexpected')
        return state_up_device, state_red_device, ip_address_A, ip_address_B
