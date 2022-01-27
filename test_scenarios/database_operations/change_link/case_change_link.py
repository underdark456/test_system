from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes
from src.file_manager.file_manager import FileManager
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.database_operations.change_link'
backup_name = 'default_config.txt'


class ChangeLinkCase(CustomTestCase):
    """Check if station's controller can be changed, as well as SW upload controller"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __execution_time__ = 5  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.net = Network.create(cls.driver, 0, {'name': 'test_net'})
        cls.vno = Vno.create(cls.driver, cls.net.get_id(), {'name': 'test_vno'})
        cls.tp = Teleport.create(cls.driver, cls.net.get_id(), {'name': 'test_tp'})
        cls.ctrl1 = Controller.create(cls.driver, cls.net.get_id(), {
            'name': 'ctrl-1',
            'teleport': f'teleport:{cls.tp.get_id()}',
            'mode': ControllerModes.MF_HUB,
        })
        cls.ctrl2 = Controller.create(cls.driver, cls.net.get_id(), {
            'name': 'ctrl-2',
            'teleport': f'teleport:{cls.tp.get_id()}',
            'mode': ControllerModes.MF_HUB
        })
        # Creating a new station and assigning it to `ctrl1`
        cls.stn = Station.create(cls.driver, cls.vno.get_id(), {
            'name': 'test_stn',
            'serial': '12345',
            'enable': 'ON',
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{cls.ctrl1.get_id()}'
        })
        fm = FileManager()
        fm.upload_uhp_software('dummy_soft.240')
        cls.sw_upload = SwUpload.create(
            cls.driver,
            cls.net.get_id(),
            {'name': 'test_sw_up', 'tx_controller': f'controller:{cls.ctrl1.get_id()}', 'sw_file': 'dummy_soft.240'})

    def test_change_station_controller(self):
        """Check if the station's controller can be changed to another one"""
        # Changing the station's controller to `ctrl2`
        self.stn.send_param('rx_controller', f'controller:{self.ctrl2.get_id()}')
        self.assertEqual(self.stn.get_param('rx_controller').split()[0].split(':')[1], str(self.ctrl2.get_id()))

    def test_change_sw_upload_tx_controller(self):
        """Check if the SW upload `tx_controller` can be successfully changed"""
        # Changing the station's controller to `ctrl2`
        self.sw_upload.send_param('tx_controller', f'controller:{self.ctrl2.get_id()}')
        self.assertEqual(self.sw_upload.get_param('tx_controller').split()[0].split(':')[1], str(self.ctrl2.get_id()))
