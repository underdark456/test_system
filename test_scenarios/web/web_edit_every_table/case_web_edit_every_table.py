import ipaddress
import time

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.access import Access
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.bal_controller import BalController
from src.nms_entities.basic_entities.camera import Camera
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_port_map import ControllerPortMap
from src.nms_entities.basic_entities.controller_rip import ControllerRip
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.dashboard import Dashboard
from src.nms_entities.basic_entities.device import Device
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.profile import Profile
from src.nms_entities.basic_entities.scheduler import Scheduler
from src.nms_entities.basic_entities.scheduler_range import SchRange
from src.nms_entities.basic_entities.scheduler_service import SchService
from src.nms_entities.basic_entities.server import Server
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.sr_controller import SrController
from src.nms_entities.basic_entities.sr_license import SrLicense
from src.nms_entities.basic_entities.sr_teleport import SrTeleport
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.web.web_edit_every_table'
backup_name = 'case_database_performance.txt'


class WebEditEveryTableCase(CustomTestCase):
    """WEB interface edit each table: first, middle, and last entries"""

    __author__ = 'dkudryashov'
    __version__ = '0.1'
    __execution_time__ = 220  # approximate case execution time in seconds

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path), driver_id='case_web_edit_every_table'
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        time.sleep(5)  # totally make sure that config is loaded

        cls.options = OptionsProvider.get_options(options_path)

    def _edit_name(self, entity, first: int, middle: int, last: int, parent_id=0):
        for n in (first, middle, last):
            _obj = entity(self.driver, parent_id, n)
            _obj.send_param('name', f'new-{n}')
            self.assertFalse(_obj.has_param_error('name'))

    def test_edit_access(self):
        """Edit second, middle, and last entries of Access table"""
        total = self.options.get('number_of_access')
        for n in (1, total // 2, total - 1):
            _obj = Access(self.driver, 0, n)
            _obj.send_param('use', True)
            self.assertTrue(_obj.read_param('use'))

    def test_edit_alert(self):
        """Edit first, middle, and last entries of Alert table"""
        total = self.options.get('number_of_alert')
        self._edit_name(Alert, 0, total // 2, total - 1)

    def test_edit_bal_controller(self):
        """Edit first, middle, and last entries of Bal Controller table"""
        total = self.options.get('number_of_bal_controller')
        self._edit_name(BalController, 0, total // 2, total - 1)

    def test_edit_camera(self):
        """Edit first, middle, and last entries of Camera table"""
        total = self.options.get('number_of_camera')
        self._edit_name(Camera, 0, total // 2, total - 1)

    def test_edit_controller(self):
        """Edit first, middle, and last entries of Controller table"""
        total = self.options.get('number_of_controller')
        self._edit_name(Controller, 0, total // 2, total - 1)

    def test_edit_dashboard(self):
        """Edit first, middle, and last entries of Dashboard table"""
        total = self.options.get('number_of_dashboard')
        self._edit_name(Dashboard, 0, total // 2, total - 1)

    def test_edit_device(self):
        """Edit first, middle, and last entries of Device table"""
        total = self.options.get('number_of_device')
        self._edit_name(Device, 0, total // 2, total - 1)

    def test_edit_group(self):
        """Edit second, middle, and last entries of Group table"""
        total = self.options.get('number_of_group')
        self._edit_name(UserGroup, 1, total // 2, total - 1)

    def test_edit_network(self):
        """Edit first, middle, and last entries of Network table"""
        total = self.options.get('number_of_network')
        self._edit_name(Network, 0, total // 2, total - 1)

    def test_edit_policy(self):
        """Edit first, middle, and last entries of Policy table"""
        total = self.options.get('number_of_policy')
        self._edit_name(Policy, 0, total // 2, total - 1)

    def test_edit_pol_rule(self):
        """Edit first, middle, and last entries of Policy Rules table"""
        total = self.options.get('number_of_polrule')
        for n in (0, total // 2, total - 1):
            _obj = PolicyRule(self.driver, 0, n)
            _obj.send_param('sequence', total + n + 1)
            self.assertEqual(str(total + n + 1), _obj.read_param('sequence'))

    def test_edit_port_map(self):
        """Edit first, middle, and last entries of Port Map table"""
        total = self.options.get('number_of_port_map')
        for n in (0, total // 2, total - 1):
            _obj = ControllerPortMap(self.driver, 0, n)
            _obj.send_param('external_port', total + n + 1)
            self.assertEqual(str(total + n + 1), _obj.read_param('external_port'))

    def test_edit_profile_Set(self):
        """Edit first, middle, and last entries of Profile Set table"""
        total = self.options.get('number_of_profile_set')
        self._edit_name(Profile, 0, total // 2, total - 1)

    def test_edit_rip_router(self):
        """Edit first, middle, and last entries of RIP router table"""
        total = self.options.get('number_of_rip_router')
        _ip = ipaddress.IPv4Address('127.0.0.1')
        for n in (0, total // 2, total - 1):
            _obj = ControllerRip(self.driver, 0, n)
            _obj.send_param('rip_next_hop', str(_ip))
            self.assertEqual(str(_ip), _obj.read_param('rip_next_hop'))
            _ip += 1

    def test_edit_route(self):
        """Edit first, middle, and last entries of Route table"""
        total = self.options.get('number_of_route')
        _ip = ipaddress.IPv4Address('127.10.0.1')
        for n in (0, total // 2, total - 1):
            _obj = ControllerRoute(self.driver, 0, n)
            time.sleep(5)
            _obj.send_param('ip', str(_ip))
            self.assertEqual(str(_ip), _obj.read_param('ip'))
            _ip += 1

    def test_edit_server(self):
        """Edit first, middle, and last entries of Server table"""
        total = self.options.get('number_of_server')
        self._edit_name(Server, 0, total // 2, total - 1)

    def test_edit_service(self):
        """Edit first, middle, and last entries of Service table"""
        total = self.options.get('number_of_service')
        self._edit_name(Service, 0, total // 2, total - 1)

    def test_edit_shaper(self):
        """Edit first, middle, and last entries of Shaper table"""
        total = self.options.get('number_of_shaper')
        self._edit_name(Shaper, 0, total // 2, total - 1)

    def test_edit_sr_controller(self):
        """Edit first, middle, and last entries of SR Controller table"""
        total = self.options.get('number_of_sr_controller')
        self._edit_name(SrController, 0, total // 2, total - 1)

    def test_edit_sr_license(self):
        """Edit first, middle, and last entries of SR License table"""
        total = self.options.get('number_of_sr_license')
        self._edit_name(SrLicense, 0, total // 2, total - 1)

    def test_edit_sr_teleport(self):
        """Edit first, middle, and last entries of SR Teleport table"""
        total = self.options.get('number_of_sr_teleport')
        self._edit_name(SrTeleport, 0, total // 2, total - 1)

    def test_edit_station(self):
        """Edit first, middle, and last entries of Station table"""
        total = self.options.get('number_of_station')
        self._edit_name(Station, 0, total // 2, total - 1)

    def test_edit_sw_upload(self):
        """Edit first, middle, and last entries of SW Upload table"""
        total = self.options.get('number_of_sw_upload')
        self._edit_name(SwUpload, 0, total // 2, total - 1)

    def test_edit_teleport(self):
        """Edit first, middle, and last entries of Teleport table"""
        total = self.options.get('number_of_teleport')
        self._edit_name(Teleport, 0, total // 2, total - 1)

    def test_edit_user(self):
        """Edit second, middle, and last entries of User table"""
        total = self.options.get('number_of_user')
        self._edit_name(User, 1, total // 2, total - 1)

    def test_edit_vno(self):
        """Edit first, middle, and last entries of VNO table"""
        total = self.options.get('number_of_vno')
        self._edit_name(Vno, 0, total // 2, total - 1)

    def test_edit_scheduler(self):
        """Edit first, middle, and last entries of Scheduler table"""
        total = self.options.get('number_of_scheduler')
        self._edit_name(Scheduler, 0, total // 2, total - 1)

    def test_edit_sch_range(self):
        """Edit first, middle, and last entries of Sch Range table"""
        total = self.options.get('number_of_sch_range')
        self._edit_name(SchRange, 0, total // 2, total - 1)

    def test_edit_sch_service(self):
        """Edit first, middle, and last entries of Sch Service table"""
        total = self.options.get('number_of_sch_service')
        self._edit_name(SchService, 0, total // 2, total - 1)
