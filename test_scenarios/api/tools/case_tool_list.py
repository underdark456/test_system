import random
import time

from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.enum_types_constants import AlertModesStr, ControllerModes, Checkbox, StationModes
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
from src.nms_entities.basic_entities.qos import Qos
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
from src.nms_entities.paths_manager import PathsManager
from test_scenarios.api.abstract_case import _AbstractCase
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api.tools'
backup_name = 'default_config.txt'


class ApiToolListCase(_AbstractCase):
    """API List tool case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __execution_time__ = 75  # approximate case execution time in seconds
    __express__ = True
    NUM_OF_NETS = 124
    backup = None

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.options = OptionsProvider.get_options(options_path)

    def test_list_networks(self):
        """List tool without options. Test all network IDs in the response"""
        self.backup.apply_backup(backup_name)
        net_ids = set()
        for i in range(ApiToolListCase.NUM_OF_NETS):
            Network.create(self.driver, 0, {'name': f'net-{i}'})
            net_ids.add(f'net-{i}')
        path = PathsManager.network_list(self.driver.get_type(), 0)
        reply, error, error_code = self.driver.custom_get(path)
        self.assertEqual(error_code, 0)
        list_ids = set()
        for n in reply:
            list_ids.add(n.get('name', None))
        for net_id in net_ids:
            self.assertIn(net_id, list_ids)

    def test_list_networks_with_skip(self):
        """List tool command with `list_skip` option"""
        self.backup.apply_backup(backup_name)
        for i in range(ApiToolListCase.NUM_OF_NETS):
            Network.create(self.driver, 0, params={'name': f'net-{i}'})
        path = PathsManager.network_list(self.driver.get_type(), 0, skip=10)
        reply, error, error_code = self.driver.custom_get(path)
        self.assertEqual(error_code, 0)
        self.assertEqual(len(reply), ApiToolListCase.NUM_OF_NETS - 10)

    def test_list_networks_with_max(self):
        """List tool command with `list_max` option"""
        self.backup.apply_backup(backup_name)
        for i in range(ApiToolListCase.NUM_OF_NETS):
            Network.create(self.driver, 0, {'name': f'net-{i}'})
        path = PathsManager.network_list(self.driver.get_type(), 0, max_=10)
        reply, error, error_code = self.driver.custom_get(path)
        self.assertEqual(error_code, 0)
        self.assertEqual(len(reply), 10)

    def test_list_networks_with_values(self):
        """List tool command with valid `list_vars`"""
        self.backup.apply_backup(backup_name)
        for i in range(5):
            Network.create(self.driver, 0, {
                'name': f'net-{i}',
                'alert_mode': AlertModesStr.INHERIT
            })
        path = PathsManager.network_list(self.driver.get_type(), 0, vars_=['alert_mode', ])
        reply, error, error_code = self.driver.custom_get(path)
        self.assertEqual(error_code, 0)
        for i in range(len(reply)):
            self.assertEqual(reply[i]['%row'], i)
            self.assertEqual(reply[i]['alert_mode'], AlertModesStr.INHERIT)

    def test_list_networks_all_options(self):
        """List tool command with `list_skip`, `list_max` and `list_vars` options"""
        self.backup.apply_backup(backup_name)
        for i in range(ApiToolListCase.NUM_OF_NETS):
            Network.create(self.driver, 0, {'name': f'net-{i}'})
        path = PathsManager.network_list(self.driver.get_type(), 0, skip=15, max_=3, vars_=['name', ])
        reply, error, error_code = self.driver.custom_get(path)
        self.assertEqual(error_code, 0)
        expected_nets = ('net-111', 'net-112', 'net-113')
        for net in reply:
            self.assertIn(net['name'], expected_nets)

    def test_list_networks_invalid_options(self):
        """List tool command with invalid options"""
        self.backup.apply_backup(backup_name)
        for i in range(ApiToolListCase.NUM_OF_NETS):
            Network.create(self.driver, 0, {'name': f'net-{i}'})
        for obj in self.options['invalid_numbers']:
            path = PathsManager.network_list(self.driver.get_type(), 0, skip=obj)
            res, _, error_code = self.driver.custom_get(path)
            self.assertEqual(NO_ERROR, error_code)
        for obj in self.options['invalid_numbers']:
            path = PathsManager.network_list(self.driver.get_type(), 0, max_=obj)
            _, _, error_code = self.driver.custom_get(path)
            self.assertEqual(NO_ERROR, error_code)
        path = PathsManager.network_list(self.driver.get_type(), 0, vars_=self.options['invalid_vars'])
        _, _, error_code = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_code)

    def test_many_invalid_vars(self):
        """List tool with list_vars option containing 300 random invalid vars"""
        self.backup.apply_backup(backup_name)
        Network.create(self.driver, 0, params={'name': f'test_net'})
        random_vars = [self._generate_random_string() for _ in range(300)]
        path = PathsManager.network_list(self.driver.get_type(), 0, vars_=random_vars)
        res, error, error_code = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_code)

    def test_many_valid_vars(self):
        """List tool with list_vars option containing over 120 valid vars"""
        self.backup.apply_backup(backup_name)
        Network.create(self.driver, 0, {'name': 'test_net'})
        Teleport.create(self.driver, 0, {'name': 'test_tp'})
        Controller.create(self.driver, 0, {
            'name': 'test_ctrl',
            'mode': ControllerModes.MF_HUB,
            'teleport': 'teleport:0',
        })
        Vno.create(self.driver, 0, {'name': 'test_vno'})
        Station.create(self.driver, 0, {
            'name': 'test_stn',
            'enable': Checkbox.ON,
            'serial': 1,
            'rx_controller': 'controller:0',
            'mode': StationModes.STAR,
        })
        vars_ = self.options.get('station_tool_vars')
        path = PathsManager.station_list(self.driver.get_type(), 0, vars_=vars_)
        res, error, error_code = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_code, msg=f'Error code returned {error_code}')
        for key in vars_:
            if key not in res[0].keys():
                self.fail(f'var {key} is passed in url, but not received in response')
        self.assertEqual(
            len(vars_),
            len(res[0].keys()) - 1,
            msg=f'Number of vars requested {len(vars_)}, number of values returned {len(res[0].keys()) - 1}'
        )

    def test_all_objects_list(self):
        """Getting list of every entity in the corresponding parent, i.e. controllers in network"""
        # ~12 seconds
        self.backup.apply_backup('case_database_performance.txt')
        # explicit wait to let config take place
        time.sleep(5)
        nets = Network.network_list(self.driver, 0)
        self.assertEqual(128, len(nets), msg=f'Expected 128 networks in list, got {len(nets)}')
        servers = Server.server_list(self.driver, 0)
        self.assertEqual(64, len(servers), msg=f'Expected 64 servers in list, got {len(servers)}')
        groups = UserGroup.user_group_list(self.driver, 0)
        self.assertEqual(512, len(groups), msg=f'Expected 512 groups in list, got {len(groups)}')
        users = User.user_list(self.driver, 0)
        self.assertEqual(512, len(users), msg=f'Expected 512 users in list, got {len(users)}')
        alerts = Alert.alert_list(self.driver, 0)
        self.assertEqual(2048, len(alerts), msg=f'Expected 2048 alerts in list, got {len(alerts)}')
        dashes = Dashboard.dashboard_list(self.driver, 0, parent_type='nms')
        self.assertEqual(256, len(dashes), msg=f'Expected 256 dashboards in list, got {len(dashes)}')

        teleports = Teleport.teleport_list(self.driver, 0)
        self.assertEqual(128, len(teleports), msg=f'Expected 128 teleports in list, got {len(teleports)}')
        ctrls = Controller.controller_list(self.driver, 0)
        self.assertEqual(512, len(ctrls), msg=f'Expected 512 controllers in list, got {len(ctrls)}')
        vnos = Vno.vno_list(self.driver, 0)
        self.assertEqual(512, len(vnos), msg=f'Expected 512 vnos in list, got {len(vnos)}')
        services = Service.service_list(self.driver, 0)
        self.assertEqual(512, len(services), msg=f'Expected 512 services in list, got {len(services)}')
        qos = Qos.qos_list(self.driver, 0)
        self.assertEqual(1024, len(qos), msg=f'Expected 512 qos in list, got {len(qos)}')
        shapers = Shaper.shaper_list(self.driver, 0)
        self.assertEqual(2048, len(shapers), msg=f'Expected 2048 shapers in list, got {len(shapers)}')
        policies = Policy.policy_list(self.driver, 0)
        self.assertEqual(512, len(policies), msg=f'Expected 512 policies in list, got {len(policies)}')
        polrules = PolicyRule.policy_rules_list(self.driver, 0)
        self.assertEqual(10000, len(polrules), msg=f'Expected 10000 polrules in list, got {len(polrules)}')
        accesses_net = Access.access_list(self.driver, 0, parent_type='network')
        self.assertEqual(512, len(accesses_net), msg=f'Expected 512 accesses in list, got {len(accesses_net)}')
        sr_ctrls = SrController.sr_controller_list(self.driver, 0)
        self.assertEqual(32, len(sr_ctrls), msg=f'Expected 512 sr_controllers, got {len(sr_ctrls)}')
        sr_teleports = SrTeleport.sr_teleport_list(self.driver, 0)
        self.assertEqual(128, len(sr_teleports), msg=f'Expected 128 sr_teleports in list, got {len(sr_teleports)}')
        devices = Device.device_list(self.driver, 0)
        self.assertEqual(2048, len(devices), msg=f'Expected 2048 devices in list, got {len(devices)}')
        licenses = SrLicense.sr_license_list(self.driver, 0)
        self.assertEqual(256, len(licenses), msg=f'Expected 256 licenses in list, got {len(licenses)}')
        bal_ctrls = BalController.bal_controller_list(self.driver, 0)
        self.assertEqual(32, len(bal_ctrls), msg=f'Expected 32 bal_controllers in list, got {len(bal_ctrls)}')
        profiles = Profile.profile_list(self.driver, 0)
        self.assertEqual(128, len(profiles), msg=f'Expected 128 profiles in list, got {len(profiles)}')
        sw_uploads = SwUpload.sw_upload_list(self.driver, 0)
        self.assertEqual(32, len(sw_uploads), msg=f'Expected 32 sw_uploads in list, got {len(sw_uploads)}')
        cameras = Camera.camera_list(self.driver, 0)
        self.assertEqual(64, len(cameras), msg=f'Expected 64 cameras in list, got {len(cameras)}')
        schedulers = Scheduler.scheduler_list(self.driver, 0)
        self.assertEqual(64, len(schedulers), msg=f'Expected 64 schedulers in list, got {len(schedulers)}')
        sch_ranges = SchRange.scheduler_range_list(self.driver, 0)
        self.assertEqual(64, len(sch_ranges), msg=f'Expected 64 sch_ranges in list, got {len(sch_ranges)}')
        sch_ranges = SchRange.scheduler_range_list(self.driver, 0)
        self.assertEqual(64, len(sch_ranges), msg=f'Expected 64 sch_ranges in list, got {len(sch_ranges)}')
        sch_services = SchService.scheduler_service_list(self.driver, 0)
        self.assertEqual(128, len(sch_services), msg=f'Expected 128 sch_services in list, got {len(sch_services)}')
        # Cannot get all stations at once due to 16Mbytes limit, calling list method with the same vars as in browser
        stations = Station.station_list(self.driver, 0, vars_=['name', 'enable', 'serial', 'mode', 'rx_controller'])
        self.assertEqual(32768, len(stations), msg=f'Expected 32768 stations in list, got {len(stations)}')
        # Cannot get all routes at once due to 18Mbytes limit, getting them by using max and skip extended params
        routes1 = ControllerRoute.controller_route_list(self.driver, 0, max_=30000)
        routes2 = ControllerRoute.controller_route_list(self.driver, 0, skip=30000)
        self.assertEqual(30000, len(routes1), msg=f'Expected 30000 routes in list, got {len(routes1)}')
        self.assertEqual(35000, len(routes2), msg=f'Expected 35000 routes in list, got {len(routes2)}')
        rip_routers = ControllerRip.controller_rip_list(self.driver, 0)
        self.assertEqual(256, len(rip_routers), msg=f'Expected 256 rip_routers in list, got {len(rip_routers)}')
        port_maps = ControllerPortMap.port_map_list(self.driver, 0)
        self.assertEqual(16000, len(port_maps), msg=f'Expected 16000 port_maps in list, got {len(port_maps)}')

        # Having big config in NMS can affect other test methods, loading default
        self.backup.apply_backup(backup_name)
        time.sleep(5)  # explicit wait to let it be applied completely

    @classmethod
    def tear_down_class(cls):
        if cls.backup is not None:
            # Just in case if 'case_database_performance.txt' is still loaded as it can affect test operations
            cls.backup.apply_backup('default_config.txt')
            time.sleep(5)

    @staticmethod
    def _generate_random_string(max_length=50):
        whitespace = ' \t\n\r\v\f'
        ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
        ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ascii_letters = ascii_lowercase + ascii_uppercase
        digits = '0123456789'
        punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
        printable = digits + ascii_letters + punctuation + whitespace
        random_string = ''
        for _ in range(random.randint(1, max_length+1)):
            # Keep appending random characters using chr(x)
            random_string += printable[random.randint(0, len(printable) - 1)]
        return random_string
