import random
import time

from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.exceptions import NmsDownloadException
from src.file_manager.file_manager import FileManager
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
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider
from utilities.random_objects.random_objects import RandomObjects

options_path = 'test_scenarios.backup.config_confirmation'
backup_name = 'default_config.txt'


class ConfigConfirmationCase(CustomTestCase):
    """Created config with all tables filled in is in place after saving and loading it"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'  # qos added, fixed same username and equal IP found in another station
    __execution_time = 5850  # approximate test case execution time in seconds
    __express__ = False

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        fm = FileManager()
        fm.upload_uhp_software('dummy_soft.240')

    def test_save_load_save_load(self):
        """Created objects and their parameters are in place after saving and loading config two times"""
        self.dashboards = {}
        self.groups = {}
        self.users = {}
        self.accesses = {}
        self.servers = {}
        self.alerts = {}
        self.networks = {}
        self.teleports = {}
        self.shapers = {}
        self.policies = {}
        self.rules = {}
        self.vnos = {}
        self.services = {}
        self.qos = {}
        self.sr_controllers = {}
        self.sr_licenses = {}
        self.sr_teleports = {}
        self.devices = {}
        self.bal_controllers = {}
        self.cameras = {}
        self.profiles = {}
        self.controllers = {}
        self.port_maps = {}
        self.rip_routers = {}
        self.routes = {}
        self.sw_uploads = {}
        self.stations = {}
        self.scheduler = {}
        self.sch_ranges = {}
        self.sch_services = {}
        num_sr_ctrls = 0
        num_bal_ctrls = 0
        num_of_cams = 0
        num_of_pol_rules = 0
        num_of_portmap = 0
        num_of_rip_router = 0
        num_of_sw_upload = 0
        num_of_schedulers = 0

        # Dashoboard section
        for dash_id in range(self.options.get('number_of_dashboard')):
            dash_params = RandomObjects.get_dashboard(dash_id)
            new_dash = Dashboard.create(self.driver, 0, params=dash_params)
            self.dashboards[new_dash.get_id()] = dash_params

        # User Groups and Users section
        for group_id in range(1, self.options.get('number_of_group')):  # self.options.get('number_of_group')):
            group_params = RandomObjects.get_group(group_id)
            new_group = UserGroup.create(self.driver, 0, params=group_params)
            self.groups[new_group.get_id()] = group_params

            user_params = RandomObjects.get_user(new_group.get_id())
            new_user = User.create(self.driver, new_group.get_id(), params=user_params)
            self.users[new_user.get_id()] = user_params

            access_params = RandomObjects.get_access(new_group.get_id())
            new_access = Access.create(self.driver, 0, params=access_params)
            self.accesses[new_access.get_id()] = access_params

        for server_id in range(self.options.get('number_of_server')):
            server_params = RandomObjects.get_server(server_id)
            new_server = Server.create(self.driver, 0, params=server_params)
            self.servers[new_server.get_id()] = server_params

        for alert_id in range(self.options.get('number_of_alert')):
            alert_params = RandomObjects.get_alert(alert_id)
            new_alert = Alert.create(self.driver, 0, params=alert_params)
            self.alerts[new_alert.get_id()] = alert_params

        for net_id in range(self.options.get('number_of_network')):
            # Alerts specify in 50% of cases
            if random.random() > 0.5:
                alert_id = random.choice(list(self.alerts.keys()))
            else:
                alert_id = None
            net_params = RandomObjects.get_network(net_id, alert_id)
            new_net = Network.create(self.driver, 0, params=net_params)
            self.networks[new_net.get_id()] = net_params

            tp_params = RandomObjects.get_teleport(net_id)
            new_tp = Teleport.create(self.driver, net_id, params=tp_params)
            self.teleports[new_tp.get_id()] = tp_params

            # Shapers section
            for shp in range(16):
                shp_params = RandomObjects.get_shaper(net_id * 16 + shp)
                new_shp = Shaper.create(self.driver, net_id, params=shp_params)
                self.shapers[new_shp.get_id()] = shp_params

            # Policies section
            for pol in range(4):
                pol_params = {'name': f'pol-{net_id * 4 + pol}'}
                new_pol = Policy.create(self.driver, net_id, params=pol_params)
                self.assertIsNotNone(new_pol.get_id())
                self.policies[new_pol.get_id()] = pol_params
                for r in range(20):
                    if num_of_pol_rules >= self.options.get('number_of_polrule'):
                        continue
                    rule_params = RandomObjects.get_rule(r + 1)
                    new_rule = PolicyRule.create(self.driver, new_pol.get_id(), params=rule_params)
                    self.rules[new_rule.get_id()] = rule_params
                    num_of_pol_rules += 1

            # Services section
            for ser in range(4):
                ser_params = RandomObjects.get_service(
                    net_id * 4 + ser,
                    # hub_policy_id=random.choice([*range(net_id * 4, net_id * 4 + 3)]),
                    # stn_policy_id=random.choice([*range(net_id * 4, net_id * 4 + 3)]),
                    # hub_shaper_id=random.choice([*range(net_id * 16, net_id * 16 + 15)]),
                    # stn_shaper_id=random.choice([*range(net_id * 16, net_id * 16 + 15)]),
                )
                new_ser = Service.create(self.driver, net_id, params=ser_params)
                self.services[new_ser.get_id()] = ser_params

            # QoS section
            for qos in range(8):
                qos_params = RandomObjects.get_qos(
                    net_id * 8 + qos,
                    policy_id=random.choice([*range(net_id * 4, net_id * 4 + 3)]),
                    shaper_id=random.choice([*range(net_id * 16, net_id * 16 + 15)]),
                )
                new_qos = Qos.create(self.driver, net_id, params=qos_params)
                self.qos[new_qos.get_id()] = qos_params
            # Controller section
            for ctrl in range(4):
                ctrl_params = RandomObjects.get_controller(
                    net_id * 4 + ctrl,
                    0,
                    net_id,
                )
                new_ctrl = Controller.create(self.driver, net_id, params=ctrl_params)
                self.controllers[new_ctrl.get_id()] = ctrl_params

                # Port map section (default number of port map is 16000, assigning each controller 32 port maps while
                # there are enough rows in the table
                if num_of_portmap < self.options.get('number_of_port_map'):
                    port_map_params = RandomObjects.get_port_map()
                    new_port_map = ControllerPortMap.create(self.driver, new_ctrl.get_id(), params=port_map_params)
                    self.port_maps[new_port_map.get_id()] = port_map_params
                    num_of_portmap += 1
                # RIP router section
                if num_of_rip_router < self.options.get('number_of_rip_router'):
                    rip_router_params = RandomObjects.get_rip_router(new_ser.get_id())
                    new_rip_router = ControllerRip.create(
                        self.driver,
                        new_ctrl.get_id(),
                        params=rip_router_params
                    )
                    self.rip_routers[new_rip_router.get_id()] = rip_router_params
                    num_of_rip_router += 1

                # First controller gets 39 routes, the rest get 63 routes
                if new_ctrl.get_id() == 0:
                    for i in range(39):
                        route_params = RandomObjects.get_route_ip_address(new_ser.get_id())
                        new_route = ControllerRoute.create(self.driver, new_ctrl.get_id(), params=route_params)
                        self.routes[new_route.get_id()] = route_params
                else:
                    for i in range(63):
                        route_params = RandomObjects.get_route_ip_address(new_ser.get_id())
                        new_route = ControllerRoute.create(self.driver, new_ctrl.get_id(), params=route_params)
                        self.routes[new_route.get_id()] = route_params

            if num_of_sw_upload < self.options.get('number_of_sw_upload'):
                sw_up_params = RandomObjects.get_sw_upload(net_id)
                sw_up_params['file_name'] = 'dummy_soft.240'
                new_sw_up = SwUpload.create(self.driver, net_id, params=sw_up_params)
                self.sw_uploads[new_sw_up.get_id()] = sw_up_params
                num_of_sw_upload += 1

            # SR licenses section
            for lic in range(2):
                lic_params = RandomObjects.get_sr_license(net_id * 2 + lic)
                new_lic = SrLicense.create(self.driver, net_id, params=lic_params)
                self.assertIsNotNone(new_lic.get_id())
                self.sr_licenses[new_lic.get_id()] = lic_params

            # VNO section
            for vno in range(4):
                # Alerts specify in 50% of cases
                if random.random() > 0.5:
                    alert_id = random.choice(list(self.alerts.keys()))
                else:
                    alert_id = None
                vno_params = RandomObjects.get_vno(
                    net_id * 4 + vno,
                    alert_id,
                    hub_shaper_id=random.choice([*range(net_id * 16, net_id * 16 + 15)]),
                    stn_shaper_id=random.choice([*range(net_id * 16, net_id * 16 + 15)]),
                )
                new_vno = Vno.create(self.driver, net_id, params=vno_params)
                self.vnos[new_vno.get_id()] = vno_params

                # Station section (64 station in each VNO)
                for stn in range(64):
                    stn_params = RandomObjects.get_station_mesh(
                        (net_id * 4 + vno) * 64 + stn,
                        random.randint(net_id * 4, net_id * 4 + 3)
                    )
                    new_stn = Station.create(self.driver, new_vno.get_id(), params=stn_params)
                    self.stations[new_stn.get_id()] = stn_params
                    # Each station gets a route
                    stn_route_params = RandomObjects.get_route_ip_address(new_ser.get_id())
                    new_route = StationRoute.create(self.driver, new_stn.get_id(), params=stn_route_params)
                    self.routes[new_route.get_id()] = stn_route_params

            # SR controllers section
            if num_sr_ctrls < self.options.get('number_of_sr_controller'):
                # Alerts specify in 50% of cases
                if random.random() > 0.5:
                    alert_id = random.choice(list(self.alerts.keys()))
                else:
                    alert_id = None
                sr_params = RandomObjects.get_sr_controller(net_id, alert_id)
                new_sr = SrController.create(self.driver, net_id, params=sr_params)
                self.sr_controllers[new_sr.get_id()] = sr_params
                num_sr_ctrls += 1
                # SR teleports section
                for sr_tp in range(4):
                    # Alerts specify in 50% of cases
                    if random.random() > 0.5:
                        alert_id = random.choice(list(self.alerts.keys()))
                    else:
                        alert_id = None
                    sr_tp_params = RandomObjects.get_sr_teleport(
                        net_id * 4 + sr_tp,
                        net_id,  # teleport ID
                        alert_id
                    )
                    new_sr_tp = SrTeleport.create(self.driver, net_id, params=sr_tp_params)
                    self.sr_teleports[new_sr_tp.get_id()] = sr_tp_params

                    # Devices section
                    for dev in range(16):
                        dev_params = RandomObjects.get_device((net_id * 4 + sr_tp) * 16 + dev)
                        new_dev = Device.create(self.driver, new_sr_tp.get_id(), params=dev_params)
                        self.devices[new_dev.get_id()] = dev_params

            # Balance controllers section
            if num_bal_ctrls < self.options.get('number_of_bal_controller'):
                bal_params = RandomObjects.get_bal_controller(net_id)
                new_bal = BalController.create(self.driver, net_id, params=bal_params)
                self.bal_controllers[new_bal.get_id()] = bal_params
                num_bal_ctrls += 1

            # Cameras section
            if num_of_cams < self.options.get('number_of_camera'):
                cam_params = RandomObjects.get_camera(net_id)
                new_cam = Camera.create(self.driver, net_id, params=cam_params)
                self.cameras[new_cam.get_id()] = cam_params
                num_of_cams += 1

            # Profiles section
            pro_params = RandomObjects.get_profile_set(net_id)
            new_pro = Profile.create(self.driver, net_id, params=pro_params)
            self.profiles[new_pro.get_id()] = pro_params

            # Schedulers section
            if num_of_schedulers < self.options.get('number_of_scheduler'):
                sch_params = RandomObjects.get_scheduler(net_id)
                new_sch = Scheduler.create(self.driver, net_id, params=sch_params)
                self.scheduler[new_sch.get_id()] = sch_params
                num_of_schedulers += 1

                # Scheduler Range section
                sch_range_params = RandomObjects.get_sch_range(new_sch.get_id())
                new_sch_range = SchRange.create(self.driver, new_sch.get_id(), params=sch_range_params)
                self.sch_ranges[new_sch_range.get_id()] = sch_range_params

                # Scheduler Service section
                for i in range(2):
                    sch_ser_params = RandomObjects.get_sch_service(net_id * 2 + i)
                    new_sch_ser = SchService.create(self.driver, new_sch.get_id(), params=sch_ser_params)
                    self.sch_services[new_sch_ser.get_id()] = sch_ser_params
        self.info('Creating first backup...')
        try:
            self.backup.create_backup(self.options.get('config_name1'))
        except NmsDownloadException:
            self.info('Downloading first backup expectedly failed due to the file size')
            pass

        self.info('Loading first backup from NMS...')
        result, error, error_code = self.driver.custom_post(
            'api/object/write/nms=0',
            payload={'command': "15728662", 'load_filename': self.options.get('config_name1')}
        )
        self.assertEqual(NO_ERROR, error_code)
        self.info('First backup loaded, sleeping for 60 seconds...')
        time.sleep(60)
        self.info('Creating second backup...')
        try:
            self.backup.create_backup(self.options.get('config_name2'))
        except NmsDownloadException:
            self.info('Downloading second backup expectedly failed due to the file size')
            pass
        self.info('Loading second backup from NMS...')
        result, error, error_code = self.driver.custom_post(
            'api/object/write/nms=0',
            payload={'command': "15728662", 'load_filename': self.options.get('config_name2')}
        )
        self.assertEqual(NO_ERROR, error_code)
        self.info('Second backup loaded, sleeping 60 seconds...')
        time.sleep(60)
        self.info('Checking entries...')
        self.check_stations()
        self.check_groups()
        self.check_users()
        self.check_accesses()
        self.check_servers()
        self.check_alerts()
        self.check_networks()
        self.check_teleports()
        self.check_shapers()
        self.check_vnos()
        self.check_policies()
        self.check_rules()
        self.check_services()
        self.check_qos()
        self.check_sr_controllers()
        self.check_sr_licenses()
        self.check_sr_teleports()
        self.check_devices()
        self.check_bal_controllers()
        self.check_cameras()
        self.check_profiles()
        self.check_controllers()
        self.check_port_maps()
        self.check_rip_routers()
        self.check_routes()
        self.check_sw_uploads()
        self.check_schedulers()
        self.check_sch_ranges()
        self.check_sch_services()
        self.check_dashboards()

    def check_stations(self):
        for stn_id, values_dict in self.stations.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/station={stn_id}')
            self.assertEqual(0, error_code, msg=f'Get station:{stn_id} reply error_code={error_code}')
            for key, value in values_dict.items():
                if key == 'set_alert' and values_dict.get('alert_mode') == 'Specify':
                    # `set_alert` is stored as `alert:<row> <alert_name>
                    self.assertEqual(
                        value,
                        reply.get(key).split()[0],
                        msg=f'set_alert expected {value}, got {reply.get(key).split()[0]}'
                    )
                elif key == 'set_alert':
                    continue
                elif key == 'rx_controller':
                    self.assertEqual(
                        value,
                        reply.get(key).split()[0],
                        msg=f'rx_controller expected {value}, got {reply.get(key).split()[0]}'
                    )
                elif key == 'dns_timeout' and values_dict.get('dns_caching') == 'OFF':
                    continue
                elif isinstance(reply.get(key), str):
                    self.assertEqual(
                        value.lower(),
                        reply.get(key).rstrip().lower(),
                        msg=f'{key} expected {value}, got {reply.get(key).rstrip()}'
                    )
                else:
                    self.assertEqual(
                        value,
                        reply.get(key),
                        msg=f'{key} expected {value}, got {reply.get(key)}'
                    )

    def check_groups(self):
        for group_id, values_dict in self.groups.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/group={group_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                self.assertEqual(value, reply.get(key).rstrip())

    def check_users(self):
        for user_id, values_dict in self.users.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/user={user_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                # Do not check password as NMS returns '**********' for that value
                if key == 'password':
                    continue
                self.assertEqual(value, reply.get(key).rstrip())

    def check_accesses(self):
        for access_id, values_dict in self.accesses.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/access={access_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if key == 'group':
                    self.assertEqual(value, reply.get(key).split()[0])
                else:
                    self.assertEqual(value, reply.get(key).rstrip())

    def check_servers(self):
        for server_id, values_dict in self.servers.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/server={server_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                self.assertEqual(value, reply.get(key).rstrip())

    def check_alerts(self):
        for alert_id, values_dict in self.alerts.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/alert={alert_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if key in ('file_name', 'repeat_sound') and values_dict.get('sound') == 'OFF':
                    continue
                if key == 'script_file' and values_dict.get('run_script') == 'OFF':
                    continue
                self.assertEqual(value, reply.get(key).rstrip())

    def check_networks(self):
        for net_id, values_dict in self.networks.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/network={net_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if key == 'set_alert' and values_dict.get('alert_mode') == 'Specify':
                    # `set_alert` is stored as `alert:<row> <alert_name>
                    self.assertEqual(value, reply.get(key).split()[0])
                elif key == 'set_alert':
                    continue
                else:
                    self.assertEqual(value, reply.get(key))

    def check_teleports(self):
        for tp_id, values_dict in self.teleports.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/teleport={tp_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                # `sat_lon_deg` and `time_zone` are saved as strings, but NMS returns integers
                if key in ('sat_lon_deg', 'time_zone', 'tx_offset', 'rx1_offset', 'rx2_offset'):
                    self.assertEqual(int(value), reply.get(key))
                elif isinstance(reply.get(key), int):
                    self.assertEqual(value, reply.get(key))
                else:
                    self.assertEqual(value, reply.get(key).rstrip())

    def check_shapers(self):
        for shp_id, values_dict in self.shapers.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/shaper={shp_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if (key == 'max_cir' or key == 'max_slope') and values_dict.get('max_enable') == 'OFF':
                    continue
                elif (key == 'min_cir' or key == 'down_slope' or key == 'up_slope') \
                        and values_dict.get('min_enable') == 'OFF':
                    continue
                elif (key == 'night_cir' or key == 'night_start' or key == 'night_end') and values_dict.get(
                        'night_enable') == 'OFF':
                    continue
                elif (key == 'wfq1' or key == 'wfq2' or key == 'wfq3' or key == 'wfq4'
                      or key == 'wfq5' or key == 'wfq6') and values_dict.get('wfq_enable') == 'OFF':
                    continue
                elif isinstance(reply.get(key), str):
                    self.assertEqual(value, reply.get(key).rstrip())
                else:
                    self.assertEqual(value, reply.get(key))

    def check_vnos(self):
        for vno_id, values_dict in self.vnos.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/vno={vno_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if key == 'set_alert' and values_dict.get('alert_mode') == 'Specify':
                    # `set_alert` is stored as `alert:<row> <alert_name>
                    self.assertEqual(value, reply.get(key).split()[0])
                elif key == 'set_alert':
                    continue
                elif key == 'hub_shaper' or key == 'stn_shaper':
                    self.assertEqual(value, reply.get(key).split()[0])
                else:
                    self.assertEqual(value, reply.get(key))

    def check_policies(self):
        for pol_id, values_dict in self.policies.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/policy={pol_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                self.assertEqual(value, reply.get(key).rstrip())

    def check_rules(self):
        for rule_id, values_dict in self.rules.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/polrule={rule_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if isinstance(reply.get(key), str):
                    self.assertEqual(value, reply.get(key).rstrip())
                else:
                    self.assertEqual(value, reply.get(key))

    def check_services(self):
        for ser_id, values_dict in self.services.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/service={ser_id}')
            self.assertEqual(NO_ERROR, error_code)
            for key, value in values_dict.items():
                if isinstance(reply.get(key), str):
                    self.assertEqual(value, reply.get(key).rstrip())
                else:
                    self.assertEqual(value, reply.get(key))

    def check_qos(self):
        for qos_id, values_dict in self.qos.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/qos={qos_id}')
            self.assertEqual(NO_ERROR, error_code)
            for key, value in values_dict.items():
                if key in ('shaper', 'policy', ):
                    self.assertEqual(value, reply.get(key).split()[0])
                elif key == 'policy' and values_dict.get('priority') != 'Policy':
                    continue
                elif isinstance(reply.get(key), str):
                    self.assertEqual(value, reply.get(key).rstrip())
                else:
                    self.assertEqual(value, reply.get(key))

    def check_sr_controllers(self):
        for sr_id, values_dict in self.sr_controllers.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/sr_controller={sr_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if key == 'set_alert' and values_dict.get('alert_mode') == 'Specify':
                    # `set_alert` is stored as `alert:<row> <alert_name>
                    self.assertEqual(value, reply.get(key).split()[0])
                elif key == 'set_alert':
                    continue
                elif (key == 'max_tx_down' or key == 'max_rx_down' or key == 'max_tx_fault'
                      or key == 'max_rx_fault' or key == 'ctr_timeout') and values_dict.get('check_ctr') == 'OFF':
                    continue
                elif (key == 'min_stn_up' or key == 'min_ctr_up' or key == 'stn_timeout') and \
                        values_dict.get('check_stn') == 'OFF':
                    continue
                elif (key == 'hub_cn_min' or key == 'stn_cn_min' or key == 'own_cn_min' or key == 'cn_timeout') and \
                        values_dict.get('check_cn') == 'OFF':
                    continue
                elif key == 'max_sw_fails' and values_dict.get('check_sw_fails') == 'OFF':
                    continue
                elif (key == 'min_idle' or key == 'idle_timeout') and values_dict.get('check_idle') == 'OFF':
                    continue
                elif isinstance(reply.get(key), str):
                    self.assertEqual(value, reply.get(key).rstrip())
                else:
                    self.assertEqual(value, reply.get(key))

    def check_sr_teleports(self):
        for tp_id, values_dict in self.sr_teleports.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/sr_teleport={tp_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if key == 'set_alert' and values_dict.get('alert_mode') == 'Specify':
                    # `set_alert` is stored as `alert:<row> <alert_name>
                    self.assertEqual(value, reply.get(key).split()[0])
                elif key == 'set_alert':
                    continue
                elif key == 'teleport':
                    self.assertEqual(value, reply.get(key).split()[0])
                else:
                    self.assertEqual(value, reply.get(key).rstrip())

    def check_sr_licenses(self):
        for lic_id, values_dict in self.sr_licenses.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/sr_license={lic_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                self.assertEqual(value, reply.get(key).rstrip())

    def check_devices(self):
        for dev_id, values_dict in self.devices.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/device={dev_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if key == 'set_alert' and values_dict.get('alert_mode') == 'Specify':
                    # `set_alert` is stored as `alert:<row> <alert_name>
                    self.assertEqual(value, reply.get(key).split()[0])
                elif key == 'set_alert':
                    continue
                elif (key == 'dem1_power' or key == 'dem1_ref') and values_dict.get('dem1_connect') != 'Teleport_RX':
                    continue
                elif (key == 'dem2_power' or key == 'dem2_ref') and values_dict.get('dem2_connect') != 'Teleport_RX':
                    continue
                # `tx_level_adj` is stored as float in NMS
                elif key == 'tx_level_adj':
                    self.assertEqual(float(value), reply.get(key))
                else:
                    self.assertEqual(value, reply.get(key))

    def check_bal_controllers(self):
        for bal_id, values_dict in self.bal_controllers.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/bal_controller={bal_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if (key == 'free_fault' or key == 'down_time') and values_dict.get('free_down') == 'OFF':
                    continue
                elif isinstance(reply.get(key), str):
                    self.assertEqual(value, reply.get(key).rstrip())
                elif key in ('load_higher1', 'load_higher2'):
                    self.assertEqual(int(value), reply.get(key))
                else:
                    self.assertEqual(value, reply.get(key))

    def check_cameras(self):
        for cam_id, values_dict in self.cameras.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/camera={cam_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                self.assertEqual(value, reply.get(key))

    def check_profiles(self):
        for set_id, values_dict in self.profiles.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/profile_set={set_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if key.startswith('lvl_offset'):
                    self.assertEqual(float(value), reply.get(key))
                elif key.startswith('modcod'):
                    # TODO: add modcod check (NMS returns a string)
                    continue
                else:
                    self.assertEqual(value, reply.get(key))

    def check_controllers(self):
        for ctrl_id, values_dict in self.controllers.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/controller={ctrl_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():

                if key == 'set_alert' and values_dict.get('alert_mode') == 'Specify':
                    # `set_alert` is stored as `alert:<row> <alert_name>
                    self.assertEqual(value, reply.get(key).split()[0])
                elif key == 'set_alert':
                    continue
                elif key == 'rx_voltage' and values_dict.get('rx_dc_power') == 'OFF':
                    continue
                elif key == 'dns_timeout' and values_dict.get('dns_caching') == 'OFF':
                    continue
                elif key == 'ctl_key' and values_dict.get('ctl_protect') == 'OFF':
                    continue
                elif key == 'teleport':
                    self.assertEqual(value, reply.get(key).split()[0])
                elif isinstance(reply.get(key), str):
                    self.assertEqual(value, reply.get(key).rstrip())
                elif key == 'tx_level_adj':
                    self.assertEqual(float(value), reply.get(key))
                else:
                    self.assertEqual(value, reply.get(key))

    def check_port_maps(self):
        for port_map_id, values_dict in self.port_maps.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/port_map={port_map_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                self.assertEqual(value, reply.get(key))

    def check_rip_routers(self):
        for rip_router_id, values_dict in self.rip_routers.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/rip_router={rip_router_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if key == 'service':
                    self.assertEqual(value, reply.get(key).split()[0])
                elif isinstance(reply.get(key), str):
                    self.assertEqual(value, reply.get(key).rstrip())
                else:
                    self.assertEqual(value, reply.get(key))

    def check_routes(self):
        for route_id, values_dict in self.routes.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/route={route_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if key == 'service':
                    self.assertEqual(value, reply.get(key).split()[0])
                elif key == 'stn_vlan' and values_dict.get('override_vlan') == 'OFF':
                    self.assertEqual(None, reply.get(key))
                elif isinstance(reply.get(key), str):
                    self.assertEqual(value.lower(), reply.get(key).rstrip().lower())
                else:
                    self.assertEqual(value, reply.get(key))

    def check_sw_uploads(self):
        for sw_upload_id, values_dict in self.sw_uploads.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/sw_upload={sw_upload_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if key == 'tx_controller':
                    self.assertEqual(value, reply.get(key).split()[0])
                else:
                    self.assertEqual(value, reply.get(key))

    def check_schedulers(self):
        for sch_id, values_dict in self.scheduler.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/scheduler={sch_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                self.assertEqual(value, reply.get(key))

    def check_sch_ranges(self):
        for sch_range_id, values_dict in self.sch_ranges.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/sch_range={sch_range_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                self.assertEqual(value, reply.get(key))

    def check_sch_services(self):
        for sch_ser_id, values_dict in self.sch_services.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/sch_service={sch_ser_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                if key.startswith('tx_modcod'):
                    # TODO: add modcod check (NMS returns a string)
                    continue
                elif isinstance(reply.get(key), str):
                    self.assertEqual(value, reply.get(key).rstrip())
                else:
                    self.assertEqual(value, reply.get(key))

    def check_dashboards(self):
        for dash_id, values_dict in self.dashboards.items():
            reply, error, error_code = self.driver.custom_get(f'api/object/get/dashboard={dash_id}')
            self.assertEqual(0, error_code)
            for key, value in values_dict.items():
                self.assertEqual(value, reply.get(key))
