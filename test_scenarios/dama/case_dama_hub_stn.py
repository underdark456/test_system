import time

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import DamaAB, ControlModes, RouteIds, ControllerModes, DamaTx, StationModes, RouteTypes
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


class ConfigDamaNetHubStn(CustomTestCase):
    """Configuring DAMA network: hub and station in NMS. Configuring UHP for DAMA network.
    Start DAMA network. Checking that all UHP are in operation"""

    __author__ = 'Filipp Gaidanskiy'
    __version__ = '4.0.0.25'
    __execution_time__ = 1350  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        controllers, cls.stations = OptionsProvider.get_uhp_controllers_stations(1, ['UHP200', 'UHP200X'], 1, ['ANY'])

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

        # UHP configure
        cls.dama_hub_uhp = controllers[0].get('web_driver')
        password = Network(cls.driver, 0, 0).read_param('dev_password')
        cls.dama_hub_uhp.set_nms_permission(vlan=controllers[0].get('device_vlan'), password=password)

        cls.station_01_uhp = cls.stations[0].get('web_driver')
        cls.station_01_uhp.dama_station(profile_number=2, params={
            'rx1_frq': cls.dama_hub.read_param('tx_frq'),
            'rx1_sr': cls.dama_hub.read_param('tx_sr'),
            'timeout': 120,
        })

        cls.nms = Nms(cls.driver, 0, 0)
        cls.backup.create_backup('temporary_config.txt')

        # Messages that hub or station are not in operation when they should be in operation
        cls.up_timeout = 60
        cls.msg_hub = F"hub ip={cls.dama_hub.read_param('device_ip')} not in operation after {cls.up_timeout} seconds"
        cls.msg_stn = f"with ip {cls.stations[0].get('device_ip')} is not in operation after {cls.up_timeout} seconds"

    def set_up(self):
        self.backup.apply_backup('temporary_config.txt')
        self.assertTrue(self.dama_hub.wait_up(), 'DAMA hub is not ready')
        self.assertTrue(self.station_01.wait_up(), 'Station 01 is not ready')
        self.nms.wait_next_tick()  # Waiting for next NMS tick to be sure that config reached stations.

    def test_changing_rf_settings_dama_return(self):
        """DAMA return channel settings changed and reached station"""
        for i in range(5):
            frequency = 1520000 + (100 * i)
            sr = 1000 + (100 * i)
            modcod = i + 2
            self.dama_hub.send_params({
                'a_dama_tx_frq': frequency,
                'a_dama_rx_frq': frequency,
                'a_dama_sr': sr,
                'a_dama_modcod': modcod,
            })
            # Check that station goes down after channel settings changed and goes up after new settings reach station
            self.assertTrue(self.station_01.wait_state('Down', self.up_timeout), 'Station state should be Down')
            self.assertTrue(self.station_01.wait_up(self.up_timeout), F"Station {self.msg_stn}")

    def test_switching_dama_station_chA_chB(self):
        self.assertTrue(self.dama_hub.wait_up(self.up_timeout), F"DAMA {self.msg_hub}")
        self.assertEqual(self.dama_hub_uhp.get_state(), 'operation', F"UHP dama {self.msg_hub}")
        self.assertTrue(self.station_01.wait_up(self.up_timeout), F"Station {self.msg_stn}")
        self.assertEqual(self.station_01_uhp.get_state(), 'operation', F"UHP modem {self.msg_stn}")
        for i in range(50):
            self.station_01.send_param('dama_ab', DamaAB.CHANNEL_B)
            self.nms.wait_next_tick()
            self.assertTrue(self.station_01.wait_up(self.up_timeout), F"Iteration {i + 1}. "
                                                                      F"Station {self.msg_stn} after switching to Channel B")
            self.station_01.send_param('dama_ab', DamaAB.CHANNEL_A)
            self.nms.wait_next_tick()
            self.assertTrue(self.station_01.wait_up(self.up_timeout), F"Iteration {i + 1}. "
                                                                      F"Station {self.msg_stn} after switching to Channel A")

    def test_switching_off_station(self):
        self.station_01.send_param('enable', False)
        self.assertFalse(self.station_01.wait_up(self.up_timeout), 'Disabled station is in operation')
        self.station_01.send_param('enable', True)
        self.assertTrue(self.station_01.wait_up(self.up_timeout), 'Station is not Up')

    def test_DAMA_hub_to_no_access_switching(self):
        self.dama_hub.send_param('control', ControlModes.NO_ACCESS)
        time.sleep(20)
        self.assertEqual(self.dama_hub.read_param('state'), 'Off', 'Controller state on the dashboard is incorrect')
        self.assertEqual(self.station_01_uhp.get_state(), 'operation', 'Station UHP modem is not in operation')
        self.assertEqual(self.dama_hub_uhp.get_state(), 'operation', 'Controller UHP modem is not in operation')
        # Проверяем, что режим no_access работает корректно и NMS не может конфигурировать модем контроллера
        self.dama_hub.send_param('tx_on', False)
        self.nms.wait_ticks(2)
        self.assertEqual(self.dama_hub_uhp.get_modulator_form().get('tx_on'), '1',
                         'Config from NMS applied on no_access modem')

    # TODO write methods for switching to: stats_only, unconfigured, full

    def test_DAMA_station_wrong_serial(self):
        wrong_serial = '121212'
        normal_serial = self.stations[0].get('serial')
        self.station_01.send_param('serial', wrong_serial)
        self.assertTrue(self.station_01.wait_state('Down', timeout=self.up_timeout), 'Station is in operation')
        self.station_01.send_param('serial', normal_serial)
        self.assertTrue(self.station_01.wait_up(timeout=self.up_timeout), 'Station is not in operation')

    def test_rx_controller_on_station_not_set(self):
        self.station_01.send_param('rx_controller', 0)
        self.assertTrue(self.station_01.wait_state('Idle', timeout=self.up_timeout), 'Something wrong with station')

    def test_3_reboots_of_DAMA_station(self):
        self.station_01_uhp.network_script(command='co sa')
        for _ in range(3):
            self.station_01_uhp.reboot()
            self.assertTrue(self.station_01.wait_up(self.up_timeout))

    def test_5_reboots_of_DAMA_hub(self):
        self.dama_hub_uhp.network_script(command='co sa')
        for _ in range(5):
            self.dama_hub_uhp.reboot()
            self.dama_hub.wait_state(self.dama_hub.UNREACHABLE, timeout=300)
            self.assertTrue(self.station_01.wait_up(timeout=300))



