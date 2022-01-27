import time

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider

__author__ = 'dkudryashov'
__version__ = '0.1'
options_path = 'test_scenarios.tickets.subtests.7764'
backup_name = 'default_config.txt'


# TODO: Probably not needed as a specialized all links check case has been created
class ListStationRouteCase(CustomTestCase):
    """Ticket 7764. Listing station routes via WEB leads to 404"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

    def test_list_station_routes(self):
        """Check if getting station routes via WEB does not lead to 404"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'tp-0'})
        ctrl = Controller.create(self.driver, net.get_id(), {
            'name': 'ctrl-0',
            'mode': ControllerModes.HUBLESS_MASTER,
            'teleport': f'teleport:{tp.get_id()}'
        })
        vno = Vno.create(self.driver, net.get_id(), {'name': 'vno-0'})
        stn = Station.create(self.driver, vno.get_id(), {
            'name': 'stn-0',
            'serial': 12345,
            # 'enable': 'ON',  # Currently checkboxes not supported by Web driver
            'mode': StationModes.MESH,
            'rx_controller': f'controller:{ctrl.get_id()}'
        })
        # Exception is thrown if link to station routes does not work
        path = PathsManager.station_route_list(self.driver.get_type(), stn.get_id())
        links = self.driver.driver.find_elements_by_tag_name('a')
        for link in links:
            href = link.get_attribute('href')
            if href is None:
                continue
            elif href.find(path) != -1:
                break
        else:
            self.assertFalse(False, "Correct link to station routes not found in the page")
        self.driver.load_data(path)
