import time

from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.enum_types_constants import StationModes, RouteTypes, RouteIds, Checkbox
from src.nms_entities.basic_entities.device import Device

options_path = 'test_scenarios.sr.SR_dynamic_licenses'
backup_name = 'default_config.txt'


class SrDynLicDeleteCase(CustomTestCase):
    """Check that dynamic licenses is removed from uhp after deleted in NMS"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.27'
    __review__ = 'dkudryashov'
    __execution_time__ = 200  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        controllers, stations = test_api.get_uhp_controllers_stations(
            2,
            ['UHP200', ],
            2,
            ['ANY', ],
        )
        cls.test_options = test_api.get_options(options_path)

        device1_uhp = controllers[0].get('web_driver')
        device2_uhp = controllers[1].get('web_driver')
        station1_uhp = stations[0].get('web_driver')
        station2_uhp = stations[1].get('web_driver')

        device1_uhp.set_nms_permission(
            vlan=controllers[0].get('device_vlan'),
            password=cls.test_options.get('network').get('dev_password')
        )
        device2_uhp.set_nms_permission(
            vlan=controllers[1].get('device_vlan'),
            password=cls.test_options.get('network').get('dev_password')
        )
        station1_uhp.star_station(params={
            'rx1_sr': cls.test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': cls.test_options.get('mf_hub').get('tx_frq'),
            'tx_level': cls.test_options.get('tx_level')
        })
        station2_uhp.star_station(params={
            'rx1_sr': cls.test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': cls.test_options.get('mf_hub').get('tx_frq'),
            'tx_level': cls.test_options.get('tx_level')
        })
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        cls.network = nms_api.create('nms:0', 'network', cls.test_options.get('network'))
        nms_api.create(cls.network, 'teleport', cls.test_options.get('teleport1'))
        # nms_api.create(cls.network, 'sr_license', cls.test_options.get('lic_hub'))
        # nms_api.create(cls.network, 'sr_license', cls.test_options.get('lic_inr'))
        nms_api.create(cls.network, 'sr_license', cls.test_options.get('lic_damahub'))
        vno = nms_api.create(cls.network, 'vno', {'name': 'vno_test'})
        cls.mf_hub = nms_api.create(cls.network, 'controller', cls.test_options.get('mf_hub'))
        cls.inroute = nms_api.create(cls.network, 'controller', cls.test_options.get('inroute'))
        sr_controller = nms_api.create(cls.network, 'sr_controller', cls.test_options.get('sr_controller'))
        sr_teleport = nms_api.create(sr_controller, 'sr_teleport', cls.test_options.get('sr_teleport1'))
        cls.device1 = nms_api.create(sr_teleport, 'device', cls.test_options.get('device1'))
        nms_api.update(cls.device1, {
            'ip': controllers[0].get('device_ip'),
            'gateway': controllers[0].get('device_gateway'),
            'vlan': controllers[0].get('device_vlan'),
        })
        cls.device2 = nms_api.create(sr_teleport, 'device', cls.test_options.get('device2'))
        nms_api.update(cls.device2, {
            'ip': controllers[1].get('device_ip'),
            'gateway': controllers[1].get('device_gateway'),
            'vlan': controllers[0].get('device_vlan'),
        }
        )
        nms_api.update(cls.mf_hub, {
            'binding': '2',
            'sr_controller': sr_controller,
            'sr_priority': '0',
            'dyn_license': '1',
            'license_group': '1',
            'tx_level': cls.test_options.get('tx_level'),
        })
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

        cls.station1 = nms_api.create(vno, 'station', {
            'name': f'Station1',
            'serial': stations[0].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub
        })
        cls.station2 = nms_api.create(vno, 'station', {
            'name': f'Station2',
            'serial': stations[1].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.inroute
        })

        service_local = nms_api.create(cls.network, 'service', {
            'name': 'Local',
            'stn_vlan': stations[0].get('device_vlan')
        })

        nms_api.create(cls.station1, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_local,
            'ip': stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })

        nms_api.create(cls.station1, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_local,
            'ip': '0.0.0.0',
            'gateway': stations[0].get('device_gateway'),
            'mask': '/0',
            'id': RouteIds.PRIVATE,
        })
        nms_api.create(cls.station2, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_local,
            'ip': stations[1].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })

        nms_api.create(cls.station2, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_local,
            'ip': '0.0.0.0',
            'gateway': stations[1].get('device_gateway'),
            'mask': '/0',
            'id': RouteIds.PRIVATE,
        })

        # create routing to check stations availability
        service_ping = nms_api.create(cls.network, 'service', cls.test_options.get('service_ping'))

        nms_api.create(cls.mf_hub, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.1.1'
        })
        nms_api.create(cls.station1, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.2.1'
        })
        nms_api.create(cls.station2, 'route', {
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

        nms_api.update(cls.station1, {'enable': Checkbox.ON})
        nms_api.update(cls.station2, {'enable': Checkbox.ON})

    def test_sr_dyn_lic_delete(self):
        controller1 = 'controller:0 test_ctrl'
        controller2 = 'controller:1 test_ctrl_Inr'
        for i in range(1, 11):
            self.info(f'Create/delete iteration #{i}')
            lic_hub = nms_api.create(self.network, 'sr_license', self.test_options.get('lic_hub'))
            lic_inr = nms_api.create(self.network, 'sr_license', self.test_options.get('lic_inr'))
            time.sleep(20)
            self.assertTrue(nms_api.wait_up(self.mf_hub, timeout=60), msg=f'MF Hub is not UP')
            self.assertTrue(nms_api.wait_up(self.inroute, timeout=60), msg=f'Inroute is not UP')
            self.assertTrue(nms_api.wait_up(self.station1), msg=f'Station 1 is not UP')
            self.assertTrue(nms_api.wait_up(self.station2), msg=f'Station 2 is not UP')
            state1 = nms_api.get_param(self.device1, 'state')
            state2 = nms_api.get_param(self.device2, 'state')
            self.assertEqual(state1, Device.UP, msg=f'Device 1 is not UP')
            self.assertEqual(state2, Device.UP, msg=f'Device 2 is not UP')

            hub_up_device, ip_address_hub = \
                self.find_active_device(self.device1, self.device2, controller1)
            inr_up_device, ip_address_inr = \
                self.find_active_device(self.device1, self.device2, controller2)
            device_request_hub = UhpRequestsDriver(ip_address_hub)
            device_request_inr = UhpRequestsDriver(ip_address_inr)
            nms_opt_hub = nms_api.get_sr_license_options(lic_hub)
            nms_opt_inr = nms_api.get_sr_license_options(lic_inr)
            # print(nms_opt_hub, nms_opt_inr)
            self.assertTrue(self.wait_nms_options(device_request_hub, nms_opt_hub),
                            msg=f'MF Hub has not got NMS options withing timeout')
            self.assertTrue(self.wait_nms_options(device_request_inr, nms_opt_inr),
                            msg=f'MF Hub has not got NMS options withing timeout')

            nms_api.delete(lic_hub)
            nms_api.delete(lic_inr)
            time.sleep(20)

            uhp_opt_hub = device_request_hub.get_uhp_options()
            uhp_opt_hub1 = uhp_opt_hub.replace("S2", "")
            uhp_opt_inr = device_request_inr.get_uhp_options()

            if uhp_opt_hub1.startswith('(NMS)Options:'):
                test_api.fail(self, f'Dynamic license was not deleted from MF hub, current UHP options: {uhp_opt_hub1}')
            if uhp_opt_hub1 == nms_opt_hub:
                test_api.fail(self, f'Current UHP options: {uhp_opt_hub1} should not be equal to {nms_opt_hub}')

            if uhp_opt_inr.startswith('(NMS)Options:'):
                test_api.fail(self, f'Dynamic license was not deleted from Inroute, current UHP options: {uhp_opt_inr}')
            if uhp_opt_inr == nms_opt_inr:
                test_api.fail(self, f'Current UHP options: {uhp_opt_inr} should not be equal to {nms_opt_inr}')

    def find_active_device(self, sr_device1, sr_device2, controller):
        # find active device
        if nms_api.get_param(sr_device1, 'controller') == controller:
            ip_address_a = nms_api.get_param(sr_device1, 'ip')
            state_up_device = sr_device1
        elif nms_api.get_param(sr_device2, 'controller') == controller:
            ip_address_a = nms_api.get_param(sr_device2, 'ip')
            state_up_device = sr_device2
        else:
            self.fail('Devices statuses are unexpected')

        return state_up_device, ip_address_a

    @staticmethod
    def wait_nms_options(uhp_driver, nms_options, timeout=30, step_timeout=5):
        st_time = time.time()
        while True:
            uhp_opt = uhp_driver.get_uhp_options()
            uhp_opt = uhp_opt.replace("S2", "")
            # print(uhp_opt, nms_options)
            if uhp_opt.startswith('(NMS)Options:') and uhp_opt.lstrip('(NMS)Options:').strip() == nms_options.strip():
                return True
            if st_time + timeout < time.time():
                return False
            time.sleep(step_timeout)
