import ipaddress

from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes, RouteTypes, RouteIds
from src.nms_entities.basic_entities.controller import Controller
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
    """Station having all routes, rip_routers, port_maps, and sch_tasks"""
    backup = BackupManager()
    backup.apply_backup(backup_name)
    if driver is None:
        api = get_drivers()
    else:
        api = driver

    options = get_options()
    # Used in station routes
    ip_address = ipaddress.IPv4Address('127.0.0.1')

    net = Network.create(api, 0, {'name': 'test_net'})
    tp = Teleport.create(api, net.get_id(), {'name': 'test_tp', 'sat_name': f'test_sat'})
    mf_hub = Controller.create(
        api,
        net.get_id(),
        {'name': 'mf_hub', 'mode': ControllerModes.MF_HUB, 'teleport': f'teleport:{tp.get_id()}'})
    vno = Vno.create(api, net.get_id(), {'name': 'test_vno'})
    scheduler = Scheduler.create(api, net.get_id(), {'name': 'test_sched'})
    for i in range(options.get('number_of_service')):
        Service.create(api, net.get_id(), {'name': f'service{i}'})
    sch_ser = SchService.create(api, scheduler.get_id(), {'name': 'test_sch_ser'})
    SchRange.create(api, scheduler.get_id(), {'name': 'test_sch_ran'})
    stn = Station.create(api, vno.get_id(), {
        'name': 'test_stn',
        'enable': True,
        'serial': 12345,
        'mode': StationModes.STAR,
        'rx_controller': f'controller:{mf_hub.get_id()}',
    })
    for i in range(options.get('number_of_sch_task')):
        SchTask.create(api, stn.get_id(), {
            'name': f'sch_task{i}',
            'sch_service': f'sch_service:{sch_ser.get_id()}',
        })
    for i in range(options.get('number_of_rip_router')):
        StationRip.create(api, stn.get_id(), {
            'service': f'service:{i}',
            'rip_next_hop': str(ip_address + 65000 + i),
        })
    for i in range(options.get('number_of_port_map')):
        StationPortMap.create(api, stn.get_id(), {
            'external_port': i,
            'internal_ip': str(ip_address + i),
            'internal_port': 16000 + i,
        })
    for i in range(options.get('number_of_route')):
        StationRoute.create(api, stn.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:0',
            'ip': str(ip_address + i),
            'id': RouteIds.PRIVATE,
        })

    backup.create_backup('station_with_all_objects.txt')


if __name__ == '__main__':
    create_config()
