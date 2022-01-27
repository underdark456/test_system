import random
import time

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import TdmaSearchModes, ControllerModes, ControlModes, AlertModes, \
    StationModes, RouteTypes, TdmaInputModes, PriorityTypes, RouteIds
from src.exceptions import ObjectNotCreatedException
from src.file_manager.file_manager import FileManager
from src.nms_entities.basic_entities.access import Access
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.camera import Camera
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.dashboard import Dashboard
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.profile import Profile
from src.nms_entities.basic_entities.qos import Qos
from src.nms_entities.basic_entities.server import Server
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.nms_entities.basic_entities.service import Service
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.database_operations.create_delete_loop'
backup_name = 'default_config.txt'


class MultipleCreateDeleteCase(CustomTestCase):
    """The scenario creates a config with a lot of NMS entities and deletes them in a cycle"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __execution_time__ = 18600  # approximate test case execution time is seconds
    __express__ = False  # this test case is not intended to be part of express tests

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.options = OptionsProvider.get_options(options_path)
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.fm = FileManager()
        cls.fm.delete_uhp_software('dummy_soft.240')

    def test_create_delete_cycle(self):
        """Create maximum number of NMS objects and deletes them in a cycle"""
        # The `number_of_test_cycle` is given in the options.

        # The built NMS config is the following:
        #     - maximum number of `User groups` (512 by default) with one user in each;
        #     - maximum number of `Servers` (64 by default);
        #     - maximum number of `Alerts` (2048 by default);
        #     - maximum number of NMS `Accesses` (1024 by default);
        #     - maximum number of Networks (128 by default);
        #         - each network has a Teleport (summing up to 128 by default);
        #         - each network has 16 Shapers (summing up to 2048 by default);
        #         - each network has 4 Controllers (summing ip to 512 by default);
        #             - each controller has 62 routes (IP addresses);
        #         - each network has 4 VNOs with bound Hub shaper and Station shaper (summing up to 512 by default);
        #             - each VNO has 64 Stations;
        #                 - each station has 1 route (IP address);
        #         - each network has 4 Policies (summing up to 512 by default);
        #             - each policy has 19 rules (summing up to 9728);
        #         - each network has 4 Services (summing up to 512 by default) with random number of access groups;

        st_time_all = time.perf_counter()
        for i in range(self.options.get('number_of_test_cycle')):
            st_time = time.perf_counter()
            self.shaper_names = set()
            self.controller_names = set()
            self.station_names = set()
            self.station_serial = set()
            self.vno_names = set()
            self.ser_names = set()
            self.qos_names = set()
            self.random_ipv4 = set()
            number_of_routes = 0  # number of creating routes is not maximum
            rest_number_of_cameras = self.options.get('number_of_camera')
            self.info(f'Create delete cycle number {i+1}')
            # User Groups and Users section
            for group_id in range(1, self.options.get('number_of_group')):
                new_group = UserGroup.create(self.driver, 0, params={'name': f'group-{group_id}'})
                self.assertIsNotNone(new_group.get_id())
                new_user = User.create(self.driver, new_group.get_id(), params={
                    'name': f'user-{group_id}',
                    'email': f'user_0@group{group_id}.com',
                    'first_name': f'user{group_id}',
                    'last_name': f'{group_id}_user_{group_id}',
                    'password': random.randint(10000, 100000)
                })
                self.assertIsNotNone(new_user.get_id())

            # Servers section
            for server_id in range(self.options.get('number_of_server')):
                new_server = Server.create(self.driver, 0, params={
                    'name': f'server-{server_id}',
                    'ip': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
                    'enable': 1,
                    'location': f'msk-{server_id}-msk'
                })
                self.assertIsNotNone(new_server.get_id())

            # Alerts section
            for alert_id in range(self.options.get('number_of_alert')):
                new_alert = Alert.create(self.driver, 0, params={
                    'name': f'alert-{alert_id}',
                    'priority': random.randint(0, 2),
                    'popup': True,
                })
                self.assertIsNotNone(new_alert.get_id())

            # Accesses section
            for access_id in range(1, self.options.get('number_of_group')):
                new_access = Access.create(self.driver, 0, params={
                    'group': f'group:{access_id}',
                    'edit': random.randint(0, 1),
                    'use': random.randint(0, 1)
                })
                self.assertIsNotNone(new_access.get_id())

            # Networks section
            for net_id in range(self.options.get('number_of_network')):
                new_net = Network.create(self.driver, 0, params={
                    'name': f'net-{net_id}',
                    'alert_mode': random.randint(0, 1),
                    'traffic_scale': random.randint(0, 50000),
                    'level_scale': random.randint(0, 35),
                    'dev_password': random.randint(10000, 100000),
                })
                self.assertIsNotNone(new_net.get_id())

                # Cameras section
                if rest_number_of_cameras > 0:
                    new_cam = Camera.create(self.driver, net_id, params=self.get_random_camera(net_id))
                    self.assertIsNotNone(new_cam.get_id())
                    rest_number_of_cameras -= 1

                # Profile section
                new_profile = Profile.create(self.driver, net_id, params=self.get_random_profile(net_id))
                self.assertIsNotNone(new_profile.get_id())

                # Teleports section
                new_tp = Teleport.create(self.driver, net_id, params=self.get_random_teleport(net_id))
                self.assertIsNotNone(new_tp.get_id())

                # Shapers section
                for s in range(16):
                    new_shp = Shaper.create(self.driver, net_id, params=self.get_random_shaper())
                    self.assertIsNotNone(new_shp.get_id())

                # Policies section
                for p in range(4):
                    new_pol = Policy.create(self.driver, net_id, params={'name': f'pol-{net_id}-{p}'})
                    self.assertIsNotNone(new_pol.get_id())
                    # Policy rule section (19 rules in each Policy)
                    for r in range(19):
                        new_rule = PolicyRule.create(
                            self.driver,
                            new_pol.get_id(),
                            params=self.get_random_rule(sequence=r + 1)
                        )
                        self.assertIsNotNone(new_rule.get_id())

                # Services section
                for ser in range(4):
                    new_ser = Service.create(self.driver, net_id, params=self.get_random_service())
                    self.assertIsNotNone(new_ser.get_id())

                # Qos section
                for qos in range(8):
                    new_qos = Qos.create(self.driver, net_id, params=self.get_random_qos(net_id))
                    self.assertIsNotNone(new_qos.get_id())

                # Controllers section
                for ctrl in range(4):
                    new_ctrl = Controller.create(
                        self.driver,
                        net_id,
                        params=self.get_random_controller(net_id)
                    )
                    self.assertIsNotNone(new_ctrl.get_id())

                    # Controller routing section
                    for cr in range(62):
                        new_route = ControllerRoute.create(
                            self.driver,
                            new_ctrl.get_id(),
                            params=self.get_random_ctrl_route(new_net.get_id())
                        )
                        self.assertIsNotNone(new_route.get_id())
                        number_of_routes += 1

                # VNOs section
                for vno in range(4):
                    try:
                        new_vno = Vno.create(self.driver, net_id, params=self.get_random_vno(net_id))
                        self.assertIsNotNone(new_vno.get_id())
                    except ObjectNotCreatedException:
                        break

                    # VNO stations section
                    for stn in range(64):
                        try:
                            params = self.get_random_station(net_id)
                            new_stn = Station.create(
                                self.driver,
                                new_vno.get_id(),
                                params=params
                            )
                        except ObjectNotCreatedException as exc:
                            print(f'Station is not created, params={params}')
                            raise ObjectNotCreatedException(exc)
                        self.assertIsNotNone(new_stn.get_id())

                        # Station routes section
                        new_route = StationRoute.create(
                            self.driver,
                            new_stn.get_id(),
                            params=self.get_random_stn_route(new_net.get_id())
                        )
                        self.assertIsNotNone(new_route.get_id())
                        number_of_routes += 1

            # Dashboard section
            for dash_id in range(self.options.get('number_of_dashboard')):
                new_dash = Dashboard.create(self.driver, 0, params={'name': f'dash-{dash_id}'})
                self.assertIsNotNone(new_dash.get_id())

            # Deleting the created objects
            users_id = list(range(1, self.options.get('number_of_group')))
            random.shuffle(users_id)
            for user_id in users_id:
                User(self.driver, user_id, user_id).delete()

            accesses_id = list(range(1, self.options.get('number_of_group')))
            random.shuffle(accesses_id)
            for access_id in accesses_id:
                Access(self.driver, 0, access_id).delete()

            groups_id = list(range(1, self.options.get('number_of_group')))
            random.shuffle(groups_id)
            for group_id in groups_id:
                UserGroup(self.driver, 0, group_id).delete()

            servers_id = list(range(self.options.get('number_of_server')))
            random.shuffle(servers_id)
            for server_id in servers_id:
                Server(self.driver, 0, server_id).delete()

            alerts_id = list(range(self.options.get('number_of_alert')))
            random.shuffle(alerts_id)
            for alert_id in alerts_id:
                Alert(self.driver, 0, alert_id).delete()

            for dash_id in range(self.options.get('number_of_dashboard')):
                Dashboard(self.driver, 0, dash_id).delete()

            # Alternative way to delete all the created routes. The original method is extremely slow
            for j in range(number_of_routes):
                path = f'api/object/delete/route={j}'
                self.driver.custom_get(path)

            # Deleting the rest of objects
            for net_id in range(self.options.get('number_of_network')):
                vnos = Vno.vno_list(self.driver, net_id)
                for vno_id in vnos:
                    stations = Station.station_list(self.driver, vno_id)
                    for stn_id in stations:
                        self.driver.custom_get(f'api/object/delete/station={stn_id}')
                    Vno(self.driver, net_id, vno_id).delete()

                ctrls = Controller.controller_list(self.driver, net_id)
                for ctrl_id in ctrls:
                    Controller(self.driver, net_id, ctrl_id).delete()

                services = Service.service_list(self.driver, net_id)
                for ser_id in services:
                    Service(self.driver, net_id, ser_id).delete()

                qoses = Qos.qos_list(self.driver, net_id)
                for qos_id in qoses:
                    Qos(self.driver, net_id, qos_id).delete()

                policies = Policy.policy_list(self.driver, net_id)
                for pol_id in policies:
                    rules = PolicyRule.policy_rules_list(self.driver, pol_id)
                    for rule_id in rules:
                        PolicyRule(self.driver, pol_id, rule_id).delete()
                    Policy(self.driver, net_id, pol_id).delete()

                shapers = Shaper.shaper_list(self.driver, net_id)
                for shp_id in shapers:
                    Shaper(self.driver, net_id, shp_id).delete()

                teleports = Teleport.teleport_list(self.driver, net_id)
                for tp_id in teleports:
                    Teleport(self.driver, net_id, tp_id).delete()

                cameras = Camera.camera_list(self.driver, net_id)
                for cam_id in cameras:
                    Camera(self.driver, net_id, cam_id).delete()

                profiles = Profile.profile_list(self.driver, net_id)
                for pro_id in profiles:
                    Profile(self.driver, net_id, pro_id).delete()

                Network(self.driver, 0, net_id).delete()

            self.info(f'Create delete cycle time: {time.perf_counter() - st_time} seconds')

        self.info(f'{self.options.get("number_of_test_cycle")} iterations execution time '
                  f'is {time.perf_counter() - st_time_all} seconds')

    @staticmethod
    def get_random_teleport(net_id):
        params = {
            'name': f'tp-{net_id}',
            'sat_name': f'sat-{net_id}',
            'sat_lon_deg': random.randint(-179, 179),
            'sat_lon_min': random.randint(0, 59),
            'lat_deg': random.randint(0, 89),
            'lat_min': random.randint(0, 59),
            'lat_south': random.randint(0, 1),
            'lon_deg': random.randint(0, 179),
            'lon_min': random.randint(0, 59),
            'lon_west': random.randint(0, 1),
            'time_zone': random.randint(-12, 12),
            'tx_lo': random.randint(0, 33000000),
            'tx_offset': random.randint(-10000, 10000),
            'tx_spi': random.randint(0, 1),
            'rx1_lo': random.randint(0, 33000000),
            'rx1_offset': random.randint(-10000, 10000),
            'rx1_spi': random.randint(0, 1),
            'rx2_lo': random.randint(0, 33000000),
            'rx2_offset': random.randint(-10000, 10000),
            'rx2_spi': random.randint(0, 1),
            'dvb_search': random.randint(0, 10000),
            'tdma_search': random.choice([*TdmaSearchModes()])
        }
        return params

    def get_random_shaper(self):
        name = f'shp-{random.randint(1, 100000000)}'
        while name in self.shaper_names:
            name = f'shp-{random.randint(1, 100000000)}'
        self.shaper_names.add(name)
        params = {
            'name': name,
            'template': random.randint(0, 1),
            'cir': random.randint(1, 250000),
            'up_queue': random.randint(0, 7),
            'max_enable': random.randint(0, 1),
            'max_cir': random.randint(1, 250000),
            'max_slope': random.randint(1, 16),
            'min_enable': random.randint(0, 1),
            'min_cir': random.randint(1, 250000),
            'down_slope': random.randint(1, 16),
            'up_slope': random.randint(1, 16),
            'wfq_enable': random.randint(0, 1),
            'wfq1': 35,
            'wfq2': 15,
            'wfq3': 10,
            'wfq4': 20,
            'wfq5': 10,
            'wfq6': 10,
            'night_enable': random.randint(0, 1),
            'night_cir': random.randint(1, 250000),
            'night_start': random.randint(0, 23),
            'night_end': random.randint(0, 23)
        }
        return params

    def get_random_controller(self, net_id):
        name = f'ctrl-{random.randint(1, 99999999)}'
        while name in self.controller_names:
            name = f'ctrl-{random.randint(1, 99999999)}'
        self.controller_names.add(name)
        params = {
            'name': name,
            'mode': ControllerModes.MF_HUB,
            'control': random.choice([*ControlModes()]),
            'up_timeout': random.randint(10, 250),
            'allow_local': random.randint(0, 1),
            'alert_mode': random.choice([AlertModes.OFF, AlertModes.INHERIT, ]),
            'traffic_scale': random.randint(0, 50000),
            'level_scale': random.randint(0, 35),
            'device_ip': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'device_mask': f'/{random.randint(1, 32)}',
            'device_vlan': random.randint(0, 4095),
            'device_gateway': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'teleport': f'teleport:{net_id}',
            'tx_10m': random.randint(0, 1),
            'tx_dc_power': random.randint(0, 1),
            'rx_10m': random.randint(0, 1),
            'rx_dc_power': random.randint(0, 1),
            'rx_voltage': random.randint(0, 1),
            'tx_on': random.randint(0, 1),
            'tx_level': random.randint(1, 46),
            'tlc_enable': random.randint(0, 1),
            'tlc_max_lvl': random.randint(1, 46),
            'tlc_net_own': random.randint(0, 16),
            'tlc_avg_min': random.randint(0, 16),
            'tlc_cn_stn': random.randint(0, 23),
            'tlc_cn_hub': random.randint(0, 23),
            'rx1_input': random.randint(0, 2),
            'rx1_frq': random.randint(950000, 33000000),
            'rx1_sr': random.randint(100, 200000),
            'check_rx': random.randint(0, 1),
            'own_cn_low': random.randint(0, 25),
            'own_cn_high': random.randint(26, 50),
            'rx2_input': random.randint(0, 2),
            'rx2_frq': random.randint(950000, 33000000),
            'rx2_sr': random.randint(100, 200000),
            'stn_number': random.randint(1, 2040),
            'frame_length': random.choice([i for i in range(16, 252, 4)]),
            'slot_length': random.randint(2, 15),
            'roaming_enable': random.randint(0, 1),
            'roaming_slots': random.randint(1, 32),
            'tdma_input': TdmaInputModes.RX1,  # leave RX1 to be compatible with all UHP models
            'tdma_sr': random.randint(100, 11000),
            'tdma_roll': random.randint(0, 1),
            'mf1_en': random.randint(0, 1),
            'mf2_en': random.randint(0, 1),
            'mf3_en': random.randint(0, 1),
            'mf4_en': random.randint(0, 1),
            'mf5_en': random.randint(0, 1),
            'mf6_en': random.randint(0, 1),
            'mf7_en': random.randint(0, 1),
            'mf8_en': random.randint(0, 1),
            'mf9_en': random.randint(0, 1),
            'mf10_en': random.randint(0, 1),
            'mf11_en': random.randint(0, 1),
            'mf12_en': random.randint(0, 1),
            'mf13_en': random.randint(0, 1),
            'mf14_en': random.randint(0, 1),
            'mf15_en': random.randint(0, 1),
            'mf16_en': random.randint(0, 1),
            'mf1_rx': random.randint(950000, 33000000),
            'mf1_tx': random.randint(950000, 33000000),
            'mf2_rx': random.randint(950000, 33000000),
            'mf2_tx': random.randint(950000, 33000000),
            'mf3_rx': random.randint(950000, 33000000),
            'mf3_tx': random.randint(950000, 33000000),
            'mf4_rx': random.randint(950000, 33000000),
            'mf4_tx': random.randint(950000, 33000000),
            'mf5_rx': random.randint(950000, 33000000),
            'mf5_tx': random.randint(950000, 33000000),
            'mf6_rx': random.randint(950000, 33000000),
            'mf6_tx': random.randint(950000, 33000000),
            'mf7_rx': random.randint(950000, 33000000),
            'mf7_tx': random.randint(950000, 33000000),
            'mf8_rx': random.randint(950000, 33000000),
            'mf8_tx': random.randint(950000, 33000000),
            'mf9_rx': random.randint(950000, 33000000),
            'mf9_tx': random.randint(950000, 33000000),
            'mf10_rx': random.randint(950000, 33000000),
            'mf10_tx': random.randint(950000, 33000000),
            'mf11_rx': random.randint(950000, 33000000),
            'mf11_tx': random.randint(950000, 33000000),
            'mf12_rx': random.randint(950000, 33000000),
            'mf12_tx': random.randint(950000, 33000000),
            'mf13_rx': random.randint(950000, 33000000),
            'mf13_tx': random.randint(950000, 33000000),
            'mf14_rx': random.randint(950000, 33000000),
            'mf14_tx': random.randint(950000, 33000000),
            'mf15_rx': random.randint(950000, 33000000),
            'mf15_tx': random.randint(950000, 33000000),
            'mf16_rx': random.randint(950000, 33000000),
            'mf16_tx': random.randint(950000, 33000000)
        }
        return params

    def get_random_station(self, net_id):
        # mode = random.choice([*StationModes()])
        name = f'stn-{random.randint(1, 100000000)}'
        while name in self.station_names:
            name = f'stn-{random.randint(1, 100000000)}'
        self.station_names.add(name)
        serial = random.randint(1, 99999999)
        while serial in self.station_serial:
            serial = random.randint(1, 99999999)
        self.station_serial.add(serial)
        params = {
            'name': name,
            'enable': random.randint(0, 1),
            'serial': serial,
            'rx_controller': f'controller:{random.randint(net_id * 4, net_id * 4 + 3)}',
            'mode': StationModes.STAR,
            'alert_mode': random.choice([AlertModes.OFF, AlertModes.INHERIT, ]),
            'traffic_scale': random.randint(0, 50000),
            'level_scale': random.randint(0, 35),
            'customer': random.randint(1, 10000000),
            'phone1': f'+7{random.randint(1000000, 9999999)}',
            'phone2': f'+7{random.randint(1000000, 9999999)}',
            'fixed_location': True,
            'lat_deg': random.randint(0, 89),
            'lat_min': random.randint(0, 59),
            'lat_south': random.randint(0, 1),
            'lon_deg': random.randint(0, 179),
            'lon_min': random.randint(0, 59),
            'lon_west': random.randint(0, 1),
            'time_zone': random.randint(-12, 12),
        }
        return params

    def get_random_vno(self, net_id):
        name = f'vno-{random.randint(1, 100000000)}'
        while name in self.vno_names:
            name = f'vno-{random.randint(1, 100000000)}'
        self.vno_names.add(name)
        params = {
            'name': name,
            'alert_mode': random.randint(0, 1),
            'traffic_scale': random.randint(0, 50000),
            'level_scale': random.randint(0, 35),
            'hub_shaper': f'shaper:{random.randint(net_id * 16, net_id * 16 + 15)}',
            'stn_shaper': f'shaper:{random.randint(net_id * 16, net_id * 16 + 15)}'
        }
        return params

    def get_random_qos(self, net_id):
        name = f'qos-{random.randint(1, 100000000)}'
        while name in self.qos_names:
            name = f'qos-{random.randint(1, 100000000)}'
        self.qos_names.add(name)
        # Choosing policy in 50% of cases
        if random.random() < 0.5:
            priority = PriorityTypes.POLICY
        else:
            priority = random.randint(0, 6)
        params = {
            'name': name,
            'priority': priority,
            'policy': f'policy:{random.randint(net_id * 4, net_id * 4 + 3)}',
            'shaper': f'shaper:{random.randint(net_id * 16, net_id * 16 + 15)}',
        }
        return params

    def get_random_service(self):
        name = f'ser-{random.randint(1, 100000000)}'
        while name in self.ser_names:
            name = f'ser-{random.randint(1, 100000000)}'
        self.ser_names.add(name)
        params = {
            'name': name,
            'hub_vlan': random.randint(0, 4095),
            'stn_vlan': random.randint(0, 4095),
            'ctr_normal': random.randint(0, 1),
            'ctr_gateway': random.randint(0, 1),
            'ctr_mesh': random.randint(0, 1),
            'stn_normal': random.randint(0, 1),
            'stn_gateway': random.randint(0, 1),
            'stn_mesh': random.randint(0, 1),
            'group_id': random.randint(0, 999),
            'mesh_routing': random.randint(0, 2),
            'nonlocal': random.randint(0, 1),
            'rip_announced': random.randint(0, 1)
        }
        return params

    def get_random_ctrl_route(self, net_id):
        random_ipv4 = ".".join(map(str, (random.randint(1, 255) for _ in range(4))))
        while random_ipv4 in self.random_ipv4:
            random_ipv4 = ".".join(map(str, (random.randint(1, 255) for _ in range(4))))
        self.random_ipv4.add(random_ipv4)
        mode = random.choice([RouteTypes.IP_ADDRESS])
        params = {
            "type": mode,
            "ip": random_ipv4,
            "mask": "/32",
            "gateway": "0.0.0.0",
            "v6_ip": "::",
            "v6_mask": "/120",
            "v6_gateway": "::",
            "override_vlan": random.randint(0, 1),
            "service": f"service:{random.randint(net_id * 4, net_id * 4 + 3)}",
            "stn_vlan": random.randint(0, 4095),
            "id": random.randint(0, 3)
        }
        return params

    def get_random_stn_route(self, net_id):
        random_ipv4 = ".".join(map(str, (random.randint(1, 255) for _ in range(4))))
        while random_ipv4 in self.random_ipv4:
            random_ipv4 = ".".join(map(str, (random.randint(1, 255) for _ in range(4))))
        self.random_ipv4.add(random_ipv4)
        mode = random.choice([RouteTypes.IP_ADDRESS])
        params = {
            "type": mode,
            "ip": random_ipv4,
            "mask": "/32",
            "gateway": "0.0.0.0",
            "v6_ip": "::",
            "v6_mask": "/120",
            "v6_gateway": "::",
            "override_vlan": random.randint(0, 1),
            "service": f"service:{random.randint(net_id * 4, net_id * 4 + 3)}",
            "stn_vlan": random.randint(0, 4095),
            "id": RouteIds.PRIVATE,
        }
        return params

    @staticmethod
    def get_random_rule(sequence):
        # Only action SET QUEUE so far
        params = {
            "sequence": sequence,
            "type": 1,
            "action_type": 2,
            "queue": random.randint(0, 6),
        }
        return params

    def get_random_camera(self, net_id):
        random_ipv4 = ".".join(map(str, (random.randint(1, 255) for _ in range(4))))
        while random_ipv4 in self.random_ipv4:
            random_ipv4 = ".".join(map(str, (random.randint(1, 255) for _ in range(4))))
        self.random_ipv4.add(random_ipv4)
        params = {
            'name': f'cam-{net_id}',
            'url': random_ipv4
        }
        return params

    @staticmethod
    def get_random_profile(net_id):
        params = {
            'name': f'pro-{net_id}',
            'mode2': random.randint(0, 6),
            'rx_frq2': random.randint(950000, 33000000),
            'tx_frq2': random.randint(950000, 33000000),
            'sym_rate2': random.randint(100, 200000),
            'demod_power2': random.randint(0, 1),
            'lvl_offset2': random.randint(-12, 12),
            'frame_len2': 64,
            'slot_len2': 8,
            'stn_number2': 10,
            'modcod2': 1,
            'mode3': random.randint(0, 6),
            'rx_frq3': random.randint(950000, 33000000),
            'tx_frq3': random.randint(950000, 33000000),
            'sym_rate3': random.randint(100, 200000),
            'demod_power3': random.randint(0, 1),
            'lvl_offset3': random.randint(-12, 12),
            'frame_len3': 64,
            'slot_len3': 8,
            'stn_number3': 10,
            'modcod3': 1,
            'mode4': random.randint(0, 6),
            'rx_frq4': random.randint(950000, 33000000),
            'tx_frq4': random.randint(950000, 33000000),
            'sym_rate4': random.randint(100, 200000),
            'demod_power4': random.randint(0, 1),
            'lvl_offset4': random.randint(-12, 12),
            'frame_len4': 64,
            'slot_len4': 8,
            'stn_number4': 10,
            'modcod4': 1,
            'mode5': random.randint(0, 6),
            'rx_frq5': random.randint(950000, 33000000),
            'tx_frq5': random.randint(950000, 33000000),
            'sym_rate5': random.randint(100, 200000),
            'demod_power5': random.randint(0, 1),
            'lvl_offset5': random.randint(-12, 12),
            'frame_len5': 64,
            'slot_len5': 8,
            'stn_number5': 10,
            'modcod5': 1,
            'mode6': random.randint(0, 6),
            'rx_frq6': random.randint(950000, 33000000),
            'tx_frq6': random.randint(950000, 33000000),
            'sym_rate6': random.randint(100, 200000),
            'demod_power6': random.randint(0, 1),
            'lvl_offset6': random.randint(-12, 12),
            'frame_len6': 64,
            'slot_len6': 8,
            'stn_number6': 10,
            'modcod6': 1,
            'mode7': random.randint(0, 6),
            'rx_frq7': random.randint(950000, 33000000),
            'tx_frq7': random.randint(950000, 33000000),
            'sym_rate7': random.randint(100, 200000),
            'demod_power7': random.randint(0, 1),
            'lvl_offset7': random.randint(-12, 12),
            'frame_len7': 64,
            'slot_len7': 8,
            'stn_number7': 10,
            'modcod7': 1,
            'mode8': random.randint(0, 6),
            'rx_frq8': random.randint(950000, 33000000),
            'tx_frq8': random.randint(950000, 33000000),
            'sym_rate8': random.randint(100, 200000),
            'demod_power8': random.randint(0, 1),
            'lvl_offset8': random.randint(-12, 12),
            'frame_len8': 64,
            'slot_len8': 8,
            'stn_number8': 10,
            'modcod8': 1
        }
        return params
