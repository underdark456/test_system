from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
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

options_path = 'test_scenarios.sr.SR_set_up_cases'
backup_name = 'default_config.txt'


class SrSetUpMfCase(CustomTestCase):
    """Set up Star topology in Smart Redundancy. 2 Devices, 4 Stations"""

    __author__ = 'vpetuhova'
    __version__ = '0.1'
    __review__ = 'dkudryashov'
    __execution_time__ = 250  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        cls.system_options = OptionsProvider.get_system_options(options_path)

        # set config default on UHPs
        cls.devices, cls.stations = OptionsProvider.get_uhp_controllers_stations(
            2,
            ['UHP200', ],
            4,
            ['ANY'],
        )

        cls.nms = Nms(cls.driver, 0, 0)

        # connect Device1
        cls.uhp1 = cls.devices[0].get('web_driver')
        cls.uhp1.set_nms_permission(
            vlan=cls.devices[0].get('device_vlan'),
            password=cls.options.get('network').get('dev_password'),
        )

        # connect Device2
        cls.uhp2 = cls.devices[1].get('web_driver')
        cls.uhp2.set_nms_permission(
            vlan=cls.devices[1].get('device_vlan'),
            password=cls.options.get('network').get('dev_password'),
        )

        # configuring profiles at stations
        cls.st0 = cls.stations[0].get('web_driver')
        cls.st0.star_station(params={
            'rx1_frq': cls.options.get('controller_MF').get('tx_frq'),
            'rx1_sr': cls.options.get('controller_MF').get('tx_sr'),
            'tx_level': cls.options.get('tx_level'),
        })

        cls.st1 = cls.stations[1].get('web_driver')
        cls.st1.star_station(params={
            'rx1_frq': cls.options.get('controller_MF').get('tx_frq'),
            'rx1_sr': cls.options.get('controller_MF').get('tx_sr'),
            'tx_level': cls.options.get('tx_level'),
        })

        cls.st2 = cls.stations[2].get('web_driver')
        cls.st2.star_station(params={
            'rx1_frq': cls.options.get('controller_MF').get('tx_frq'),
            'rx1_sr': cls.options.get('controller_MF').get('tx_sr'),
            'tx_level': cls.options.get('tx_level'),
        })

        cls.st3 = cls.stations[3].get('web_driver')
        cls.st3.star_station(params={
            'rx1_frq': cls.options.get('controller_MF').get('tx_frq'),
            'rx1_sr': cls.options.get('controller_MF').get('tx_sr'),
            'tx_level': cls.options.get('tx_level'),
        })

    def test_SR_set_up_MF(self):
        net = Network.create(self.driver, 0, self.options.get('network'))
        Teleport.create(self.driver, net.get_id(), self.options.get('teleport'))
        sr_ctrl = SrController.create(self.driver, net.get_id(), self.options.get('SR_controller'))
        sr_teleport = SrTeleport.create(self.driver, sr_ctrl.get_id(), self.options.get('SR_teleport'))
        sr_device1 = Device.create(self.driver, sr_teleport.get_id(), self.options.get('Device1'))
        sr_device2 = Device.create(self.driver, sr_teleport.get_id(), self.options.get('Device2'))

        sr_device1.send_params({
            'ip': self.devices[0].get('device_ip'),
            'vlan': self.devices[0].get('device_vlan'),
            'gateway': self.devices[0].get('device_gateway'),
        })
        sr_device2.send_params({
            'ip': self.devices[1].get('device_ip'),
            'vlan': self.devices[1].get('device_vlan'),
            'gateway': self.devices[1].get('device_gateway'),
        })

        SrLicense.create(self.driver, net.get_id(), self.options.get('lic_hub'))
        ctrl = Controller.create(self.driver, net.get_id(), self.options.get('controller_MF'))
        ctrl.send_params({
            'binding': '2',
            'sr_controller': f'sr_controller: {sr_ctrl.get_id()}',
            'tx_on': '1',
            'tx_level': self.options.get('tx_level'),
            'no_stn_check': '1',
            'dyn_license': '1',
            'license_group': '1'
        })
        sr_ctrl.send_param('enable', True)

        if not ctrl.wait_up(timeout=240):
            raise NmsControlledModeException('Timeout! Controller is not in UP state')

        vno_test = Vno.create(self.driver, net.get_id(), {'name': 'vno_test'})
        stn1 = Station.create(self.driver, vno_test.get_id(), {
            'name': f'Station1',
            'serial': self.stations[0].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{ctrl.get_id()}'
        })
        stn2 = Station.create(self.driver, vno_test.get_id(), {
            'name': f'Station2',
            'serial': self.stations[1].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{ctrl.get_id()}'
        })
        stn3 = Station.create(self.driver, vno_test.get_id(), {
            'name': f'Station3',
            'serial': self.stations[2].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{ctrl.get_id()}'
        })
        stn4 = Station.create(self.driver, vno_test.get_id(), {
            'name': f'Station4',
            'serial': self.stations[3].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{ctrl.get_id()}'
        })

        ser = Service.create(self.driver, net.get_id(), {
            'name': 'Local',
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
        StationRoute.create(self.driver, stn1.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{service.get_id()}',
            'ip': '192.168.2.1'
        })
        StationRoute.create(self.driver, stn2.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{service.get_id()}',
            'ip': '192.168.3.1'
        })
        StationRoute.create(self.driver, stn3.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{service.get_id()}',
            'ip': '192.168.4.1'
        })
        StationRoute.create(self.driver, stn4.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{service.get_id()}',
            'ip': '192.168.5.1'
        })
        ControllerRoute.create(self.driver, ctrl.get_id(), {
            'type': RouteTypes.NETWORK_RX,
            'service': f'service:{service.get_id()}'
        })

        # local routing
        StationRoute.create(self.driver, stn1.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': self.stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(self.driver, stn1.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{ser.get_id()}',
            'gateway': self.stations[0].get('device_gateway'),
            'mask': '/0',
            'ip': '0.0.0.0',
            'id': RouteIds.PRIVATE,
        })
        stn1.send_param('enable', True)
        stn_up_timeout = 45
        if not stn1.wait_up(timeout=stn_up_timeout):
            self.fail(f'Station 1 is not UP after {stn_up_timeout} seconds')

        StationRoute.create(self.driver, stn2.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': self.stations[1].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(self.driver, stn2.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{ser.get_id()}',
            'gateway': self.stations[1].get('device_gateway'),
            'mask': '/0',
            'ip': '0.0.0.0',
            'id': RouteIds.PRIVATE,
        })
        stn2.send_param('enable', True)
        if not stn2.wait_up(timeout=stn_up_timeout):
            self.fail(f'Station 2 is not UP after {stn_up_timeout} seconds')

        StationRoute.create(self.driver, stn3.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': self.stations[2].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(self.driver, stn3.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{ser.get_id()}',
            'gateway': self.stations[2].get('device_gateway'),
            'mask': '/0',
            'ip': '0.0.0.0',
            'id': RouteIds.PRIVATE,
        })
        stn3.send_param('enable', True)
        if not stn3.wait_up(timeout=stn_up_timeout):
            self.fail(f'Station 3 is not UP after {stn_up_timeout} seconds')

        StationRoute.create(self.driver, stn4.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': self.stations[3].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(self.driver, stn4.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{ser.get_id()}',
            'gateway': self.stations[3].get('device_gateway'),
            'mask': '/0',
            'ip': '0.0.0.0',
            'id': RouteIds.PRIVATE,
        })
        stn4.send_param('enable', True)
        if not stn4.wait_up(timeout=stn_up_timeout):
            self.fail(f'Station 4 is not UP after {stn_up_timeout} seconds')

        self.nms.wait_next_tick()
        self.nms.wait_next_tick()
        self.nms.wait_next_tick()

        # checking SR devices statuses
        state1 = sr_device1.get_param('state')
        state2 = sr_device2.get_param('state')

        if not (state1 == 'Up' and state2 == 'Redundant') and not (state2 == 'Up' and state1 == 'Redundant'):
            self.fail('Fault state! One of the device must be UP while another one is redundant')

        # to check the availability of stations
        if sr_device1.get_param('state') == 'Up':
            ip_address = sr_device1.get_param('ip')
        elif sr_device2.get_param('state') == 'Up':
            ip_address = sr_device2.get_param('ip')
        else:  # ?????????? ???? ???????????? ????????, ???????? ???????????????????? ?????? ??????????
            self.error('None of the devices in UP state')
            ip_address = None

        self.ctrl_telnet = UhpTelnetDriver(ip_address)
        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station 1 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.3.1', vlan=206):
            self.fail(f'Station 2 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.4.1', vlan=206):
            self.fail(f'Station 3 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.5.1', vlan=206):
            self.fail(f'Station 4 does not respond to ICMP echo requests!')

    def tear_down(self):
        if self.ctrl_telnet is not None:
            self.ctrl_telnet.close()
