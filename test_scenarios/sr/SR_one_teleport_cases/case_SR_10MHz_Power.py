import time

from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import StationModes, RouteTypes, RouteIds

options_path = 'test_scenarios.sr.SR_one_teleport_cases'
backup_name = 'default_config.txt'


class Sr10MhzPowerCase(CustomTestCase):
    """Check site setup settings in a network under SR ctrl"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.22'
    __execution_time__ = 430  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        uhp_options = test_api.get_uhp_by_model('UHP200', number=4)
        test_options = test_api.get_options(options_path)

        device1_uhp = uhp_options[0].get('web_driver')
        device2_uhp = uhp_options[1].get('web_driver')
        device3_uhp = uhp_options[2].get('web_driver')
        station1_uhp = uhp_options[3].get('web_driver')

        device1_uhp.set_nms_permission(vlan=uhp_options[0].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        device2_uhp.set_nms_permission(vlan=uhp_options[1].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        device3_uhp.set_nms_permission(vlan=uhp_options[1].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        station1_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': test_options.get('stations_tx_lvl')
        })

        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        network = nms_api.create('nms:0', 'network', test_options.get('network'))
        nms_api.create(network, 'teleport', test_options.get('teleport'))
        nms_api.create(network, 'sr_license', test_options.get('lic_hub'))
        vno = nms_api.create(network, 'vno', {'name': 'vno_test'})
        mf_hub = nms_api.create(network, 'controller', test_options.get('mf_hub'))
        sr_controller = nms_api.create(network, 'sr_controller', test_options.get('sr_controller'))
        sr_teleport = nms_api.create(sr_controller, 'sr_teleport', test_options.get('sr_teleport'))
        nms_api.update(sr_teleport,
                       {'tx_10m': '1',
                        'tx_dc_power': '1',
                        'rx_10m': '1',
                        'rx_dc_power': '1'
                        })
        cls.device1 = nms_api.create(sr_teleport, 'device', test_options.get('device1'))
        nms_api.update(cls.device1, {
            'ip': uhp_options[0].get('device_ip'),
            'gateway': uhp_options[0].get('device_gateway'),
            'vlan': uhp_options[0].get('device_vlan'),
            'mod_power': '1',
            'mod_ref': '1',
            'dem1_power': '1',
            'dem1_ref': '1'
        })
        cls.device2 = nms_api.create(sr_teleport, 'device', test_options.get('device2'))
        nms_api.update(cls.device2, {
            'ip': uhp_options[1].get('device_ip'),
            'gateway': uhp_options[1].get('device_gateway'),
            'vlan': uhp_options[1].get('device_vlan'),
            'mod_power': '1',
            'mod_ref': '1',
            'dem1_power': '1',
            'dem1_ref': '1'
        })
        cls.device3 = nms_api.create(sr_teleport, 'device', test_options.get('device3'))
        nms_api.update(cls.device3, {
            'ip': uhp_options[2].get('device_ip'),
            'gateway': uhp_options[2].get('device_gateway'),
            'vlan': uhp_options[2].get('device_vlan'),
        })
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
            'serial': uhp_options[3].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': mf_hub
        })

        service_local = nms_api.create(network, 'service', {
            'name': 'Local',
            'stn_vlan': uhp_options[0].get('device_vlan')
        })

        nms_api.create(station1, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_local,
            'ip': uhp_options[3].get('device_ip'),
            'id': RouteIds.PRIVATE
        })

        nms_api.create(station1, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_local,
            'ip': '0.0.0.0',
            'gateway': uhp_options[3].get('device_gateway'),
            'mask': '/0',
            'id': RouteIds.PRIVATE
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
        nms_api.create(mf_hub, 'route', {
            'type': RouteTypes.NETWORK_RX,
            'service': service_ping
        })

        nms_api.update(station1, {'enable': '1'})

        state1 = nms_api.get_param(cls.device1, 'state')
        state2 = nms_api.get_param(cls.device2, 'state')
        state3 = nms_api.get_param(cls.device3, 'state')

        states = [state1, state2, state3]

        if states.count('Up') != 1 and states.count('Redundant') != 2:
            test_api.error('Devices states are not expected')

        if not nms_api.wait_up(station1):
            test_api.error('Station is not Up')
        nms_api.wait_ticks(3)

    def test_sr_10MHz_power(self):

        state_up_device, ip_address = \
            self.find_active_device(self.device1, self.device2, self.device3)

        ctrl_request = UhpRequestsDriver(ip_address)
        site_setup = ctrl_request.get_teleport_values()

        if state_up_device == self.device1 and not (site_setup['rx_dc_power'] == '1'
                                                    and site_setup['rx_10m'] == '1'
                                                    and site_setup['tx_dc_power'] == '1'
                                                    and site_setup['tx_10m'] == '1'):
            test_api.fail(self, 'Site setup settings are incorrect')
        elif state_up_device == self.device2 and not (site_setup['rx_dc_power'] == '1'
                                                      and site_setup['rx_10m'] == '1'
                                                      and site_setup['tx_dc_power'] == '1'
                                                      and site_setup['tx_10m'] == '1'):
            test_api.fail(self, 'Site setup settings are incorrect')
        elif state_up_device == self.device3 and not (site_setup['rx_dc_power'] == '0'
                                                      and site_setup['rx_10m'] == '0'
                                                      and site_setup['tx_dc_power'] == '0'
                                                      and site_setup['tx_10m'] == '0'):
            test_api.fail(self, 'Site setup settings are incorrect')

        self.ctrl_telnet = UhpTelnetDriver(ip_address)
        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station does not respond to ICMP echo requests!')
        self.ctrl_telnet.close()
        self.ctrl_telnet = None

        ctrl_request.set_modulator_on_off(tx_on=False)
        time.sleep(120)

        state_up_device, ip_address = \
            self.find_active_device(self.device1, self.device2, self.device3)

        ctrl_request = UhpRequestsDriver(ip_address)
        site_setup = ctrl_request.get_teleport_values()

        if state_up_device == self.device1 and not (site_setup['rx_dc_power'] == '1'
                                                    and site_setup['rx_10m'] == '1'
                                                    and site_setup['tx_dc_power'] == '1'
                                                    and site_setup['tx_10m'] == '1'):
            test_api.fail(self, 'Site setup settings are incorrect')
        elif state_up_device == self.device2 and not (site_setup['rx_dc_power'] == '1'
                                                      and site_setup['rx_10m'] == '1'
                                                      and site_setup['tx_dc_power'] == '1'
                                                      and site_setup['tx_10m'] == '1'):
            test_api.fail(self, 'Site setup settings are incorrect')
        elif state_up_device == self.device3 and not (site_setup['rx_dc_power'] == '0'
                                                      and site_setup['rx_10m'] == '0'
                                                      and site_setup['tx_dc_power'] == '0'
                                                      and site_setup['tx_10m'] == '0'):
            test_api.fail(self, 'Site setup settings are incorrect')

        self.ctrl_telnet = UhpTelnetDriver(ip_address)
        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station does not respond to ICMP echo requests!')
        self.ctrl_telnet.close()
        self.ctrl_telnet = None

        ctrl_request.set_modulator_on_off(tx_on=False)
        time.sleep(120)

        state_up_device, ip_address = \
            self.find_active_device(self.device1, self.device2, self.device3)

        ctrl_request = UhpRequestsDriver(ip_address)
        site_setup = ctrl_request.get_teleport_values()

        if state_up_device == self.device1 and not (site_setup['rx_dc_power'] == '1'
                                                    and site_setup['rx_10m'] == '1'
                                                    and site_setup['tx_dc_power'] == '1'
                                                    and site_setup['tx_10m'] == '1'):
            test_api.fail(self, 'Site setup settings are incorrect')
        elif state_up_device == self.device2 and not (site_setup['rx_dc_power'] == '1'
                                                      and site_setup['rx_10m'] == '1'
                                                      and site_setup['tx_dc_power'] == '1'
                                                      and site_setup['tx_10m'] == '1'):
            test_api.fail(self, 'Site setup settings are incorrect')
        elif state_up_device == self.device3 and not (site_setup['rx_dc_power'] == '0'
                                                      and site_setup['rx_10m'] == '0'
                                                      and site_setup['tx_dc_power'] == '0'
                                                      and site_setup['tx_10m'] == '0'):
            test_api.fail(self, 'Site setup settings are incorrect')

        self.ctrl_telnet = UhpTelnetDriver(ip_address)
        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station does not respond to ICMP echo requests!')

    def tear_down(self):
        if self.ctrl_telnet is not None:
            self.ctrl_telnet.close()

    def find_active_device(self, sr_device1, sr_device2, sr_device3):
        # find active device
        if nms_api.get_param(sr_device1, 'state') == 'Up':
            ip_address = nms_api.get_param(sr_device1, 'ip')
            state_up_device = sr_device1
        elif nms_api.get_param(sr_device2, 'state') == 'Up':
            ip_address = nms_api.get_param(sr_device2, 'ip')
            state_up_device = sr_device2
        elif nms_api.get_param(sr_device3, 'state') == 'Up':
            ip_address = nms_api.get_param(sr_device3, 'ip')
            state_up_device = sr_device3
        else:
            self.fail('Devices statuses are unexpected')
        return state_up_device, ip_address
