import random

from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_SUCH_TABLE, NO_SUCH_ROW, NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.abstract_http_driver import API
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, RouteTypes
from src.file_manager.file_manager import FileManager
from src.nms_entities.basic_entities.access import Access
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.bal_controller import BalController
from src.nms_entities.basic_entities.camera import Camera
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.dashboard import Dashboard
from src.nms_entities.basic_entities.device import Device
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.profile import Profile
from src.nms_entities.basic_entities.qos import Qos
from src.nms_entities.basic_entities.scheduler import Scheduler
from src.nms_entities.basic_entities.scheduler_range import SchRange
from src.nms_entities.basic_entities.scheduler_service import SchService
from src.nms_entities.basic_entities.scheduler_task import SchTask
from src.nms_entities.basic_entities.server import Server
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.sr_controller import SrController
from src.nms_entities.basic_entities.sr_license import SrLicense
from src.nms_entities.basic_entities.sr_teleport import SrTeleport
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_port_map import StationPortMap
from src.nms_entities.basic_entities.station_rip import StationRip
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api.tools'
backup_name = 'default_config.txt'


class ApiSearchToolCase(CustomTestCase):
    """API Search Tool. Searching NMS objects by their names, IPs etc."""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 45  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.nms = Nms(cls.driver, 0, 0)
        cls.options = OptionsProvider.get_options(options_path)
        cls.fm = FileManager()
        cls.fm.upload_uhp_software('dummy_soft.240')

    def test_search_tool_128_networks(self):
        """Search tool response test"""
        self.backup.apply_backup(backup_name)
        base_name = 'network_with_a_long_name_'
        for i in range(128):
            Network.create(self.driver, 0, {'name': f'{base_name}{i}'})
        path = 'api/search/get/nms=0'
        for length in range(1, 15):
            reply, error, error_code = self.driver.custom_post(path, payload={'search': base_name[:length]})
            self.assertEqual(0, error_code, msg=f'Reply error_code is {error_code}')
            if length == 1:
                self.assertEqual(0, len(reply), f'Expected 0 networks in reply using only one character to search')
            else:
                self.assertEqual(
                    128,
                    len(reply),
                    f'Expected 128 networks in reply using {length} characters, got {len(reply)}'
                )
        # Search using characters in the middle
        for begin in range(5, 10):
            reply, error, error_code = self.driver.custom_post(path, payload={'search': base_name[begin:begin+5]})
            self.assertEqual(0, error_code, msg=f'Reply error_code is {error_code}')
            self.assertEqual(
                128,
                len(reply),
                f'Expected 128 networks in reply when searching using characters in the middle of names, '
                f'got {len(reply)}'
            )

    def test_search_any_entity(self):
        """Search tool can find any NMS object by its name, ip or sequence"""
        self.backup.apply_backup(backup_name)
        names = self.options.get('search_tool_unique_names')
        Nms.update(self.driver, 0, 0, {'name': names.get('nms')})
        Server.create(self.driver, 0, {'name': names.get('server')})
        UserGroup.create(self.driver, 0, {'name': names.get('group')})
        User.create(self.driver, 0, {'name': names.get('user')})
        Alert.create(self.driver, 0, {'name': names.get('alert'), 'popup': True})
        Dashboard.create(self.driver, 0, {'name': names.get('dashboard')})

        Network.create(self.driver, 0, {'name': names.get('network')})
        Teleport.create(self.driver, 0, {'name': names.get('teleport'), 'sat_name': 'sat'})
        Controller.create(
            self.driver,
            0,
            {'name': names.get('controller'), 'mode': ControllerModes.MF_HUB, 'teleport': 'teleport:0'}
        )
        Vno.create(self.driver, 0, {'name': names.get('vno')})
        Service.create(self.driver, 0, {'name': names.get('service')})
        Shaper.create(self.driver, 0, {'name': names.get('shaper')})
        Policy.create(self.driver, 0, {'name': names.get('policy')})
        PolicyRule.create(self.driver, 0, {'sequence': 8762})
        SrController.create(self.driver, 0, {'name': names.get('sr_controller')})
        SrTeleport.create(self.driver, 0, {'name': names.get('sr_teleport'), 'teleport': 'teleport:0'})
        Device.create(self.driver, 0, {'name': names.get('device')})
        SrLicense.create(self.driver, 0, {'name': names.get('sr_license')})
        BalController.create(self.driver, 0, {'name': names.get('bal_controller')})
        Profile.create(self.driver, 0, {'name': names.get('profile_set')})
        SwUpload.create(self.driver, 0, {'name': names.get('sw_upload'), 'sw_file': 'dummy_soft.240'})
        Camera.create(self.driver, 0, {'name': names.get('camera')})
        Scheduler.create(self.driver, 0, {'name': names.get('scheduler')})
        SchRange.create(self.driver, 0, {'name': names.get('sch_range')})
        SchService.create(self.driver, 0, {'name': names.get('sch_service')})
        Station.create(self.driver, 0, {'name': names.get('station'), 'serial': 12345})
        StationRoute.create(
            self.driver,
            0,
            {'type': RouteTypes.IP_ADDRESS, 'service': 'service:0', 'ip': '172.16.89.2'}
        )
        StationRip.create(
            self.driver,
            0,
            {'service': 'service:0', 'rip_next_hop': '172.16.90.22'}
        )
        StationPortMap.create(self.driver, 0, {'internal_ip': '172.16.234.21'})
        SchTask.create(self.driver, 0, {'name': names.get('sch_task')})
        Qos.create(self.driver, 0, {'name': names.get('qos')})

        path = PathsManager._API_SEARCH_TOOL.format('nms', 0)
        for table, name in names.items():
            reply, error, error_code = self.driver.custom_post(path, payload={'search': name})
            self.assertEqual(0, error_code, msg=f'Reply error_code is {error_code}')
            self.assertEqual(1, len(reply), msg=f'Expected 1 object in reply, got {len(reply)}')
            self.assertEqual(name, reply[0].get('name'), msg=f'Searched {name}, returned name {reply[0].get("name")}')
            self.assertEqual(
                name,
                reply[0].get('string'),
                msg=f'Searched {name}, returned string {reply[0].get("string")}'
            )
            if table in ('group', 'user'):
                row = 1
            else:
                row = 0
            self.assertEqual(
                f'{table}={row}', reply[0].get('url'), msg=f'Expected url {table}={row}, got {reply[0].get("url")}'
            )
        # Searching by IP and sequence
        for search_string in ('8762', '172.16.89.2', '172.16.90.22', '172.16.234.21'):
            reply, error, error_code = self.driver.custom_post(path, payload={'search': search_string})
            self.assertEqual(0, error_code, msg=f'Reply error_code is {error_code}')
            self.assertEqual(1, len(reply), msg=f'Expected 1 object in reply, got {len(reply)}')
            self.assertEqual(
                search_string,
                reply[0].get('string'),
                msg=f'Searched {search_string }, returned string {reply[0].get("string")}'
            )
            if search_string == '8762':
                self.assertEqual('polrule=0', reply[0].get('url'), msg=f'Expected polrule=0, got {reply[0].get("url")}')
            elif search_string == '172.16.89.2':
                self.assertEqual('route=0', reply[0].get('url'), msg=f'Expected route=0, got {reply[0].get("url")}')
            elif search_string == '172.16.90.22':
                self.assertEqual(
                    'rip_router=0',
                    reply[0].get('url'),
                    msg=f'Expected rip_router=0, got {reply[0].get("url")}'
                )
            else:
                self.assertEqual(
                    'port_map=0',
                    reply[0].get('url'),
                    msg=f'Expected port_map=0, got {reply[0].get("url")}'
                )

    def test_multiple_objects_in_response(self):
        """Multiple objects match the searched name. Make sure that first 1000 are returned"""
        self.backup.apply_backup('32768_stations_1_vno.txt')
        path = PathsManager._API_SEARCH_TOOL.format('nms', 0)
        reply, error, error_code = self.driver.custom_post(path, payload={'search': 'stn'})
        self.assertEqual(0, error_code, msg=f'Reply error_code is {error_code}')
        # NMS returns only first 1000 matches
        self.assertEqual(1000, len(reply), msg=f'Expected 1000 object in reply, got {len(reply)}')

    def test_vno_user_cannot_search_net(self):
        """User having access to its VNO cannot get search result for controller and network"""
        self.backup.apply_backup('32768_stations_1_vno.txt')
        gr = UserGroup.create(self.driver, 0, {'name': 'vno_gr'}, parent_type='vno')
        User.create(self.driver, gr.get_id(), {'name': 'vno_user', 'password': ''})
        Access.create(self.driver, 0, {'group': f'group:{gr.get_id()}'}, parent_type='vno')
        driver_vno_user = DriversProvider.get_driver_instance(
            {
                'type': API,
                'address': self.driver.address,
                'username': 'vno_user',
                'password': '',
                'auto_login': True
            },
            driver_id='test_vno_user_cannot_search_net',
            store_driver=False,
        )
        path = PathsManager._API_SEARCH_TOOL.format('nms', 0)
        for s in ('net', 'ctrl'):
            reply, error, error_code = driver_vno_user.custom_post(path, payload={'search': s})
            self.assertEqual(0, error_code, msg=f'Reply error_code is {error_code}')
            self.assertEqual(0, len(reply), msg=f'Expected 0 objects in reply, got {len(reply)}')
        del driver_vno_user

    def test_vno_user_can_search_use_objects(self):
        """User having access to its VNO can get search result for controller there access for that user is created"""
        self.backup.apply_backup('32768_stations_1_vno.txt')
        gr = UserGroup.create(self.driver, 0, {'name': 'vno_gr'}, parent_type='vno')
        User.create(self.driver, gr.get_id(), {'name': 'vno_user', 'password': ''})
        Access.create(self.driver, 0, {'group': f'group:{gr.get_id()}'}, parent_type='vno')
        Access.create(self.driver, 0, {'group': f'group:{gr.get_id()}'}, parent_type='controller')
        driver_vno_user = DriversProvider.get_driver_instance(
            {
                'type': API,
                'address': self.driver.address,
                'username': 'vno_user',
                'password': '',
                'auto_login': True
            },
            driver_id='test_vno_user_can_search_use_objects',
            store_driver=False,
        )
        path = PathsManager._API_SEARCH_TOOL.format('nms', 0)
        for s in ('net', 'ctrl'):
            reply, error, error_code = driver_vno_user.custom_post(path, payload={'search': s})
            self.assertEqual(0, error_code, msg=f'Reply error_code is {error_code}')
            if s == 'net':
                self.assertEqual(0, len(reply), msg=f'Expected 0 objects in reply, got {len(reply)}')
            else:
                self.assertEqual(1, len(reply), msg=f'Expected 1 objects in reply, got {len(reply)}')
        del driver_vno_user

    def test_extra_long_payload_value(self):
        """Search tool extra long invalid item to search test"""
        self.backup.apply_backup(backup_name)
        path = 'api/search/get/nms=0'
        random_chars = self._generate_random_string(1000)
        reply, error, error_code = self.driver.custom_post(path, payload={'search': random_chars})
        self.assertEqual(0, error_code)

    def test_invalid_payload_key(self):
        """Search tool invalid key instead of `search` in POST request"""
        self.backup.apply_backup(backup_name)
        Network.create(self.driver, 0, {'name': f'test_net'})
        path = 'api/search/get/nms=0'
        reply, error, error_code = self.driver.custom_post(path, payload={'delete': 'test'})
        self.assertEqual(0, error_code, msg=f'Reply error_code is {error_code}')
        self.assertEqual(0, len(reply), msg=f'Expected 0 entries in reply, got {len(reply)}')

    def test_invalid_table_row(self):
        """Search tool invalid table or row"""
        self.backup.apply_backup(backup_name)
        Network.create(self.driver, 0, {'name': f'test_net'})
        path = 'api/search/get/nms=1'
        reply, error, error_code = self.driver.custom_post(path, payload={'search': 'test'})
        self.assertEqual(NO_SUCH_ROW, error_code, msg=f'Reply error_code is {error_code}')
        path = 'api/search/get/uhp=0'
        reply, error, error_code = self.driver.custom_post(path, payload={'search': 'test'})
        self.assertEqual(NO_SUCH_TABLE, error_code, msg=f'Expected -1 error_code, got {error_code}')

    def test_investigator_search_supported_unsupported(self):
        """Check that every supported object can be found via investigator search. Unsupported object cannot be found"""
        names = self.options.get('search_tool_unique_names')
        self.backup.apply_backup(backup_name)
        self.nms.send_param('name', names.get('nms'))
        path = 'api/search/get/nms=0?search=investigator'
        Network.create(self.driver, 0, {'name': names.get('network')})
        Teleport.create(self.driver, 0, {'name': names.get('teleport'), 'sat_name': 'sat'})
        Controller.create(
            self.driver,
            0,
            {'name': names.get('controller'), 'mode': ControllerModes.MF_HUB, 'teleport': 'teleport:0'},
        )
        Controller.create(
            self.driver,
            0,
            {'name': 'best_hubless', 'mode': ControllerModes.HUBLESS_MASTER, 'teleport': 'teleport:0'},
        )
        Vno.create(self.driver, 0, {'name': names.get('vno')})
        Station.create(self.driver, 0, {
            'name': names.get('station'),
            'serial': 10000
        })
        SwUpload.create(self.driver, 0, {'name': names.get('sw_upload'), 'sw_file': 'dummy_soft.240'})
        SrController.create(self.driver, 0, {'name': names.get('sr_controller')})
        SrTeleport.create(self.driver, 0, {'name': names.get('sr_teleport'), 'teleport': 'teleport:0'})
        Device.create(self.driver, 0, {'name': names.get('device')})
        BalController.create(self.driver, 0, {'name': names.get('bal_controller')})
        Scheduler.create(self.driver, 0, {'name': names.get('scheduler')})
        check_obj = [
            'nms', 'network', 'controller', 'vno', 'station', 'sw_upload', 'sr_controller', 'sr_teleport', 'device',
            'bal_controller', 'scheduler',
        ]
        for _obj, name in {next_obj: names.get(next_obj) for next_obj in check_obj}.items():
            with self.subTest(f'Searching supported {_obj} named {name}'):
                reply, error, error_code = self.driver.custom_post(path, payload={'search': name})
                self.assertEqual(NO_ERROR, error_code, msg=f'Error code {error_code}')
                self.assertEqual(1, len(reply), msg=f'Got reply length of {len(reply)} instead of 1')
                self.assertEqual(_obj, reply[0].get('url').split('=')[0], msg=f'Expected {_obj} in url')
                self.assertEqual(name, reply[0].get('name'), msg=f'Expected {name} in reply name key')
                self.assertEqual(name, reply[0].get('string'), msg=f'Expected {name} in reply string key')
        # Trying to search unsupported objects
        Server.create(self.driver, 0, {'name': names.get('server')})
        gr = UserGroup.create(self.driver, 0, {'name': names.get('group')})
        User.create(self.driver, gr.get_id(), {'name': names.get('user')})
        Alert.create(self.driver, 0, {'name': names.get('alert'), 'popup': True})
        Dashboard.create(self.driver, 0, {'name': names.get('dashboard')})
        Service.create(self.driver, 0, {'name': names.get('service')})
        Shaper.create(self.driver, 0, {'name': names.get('shaper')})
        Policy.create(self.driver, 0, {'name': names.get('policy')})
        SrLicense.create(self.driver, 0, {'name': names.get('sr_license')})
        Profile.create(self.driver, 0, {'name': names.get('profile_set')})
        Camera.create(self.driver, 0, {'name': names.get('camera')})
        SchRange.create(self.driver, 0, {'name': names.get('sch_range')})
        SchService.create(self.driver, 0, {'name': names.get('sch_service')})
        SchTask.create(self.driver, 0, {'name': names.get('sch_task')})
        Qos.create(self.driver, 0, {'name': names.get('qos')})
        _obj_dict = {next_obj: names.get(next_obj) for next_obj in names.keys() if next_obj not in check_obj}
        for _obj, name in _obj_dict.items():
            with self.subTest(f'Searching unsupported {_obj} named {name}'):
                reply, error, error_code = self.driver.custom_post(path, payload={'search': name})
                self.assertEqual(NO_ERROR, error_code, msg=f'Error code {error_code}')
                self.assertEqual(0, len(reply), msg=f'Got reply length of {len(reply)} instead of 0')

    @staticmethod
    def _generate_random_string(length=50):
        whitespace = ' \t\n\r\v\f'
        ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
        ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ascii_letters = ascii_lowercase + ascii_uppercase
        digits = '0123456789'
        punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
        printable = digits + ascii_letters + punctuation + whitespace
        random_string = ''
        for _ in range(length):
            # Keep appending random characters using chr(x)
            random_string += printable[random.randint(0, len(printable) - 1)]
        return random_string
