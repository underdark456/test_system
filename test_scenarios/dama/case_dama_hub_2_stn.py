from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import RouteIds, ControllerModes, StationModes, RouteTypes, DamaAB, DamaTx, DamaABStr
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.dama'
backup_name = 'default_config.txt'


class ConfigDamaNetHub2Stn(CustomTestCase):
    """Configuring DAMA network: hub and two stations in NMS. Configuring UHP for DAMA network.
        Start DAMA network. Checking that all UHP are in operation"""

    system_options = None
    options = None
    stations = None
    __author__ = 'Filipp Gaidanskiy'
    __version__ = '4.0.0.25'
    __execution_time__ = 1350  # approximate test case execution time in seconds
    __express__ = True
    backup = None
    driver = None

    @classmethod
    def set_up_class(cls):
        controllers, cls.stations = OptionsProvider.get_uhp_controllers_stations(1, ['UHP200', 'UHP200X'], 2, ['ANY'])
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        cls.system_options = OptionsProvider.get_system_options(options_path)

        # Configuring NMS
        cls.network = Network.create(cls.driver, 0, {
            'name': 'Network'
        })
        cls.teleport = Teleport.create(cls.driver, 0, {
            'name': 'Teleport',
            'tx_lo': 0,
            'rx1_lo': 0,
            'rx2_lo': 0,
        })
        cls.service = Service.create(cls.driver, 0, {
            'hub_vlan': controllers[0].get('device_vlan'),
            'stn_vlan': cls.stations[0].get('device_vlan'),
            'name': 'Service'
        })
        cls.dama_hub = Controller.create(cls.driver, 0, {
            'name': 'DAMA_hub',
            'mode': ControllerModes.DAMA_HUB,
            'teleport': 'teleport:0',
            'device_ip': controllers[0].get('device_ip'),
            'device_vlan': controllers[0].get('device_vlan'),
            'device_gateway': controllers[0].get('device_gateway'),
            'tx_level': cls.options.get('tx_level'),
            'a_dama_modcod': '4',
            'a_dama_level': cls.options.get('tx_level'),
            'b_dama_level': cls.options.get('tx_level'),
            'net_id': cls.system_options.get('net_id'),
            'tx_frq': '1230000',
            'tx_sr': '2500',
            'tx_on': True,
            'a_dama_tx_frq': '1200000',
            'a_dama_rx_frq': '1200000',
            'a_dama_sr': '5000',
            'a_dama_tx': DamaTx.ON,
            'b_dama_tx_frq': '1210000',
            'b_dama_rx_frq': '1210000',
            'b_dama_sr': '3000',
            'b_dama_tx': DamaTx.ON,
        })
        cls.vno = Vno.create(cls.driver, 0, {
            'name': 'VNO'
        })
        cls.station_01 = Station.create(cls.driver, 0, {
            'name': 'station_01',
            'mode': StationModes.DAMA,
            'rx_controller': 'controller:0',
            'enable': True,
            'serial': cls.stations[0].get('serial'),
            'dama_ab': DamaAB.CHANNEL_A
        })
        StationRoute.create(cls.driver, 0, {
            'ip': cls.stations[0].get('device_ip'),
            'type': RouteTypes.IP_ADDRESS,
            'service': 'service:0',
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(cls.driver, 0, {
            'type': RouteTypes.STATIC_ROUTE,
            'service': 'service:0',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': cls.stations[0].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })
        cls.station_02 = Station.create(cls.driver, 0, {
            'name': 'station_02',
            'mode': StationModes.DAMA,
            'rx_controller': 'controller:0',
            'enable': True,
            'serial': cls.stations[1].get('serial'),
            'dama_ab': DamaAB.CHANNEL_B
        })
        StationRoute.create(cls.driver, 1, {
            'ip': cls.stations[1].get('device_ip'),
            'type': RouteTypes.IP_ADDRESS,
            'service': 'service:0',
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(cls.driver, 1, {
            'type': RouteTypes.STATIC_ROUTE,
            'service': 'service:0',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': cls.stations[1].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })

        # Configuring UHP
        cls.dama_hub_uhp = controllers[0].get('web_driver')
        password = Network(cls.driver, 0, 0).read_param('dev_password')
        cls.dama_hub_uhp.set_nms_permission(vlan=controllers[0].get('device_vlan'), password=password)

        cls.station_01_uhp = cls.stations[0].get('web_driver')
        cls.station_01_uhp.dama_station(profile_number=2, params={
            'rx1_frq': cls.dama_hub.read_param('tx_frq'),
            'rx1_sr': cls.dama_hub.read_param('tx_sr'),
            'timeout': 120,
        })
        cls.station_02_uhp = cls.stations[1].get('web_driver')
        cls.station_02_uhp.dama_station(profile_number=2, params={
            'rx1_frq': cls.dama_hub.read_param('tx_frq'),
            'rx1_sr': cls.dama_hub.read_param('tx_sr'),
            'timeout': 120,
        })
        cls.nms = Nms(cls.driver, 0, 0)
        cls.backup.create_backup('temporary_config.txt')

    def set_up(self):
        self.backup.apply_backup('temporary_config.txt')
        self.assertTrue(self.dama_hub.wait_up(), 'DAMA hub is not ready')
        self.assertTrue(self.station_01.wait_up(), 'Station 01 is not ready')
        self.assertTrue(self.station_02.wait_up(), 'Station 02 is not ready')
        self.nms.wait_next_tick()  # To be sure that config reached stations we are waiting for next NMS tick

    def test_2_stns_on_one_channel(self):
        self.station_02.update(self.driver, 0, 1, {
            'rx_controller': f'controller:{self.dama_hub.get_id()}',
            'dama_ab': DamaAB.CHANNEL_A
        })
        self.assertEqual(self.station_02.get_param('dama_ab'), DamaABStr.CHANNEL_B)

    def test_(self):
        pass
