import time

from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import StationModes, RouteTypes, RouteIds

options_path = 'test_scenarios.sr.SR_one_teleport_cases'
backup_name = 'default_config.txt'


class SrDevInaccessCase(CustomTestCase):
    """After a short time of the device inaccessibility the net(MF-Hub+2 stations) under SR ctrl is still in UP state"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.22'
    __execution_time__ = 185  # approximate case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        devices, stations = test_api.get_uhp_controllers_stations(2, ['UHP200', ], 2, ['ANY', ])
        test_options = test_api.get_options(options_path)

        device1_uhp = devices[0].get('web_driver')
        device2_uhp = devices[1].get('web_driver')
        station1_uhp = stations[0].get('web_driver')
        station2_uhp = stations[1].get('web_driver')

        device1_uhp.set_nms_permission(vlan=devices[0].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        device2_uhp.set_nms_permission(vlan=devices[1].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        station1_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': test_options.get('stations_tx_lvl')
        })
        station2_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': test_options.get('stations_tx_lvl')
        })

        network = nms_api.create('nms:0', 'network', test_options.get('network'))
        nms_api.create(network, 'teleport', test_options.get('teleport'))
        nms_api.create(network, 'sr_license', test_options.get('lic_hub'))
        vno = nms_api.create(network, 'vno', {'name': 'vno_test'})
        mf_hub = nms_api.create(network, 'controller', test_options.get('mf_hub'))
        sr_controller = nms_api.create(network, 'sr_controller', test_options.get('sr_controller'))
        sr_teleport = nms_api.create(sr_controller, 'sr_teleport', test_options.get('sr_teleport'))
        cls.device1 = nms_api.create(sr_teleport, 'device', test_options.get('device1'))
        nms_api.update(cls.device1, {
            'ip': devices[0].get('device_ip'),
            'gateway': devices[0].get('device_gateway'),
            'vlan': devices[0].get('device_vlan'),
        })
        cls.device2 = nms_api.create(sr_teleport, 'device', test_options.get('device2'))
        nms_api.update(cls.device2, {
            'ip': devices[1].get('device_ip'),
            'gateway': devices[1].get('device_gateway'),
            'vlan': devices[1].get('device_vlan'),
        }
        )
        nms_api.update(mf_hub, {
            'binding': '2',
            'sr_controller': sr_controller,
            'dyn_license': '1',
            'license_group': '1'
        }
                       )
        nms_api.update(sr_controller, {'enable': '1'})

        if not nms_api.wait_up(mf_hub, timeout=240):
            test_api.error('Controller is not in UP state')

        station1 = nms_api.create(vno, 'station', {
            'name': f'Station1',
            'serial': stations[0].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': mf_hub
        }
                                  )
        station2 = nms_api.create(vno, 'station', {
            'name': f'Station2',
            'serial': stations[1].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': mf_hub
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

        service_ping = nms_api.create(network, 'service', test_options.get('service_ping'))

        nms_api.create(mf_hub, 'route', {
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
        nms_api.create(mf_hub, 'route', {
            'type': RouteTypes.NETWORK_RX,
            'service': service_ping
        })

        nms_api.update(station1, {'enable': '1'})
        nms_api.update(station2, {'enable': '1'})

        state1 = nms_api.get_param(cls.device1, 'state')
        state2 = nms_api.get_param(cls.device2, 'state')

        if not (state1 == 'Up' and state2 == 'Redundant') and not (state2 == 'Up' and state1 == 'Redundant'):
            test_api.error('Devices states are not expected')

        if not nms_api.wait_up(station1) and nms_api.wait_up(station2):
            test_api.error('One of the stations is not Up')
        nms_api.wait_ticks(3)

    def test_sr_no_connect(self):
        state1 = nms_api.get_param(self.device1, 'state')
        state2 = nms_api.get_param(self.device2, 'state')

        state_up_device, state_red_device, ip_address_A, ip_address_B = \
            self.find_active_device(self.device1, self.device2)

        ctrl_request_A = UhpRequestsDriver(ip_address_A)
        ctrl_request_A.set_nms_permission(vlan=nms_api.get_param('device:0', 'vlan'), password='2t56564')
        time.sleep(10)

        ctrl_request_A.set_nms_permission(vlan=nms_api.get_param('device:0', 'vlan'),
                                          password=nms_api.get_param('network:0', 'dev_password'))

        # Waiting 3 ticks to renew devices states
        nms_api.wait_ticks(3)
        state11 = nms_api.get_param(self.device1, 'state')
        state22 = nms_api.get_param(self.device2, 'state')
        if state1 != state11 or state2 != state22:
            test_api.fail(
                self,
                'Devices states have changed after a short period of one of the devices inaccessibility'
            )

        self.ctrl_telnet = UhpTelnetDriver(ip_address_A)
        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station 1 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.3.1', vlan=206):
            self.fail(f'Station 2 does not respond to ICMP echo requests!')

    def tear_down(self):
        if self.ctrl_telnet is not None:
            self.ctrl_telnet.close()

    @staticmethod
    def find_active_device(sr_device1, sr_device2):
        # find active device
        if nms_api.get_param(sr_device1, 'state') == 'Up':
            ip_address_A = nms_api.get_param(sr_device1, 'ip')
            ip_address_B = nms_api.get_param(sr_device2, 'ip')
            state_up_device = sr_device1
            state_red_device = sr_device2
        else:
            ip_address_A = nms_api.get_param(sr_device2, 'ip')
            ip_address_B = nms_api.get_param(sr_device1, 'ip')
            state_up_device = sr_device2
            state_red_device = sr_device1
        return state_up_device, state_red_device, ip_address_A, ip_address_B
