import time
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import RouteTypes, CheckboxStr, StationModes, RouteIds
from src.exceptions import NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.device import Device
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.sr_controller import SrController
from src.nms_entities.basic_entities.sr_license import SrLicense
from src.nms_entities.basic_entities.sr_teleport import SrTeleport
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.sr.SR_one_teleport_cases'
backup_name = 'default_config.txt'


class SrSwitchModOffCase(CustomTestCase):
    """Check switching MF hub controller to another device when the modulator is turned off. 2 devices, 2 stations"""

    __author__ = 'vpetuhova'
    __version__ = '0.1'
    __execution_time__ = 1660  # approximate case execution time in seconds
    dev1_telnet = None
    dev2_telnet = None

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.nms = Nms(cls.driver, 0, 0)

        cls.options = OptionsProvider.get_options(options_path)
        cls.devices, cls.stations = OptionsProvider.get_uhp_controllers_stations(2, ['UHP200', ], 2, ['ANY', ])
        cls.device1_uhp = cls.devices[0].get('web_driver')
        cls.device2_uhp = cls.devices[1].get('web_driver')
        cls.stn1_uhp = cls.stations[0].get('web_driver')
        cls.stn2_uhp = cls.stations[1].get('web_driver')

        # connect Device1
        cls.device1_uhp.set_nms_permission(
            vlan=cls.devices[0].get('device_vlan'),
            password=cls.options.get('network').get('dev_password'))

        # connect Device2
        cls.device2_uhp.set_nms_permission(
            vlan=cls.devices[1].get('device_vlan'),
            password=cls.options.get('network').get('dev_password')
        )

        # configuring profiles at stations
        cls.stn1_uhp.star_station(params={
            'rx1_sr': cls.options.get('mf_hub').get('tx_sr'),
            'rx1_frq': cls.options.get('mf_hub').get('tx_frq'),
            'tx_level': cls.options.get('stations_tx_lvl'),
        })
        cls.stn2_uhp.star_station(params={
            'rx1_sr': cls.options.get('mf_hub').get('tx_sr'),
            'rx1_frq': cls.options.get('mf_hub').get('tx_frq'),
            'tx_level': cls.options.get('stations_tx_lvl'),
        })

    def test_SR_switch_modOff(self):

        net = Network.create(self.driver, 0, self.options.get('network'))
        Teleport.create(self.driver, net.get_id(), self.options.get('teleport'))
        sr_ctrl = SrController.create(self.driver, net.get_id(), self.options.get('sr_controller'))
        sr_teleport = SrTeleport.create(self.driver, sr_ctrl.get_id(), self.options.get('sr_teleport'))
        dev1 = Device.create(self.driver, sr_teleport.get_id(), self.options.get('device1'))
        dev2 = Device.create(self.driver, sr_teleport.get_id(), self.options.get('device2'))

        dev1.send_params({
            'ip': self.devices[0].get('device_ip'),
            'gateway': self.devices[0].get('device_gateway'),
            'vlan': self.devices[0].get('device_vlan'),
        })
        dev2.send_params({
            'ip': self.devices[1].get('device_ip'),
            'gateway': self.devices[1].get('device_gateway'),
            'vlan': self.devices[1].get('device_vlan'),
        })

        SrLicense.create(self.driver, net.get_id(), self.options.get('lic_hub'))
        ctrl = Controller.create(self.driver, net.get_id(), self.options.get('mf_hub'))
        ctrl.send_params({
            'binding': '2',
            'sr_controller': f'sr_controller: {sr_ctrl.get_id()}',
            'dyn_license': '1',
            'license_group': '1'
        })
        sr_ctrl.send_param('enable', True)

        if not ctrl.wait_up(timeout=240):
            raise NmsControlledModeException('Controller is not in UP state')

        vno_test = Vno.create(self.driver, net.get_id(), {'name': 'vno_test'})
        station_0 = Station.create(self.driver, vno_test.get_id(), {
            'name': f'Station1',
            'serial': self.stations[0].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{ctrl.get_id()}'
        })
        station_1 = Station.create(self.driver, vno_test.get_id(), {
            'name': f'Station2',
            'serial': self.stations[1].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{ctrl.get_id()}'
        })

        ser = Service.create(self.driver, net.get_id(), {
            'name': 'local',
            'stn_vlan': self.stations[0].get('device_vlan')
        })

        # service and routing for ping
        service = Service.create(self.driver, 0, {'name': 'ping_service', 'hub_vlan': 206, 'stn_vlan': 306,
                                                  'stn_normal': CheckboxStr.ON, })
        ControllerRoute.create(self.driver, ctrl.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{service.get_id()}',
            'ip': '192.168.1.1'
        })
        StationRoute.create(self.driver, station_0.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{service.get_id()}',
            'ip': '192.168.2.1'
        })
        StationRoute.create(self.driver, station_1.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{service.get_id()}',
            'ip': '192.168.3.1'
        })
        ControllerRoute.create(self.driver, ctrl.get_id(), {
            'type': RouteTypes.NETWORK_RX,
            'service': f'service:{service.get_id()}'
        })

        # local routing
        StationRoute.create(self.driver, station_0.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': self.stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })

        StationRoute.create(self.driver, station_0.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:0',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': self.stations[0].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })
        station_0.send_param('enable', True)
        if not station_0.wait_up():
            self.fail('Station 1 is not UP')

        StationRoute.create(self.driver, station_1.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': self.stations[1].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(self.driver, station_1.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:0',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': self.stations[1].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })
        station_1.send_param('enable', True)
        if not station_1.wait_up():
            self.fail('Station 2 is not UP')

        sr_device1 = Device(self.driver, 0, 0)
        sr_device2 = Device(self.driver, 0, 1)

        self.dev1_telnet = UhpTelnetDriver(sr_device1.get_param('ip'))
        self.dev2_telnet = UhpTelnetDriver(sr_device2.get_param('ip'))

        number_of_iterations = 10
        for i in range(number_of_iterations):
            self.info(f'Iteration {i + 1} out of {number_of_iterations}')
            # check SR devices statuses
            state1 = sr_device1.get_param('state')
            state2 = sr_device2.get_param('state')

            states = [state1, state2]

            # if not (state1 == 'Up' and state2 == 'Redundant') and not (state2 == 'Up' and state1 == 'Redundant'):
            if states.count('Up') != 1 and states.count('Redundant') != 1:
                self.fail(f'Devices states should be Up and Redundant, current states {state1} and {state2}')

            state_up_device, state_red_device, ip_address_A, ip_address_B = \
                self.find_active_device(sr_device1, sr_device2)

            ctrl_request_A = UhpRequestsDriver(ip_address_A)
            ctrl_request_B = UhpRequestsDriver(ip_address_B)
            # modulator off on active device
            ctrl_request_A.set_modulator_on_off(tx_on=False)

            if not state_up_device.wait_state('Down'):
                self.fail('Device is not Down after setting its modulator off')

            ctrl_request_B.wait_operation_state()
            time.sleep(60)

            if not state_red_device.wait_up():
                self.fail('Redundant device is not in UP state')

            time.sleep(30)
            if not station_0.wait_up():
                self.fail('Station 1 is not UP after switching to redundant device')
            if not station_1.wait_up():
                self.fail('Station 2 is not UP after switching to redundant device')

            self.nms.wait_next_tick()
            self.nms.wait_next_tick()

            # to check the availability of stations
            if sr_device1.get_param('state') == 'Up':
                # ip_address = sr_device1.get_param('ip')
                ctrl_telnet = self.dev1_telnet
            elif sr_device2.get_param('state') == 'Up':
                # ip_address = sr_device2.get_param('ip')
                ctrl_telnet = self.dev2_telnet
            else:  # Этого не должно быть, если предыдущий код верен
                self.error('None of the devices is in UP state')
                ctrl_telnet = None

            if not ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
                self.fail(f'Station 1 does not respond to ICMP echo requests!')
            if not ctrl_telnet.ping(ip_address='192.168.3.1', vlan=206):
                self.fail(f'Station 2 does not respond to ICMP echo requests!')

    def tear_down(self):
        if self.dev1_telnet is not None:
            self.dev1_telnet.close()
        if self.dev2_telnet is not None:
            self.dev2_telnet.close()

    @staticmethod
    def find_active_device(sr_device1, sr_device2):
        # find active device
        if sr_device1.get_param('state') == 'Up':
            ip_address_A = sr_device1.get_param('ip')
            ip_address_B = sr_device2.get_param('ip')
            state_up_device = sr_device1
            state_red_device = sr_device2
        else:
            ip_address_A = sr_device2.get_param('ip')
            ip_address_B = sr_device1.get_param('ip')
            state_up_device = sr_device2
            state_red_device = sr_device1
        return state_up_device, state_red_device, ip_address_A, ip_address_B
