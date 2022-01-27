import ipaddress

from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, CheckboxStr, RouteTypes
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

options_path = 'utilities.create_config_for_test_cases'
backup_name = 'default_config.txt'
__author__ = 'dkudryashov'


def get_drivers():
    connection_options = OptionsProvider.get_connection('global_options', API_CONNECT)
    api = DriversProvider.get_driver_instance(connection_options)
    return api


def get_options():
    options = OptionsProvider.get_options(options_path)
    return options


def create_config(driver=None):
    # ~1870 seconds
    """Create all objects"""

    def next_entity(name, class_, list_, parent_name, parent_id, params):
        """Fill up completely rows of an entity. The number of rows are taken from options

        :param str name: entity's name
        :param AbstractBasicObject class_: a test system object representing NMS entity
        :param AbstractBasicObject method list_: object getting list od IDs method
        :param str parent_name: the name of the parent object
        :param int parent_id: ID of the parent object
        :param dict params: the parameters passed to the object constructor
        """
        for i in range(nms_entities.get(f'number_of_{name}')):
            if name in ('group', 'user') and i == 511:
                break
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
                params_c['serial'] = i + 1
            if params.get('external_port') is not None:
                ext_port = params_c.get('external_port')
                params_c['external_port'] = ext_port + i + 1

            try:
                if name.startswith('access'):
                    class_.create(api, parent_id, params_c, parent_type=parent_name)
                else:
                    class_.create(api, parent_id, params_c)
            # Handle table full
            except ObjectNotCreatedException:
                print(name, i)

    backup = BackupManager()
    backup.apply_backup(backup_name)
    if driver is None:
        api = get_drivers()
    else:
        api = driver
    options = get_options()
    nms_entities = options
    names = options.get('names')

    # Uploading a dummy UHP software file to be able to create sw_upload
    fm = FileManager()
    fm.upload_uhp_software('dummy_soft.240')

    next_entity('network', Network, Network.network_list, 'nms', 0, {'name': f'{names.get("network")}%'})
    next_entity('server', Server, Server.server_list, 'nms', 0, {'name': f'{names.get("server")}%'})
    next_entity(
        'group', UserGroup, UserGroup.user_group_list, 'nms', 0, {'name': f'{names.get("group")}%'}
    )
    next_entity('user', User, User.user_list, 'group', 0, {'name': f'{names.get("user")}%'})
    next_entity('alert', Alert, Alert.alert_list, 'nms', 0, {'name': f'{names.get("alert")}%', 'popup': True})
    next_entity('access_net0', Access, Access.access_list, 'network', 0, {'group': 'group:%'})
    next_entity('access_net1', Access, Access.access_list, 'network', 1, {'group': 'group:%'})
    next_entity(
        'dashboard', Dashboard, Dashboard.dashboard_list, 'nms', 0, {'name': f'{names.get("dashboard")}%'}
    )
    next_entity(
        'teleport', Teleport, Teleport.teleport_list, 'network', 0, {
            'name': f'{names.get("teleport")}%',
            'sat_name': '1',
        }
    )
    next_entity('controller', Controller, Controller.controller_list, 'network', 0, {
        'name': f'{names.get("controller")}%', 'mode': ControllerModes.MF_HUB, 'teleport': 'teleport:0'
    })
    next_entity('vno', Vno, Vno.vno_list, 'network', 0, {'name': f'{names.get("vno")}%'})
    next_entity(
        'service', Service, Service.service_list, 'network', 0, {'name': f'{names.get("service")}%'}
    )
    next_entity(
        'qos', Qos, Qos.qos_list, 'network', 0, {'name': f'{names.get("qos")}%'}
    )
    next_entity('shaper', Shaper, Shaper.shaper_list, 'network', 0, {'name': f'{names.get("shaper")}%'})
    next_entity('policy', Policy, Policy.policy_list, 'network', 0, {'name': f'{names.get("policy")}%'})
    next_entity('polrule', PolicyRule, PolicyRule.policy_rules_list, 'policy', 0, {
        'sequence': 1
    })
    next_entity(
        'sr_controller',
        SrController,
        SrController.sr_controller_list,
        'network',
        0,
        {'name': f'{names.get("sr_controller")}%'}
    )
    next_entity(
        'sr_teleport',
        SrTeleport,
        SrTeleport.sr_teleport_list,
        'sr_controller',
        0,
        {'name': f'{names.get("sr_teleport")}%', 'teleport': 'teleport:0'}
    )
    next_entity(
        'device',
        Device,
        Device.device_list,
        'sr_teleport',
        0,
        {'name': f'{names.get("device")}%'}
    )
    next_entity(
        'sr_license',
        SrLicense,
        SrLicense.sr_license_list,
        'network',
        0,
        {'name': f'{names.get("sr_license")}%'}
    )
    next_entity('bal_controller', BalController, BalController.bal_controller_list, 'network', 0, {
        'name': f'{names.get("bal_controller")}%'
    })
    next_entity(
        'profile_set', Profile, Profile.profile_list, 'network', 0, {'name': f'{names.get("profile_set")}%'}
    )
    next_entity('sw_upload', SwUpload, SwUpload.sw_upload_list, 'network', 0, {
        'name': f'{names.get("sw_upload")}%', 'sw_file': 'dummy_soft.240',
    })
    next_entity('camera', Camera, Camera.camera_list, 'network', 0, {'name': f'{names.get("camera")}%'})
    next_entity(
        'scheduler', Scheduler, Scheduler.scheduler_list, 'network', 0, {'name': f'{names.get("scheduler")}%'}
    )
    next_entity(
        'sch_range',
        SchRange,
        SchRange.scheduler_range_list,
        'scheduler',
        0,
        {'name': f'{names.get("sch_range")}%'}
    )
    next_entity(
        'sch_service',
        SchService,
        SchService.scheduler_service_list,
        'scheduler',
        0,
        {'name': f'{names.get("sch_service")}%'}
    )
    next_entity(
        'route',
        ControllerRoute,
        ControllerRoute.controller_route_list,
        'controller',
        0,
        {'type': RouteTypes.IP_ADDRESS, 'service': 'service:0', 'ip': '127.1.0.0', 'mask': '/32'}
    )
    next_entity(
        'rip_router',
        ControllerRip,
        ControllerRip.controller_rip_list,
        'controller',
        0,
        {'service': 'service:%'}
    )
    next_entity(
        'port_map',
        ControllerPortMap,
        ControllerPortMap.port_map_list,
        'controller',
        0,
        {'external_port': 0}
    )
    next_entity('station', Station, Station.station_list, 'vno', 0, {
        'name': f'{names.get("station")}%',
        'serial': 1,
        # 'mode': StationModes.STAR,
        'enable': CheckboxStr.ON,
        'rx_controller': 'controller:0'
    })
    next_entity('sch_task', SchTask, SchTask.scheduler_task_list, 'station', 0, {
        'name': f'{names.get("sch_task")}%',
        'sch_service': 'sch_service:0',
    })

    try:
        backup.create_backup('case_database_performance.txt')
    except Exception as exc:
        print(f'Cannot create backup: {exc}')


if __name__ == '__main__':
    create_config()
