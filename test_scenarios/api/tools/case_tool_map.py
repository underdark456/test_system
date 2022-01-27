from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR, NO_SUCH_TABLE
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes, Checkbox
from src.file_manager.file_manager import FileManager
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api.tools'
backup_name = '10000_stations_in_1_network.txt'


class ApiMapToolCase(CustomTestCase):
    """Map tool request test case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time = 14  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.options = OptionsProvider.get_options(options_path)

    def get_map(self, parent_name='network', parent_id=0, expected_stn_num=None):
        if expected_stn_num is None:
            num_of_stations = len(Station.station_list(self.driver, 0, vars_=['name', ]))
        else:
            num_of_stations = expected_stn_num
        for marker_mode in self.options.get('map_marker_modes'):
            path = PathsManager._API_OBJECT_MAP.format(parent_name, parent_id)
            reply, error, error_code = self.driver.custom_post(path, payload={'marker_mode': marker_mode})
            self.assertEqual(
                NO_ERROR,
                error_code,
                msg=f'{parent_name.capitalize()} marker mode {marker_mode} response error code {error_code}'
            )
            self.assertEqual(
                num_of_stations,
                len(reply.get('list')),
                msg=f'{parent_name.capitalize()} marker mode {marker_mode} '
                    f'number of stations {len(reply.get("list"))}, '
                    f'expected {num_of_stations}'
            )
            # TODO: figure out `var` parameter
            for stn in reply.get('list'):
                self.assertIsNotNone(
                    stn.get('var'),
                    msg=f'{parent_name.capitalize()} marker mode {marker_mode} `var` is absent in one of the station'
                )

    def test_get_network_map(self):
        """API get map network test"""
        self.get_map('network')

    def test_get_vno_map(self):
        """API get map vno test"""
        self.get_map('vno')

    def test_get_controller_map(self):
        """API get map controller test"""
        for i in range(5):
            self.get_map('controller', parent_id=i, expected_stn_num=2000)

    def test_invalid_marker_mode(self):
        """API invalid marker mode test"""
        for marker_mode in ('sudo', 'nms', 'nousecryingoverspiltmilk'):
            path = PathsManager._API_OBJECT_MAP.format('network', 0)
            reply, error, error_code = self.driver.custom_post(path, payload={'marker_mode': marker_mode})
            self.assertEqual(NO_ERROR, error_code)

    def test_beams(self):
        """Getting map with beams (ticket 8040)"""
        _file_manager = FileManager()
        _file_manager.upload_beam('Chinasat_11.gxt')
        _file_manager.upload_beam('Chinasat_12.gxt')
        test_net = Network.create(self.driver, 0, {
            'name': 'net_with_beams',
            'beam1_file': 'Chinasat_11.gxt',
            'beam2_file': 'Chinasat_12.gxt',
            'beam3_file': 'Chinasat_11.gxt',
            'beam4_file': 'Chinasat_12.gxt',
        })
        test_tp = Teleport.create(self.driver, test_net.get_id(), {'name': 'tp_with_beams'})
        test_vno = Vno.create(self.driver, test_net.get_id(), {'name': 'vno_with_beams'})
        test_ctrl = Controller.create(self.driver, test_net.get_id(), {
            'name': 'ctrl_with_beams',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{test_tp.get_id()}',
        })
        Station.create(self.driver, test_vno.get_id(), {
            'name': 'stn_with_beams',
            'serial': 137310,
            'mode': StationModes.STAR,
            'enable': Checkbox.ON,
            'rx_controller': f'controller:{test_ctrl.get_id()}',
        })
        path = f'api/map/both/network={test_net.get_id()}'
        reply, error, error_code = self.driver.custom_post(path, payload={'marker_mode': 'num_state'})
        self.assertEqual('', error, msg=f'Invalid json in response upon requesting map with beams')
        self.assertEqual(NO_ERROR, error_code, msg=f'Response error code is not {NO_ERROR}')
        self.assertEqual(4, len(reply.get('beams')), msg=f'Expected 4 beams in response, got {len(reply.get("beams"))}')

    def test_invalid_map_parent(self):
        """API map tool invalid object"""
        for parent_name in ('uhp', 'easy'):
            path = PathsManager._API_OBJECT_MAP.format(parent_name, 0)
            reply, error, error_code = self.driver.custom_post(path, payload={'marker_mode': 'num_state'})
            self.assertEqual(NO_SUCH_TABLE, error_code)

    def test_invalid_tool_methods(self):
        """API map tool invalid methods"""
        for method in ('delete', 'get', 'write', 'update'):
            path = f'api/map/{method}/network=0'
            reply, error, error_code = self.driver.custom_post(path, payload={'marker_mode': 'num_state'})
            self.assertEqual(NO_ERROR, error_code)
        path = f'api/map//network=0'
        reply, error, error_code = self.driver.custom_post(path, payload={'marker_mode': 'num_state'})
        self.assertEqual(NO_ERROR, error_code)





