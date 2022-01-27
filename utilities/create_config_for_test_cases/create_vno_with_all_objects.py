import ipaddress
import random

from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes, RouteTypes, RouteIds
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.dashboard import Dashboard
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.scheduler import Scheduler
from src.nms_entities.basic_entities.scheduler_range import SchRange
from src.nms_entities.basic_entities.scheduler_service import SchService
from src.nms_entities.basic_entities.scheduler_task import SchTask
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_port_map import StationPortMap
from src.nms_entities.basic_entities.station_rip import StationRip
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

__author__ = 'dkudryashov'
__version__ = '0.1'
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
    """Vno having all sub vnos, accesses, groups, dashboards and stations with rip_routers, port_maps, and sch_tasks"""
    # Stations are scattered across all Sub Vnos
    backup = BackupManager()
    backup.apply_backup(backup_name)
    if driver is None:
        api = get_drivers()
    else:
        api = driver

    options = get_options()
    # Used in station routes
    ip_address = ipaddress.IPv4Address('127.0.0.1')

    sch_task_created = 0
    station_route_created = 0
    station_rip_created = 0
    station_port_map_created = 0

    net = Network.create(api, 0, {'name': 'test_net'})
    tp = Teleport.create(api, net.get_id(), {'name': 'test_tp', 'sat_name': 'test_sat'})
    mf_hub = Controller.create(
        api,
        net.get_id(),
        {'name': 'mf_hub', 'mode': ControllerModes.MF_HUB, 'teleport': f'teleport:{tp.get_id()}'})
    vno = Vno.create(api, net.get_id(), {'name': 'test_vno'})
    for i in range(options.get('number_of_vno') - 1):
        Vno.create(api, i, {'name': f's{i}'}, parent_type='vno')
    # for i in range(1, options.get('number_of_group')):
    #     UserGroup.create(api, 0, {'name': f'gr{i}'}, parent_type='vno')
    # for i in range(1, options.get('number_of_user')):
    #     User.create(api, i, {'name': f'us{i}'})
    # for i in range(512):
    #     Access.create(api, mf_hub.get_id(), {'group': f'group:{i}', 'edit': True}, parent_type='vno')
    for i in range(options.get('number_of_dashboard')):
        Dashboard.create(api, vno.get_id(), {'name': f'd{i}'}, parent_type='vno')

    scheduler = Scheduler.create(api, net.get_id(), {'name': 'test_sched'})
    for i in range(options.get('number_of_service')):
        Service.create(api, net.get_id(), {'name': f's{i}'})
    sch_ser = SchService.create(api, scheduler.get_id(), {'name': 'test_sch_ser'})
    SchRange.create(api, scheduler.get_id(), {'name': 'test_sch_ran'})
    # Stations are created randomly in the main vno and its sub vnos
    next_stn_route = ipaddress.IPv4Address('127.0.0.1')
    for i in range(options.get('number_of_station')):
        stn = Station.create(api, random.randint(0, options.get('number_of_vno') - 1), {
            'name': f's{i}',
            'enable': True,
            'serial': i + 1,
            'mode': StationModes.STAR,
            'rx_controller': f'controller:{mf_hub.get_id()}',
        })
        if sch_task_created < options.get('number_of_sch_task'):
            SchTask.create(api, stn.get_id(), {
                'name': f'sch_task{i}',
                'sch_service': f'sch_service:{sch_ser.get_id()}',
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

    backup.create_backup('vno_with_all_objects.txt')


if __name__ == '__main__':
    create_config()
