from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import RouteTypes, CheckboxStr, StationModes, RouteIds, Checkbox
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


class SrSetUpMfHubMfInrCase(CustomTestCase):
    """Set up Star topology (MF-Hub + Mf-Inroute) in Smart Redundancy. 3 Devices, 4 Stations"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.26'
    __review__ = 'dkudryashov'
    __execution_time__ = None  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        # set config default on UHPs
        cls.devices, cls.stations = OptionsProvider.get_uhp_controllers_stations(
            3,
            ['UHP200', ],
            4,
            ['ANY', ],
        )

        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        cls.system_options = OptionsProvider.get_system_options(options_path)

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

        # connect Device3
        cls.uhp3 = cls.devices[2].get('web_driver')
        cls.uhp3.set_nms_permission(
            vlan=cls.devices[2].get('device_vlan'),
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

    def test_SR_set_up_MFHubMfInr(self):
        net = Network.create(self.driver, 0, self.options.get('network'))
        Teleport.create(self.driver, net.get_id(), self.options.get('teleport'))
        SrLicense.create(self.driver, net.get_id(), self.options.get('lic_hub'))
        SrLicense.create(self.driver, net.get_id(), self.options.get('lic_inr'))
        sr_ctrl = SrController.create(self.driver, net.get_id(), self.options.get('SR_controller'))
        sr_teleport = SrTeleport.create(self.driver, sr_ctrl.get_id(), self.options.get('SR_teleport'))
        sr_device1 = Device.create(self.driver, sr_teleport.get_id(), self.options.get('Device1'))
        sr_device2 = Device.create(self.driver, sr_teleport.get_id(), self.options.get('Device2'))
        sr_device3 = Device.create(self.driver, sr_teleport.get_id(), self.options.get('Device3'))

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
        sr_device3.send_params({
            'ip': self.devices[2].get('device_ip'),
            'vlan': self.devices[2].get('device_vlan'),
            'gateway': self.devices[2].get('device_gateway'),
        })

        mf_hub = Controller.create(self.driver, net.get_id(), self.options.get('controller_MF'))
        mf_hub.send_params({
            'binding': '2',
            'sr_controller': f'sr_controller: {sr_ctrl.get_id()}',
            'tx_on': '1',
            'tx_level': (46 if self.options.get('tx_level') + 10 > 46 else self.options.get('tx_level') + 10),
            'dyn_license': '1',
            'license_group': '1',
            'mf1_tx': '1000000',
            'mf1_rx': '1000000',
            'mf2_en': Checkbox.ON,
            'mf2_tx': '1002000',
            'mf2_rx': '1002000',
            'mf3_en': Checkbox.ON,
            'mf3_tx': '1004000',
            'mf3_rx': '1004000',
            'mf4_en': Checkbox.ON,
            'mf4_tx': '1006000',
            'mf4_rx': '1006000',
            'mf5_en': Checkbox.ON,
            'mf5_tx': '1008000',
            'mf5_rx': '1008000',
        })

        mf_inroute = Controller.create(self.driver, net.get_id(), self.options.get('MfInroute'))
        mf_inroute.send_params({
            'binding': '2',
            'sr_controller': f'sr_controller: {sr_ctrl.get_id()}',
            'dyn_license': '1',
            'license_group': '2',
        })

        vno_test = Vno.create(self.driver, net.get_id(), {'name': 'vno_test'})
        stn0 = Station.create(self.driver, vno_test.get_id(), {
            'name': f'Station1',
            'serial': self.stations[0].get('serial'),
            'enable': True,
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{mf_hub.get_id()}'
        })
        stn1 = Station.create(self.driver, vno_test.get_id(), {
            'name': f'Station2',
            'serial': self.stations[1].get('serial'),
            'enable': True,
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{mf_hub.get_id()}'
        })
        stn2 = Station.create(self.driver, vno_test.get_id(), {
            'name': f'Station3',
            'serial': self.stations[2].get('serial'),
            'enable': True,
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{mf_hub.get_id()}'
        })
        stn3 = Station.create(self.driver, vno_test.get_id(), {
            'name': f'Station4',
            'serial': self.stations[3].get('serial'),
            'enable': True,
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{mf_hub.get_id()}'
        })
        # Dummy station
        Station.create(self.driver, vno_test.get_id(), {
            'name': 'Fake',
            'serial': '111',
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{mf_hub.get_id()}',
            'enable': True,
        })
        ser = Service.create(self.driver, net.get_id(), {
            'name': 'Local',
            'stn_vlan': self.stations[0].get('device_vlan'),
        })

        # service and routing for ping
        service = Service.create(self.driver, 0, {'name': 'ping_service', 'hub_vlan': 206, 'stn_vlan': 306,
                                                  'stn_normal': CheckboxStr.ON, })
        ControllerRoute.create(self.driver, mf_hub.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{service.get_id()}',
            'ip': '192.168.1.1'
        })
        StationRoute.create(self.driver, stn0.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{service.get_id()}',
            'ip': '192.168.2.1'
        })
        StationRoute.create(self.driver, stn1.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{service.get_id()}',
            'ip': '192.168.3.1'
        })
        StationRoute.create(self.driver, stn2.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{service.get_id()}',
            'ip': '192.168.4.1'
        })
        StationRoute.create(self.driver, stn3.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{service.get_id()}',
            'ip': '192.168.5.1'
        })
        ControllerRoute.create(self.driver, mf_hub.get_id(), {
            'type': RouteTypes.NETWORK_RX,
            'service': f'service:{service.get_id()}'
        })

        # local stations' routes
        StationRoute.create(self.driver, stn0.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': self.stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(self.driver, stn0.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{ser.get_id()}',
            'gateway': self.stations[0].get('device_gateway'),
            'mask': '/0',
            'ip': '0.0.0.0',
            'id': RouteIds.PRIVATE,
        })

        StationRoute.create(self.driver, stn1.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': self.stations[1].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(self.driver, stn1.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{ser.get_id()}',
            'gateway': self.stations[1].get('device_gateway'),
            'mask': '/0',
            'ip': '0.0.0.0',
            'id': RouteIds.PRIVATE,
        })

        StationRoute.create(self.driver, stn2.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': self.stations[2].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(self.driver, stn2.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{ser.get_id()}',
            'gateway': self.stations[2].get('device_gateway'),
            'mask': '/0',
            'ip': '0.0.0.0',
            'id': RouteIds.PRIVATE,
        })

        StationRoute.create(self.driver, stn3.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': self.stations[3].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(self.driver, stn3.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{ser.get_id()}',
            'gateway': self.stations[3].get('device_gateway'),
            'mask': '/0',
            'ip': '0.0.0.0',
            'id': RouteIds.PRIVATE,
        })

        sr_ctrl.send_param('enable', True)
        if not mf_inroute.wait_up(timeout=240):
            raise NmsControlledModeException('Timeout! Controller MFInroute is not in UP state')

        if not stn0.wait_up(timeout=45):
            self.fail('Station 1 is not UP!')

        if not stn1.wait_up(timeout=45):
            self.fail('Station 2 is not UP!')

        if not stn2.wait_up(timeout=45):
            self.fail('Station 3 is not UP!')

        if not stn3.wait_up(timeout=45):
            self.fail('Station 4 is not UP!')

        self.nms.wait_ticks(3)

        # checking SR devices statuses
        state1 = sr_device1.get_param('state')
        state2 = sr_device2.get_param('state')
        state3 = sr_device3.get_param('state')

        states = [state1, state2, state3]

        if states.count(Device.UP) != 2 and states.count(Device.REDUNDANT) != 1:
            self.fail('Fault state! Two of the devices must be UP, while the third one is Redundant')

        # to check the availability of stations
        if sr_device1.get_param('state') == 'Up' and sr_device1.get_param('controller') == 'controller:0 test_ctrl':
            ip_address = sr_device1.get_param('ip')
        elif sr_device2.get_param('state') == 'Up' and sr_device2.get_param('controller') == 'controller:0 test_ctrl':
            ip_address = sr_device2.get_param('ip')
        elif sr_device3.get_param('state') == 'Up' and sr_device3.get_param('controller') == 'controller:0 test_ctrl':
            ip_address = sr_device3.get_param('ip')
        else:  # Этого не должно быть, если предыдущий код верен
            ip_address = None
            self.fail('None of the devices in UP state')

        self.ctrl_telnet = UhpTelnetDriver(ip_address)
        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station1 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.3.1', vlan=206):
            self.fail(f'Station2 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.4.1', vlan=206):
            self.fail(f'Station3 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.5.1', vlan=206):
            self.fail(f'Station4 does not respond to ICMP echo requests!')

    def tear_down(self):
        if self.ctrl_telnet is not None:
            self.ctrl_telnet.close()
