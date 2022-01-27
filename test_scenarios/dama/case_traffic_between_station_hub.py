import time

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.exceptions import UhpUpStateException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.dama'
backup_name = 'dama_net_hub_stn.txt'


class TrafficBtwStationHubCase(CustomTestCase):
    """Run traffic between dama hub and station in both directions to check how it displays in NMS"""

    __author__ = 'Filipp Gaidanskiy'
    __version__ = '4.0.0.21'
    __execution_time__ = 85
    __express__ = True
    backup = None
    driver = None
    dama_hub_uhp = None
    station_01_uhp = None

    @classmethod
    def set_up_class(cls):
        controllers, cls.stations = OptionsProvider.get_uhp_controllers_stations(1, ['UHP200', 'UHP200X'], 1, ['ANY'])
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.options = OptionsProvider.get_options(options_path)

        # Configuring NMS for first start
        cls.nms = Nms(cls.driver, 0, 0)
        cls.network = Network(cls.driver, 0, 0)
        cls.vno = Vno(cls.driver, 0, 0)
        cls.dama_hub = Controller.update(cls.driver, 0, 0, {
            'device_ip': controllers[0].get('device_ip'),
            'device_vlan': controllers[0].get('device_vlan'),
            'device_gateway': controllers[0].get('device_gateway'),
            'tx_level': cls.options.get('tx_level'),
            'a_dama_level': cls.options.get('tx_level'),
            'b_dama_level': cls.options.get('tx_level'),
        })
        cls.station_01 = Station.update(cls.driver, 0, 0, {
            'serial': cls.stations[0].get('serial')
        })
        Service.update(cls.driver, 0, 0, {
            'stn_vlan': cls.stations[0].get('device_vlan')
        })
        StationRoute.update(cls.driver, 0, 0, {
            'ip': cls.stations[0].get('device_ip')
        })
        StationRoute.update(cls.driver, 0, 1, {
            'gateway': cls.stations[0].get('device_gateway')
        })

        cls.dama_hub.send_param('tx_on', True)

        # UHP configure
        cls.dama_hub_uhp = controllers[0].get('web_driver')
        password = Network(cls.driver, 0, 0).read_param('dev_password')
        cls.dama_hub_uhp.set_nms_permission(vlan=controllers[0].get('device_vlan'), password=password)
        cls.station_01_uhp = cls.stations[0].get('web_driver')
        cls.station_01_uhp.dama_station(profile_number=2, params={
            'rx1_frq': cls.dama_hub.read_param('tx_frq'),
            'rx1_sr': cls.dama_hub.read_param('tx_sr'),
            'timeout': 120
        })

        cls.dama_hub_uhp.traffic_generator({  # Sat. bandwidth	326400 bps with these values
            'enabled': 1,
            'ipv4': '101.1.1.11',
            'vlan': '100',
            'pps_from': '200',
            'pps_to': '200',
            'pkt_len_from': '200',
            'pkt_len_to': '200',
        })
        cls.station_01_uhp.traffic_generator({  # Sat. bandwidth	326400 bps with these values
            'enabled': 1,
            'ipv4': '101.0.0.11',
            'vlan': '110',
            'pps_from': '200',
            'pps_to': '200',
            'pkt_len_from': '200',
            'pkt_len_to': '200',
        })
        if not cls.dama_hub.wait_up() or not cls.station_01.wait_up():
            raise UhpUpStateException('DAMA Hub or station is not up')
        time.sleep(30)

    def test_traffic_between_dama_hub_station(self):
        return_traffic = int(self.dama_hub.read_param('return_rate_all'))
        forward_traffic = int(self.dama_hub.read_param('forward_rate_all'))
        self.assertIn(return_traffic, range(630, 670), f'Return traffic rate is not in range')
        self.assertIn(forward_traffic, range(630, 670), f'Forward traffic rate is not in range')

    def test_traffic_values_comparing(self):
        ret_hub = self.dama_hub.read_param('return_rate_all')
        fwd_hub = self.dama_hub.read_param('forward_rate_all')
        ret_station = self.station_01.read_param('return_rate_all')
        fwd_station = self.station_01.read_param('forward_rate_all')
        ret_net = self.network.read_param('return_rate_all')
        fwd_net = self.network.read_param('forward_rate_all')
        ret_vno = self.vno.read_param('return_rate_all')
        fwd_vno = self.vno.read_param('forward_rate_all')
        self.assertAlmostEqual(fwd_hub, fwd_station, delta=20, msg=f'Hub fwd all {fwd_hub}, stn fwd all {fwd_station}')
        self.assertAlmostEqual(fwd_hub, fwd_vno, delta=20, msg=f'Hub fwd all {fwd_hub}, vno fwd all {fwd_vno}')
        self.assertAlmostEqual(fwd_hub, fwd_net, delta=20, msg=f'Hub fwd all {fwd_hub}, net fwd all {fwd_net}')
        self.assertAlmostEqual(ret_hub, ret_station, delta=20, msg=f'Hub ret all {ret_hub}, stn ret all {ret_station}')
        self.assertAlmostEqual(ret_hub, ret_vno, delta=20, msg=f'Hub ret all {ret_hub}, vno ret all {ret_vno}')
        self.assertAlmostEqual(ret_hub, ret_net, delta=20, msg=f'Hub ret all {ret_hub}, net ret all {ret_net}')

    @classmethod
    def tear_down_class(cls):
        cls.dama_hub_uhp.traffic_generator()
        cls.station_01_uhp.traffic_generator()
