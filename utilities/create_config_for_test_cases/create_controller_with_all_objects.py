import ipaddress

from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, RouteTypes, RouteIds
from src.nms_entities.basic_entities.access import Access
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_port_map import ControllerPortMap
from src.nms_entities.basic_entities.controller_rip import ControllerRip
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.user_group import UserGroup
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
    """Controller having all routes, rip_routers, port_maps, and accesses"""
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
    tp = Teleport.create(api, net.get_id(), {'name': 'test_tp', 'sat_name': 'test_sat'})
    mf_hub = Controller.create(
        api,
        net.get_id(),
        {'name': 'mf_hub', 'mode': ControllerModes.MF_HUB, 'teleport': f'teleport:{tp.get_id()}'})
    for i in range(options.get('number_of_service')):
        Service.create(api, net.get_id(), {'name': f'service{i}'})
    for i in range(1, options.get('number_of_group')):
        UserGroup.create(api, 0, {'name': f'gr{i}'})
    for i in range(1, options.get('number_of_user')):
        User.create(api, i, {'name': f'us{i}'})

    for i in range(512):
        Access.create(api, mf_hub.get_id(), {'group': f'group:{i}', 'edit': True}, parent_type='controller')

    for i in range(options.get('number_of_rip_router')):
        ControllerRip.create(api, mf_hub.get_id(), {
            'service': f'service:{i}',
            'rip_next_hop': str(ip_address + 65000 + i),
        })
    for i in range(options.get('number_of_port_map')):
        ControllerPortMap.create(api, mf_hub.get_id(), {
            'external_port': i,
            'internal_ip': str(ip_address + i),
            'internal_port': 16000 + i,
        })
    for i in range(options.get('number_of_route')):
        ControllerRoute.create(api, mf_hub.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:0',
            'ip': str(ip_address + i),
            'id': RouteIds.PRIVATE,
        })

    backup.create_backup('controller_with_all_objects.txt')


if __name__ == '__main__':
    create_config()
