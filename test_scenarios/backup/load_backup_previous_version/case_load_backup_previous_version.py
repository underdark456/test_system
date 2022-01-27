from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.backup.load_backup_previous_version'
backup_name = 'config_4_0_0_11.txt'


class LoadBackupPreviousVersionCase(CustomTestCase):
    """Loading config from previous 4.0.0.11 NMS version. Invalid vars and values should be ignored and config loaded"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = None  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()

    def test_applying_old_backup(self):
        """Obsolete vars and invalid values should be ignored. Config is applied using only valid vars and values"""
        self.backup.apply_backup(backup_name)
        net1 = Network(self.driver, 0, 0)
        net1.load()
        net2 = Network(self.driver, 0, 1)
        net2.load()
        tp1 = Teleport(self.driver, 0, 0)
        tp1.load()
        tp2 = Teleport(self.driver, 0, 1)
        tp2.load()
        ctrl1 = Controller(self.driver, 0, 0)
        ctrl1.load()
        ctrl2 = Controller(self.driver, 0, 1)
        ctrl2.load()
        ctrl3 = Controller(self.driver, 0, 2)
        ctrl3.load()
        ser1 = Service(self.driver, 0, 0)
        ser1.load()
        ser2 = Service(self.driver, 0, 1)
        ser2.load()
        shp1 = Shaper(self.driver, 0, 0)
        shp1.load()
        pol1 = Policy(self.driver, 0, 0)
        pol1.load()
        vno1 = Vno(self.driver, 0, 0)
        vno1.load()
        vno2 = Vno(self.driver, 0, 1)
        vno2.load()
        stn1 = Station(self.driver, 0, 0)
        stn1.load()
        stn2 = Station(self.driver, 0, 1)
        stn2.load()
        stn3 = Station(self.driver, 0, 2)
        stn3.load()

