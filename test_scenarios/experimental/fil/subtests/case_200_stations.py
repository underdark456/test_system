from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import StationModes
from src.nms_entities.basic_entities import vno
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.station import Station
from src.options_providers.options_provider import OptionsProvider

options_path = ''
backup_name = ''


class Case(CustomTestCase):
    """"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )

    def test_stations_in_controller(self):
        for j in range(20):
            Station.create(self.driver, 0, params={
                'name': f'stn-{j+20}',
                'serial': j + 1,
                'mode': StationModes.STAR,
                'rx_controller': f'controller:15',
                'enable': 'ON',
            })

