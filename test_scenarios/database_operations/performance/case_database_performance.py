import ipaddress
import time

from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, CheckboxStr, RouteTypes, StationModes
from src.exceptions import ObjectNotCreatedException
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
from src.nms_entities.basic_entities.scheduler_task import SchTask
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
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

options_path = 'test_scenarios.database_operations.performance'
backup_name = 'default_config.txt'


class DatabasePerformanceCase(CustomTestCase):
    """Database create/delete/edit/search/list performance"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __execution_time__ = None  # approximate test case execution time in seconds
    __express__ = False

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, API_CONNECT)
        )
        cls.backup = BackupManager()
        cls.options = OptionsProvider.get_options(options_path)
        cls.nms_entities = cls.options.get('nms_entities')
        cls.names = cls.options.get('names')
        cls.creation_time = cls.options.get('creation_time')
        cls.deletion_time = cls.options.get('deletion_time')
        fm = FileManager()
        fm.upload_uhp_software('dummy_soft.240')

    def test_all_objects_creation_performance(self):
        # ~1870 seconds
        """Database all objects creation performance test"""
        self.backup.apply_backup(backup_name)
        self.next_entity('network', Network, Network.network_list, 'nms', 0, {'name': f'{self.names.get("network")}%'})
        self.next_entity('server', Server, Server.server_list, 'nms', 0, {'name': f'{self.names.get("server")}%'})
        self.next_entity(
            'group', UserGroup, UserGroup.user_group_list, 'nms', 0, {'name': f'{self.names.get("group")}%'}
        )
        self.next_entity('user', User, User.user_list, 'group', 0, {'name': f'{self.names.get("user")}%'})
        self.next_entity(
            'alert',
            Alert,
            Alert.alert_list,
            'nms',
            0,
            {'name': f'{self.names.get("alert")}%', 'popup': True}
        )
        self.next_entity('access_net0', Access, Access.access_list, 'network', 0, {'group': 'group:%'})
        self.next_entity('access_net1', Access, Access.access_list, 'network', 1, {'group': 'group:%'})
        self.next_entity(
            'dashboard', Dashboard, Dashboard.dashboard_list, 'nms', 0, {'name': f'{self.names.get("dashboard")}%'}
        )
        self.next_entity(
            'teleport', Teleport, Teleport.teleport_list, 'network', 0, {'name': f'{self.names.get("teleport")}%'}
        )
        self.next_entity('controller', Controller, Controller.controller_list, 'network', 0, {
            'name': f'{self.names.get("controller")}%', 'mode': ControllerModes.MF_HUB, 'teleport': 'teleport:0'
        })
        self.next_entity('vno', Vno, Vno.vno_list, 'network', 0, {'name': f'{self.names.get("vno")}%'})
        self.next_entity(
            'service', Service, Service.service_list, 'network', 0, {'name': f'{self.names.get("service")}%'}
        )
        self.next_entity(
            'qos', Qos, Qos.qos_list, 'network', 0, {'name': f'{self.names.get("qos")}%'}
        )
        self.next_entity('shaper', Shaper, Shaper.shaper_list, 'network', 0, {'name': f'{self.names.get("shaper")}%'})
        self.next_entity('policy', Policy, Policy.policy_list, 'network', 0, {'name': f'{self.names.get("policy")}%'})
        self.next_entity('polrule', PolicyRule, PolicyRule.policy_rules_list, 'policy', 0, {
            'sequence': 1
        })
        self.next_entity(
            'sr_controller',
            SrController,
            SrController.sr_controller_list,
            'network',
            0,
            {'name': f'{self.names.get("sr_controller")}%'}
        )
        self.next_entity(
            'sr_teleport',
            SrTeleport,
            SrTeleport.sr_teleport_list,
            'sr_controller',
            0,
            {'name': f'{self.names.get("sr_teleport")}%', 'teleport': 'teleport:0'}
        )
        self.next_entity(
            'device',
            Device,
            Device.device_list,
            'sr_teleport',
            0,
            {'name': f'{self.names.get("device")}%', 'ip': '127.0.0.1'}
        )
        self.next_entity(
            'sr_license',
            SrLicense,
            SrLicense.sr_license_list,
            'network',
            0,
            {'name': f'{self.names.get("sr_license")}%'}
        )
        self.next_entity('bal_controller', BalController, BalController.bal_controller_list, 'network', 0, {
            'name': f'{self.names.get("bal_controller")}%', 'enable': CheckboxStr.ON
        })
        self.next_entity(
            'profile_set', Profile, Profile.profile_list, 'network', 0, {'name': f'{self.names.get("profile_set")}%'}
        )
        self.next_entity('sw_upload', SwUpload, SwUpload.sw_upload_list, 'network', 0, {
            'name': f'{self.names.get("sw_upload")}%', 'tx_controller': 'controller:0', 'sw_file': 'dummy_soft.240',
        })
        self.next_entity('camera', Camera, Camera.camera_list, 'network', 0, {'name': f'{self.names.get("camera")}%'})
        self.next_entity(
            'scheduler', Scheduler, Scheduler.scheduler_list, 'network', 0, {'name': f'{self.names.get("scheduler")}%'}
        )
        self.next_entity(
            'sch_range',
            SchRange,
            SchRange.scheduler_range_list,
            'scheduler',
            0,
            {'name': f'{self.names.get("sch_range")}%'}
        )
        self.next_entity(
            'sch_service',
            SchService,
            SchService.scheduler_service_list,
            'scheduler',
            0,
            {'name': f'{self.names.get("sch_service")}%'}
        )
        self.next_entity(
            'route',
            ControllerRoute,
            ControllerRoute.controller_route_list,
            'controller',
            0,
            {'type': RouteTypes.IP_ADDRESS, 'service': 'service:0', 'ip': '127.1.0.0', 'mask': '/32'}
        )
        self.next_entity(
            'rip_router',
            ControllerRip,
            ControllerRip.controller_rip_list,
            'controller',
            0,
            {'service': 'service:%'}
        )
        self.next_entity(
            'port_map',
            ControllerPortMap,
            ControllerPortMap.port_map_list,
            'controller',
            0,
            {'external_port': 0}
        )
        self.next_entity('station', Station, Station.station_list, 'vno', 0, {
                'name': f'{self.names.get("station")}%',
                'serial': 1,
                'mode': StationModes.STAR,
                'enable': CheckboxStr.ON,
                'rx_controller': 'controller:0'
        })
        self.next_entity('sch_task', SchTask, SchTask.scheduler_task_list, 'station', 0, {
            'name': f'{self.names.get("sch_task")}%',
            'sch_service': 'sch_service:0',
        })

        # Not need to create config in each test run
        # try:
        #     self.backup.create_backup('case_database_performance.txt')
        # except Exception as exc:
        #     self.info(f'Cannot create backup: {exc}')

    def test_all_objects_deletion_performance(self):
        # ~18000 seconds execution time
        """Database all objects deletion performance test. Performed on a full database"""
        self.backup.apply_backup('case_database_performance.txt')
        self.delete_next_entity('sch_task', SchTask, 'station')
        self.delete_next_entity('station', Station, 'vno')
        self.delete_next_entity('port_map', ControllerPortMap, 'controller')
        self.delete_next_entity('rip_router', ControllerRip, 'controller')
        self.delete_next_entity('route', ControllerRoute, 'controller')
        self.delete_next_entity('sch_service', SchService, 'scheduler')
        self.delete_next_entity('sch_range', SchRange, 'scheduler')
        self.delete_next_entity('scheduler', Scheduler, 'network')
        self.delete_next_entity('camera', Camera, 'network')
        self.delete_next_entity('sw_upload', SwUpload, 'network')
        self.delete_next_entity('profile_set', Profile, 'network')
        self.delete_next_entity('bal_controller', BalController, 'network')
        self.delete_next_entity('sr_license', SrLicense, 'network')
        self.delete_next_entity('device', Device, 'sr_teleport')
        self.delete_next_entity('sr_teleport', SrTeleport, 'sr_controller')
        self.delete_next_entity('sr_controller', SrController, 'network')
        self.delete_next_entity('polrule', PolicyRule, 'policy')
        self.delete_next_entity('policy', Policy, 'network')
        self.delete_next_entity('shaper', Shaper, 'network')
        self.delete_next_entity('service', Service, 'network')
        self.delete_next_entity('vno', Vno, 'network')
        self.delete_next_entity('controller', Controller, 'network')
        self.delete_next_entity('teleport', Teleport, 'network')
        self.delete_next_entity('dashboard', Dashboard, 'nms')
        self.delete_next_entity('access_net1', Access, 'network')
        self.delete_next_entity('access_net0', Access, 'network')
        self.delete_next_entity('alert', Alert, 'network')
        self.delete_next_entity('user', User, 'group')
        self.delete_next_entity('group', UserGroup, 'nms')
        self.delete_next_entity('server', Server, 'nms')
        self.delete_next_entity('network', Network, 'nms')

    def test_search_entry_performance(self):
        """Search object by name or get object by ID performance. Performed on a full database"""
        # ~55 seconds
        self.backup.apply_backup('case_database_performance.txt')
        time.sleep(10)
        exp_search_time = self.options.get('expected_search_time')
        for entity, number in self.nms_entities.items():
            if entity in ('polrule', 'route', 'rip_router', 'port_map'):
                for row in (0, (number - 1) // 2, number - 1):
                    path = f'api/object/get/{entity}={row}'
                    with self.subTest(f'{entity}:{row} search time expected less than {exp_search_time} sec'):
                        st_time = time.perf_counter()
                        reply, error, error_code = self.driver.custom_get(path)
                        self.assertEqual(NO_ERROR, error_code, f'Returned error_code {error_code}')
                        end_time = time.perf_counter()
                        search_time = round(end_time - st_time, 3)
                        self.assertLess(search_time, exp_search_time, msg=f'Actual search time {search_time}')
            elif entity == 'access_net0':
                total = self.nms_entities.get('access_net0') + self.nms_entities.get('access_net1')
                for row in (0, (total - 1) // 2, total - 1):
                    path = f'api/object/get/access={row}'
                    with self.subTest(f'access:{row} search time expected less than {exp_search_time} sec'):
                        st_time = time.perf_counter()
                        reply, error, error_code = self.driver.custom_get(path)
                        self.assertEqual(NO_ERROR, error_code, f'Returned error_code {error_code}')
                        end_time = time.perf_counter()
                        search_time = round(end_time - st_time, 3)
                        self.assertLess(search_time, exp_search_time, msg=f'Actual search time {search_time}')
            elif entity == 'access_net1':
                continue
            else:
                path = 'api/search/get/nms=0?search=global'
                if entity in ('user', 'group'):
                    _end = number - 2  # user:0 and group:0 are in default config
                else:
                    _end = number - 1
                for row in (0, _end // 2, _end):
                    name = f'{self.names.get(entity)}{row}'
                    with self.subTest(f'{entity} named {name} search time expected less than {exp_search_time} sec'):
                        st_time = time.perf_counter()
                        reply, error, error_code = self.driver.custom_post(path, payload={'search': name})
                        self.assertEqual(NO_ERROR, error_code, f'Returned error_code {error_code}')
                        self.assertEqual(1, len(reply), msg=f'Number of entries in reply {len(reply)}, expected 1')
                        end_time = time.perf_counter()
                        search_time = round(end_time - st_time, 3)
                        self.assertLess(search_time, exp_search_time, msg=f'Actual search time {search_time}')
                    # self.info(f'{entity} named {name} search time is {search_time} seconds')

    def test_delete_row_performance(self):
        """Each entity delete first, last, and middle object. Performed on a full database"""
        # ~ 18 seconds
        self.backup.apply_backup('case_database_performance.txt')
        time.sleep(10)
        for entity in self.options.get('deletion_order'):
            if entity == 'station':
                exp_delete_time = self.options.get('expected_station_delete_time')
            else:
                exp_delete_time = self.options.get('expected_delete_time')

            if entity == 'access_net0':
                entity = 'access'
                number = self.nms_entities.get('access_net0') + self.nms_entities.get('access_net1')
            elif entity in ('access_net1', 'group', 'service'):
                continue
            else:
                number = self.nms_entities.get(entity)
            for row in (1, (number - 1) // 2, number - 1):
                path = f'api/object/delete/{entity}={row}'
                with self.subTest(f'{entity}:{row} delete time expected less than {exp_delete_time} sec'):
                    st_time = time.perf_counter()
                    reply, error, error_code = self.driver.custom_get(path)
                    end_time = time.perf_counter()
                    self.assertEqual(NO_ERROR, error_code, f'Returned error_code {error_code}')
                    delete_time = round(end_time - st_time, 3)

                    self.assertLess(delete_time, exp_delete_time, msg=f'Actual delete time {exp_delete_time}')
                # self.info(f'{entity}:{row} delete time is {delete_time} seconds')

    def test_edit_row_performance(self):
        """Each entity edit first, last, and middle object. Performed on a full database"""
        # ~18 seconds
        self.backup.apply_backup('case_database_performance.txt')
        time.sleep(10)
        exp_edit_time = self.options.get('expected_edit_time')
        for entity, number in self.nms_entities.items():
            if entity != 'access_net1':
                number = self.nms_entities.get(entity)
            else:
                number = self.nms_entities.get('access_net0') + self.nms_entities.get('access_net1')
            for row in (1, (number - 1) // 2, number - 1):
                if entity == 'access_net0':
                    continue
                elif entity in ('access_net1', 'access'):
                    entity = 'access'
                    edit_param = 'use'
                    edit_value = 1
                elif entity == 'polrule':
                    edit_param = 'sequence'
                    edit_value = row + 10001
                elif entity == 'route':
                    edit_param = 'override_vlan'
                    edit_value = 1
                elif entity == 'rip_router':
                    edit_param = 'lan_rx'
                    edit_value = 1
                elif entity == 'port_map':
                    edit_param = 'internal_port'
                    edit_value = 100
                else:
                    edit_param = 'name'
                    edit_value = f'new_name{row}'
                path = f'api/object/write/{entity}={row}'
                with self.subTest(f'{entity}:{row} edit time expected less than {exp_edit_time} sec'):
                    st_time = time.perf_counter()
                    reply, error, error_code = self.driver.custom_post(path, payload={edit_param: edit_value})
                    end_time = time.perf_counter()
                    self.assertEqual(NO_ERROR, error_code, f'Returned error_code {error_code}')
                    edit_time = round(end_time - st_time, 3)
                    self.assertLess(edit_time, exp_edit_time, msg=f'Actual edit time {exp_edit_time}')
                # self.info(f'{entity}:{row} edit time is {edit_time} seconds')

    def test_list_each_table_performance(self):
        """List all rows performance. Performed on a full database (but list only 5000 stations)"""
        # ~22 seconds
        self.backup.apply_backup('case_database_performance.txt')
        time.sleep(10)
        for entity, number in self.nms_entities.items():
            exp_list_time = self.options.get('expected_list_time').get(entity)
            if entity in ('network', 'server', 'group', 'alert', 'dashboard'):
                parent = 'nms'
                row = 0
            elif entity in ('teleport', 'controller', 'vno', 'service', 'shaper', 'policy', 'sr_controller',
                            'sr_license', 'bal_controller', 'profile_set', 'sw_upload', 'camera', 'scheduler', 'qos'):
                parent = 'network'
                row = 0
            elif entity == 'user':
                parent = 'group'
                row = 0
            elif entity == 'sr_teleport':
                parent = 'sr_controller'
                row = 0
            elif entity == 'device':
                parent = 'sr_teleport'
                row = 0
            elif entity == 'polrule':
                parent = 'policy'
                row = 0
            elif entity in ('sch_range', 'sch_service'):
                parent = 'scheduler'
                row = 0
            elif entity in ('route', 'rip_router', 'port_map'):
                parent = 'controller'
                row = 0
            elif entity == 'station':
                parent = 'vno'
                row = 0
            elif entity == 'sch_task':
                parent = 'station'
                row = 0
            elif entity == 'access_net0':
                entity = 'access'
                parent = 'network'
                row = 0
            elif entity == 'access_net1':
                entity = 'access'
                parent = 'network'
                row = 1
            else:
                continue
            # Too many parameters in stations - cannot get all of them due to 16 Mbytes limit
            if entity == 'station':
                number = 5000
                path = f'api/list/get/{parent}={row}/list_items={entity}/list_max={number}'
            else:
                path = f'api/list/get/{parent}={row}/list_items={entity}/list_max=65000'
            with self.subTest(f'{entity} get list expected time less than {exp_list_time} sec'):
                st_time = time.perf_counter()
                reply, error, error_code = self.driver.custom_get(path)
                end_time = time.perf_counter()
                list_time = round(end_time - st_time, 3)
                self.assertEqual(NO_ERROR, error_code, f'Returned error_code {error_code}')
                self.assertEqual(number, len(reply), msg=f'Number of rows in reply {len(reply)}, expected {number}')
                self.assertLess(list_time, exp_list_time, msg=f'Actual list time {list_time}')
            # self.info(f'{entity} get list time is {list_time} seconds')

    def delete_next_entity(self, name, class_, parent_name):
        """Delete completely all the rows of an entity. The number of rows are taken from options

        :param str name: entity's name
        :param AbstractBasicObject class_: a test system object representing NMS entity
        :param str parent_name: the name of the parent object
        """
        st_time = time.perf_counter()
        for i in range(self.nms_entities.get(name)):
            if name == 'group' and i == 0:
                continue
            elif name == 'user' and i == 0:
                continue
            elif name == 'access_net0':
                obj_ = class_(self.driver, 0, i + 1)
            elif name == 'access_net1':
                if i == 511:
                    continue
                obj_ = class_(self.driver, 1, 512 + i + 1)
            else:
                obj_ = class_(self.driver, 0, i)
            obj_.delete()
            # self.assertIsNone(obj_.get_id())
        end_time = time.perf_counter()
        measured_time = round(end_time - st_time, 3)
        expected_time = self.deletion_time.get(f'{name}_del_time')
        self.info(f'{self.nms_entities.get(name)} {name}s deletion time {end_time - st_time} seconds')
        with self.subTest(msg=f'{self.nms_entities.get(name)} {name}s deletion time {measured_time} seconds'):
            self.assertLess(
                measured_time,
                expected_time + expected_time * 0.15,
                msg=f'expected time not greater {expected_time + expected_time * 0.15}, actual time {measured_time}'
            )

    def next_entity(self, name, class_, list_, parent_name, parent_id, params):
        """Fill up completely rows of an entity. The number of rows are taken from options

        :param str name: entity's name
        :param AbstractBasicObject class_: a test system object representing NMS entity
        :param AbstractBasicObject method list_: object getting list od IDs method
        :param str parent_name: the name of the parent object
        :param int parent_id: ID of the parent object
        :param dict params: the parameters passed to the object constructor
        """
        st_time = time.perf_counter()

        for i in range(self.nms_entities.get(name)):
            params_c = params.copy()
            if params.get('name') is not None:
                name_c = params_c.get('name')
                params_c['name'] = name_c.replace('%', str(i))
            if params.get('group') is not None:
                group_c = params_c.get('group')
                params_c['group'] = group_c.replace('%', str(i))
            if name == 'rip_router' and params.get('service') is not None:
                service_c = params_c.get('service')
                params_c['service'] = service_c.replace('%', str(i))
            # Increasing IPv4 address by one at each iteration
            if params.get('ip') is not None:
                ip = params.get('ip')
                params_c['ip'] = str(ipaddress.IPv4Address(ip) + i + 1)
            if params.get('sequence') is not None:
                sequence = params_c.get('sequence')
                params_c['sequence'] = sequence + i + 1
            if params.get('serial') is not None:
                serial = params_c.get('serial')
                params_c['serial'] = serial + i + 1
            if params.get('external_port') is not None:
                ext_port = params_c.get('external_port')
                params_c['external_port'] = ext_port + i + 1

            try:
                if name.startswith('access'):
                    class_.create(self.driver, parent_id, params_c, parent_type=parent_name)
                else:
                    class_.create(self.driver, parent_id, params_c)
            # Handle table full
            except ObjectNotCreatedException:
                pass
        end_time = time.perf_counter()

        if name.startswith('access'):
            number_of_entities = len(list_(self.driver, parent_id, parent_type=parent_name))
        # Cannot get large list of large number of entities at once due to 8 Mbytes limit
        elif name == 'route':
            num1 = len(list_(self.driver, parent_id, max_=15000))
            num2 = len(list_(self.driver, parent_id, skip=15000, max_=15000))
            num3 = len(list_(self.driver, parent_id, skip=30000, max_=15000))
            num4 = len(list_(self.driver, parent_id, skip=45000, max_=15000))
            num5 = len(list_(self.driver, parent_id, skip=60000, max_=15000))
            number_of_entities = num1 + num2 + num3 + num4 + num5
        # Cannot get large list of large number of entities at once due to 8 Mbytes limit
        elif name == 'station':
            num1 = len(list_(self.driver, parent_id, max_=10000, vars_=['name']))
            num2 = len(list_(self.driver, parent_id, skip=10000, max_=10000, vars_=['name']))
            num3 = len(list_(self.driver, parent_id, skip=20000, max_=10000, vars_=['name']))
            num4 = len(list_(self.driver, parent_id, skip=30000, max_=10000, vars_=['name']))
            number_of_entities = num1 + num2 + num3 + num4
        else:
            number_of_entities = len(list_(self.driver, parent_id))
        self.assertEqual(
            self.nms_entities.get(name),
            number_of_entities,
            msg=f'{self.nms_entities.get(name)} {name}s created'
        )
        measured_time = round(end_time - st_time, 3)
        expected_time = self.creation_time.get(f'{name}_exp_time')
        self.info(f'{self.nms_entities.get(name)} {name}s creation time {end_time - st_time} seconds')
        with self.subTest(msg=f'{self.nms_entities.get(name)} {name}s creation time {measured_time} seconds'):
            self.assertLess(
                measured_time,
                expected_time + expected_time * 0.15,
                msg=f'expected time not greater {expected_time + expected_time * 0.15}, actual time {measured_time}'
            )
