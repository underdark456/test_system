import time
from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, ControlModes, AlertModes
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api.alert'
backup_name = 'default_config.txt'


@skip('Not ready, probably not needed')
class ApiTriggerAlertsCase(CustomTestCase):

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.23'
    __execution_time__ = None  # approximate case execution time in seconds

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()

    def test_1000_alerts(self):
        self.backup.apply_backup(backup_name)
        self.alert = Alert.create(self.driver, 0, {'name': 'al1', 'popup': True})
        self.net = Network.create(self.driver, 0, {
            'name': 'net',
            'alert_mode': AlertModes.SPECIFY,
            'set_alert': f'alert:{self.alert.get_id()}',
        })
        self.tp = Teleport.create(self.driver, 0, {'name': 'tp'})
        self.mf_hub = Controller.create(self.driver, 0, {
            'name': 'mf_hub',
            'teleport': f'teleport:{self.tp.get_id()}',
            'mode': ControllerModes.MF_HUB,
            'stn_number': 1001
        })
        self.vno = Vno.create(self.driver, 0, {'name': 'vno'})
        for i in range(100):
            Station.create(self.driver, 0, {
                'name': f'stn{i}',
                'serial': 10000 + i,
                'enable': True,
                'rx_controller': 'controller:0'
            })

    def test_sample_first(self):
        self.backup.apply_backup('10000_stations_in_1_network.txt')
        self.net = Network(self.driver, 0, 0)
        self.alert = Alert.create(self.driver, self.net.get_id(), {'name': 'al1', 'popup': True})
        self.net.send_params({'alert_mode': AlertModes.SPECIFY, 'set_alert': f'alert:{self.alert.get_id()}'})
        for i in range(32768):
            stn = Station(self.driver, 0, i)
            stn.send_param('rx_controller', '')

    def test_sample(self):
        """One line string describing the test case"""
        self.backup.apply_backup(backup_name)
        self.net = Network.create(self.driver, 0, {'name': 'net'})
        self.tp = Teleport.create(self.driver, self.net.get_id(), {'name': 'tp'})
        self.alert = Alert.create(self.driver, self.net.get_id(), {'name': 'al1', 'popup': True})
        self.net.send_params({'alert_mode': AlertModes.SPECIFY, 'set_alert': f'alert:{self.alert.get_id()}'})
        for i in range(512):
            Controller.create(self.driver, 0, {
                'name': f'mf{i}',
                'mode': ControllerModes.MF_HUB,
                'teleport': f'teleport:{self.tp.get_id()}',
            })
        for i in range(100):
            time.sleep(10)
            for j in range(512):
                Controller.update(self.driver, self.net.get_id(), i, {
                    'control': ControlModes.NO_ACCESS
                })
            time.sleep(10)
            for j in range(512):
                Controller.update(self.driver, self.net.get_id(), i, {
                    'control': ControlModes.FULL
                })
