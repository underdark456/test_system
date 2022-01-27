import time

from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import StationModes, RouteTypes, RouteIds

options_path = 'test_scenarios.sr.SR_one_teleport_cases'
backup_name = 'default_config.txt'


class SrConnectionSettingsCase(CustomTestCase):
    """Check connection settings to attach different controllers"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.26'
    __execution_time__ = 310  # approximate case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        controllers, stations = test_api.get_uhp_controllers_stations(4, ['UHP200'], 2, ['ANY', ])
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
            'tx_level': test_options.get('stations_tx_lvl')
        })
        station2_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': test_options.get('stations_tx_lvl')
        })
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        network = nms_api.create('nms:0', 'network', test_options.get('network'))
        nms_api.create(network, 'teleport', test_options.get('teleport'))
        nms_api.create(network, 'sr_license', test_options.get('lic_hub'))
        nms_api.create(network, 'sr_license', test_options.get('lic_inr'))
        vno = nms_api.create(network, 'vno', {'name': 'vno_test'})
        cls.mf_hub = nms_api.create(network, 'controller', test_options.get('mf_hub'))
        cls.inroute = nms_api.create(network, 'controller', test_options.get('inroute'))
        sr_controller = nms_api.create(network, 'sr_controller', test_options.get('sr_controller'))
        sr_teleport = nms_api.create(sr_controller, 'sr_teleport', test_options.get('sr_teleport'))
        cls.device1 = nms_api.create(sr_teleport, 'device', test_options.get('device1'))
        nms_api.update(cls.device1, {
            'ip': controllers[0].get('device_ip'),
            'gateway': controllers[0].get('device_gateway'),
            'vlan': controllers[0].get('device_vlan'),
            'dem2_connect': '0',
            'tx_level_adj': '5'
        })
        cls.device2 = nms_api.create(sr_teleport, 'device', test_options.get('device2'))
        nms_api.update(cls.device2, {
            'ip': controllers[1].get('device_ip'),
            'gateway': controllers[1].get('device_gateway'),
            'vlan': controllers[1].get('device_vlan'),
            'dem2_connect': '0',
            'tx_level_adj': '-3'
        })
        cls.device3 = nms_api.create(sr_teleport, 'device', test_options.get('device3'))
        nms_api.update(cls.device3, {
            'ip': controllers[2].get('device_ip'),
            'gateway': controllers[2].get('device_gateway'),
            'vlan': controllers[2].get('device_vlan'),
            'mod_connect': '2'
        })
        cls.device4 = nms_api.create(sr_teleport, 'device', test_options.get('device4'))
        nms_api.update(cls.device4, {
            'ip': controllers[3].get('device_ip'),
            'gateway': controllers[3].get('device_gateway'),
            'vlan': controllers[3].get('device_vlan'),
            'mod_connect': '2'}
        )
        nms_api.update(cls.mf_hub, {
            'binding': '2',
            'sr_controller': sr_controller,
            'sr_priority': '0',
            'dyn_license': '1',
            'license_group': '1'
        }
                       )
        nms_api.update(cls.inroute, {
            'binding': '2',
            'sr_controller': sr_controller,
            'sr_priority': '2',
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
            'stn_vlan': controllers[0].get('device_vlan')
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
        state3 = nms_api.get_param(cls.device3, 'state')
        state4 = nms_api.get_param(cls.device4, 'state')

        if not (state1 == 'Up' and state2 == 'Redundant' and
                nms_api.get_param(cls.device1, 'controller') == 'controller:0 test_ctrl') and not \
                (state1 == 'Redundant' and state2 == 'Up' and
                 nms_api.get_param(cls.device2, 'controller') == 'controller:0 test_ctrl'):
            test_api.error('Controller Hub is not in Up state')

        if not (state3 == 'Up' and state4 == 'Redundant' and
                nms_api.get_param(cls.device3, 'controller') == 'controller:1 test_ctrl_Inr') and not \
                (state3 == 'Redundant' and state4 == 'Up' and
                 nms_api.get_param(cls.device4, 'controller') == 'controller:1 test_ctrl_Inr'):
            test_api.error('Controller Inroute is not in Up state')

        if not nms_api.wait_up(station1, timeout=45) or not nms_api.wait_up(station2, timeout=45):
            test_api.error('One of the stations is not Up')
        nms_api.wait_ticks(3)

    def test_sr_connection_settings(self):
        controller1 = 'controller:0 test_ctrl'
        controller2 = 'controller:1 test_ctrl_Inr'
        # Find device with controller MF-Hub
        hub_up_device, hub_red_device, ip_hub_A, ip_hub_B = \
            self.find_active_device(self.device1, self.device2, controller1)

        # Find device with controller Inroute
        inr_up_device, inr_red_device, ip_inr_A, ip_inr_B = \
            self.find_active_device(self.device3, self.device4, controller2)

        tx_lvl_nms = nms_api.get_param(self.mf_hub, 'tx_level')
        tx_lvl_adj = nms_api.get_param(hub_up_device, 'tx_level_adj')

        mf_hub_request_A = UhpRequestsDriver(ip_hub_A)
        tx_lvl_uhp = mf_hub_request_A.get_modulator_stats()['set_lvl']
        tx_lvl = - (tx_lvl_nms - tx_lvl_adj)
        tx_lvl = str(tx_lvl)

        if not tx_lvl == tx_lvl_uhp:
            test_api.fail(self, 'Wrong tx level on UHP')

        self.ctrl_telnet = UhpTelnetDriver(ip_hub_A)
        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station 1 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.3.1', vlan=206):
            self.fail(f'Station 2 does not respond to ICMP echo requests!')
        self.ctrl_telnet.close()
        self.ctrl_telnet = None

        mf_hub_request_A.set_modulator_on_off(tx_on=False)
        time.sleep(45)

        if not nms_api.wait_log_message(inr_red_device, 'Up'):
            test_api.fail(self, 'There are no expected log messages')

        # Find device with controller MF-Hub
        hub_up_device, hub_red_device, ip_hub_A, ip_hub_B = \
            self.find_active_device(self.device1, self.device2, controller1)

        # Find device with controller Inroute
        inr_up_device, inr_red_device, ip_inr_A, ip_inr_B = \
            self.find_active_device(self.device3, self.device4, controller2)

        tx_lvl_nms = nms_api.get_param(self.mf_hub, 'tx_level')
        tx_lvl_adj = nms_api.get_param(hub_up_device, 'tx_level_adj')

        mf_hub_request_A = UhpRequestsDriver(ip_hub_A)
        tx_lvl_uhp = mf_hub_request_A.get_modulator_stats()['set_lvl']
        tx_lvl = - (tx_lvl_nms - tx_lvl_adj)
        tx_lvl = str(tx_lvl)

        if not tx_lvl == tx_lvl_uhp:
            test_api.fail(self, 'Wrong tx level on UHP')

        self.ctrl_telnet = UhpTelnetDriver(ip_hub_A)
        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.3.1', vlan=206):
            self.fail(f'Station does not respond to ICMP echo requests!')

    def tear_down(self):
        if self.ctrl_telnet is not None:
            self.ctrl_telnet.close()

    def find_active_device(self, sr_device1, sr_device2, controller):
        # find active device
        if nms_api.get_param(sr_device1, 'state') == 'Up' and \
                nms_api.get_param(sr_device1, 'controller') == controller:
            ip_address_A = nms_api.get_param(sr_device1, 'ip')
            ip_address_B = nms_api.get_param(sr_device2, 'ip')
            state_up_device = sr_device1
            state_red_device = sr_device2
        elif nms_api.get_param(sr_device2, 'state') == 'Up' and \
                nms_api.get_param(sr_device2, 'controller') == controller:
            ip_address_A = nms_api.get_param(sr_device2, 'ip')
            ip_address_B = nms_api.get_param(sr_device1, 'ip')
            state_up_device = sr_device2
            state_red_device = sr_device1
        else:
            self.fail('Devices statuses are unexpected')

        return state_up_device, state_red_device, ip_address_A, ip_address_B
