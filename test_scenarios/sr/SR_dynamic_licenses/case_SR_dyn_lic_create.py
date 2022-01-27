from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.enum_types_constants import StationModes, RouteTypes, RouteIds

options_path = 'test_scenarios.sr.SR_dynamic_licenses'
backup_name = 'default_config.txt'


class SrDynLicCreateCase(CustomTestCase):
    """Check that dynamic licenses can be created and attached. 2 Devices (MF hub, Inroute), 2 Star Stations"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.21'
    __review__ = 'dkudryashov'
    __execution_time__ = 180  # approximate test case execution time in seconds
    __express__ = True
    hub_lic = None
    inr_lic = None

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        controllers, stations = test_api.get_uhp_controllers_stations(
            2,
            ['UHP200', ],
            2,
            ['ANY', ]
        )
        test_options = test_api.get_options(options_path)

        device1_uhp = controllers[0].get('web_driver')
        device2_uhp = controllers[1].get('web_driver')
        station1_uhp = stations[0].get('web_driver')
        station2_uhp = stations[1].get('web_driver')

        device1_uhp.set_nms_permission(
            vlan=controllers[0].get('device_vlan'),
            password=test_options.get('network').get('dev_password')
        )
        device2_uhp.set_nms_permission(
            vlan=controllers[1].get('device_vlan'),
            password=test_options.get('network').get('dev_password')
        )
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
        nms_api.load_config(backup_name)

        network = nms_api.create('nms:0', 'network', test_options.get('network'))
        nms_api.create(network, 'teleport', test_options.get('teleport1'))
        cls.hub_lic = nms_api.create(network, 'sr_license', test_options.get('lic_hub'))
        cls.inr_lic = nms_api.create(network, 'sr_license', test_options.get('lic_inr'))
        nms_api.create(network, 'sr_license', test_options.get('lic_damahub'))
        vno = nms_api.create(network, 'vno', {'name': 'vno_test'})
        cls.mf_hub = nms_api.create(network, 'controller', test_options.get('mf_hub'))
        cls.inroute = nms_api.create(network, 'controller', test_options.get('inroute'))
        sr_controller = nms_api.create(network, 'sr_controller', test_options.get('sr_controller'))
        sr_teleport = nms_api.create(sr_controller, 'sr_teleport', test_options.get('sr_teleport1'))
        cls.device1 = nms_api.create(sr_teleport, 'device', test_options.get('device1'))
        nms_api.update(cls.device1, {
            'ip': controllers[0].get('device_ip'),
            'gateway': controllers[0].get('device_gateway'),
            'vlan': controllers[0].get('device_vlan'),
        })
        cls.device2 = nms_api.create(sr_teleport, 'device', test_options.get('device2'))
        nms_api.update(cls.device2, {
            'ip': controllers[1].get('device_ip'),
            'gateway': controllers[1].get('device_gateway'),
            'vlan': controllers[1].get('device_vlan'),
        })
        nms_api.update(cls.mf_hub, {
            'binding': '2',
            'sr_controller': sr_controller,
            'sr_priority': '0',
            'dyn_license': '1',
            'license_group': '1',
            'tx_level': (46 if test_options.get('tx_level') + 10 > 46 else test_options.get('tx_level') + 10)
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
            test_api.error('Controller Inroute is not in UP state')

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

        if not (state1 == 'Up' and state2 == 'Up'):
            test_api.error('Devices states are not expected. Both should be UP')

        if not (nms_api.wait_up(station1) and nms_api.wait_up(station2)):
            test_api.error('One of the stations or both are not Up')

    def test_sr_dyn_lic_create(self):
        # Find device with controller Inroute
        controller1 = 'controller:0 test_ctrl'
        controller2 = 'controller:1 test_ctrl_Inr'

        inr_up_device, ip_address_inr = \
            self.find_active_device(self.device1, self.device2, controller2)

        device_request_inr = UhpRequestsDriver(ip_address_inr)

        uhp_opt_inr = device_request_inr.get_uhp_options()
        nms_opt_inr = nms_api.get_sr_license_options('sr_license:1')

        if not uhp_opt_inr.startswith('(NMS)Options:'):
            test_api.fail(self, f'Dynamic license was not assigned to Inroute, current UHP options: {uhp_opt_inr}')
        if uhp_opt_inr.split('(NMS)Options:')[-1].rstrip().lstrip() != nms_opt_inr:
            test_api.fail(self, f'Expected UHP Inroute dynamic options: {nms_opt_inr}, '
                                f'current UHP options: {uhp_opt_inr}')

        hub_up_device, ip_address_hub = \
            self.find_active_device(self.device1, self.device2, controller1)

        device_request_hub = UhpRequestsDriver(ip_address_hub)
        uhp_opt_hub = device_request_hub.get_uhp_options()
        uhp_opt_hub1 = uhp_opt_hub.replace("S2", "")
        nms_opt_hub = nms_api.get_sr_license_options('sr_license:0')

        if not uhp_opt_hub1.startswith('(NMS)Options:'):
            test_api.fail(self, f'Dynamic license was not assigned to MF hub, current UHP options: {uhp_opt_hub1}')
        if uhp_opt_hub1.split('(NMS)Options:')[-1].rstrip().lstrip() != nms_opt_hub:
            test_api.fail(self, f'Expected UHP MF hub dynamic options: {nms_opt_hub}, '
                                f'current UHP options: {uhp_opt_hub1}')

    def find_active_device(self, sr_device1, sr_device2, controller):
        # find active device
        if nms_api.get_param(sr_device1, 'state') == 'Up' \
                and nms_api.get_param(sr_device1, 'controller') == controller:
            ip_address_A = nms_api.get_param(sr_device1, 'ip')
            state_up_device = sr_device1
        elif nms_api.get_param(sr_device2, 'state') == 'Up' \
                and nms_api.get_param(sr_device2, 'controller') == controller:
            ip_address_A = nms_api.get_param(sr_device2, 'ip')
            state_up_device = sr_device2
        else:
            self.fail('Devices statuses are unexpected')

        return state_up_device, ip_address_A

    @classmethod
    def tear_down_class(cls):
        """Cleaning up assigned licenses"""
        if cls.hub_lic is not None:
            nms_api.delete(cls.hub_lic)
        if cls.inr_lic is not None:
            nms_api.delete(cls.inr_lic)
        nms_api.wait_ticks(2)
