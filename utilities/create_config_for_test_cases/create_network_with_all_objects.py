import ipaddress
import random

from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes, RouteTypes, RouteIds
from src.file_manager.file_manager import FileManager
from src.nms_entities.basic_entities.access import Access
from src.nms_entities.basic_entities.bal_controller import BalController
from src.nms_entities.basic_entities.camera import Camera
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.dashboard import Dashboard
from src.nms_entities.basic_entities.device import Device
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.profile import Profile
from src.nms_entities.basic_entities.scheduler import Scheduler
from src.nms_entities.basic_entities.scheduler_range import SchRange
from src.nms_entities.basic_entities.scheduler_service import SchService
from src.nms_entities.basic_entities.scheduler_task import SchTask
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
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

__author__ = 'dkudryashov'
options_path = 'utilities.create_config_for_test_cases'
backup_name = 'default_config.txt'


def get_drivers():
    connection_options = OptionsProvider.get_connection('global_options', API_CONNECT)
    api = DriversProvider.get_driver_instance(connection_options)
    return api


def get_options():
    options = OptionsProvider.get_options(options_path)
    return options


def create_config(driver=None):
    """Network having all objects filled"""
    # Stations are scattered across all Sub Vnos
    backup = BackupManager()
    backup.apply_backup(backup_name)
    if driver is None:
        api = get_drivers()
    else:
        api = driver

    # Uploading a dummy UHP software file to be able to create sw_upload
    fm = FileManager()
    fm.upload_uhp_software('dummy_soft.240')

    options = get_options()
    # Used in station routes
    ip_address = ipaddress.IPv4Address('127.0.0.1')

    sch_task_created = 0
    station_route_created = 0
    station_rip_created = 0
    station_port_map_created = 0

    net = Network.create(api, 0, {'name': 'net'})
    for i in range(options.get('number_of_teleport')):
        Teleport.create(api, net.get_id(), {'name': i, 'sat_name': f's{i}'})
    for i in range(options.get('number_of_controller')):
        Controller.create(api, net.get_id(), {
            'name': i,
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{random.randint(0, options.get("number_of_teleport") - 1)}',
        })
    for i in range(options.get('number_of_service')):
        Service.create(api, net.get_id(), {'name': i})
    for i in range(options.get('number_of_shaper')):
        Shaper.create(api, net.get_id(), {'name': i})
    for i in range(options.get('number_of_policy')):
        Policy.create(api, net.get_id(), {'name': i})
    for i in range(1, options.get('number_of_polrule') + 1):
        PolicyRule.create(api, random.randint(0, options.get('number_of_policy') - 1), {'sequence': i})
    for i in range(1, options.get('number_of_group')):
        UserGroup.create(api, 0, {'name': i}, parent_type='network')
    for i in range(1, options.get('number_of_user')):
        User.create(api, i, {'name': i})
    for i in range(512):
        Access.create(
            api,
            0,
            {'group': f'group:{i}', 'edit': True}, parent_type='network')
    for i in range(options.get('number_of_sr_controller')):
        SrController.create(api, net.get_id(), {'name': i})
    for i in range(options.get('number_of_sr_teleport')):
        SrTeleport.create(api, 0, {
            'name': i,
            'teleport': f'teleport:{random.randint(0, options.get("number_of_teleport") - 1)}'
        })
    for i in range(options.get('number_of_device')):
        Device.create(api, 0, {'name': i})
    for i in range(options.get('number_of_sr_license')):
        SrLicense.create(api, 0, {'name': i})
    for i in range(options.get('number_of_bal_controller')):
        BalController.create(api, 0, {'name': i})
    for i in range(options.get('number_of_profile_set')):
        Profile.create(api, 0, {'name': i})
    for i in range(options.get('number_of_sw_upload')):
        SwUpload.create(api, 0, {'name': i, 'sw_file': 'dummy_soft.240'})
    for i in range(options.get('number_of_camera')):
        Camera.create(api, 0, {'name': i})
    for i in range(options.get('number_of_dashboard')):
        Dashboard.create(api, net.get_id(), {'name': f'dash{i}'}, parent_type='network')
    for i in range(options.get('number_of_scheduler')):
        Scheduler.create(api, net.get_id(), {'name': i})
    for i in range(options.get('number_of_sch_service')):
        SchService.create(api, random.randint(0, options.get('number_of_scheduler') - 1), {'name': i})
    for i in range(options.get('number_of_sch_range')):
        SchRange.create(api, random.randint(0, options.get('number_of_scheduler') - 1), {'name': i})
    Vno.create(api, net.get_id(), {'name': 'v'})
    for i in range(options.get('number_of_vno') - 1):
        Vno.create(api, i, {'name': f's{i}'}, parent_type='vno')

    # Stations are created randomly in the main vno and its sub vnos
    # Cannot create all stations due to 16Mbytes limit, 25000 are created
    next_stn_route = ipaddress.IPv4Address('127.0.0.1')
    # for i in range(options.get('number_of_station')):
    for i in range(25000):
        stn = Station.create(api, random.randint(0, options.get('number_of_vno') - 1), {
            'name': i,
            'enable': True,
            'serial': 12345 + i,
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{random.randint(0, options.get("number_of_controller") - 1)}',
        })
        if sch_task_created < options.get('number_of_sch_task'):
            SchTask.create(api, stn.get_id(), {
                'name': i,
                'sch_service': f'sch_service:{random.randint(0, options.get("number_of_sch_service") - 1)}',
            })
            sch_task_created += 1
        if station_rip_created < options.get('number_of_rip_router'):
            StationRip.create(api, stn.get_id(), {
                'service': f'service:{i}',
                'rip_next_hop': str(ip_address + 65000 + i),
            })
            station_rip_created += 1
        if station_port_map_created < options.get('number_of_port_map'):
            StationPortMap.create(api, stn.get_id(), {
                'external_port': i,
                'internal_ip': str(ip_address + i),
                'internal_port': 16000 + i,
            })
            station_port_map_created += 1
        for j in range(2):
            if station_route_created < options.get('number_of_route'):
                StationRoute.create(api, stn.get_id(), {
                    'type': RouteTypes.IP_ADDRESS,
                    'service': f'service:0',
                    'ip': str(next_stn_route),
                    'id': RouteIds.PRIVATE,
                })
                next_stn_route += 1
                station_route_created += 1

    backup.create_backup('network_with_all_objects.txt')


if __name__ == '__main__':
    create_config()
