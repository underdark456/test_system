import time

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.web.web_map_tool'
backup_name = '10000_stations_in_1_network.txt'


class WebMapPerformanceCase(CustomTestCase):
    """10000 stations map performance test case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.22'
    __execution_time__ = 13  # test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        cls.expected_load_time = cls.options.get('expected_map_load_time')
        cls.net = Network(cls.driver, 0, 0)
        cls.vno = Vno(cls.driver, 0, 0)
        cls.ctrl = Controller(cls.driver, 0, 0)
        cls.stn1 = Station(cls.driver, 0, 0)

    def test_map_network(self):
        """10000 stations in one network browser performance"""
        st_time = time.perf_counter()
        self.net.get_map()
        end_time = time.perf_counter()
        self.assertLess(
            end_time - st_time,
            self.expected_load_time,
            msg=f'WEB map loading time for 10000 stations is bigger than {self.expected_load_time} seconds'
        )

    def test_map_vno(self):
        """10000 stations in one vno browser performance"""
        st_time = time.perf_counter()
        self.vno.get_map()
        end_time = time.perf_counter()
        self.assertLess(
            end_time - st_time,
            self.expected_load_time,
            msg=f'WEB map loading time for 10000 stations is bigger than {self.expected_load_time} seconds'
        )

    def test_map_controller(self):
        """2000 stations in 1 controller browser performance"""
        st_time = time.perf_counter()
        self.ctrl.get_map()
        end_time = time.perf_counter()
        self.assertLess(
            end_time - st_time,
            self.expected_load_time,
            msg=f'WEB map loading time for 10000 stations is bigger than {self.expected_load_time} seconds'
        )

    def test_map_station(self):
        """Station browser performance"""
        st_time = time.perf_counter()
        self.stn1.get_map()
        end_time = time.perf_counter()
        self.assertLess(
            end_time - st_time,
            self.expected_load_time,
            msg=f'WEB map loading time for 10000 stations is bigger than {self.expected_load_time} seconds'
        )
