from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import RouteTypes, StationModes, CheckboxStr, DamaAB, RouteIds
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


class SrSetUpDamaCase(CustomTestCase):
    """Set up DAMA topology in Smart Redundancy. 2 Devices, 2 Dama stations"""

    __author__ = 'vpetuhova'
    __review__ = 'dkudryashov'
    __version__ = '0.1'
    __execution_time__ = 190  # approximate case execution time in seconds

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

        cls.devices, cls.stations = OptionsProvider.get_uhp_controllers_stations(2, ['UHP200', ], 2, ['ANY', ])

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

        # configuring profiles at stations and set permissions
        cls.st2 = cls.stations[0].get('web_driver')
        cls.st2.dama_station(params={
            'rx1_sr': cls.options.get('controller_DAMA').get('tx_sr'),
            'rx1_frq': cls.options.get('controller_DAMA').get('tx_frq'),
            'tx_level': cls.options.get('tx_level'),
        })

        cls.st3 = cls.stations[1].get('web_driver')
        cls.st3.dama_station(params={
            'rx1_sr': cls.options.get('controller_DAMA').get('tx_sr'),
            'rx1_frq': cls.options.get('controller_DAMA').get('tx_frq'),
            'tx_level': cls.options.get('tx_level'),
        })

    def test_SR_set_DAMA(self):
        net = Network.create(self.driver, 0, self.options.get('network'))
        Teleport.create(self.driver, net.get_id(), self.options.get('teleport'))
        sr_ctrl = SrController.create(self.driver, net.get_id(), self.options.get('SR_controller'))
        sr_teleport = SrTeleport.create(self.driver, sr_ctrl.get_id(), self.options.get('SR_teleport'))
        SrLicense.create(self.driver, net.get_id(), self.options.get('lic_dama_hub'))
        sr_device1 = Device.create(self.driver, sr_teleport.get_id(), {
            'name': f'Device1',
            'mode': '2',
            'ip': self.devices[0].get('device_ip'),
            'mask': '/24',
            'gateway': self.devices[0].get('device_gateway'),
            'vlan': self.devices[0].get('device_vlan'),
            'dem2_connect': '1'
        })
        sr_device2 = Device.create(self.driver, sr_teleport.get_id(), {
            'name': f'Device2',
            'mode': '2',
            'ip': self.devices[1].get('device_ip'),
            'mask': '/24',
            'gateway': self.devices[1].get('device_gateway'),
            'vlan': self.devices[1].get('device_vlan'),
            'dem2_connect': '1'
        })

        ctrl = Controller.create(self.driver, net.get_id(), self.options.get('controller_DAMA'))
        ctrl.send_params({
            'binding': '2',
            'sr_controller': f'sr_controller: {sr_ctrl.get_id()}',
            'tx_on': '1',
            'tx_level': self.options.get('tx_level'),
            'no_stn_check': '1',
            'dyn_license': '1',
            'license_group': '1'
            }
                    )
        sr_ctrl.send_param('enable', True)

        if not ctrl.wait_up(timeout=240):
            raise NmsControlledModeException('Timeout! Controller is not in UP state')

        vno_test = Vno.create(self.driver, net.get_id(), {'name': 'vno_test'})

        dama_stn1 = Station.create(self.driver, vno_test.get_id(), {
            'name': f'dama_stn1',
            'serial': self.stations[0].get('serial'),
            'mode': StationModes.DAMA,
            'dama_ab': DamaAB.CHANNEL_A,
            'rx_controller': f'controller:{ctrl.get_id()}'
        })
        dama_stn2 = Station.create(self.driver, vno_test.get_id(), {
            'name': f'dama_stn2',
            'serial': self.stations[1].get('serial'),
            'mode': StationModes.DAMA,
            'dama_ab': DamaAB.CHANNEL_B,
            'rx_controller': f'controller:{ctrl.get_id()}'
        })

        ser = Service.create(self.driver, net.get_id(), {
            'name': 'Local',
            'stn_vlan': self.stations[0].get('device_vlan')
        })
        # service and routing for ping
        service = Service.create(self.driver, 0, {'name': 'ping_service', 'hub_vlan': 206, 'stn_vlan': 306,
                                                  'stn_normal': CheckboxStr.ON, })
        ControllerRoute.create(self.driver, ctrl.get_id(),
                               {'type': RouteTypes.IP_ADDRESS, 'service': f'service:{service.get_id()}',
                                'ip': '192.168.1.1'})
        StationRoute.create(self.driver, dama_stn1.get_id(),
                            {'type': RouteTypes.IP_ADDRESS, 'service': f'service:{service.get_id()}',
                             'ip': '192.168.4.1'})
        StationRoute.create(self.driver, dama_stn2.get_id(),
                            {'type': RouteTypes.IP_ADDRESS, 'service': f'service:{service.get_id()}',
                             'ip': '192.168.5.1'})
        ControllerRoute.create(self.driver, ctrl.get_id(),
                               {'type': RouteTypes.NETWORK_RX, 'service': f'service:{service.get_id()}'})

        # Local routes
        StationRoute.create(self.driver, dama_stn1.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': self.stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(self.driver, dama_stn1.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{ser.get_id()}',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': self.stations[0].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })
        dama_stn1.send_param('enable', True)
        if not dama_stn1.wait_up(timeout=60):
            self.fail(f'Station 1 is not UP at the beginning of the test case')

        StationRoute.create(self.driver, dama_stn2.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': self.stations[1].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(self.driver, dama_stn2.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{ser.get_id()}',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': self.stations[1].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })
        dama_stn2.send_param('enable', True)
        if not dama_stn2.wait_up(timeout=60):
            self.fail('Station 2 is not UP at the beginning of the test case')

        self.nms.wait_next_tick()
        self.nms.wait_next_tick()

        # check SR devices statuses
        state1 = sr_device1.get_param('state')
        state2 = sr_device2.get_param('state')

        if not (state1 == 'Up' and state2 == 'Redundant') and not (state2 == 'Up' and state1 == 'Redundant'):
            self.fail('Fault state! One of the device must be UP, while another one is Redundant')

        # checking availability of stations
        if sr_device1.get_param('state') == 'Up':
            ip_address = sr_device1.get_param('ip')
        elif sr_device2.get_param('state') == 'Up':
            ip_address = sr_device2.get_param('ip')
        else:  # Этого не должно быть, если предыдущий код верен
            self.error('None of the devices in UP state')
            ip_address = None

        if not dama_stn1.wait_up() or not dama_stn2.wait_up():
            self.fail('One of the station is not in UP state!')

        self.ctrl_telnet = UhpTelnetDriver(ip_address)
        if not self.ctrl_telnet.ping(ip_address='192.168.4.1', vlan=206):
            self.fail('Station 1 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.5.1', vlan=206):
            self.fail('Station 2 does not respond to ICMP echo requests!')

    def tear_down(self):
        if self.ctrl_telnet is not None:
            self.ctrl_telnet.close()
