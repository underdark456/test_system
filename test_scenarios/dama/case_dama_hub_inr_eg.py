from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, DamaTx, StationModes, DamaAB, RouteTypes, RouteIds
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider
import time
options_path = 'test_scenarios.dama'
backup_name = 'default_config.txt'


class ConfigDamaNetWithEG(CustomTestCase):
    """Creating DAMA network with hub, inroute and EG controllers"""
    __author__ = 'Filipp Gaidanskiy'
    __version__ = '4.0.0.26'
    __execution_time__ = 1350  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        controllers, cls.stations = OptionsProvider.get_uhp_controllers_stations(3, ['UHP200', 'UHP200X'], 2, ['ANY'])
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
            'binding': '0',
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
        cls.dama_inroute = Controller.create(cls.driver, 0, {
            'name': 'DAMA_inroute',
            'mode': ControllerModes.DAMA_INROUTE,
            'teleport': 'teleport:0',
            'tx_controller': 'controller:0',
            'binding': '0',
            'device_ip': controllers[1].get('device_ip'),
            'device_vlan': controllers[1].get('device_vlan'),
            'device_gateway': controllers[1].get('device_gateway'),
            'tx_level': cls.options.get('tx_level'),
            'a_dama_modcod': '5',
            'a_dama_level': cls.options.get('tx_level'),
            'b_dama_level': cls.options.get('tx_level'),
            'net_id': cls.system_options.get('net_id'),
            'tx_frq': '1240000',
            'tx_sr': '3000',
            'a_dama_tx_frq': '1300000',
            'a_dama_rx_frq': '1300000',
            'a_dama_sr': '5000',
            'a_dama_tx': DamaTx.ON,
            'b_dama_tx_frq': '1310000',
            'b_dama_rx_frq': '1310000',
            'b_dama_sr': '4000',
            'b_dama_tx': DamaTx.ON,
        })
        cls.eg = Controller.create(cls.driver, 0, {
            'name': 'External_GW',
            'mode': ControllerModes.GATEWAY,
            'teleport': 'teleport:0',
            'tx_controller': 'controller:0',
            'binding': '0',
            'device_ip': controllers[2].get('device_ip'),
            'device_vlan': controllers[2].get('device_vlan'),
            'device_gateway': controllers[2].get('device_gateway'),
            'tx_frq': '1250000',
            'tx_sr': '3000',
            'tx_level': cls.options.get('tx_level'),
            'tx_on': True,
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
            'dama_ab': DamaAB.CHANNEL_A,
            'ext_gateway': f'controller:{cls.eg.get_id()}'
        })
        StationRoute.create(cls.driver, cls.station_01.get_id(), {
            'ip': cls.stations[0].get('device_ip'),
            'type': RouteTypes.IP_ADDRESS,
            'service': 'service:0',
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(cls.driver, cls.station_01.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': 'service:0',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': cls.stations[0].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })

        # UHP configure
        cls.dama_hub_uhp = controllers[0].get('web_driver')
        password = Network(cls.driver, 0, 0).read_param('dev_password')
        cls.dama_hub_uhp.set_nms_permission(vlan=controllers[0].get('device_vlan'), password=password)

        cls.dama_inroute_uhp = controllers[1].get('web_driver')
        password = Network(cls.driver, 0, 0).read_param('dev_password')
        cls.dama_inroute_uhp.set_nms_permission(vlan=controllers[1].get('device_vlan'), password=password)

        cls.eg_uhp = controllers[2].get('web_driver')
        password = Network(cls.driver, 0, 0).read_param('dev_password')
        cls.eg_uhp.set_nms_permission(vlan=controllers[2].get('device_vlan'), password=password)

        cls.station_01_uhp = cls.stations[0].get('web_driver')
        cls.station_01_uhp.dama_station(profile_number=2, params={
            'rx1_frq': cls.dama_hub.read_param('tx_frq'),
            'rx1_sr': cls.dama_hub.read_param('tx_sr'),
            'timeout': 120,
        })
        cls.nms = Nms(cls.driver, 0, 0)
        cls.station_01_uhp.network_script(command='co sa')
        cls.backup.create_backup('temporary_config.txt')
        cls.up_timeout = 60

    def set_up(self):
        self.backup.apply_backup('temporary_config.txt')
        timeout = 300
        self.assertTrue(self.dama_hub.wait_up(timeout), 'DAMA hub is not ready')
        self.assertTrue(self.dama_inroute.wait_up(timeout), 'DAMA inroute is not ready')
        self.assertTrue(self.station_01.wait_up(timeout), 'Station 01 is not ready')
        self.assertTrue(self.eg.wait_up(timeout), 'External GW is not ready')
        time.sleep(20)
        self.assertEqual(self.station_01_uhp.get_overview().get('demodulator-2').get('state'), 'Up')

    def test_(self):
        pass

    def test_station_switching_between_inroutes(self):
        for _ in range(3):
            self.station_01.update(self.driver, 0, 0, {
                'rx_controller': 'controller:1',
            })
            self.assertTrue(self.station_01.wait_not_state(Station.UP), 'Station is in operation')
            self.assertEqual(self.station_01_uhp.get_overview().get('demodulator-2').get('state'), 'Up')
            self.station_01.wait_up()
            self.station_01.update(self.driver, 0, 0, {
                'rx_controller': 'controller:0',
            })
            self.assertTrue(self.station_01.wait_not_state(Station.UP), 'Station is in operation')
            self.assertEqual(self.station_01_uhp.get_overview().get('demodulator-2').get('state'), 'Up')
            self.station_01.wait_up()
            print(_)

    def test_changing_eg_settings(self):
        tx_frq = int(self.eg.get_param('tx_frq'))
        tx_sr = int(self.eg.get_param('tx_sr'))

        for _ in range(5):
            self.eg.update(self.driver, 0, self.eg.get_id(), {
                'tx_frq': str(tx_frq + (10000 * _)),
                'tx_sr':  str(tx_sr + (100 * _)),
            })
            time.sleep(20)
            self.assertEqual(self.station_01_uhp.get_overview().get('demodulator-2').get('state'), 'Up')
