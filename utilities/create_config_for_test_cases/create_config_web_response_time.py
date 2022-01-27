# The NMS tables are loaded fully (max number of nets etc.)
import ipaddress
import time
from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import StationModes, ControllerModes, CheckboxStr
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.user import User
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

__author__ = 'dkudryashov'


options_path = 'utilities.create_all_entities'
backup_name = 'each_entity.txt'


def get_drivers():
    connection_options = OptionsProvider.get_connection('global_options', API_CONNECT)
    api = DriversProvider.get_driver_instance(connection_options)
    return api


def get_options():
    options = OptionsProvider.get_options(options_path)
    return options


def create_config(driver=None):
    """Config for WEB throughput case - each entity plus maximum number of users in admins group"""
    backup = BackupManager()
    backup.apply_backup(backup_name)
    if driver is None:
        api = get_drivers()
    else:
        api = driver

    # First user already exists, creating users in group 0
    for i in range(1, 512):
        User.create(api, 0, {'name': f'user-{i}'})

    for i in range(1, 128):
        Network.create(api, 0, {'name': f'network-{i}'})

    device_ip = ipaddress.IPv4Address('127.0.0.1')

    for i in range(1, 512):
        Controller.create(api, 0, {
            'name': f'controller-{i}',
            'mode': ControllerModes.MF_HUB,
            'teleport': 'teleport:0',
            'device_ip': str(device_ip + i),
        })

    for i in range(1, 32768):
        Station.create(api, 0, {
            'name': f'station-{i}',
            'serial': i,
            'mode': StationModes.STAR,
            'rx_controller': 'controller:0',
            'enable': CheckboxStr.ON,
        })

    time.sleep(30)
    backup.create_backup('case_web_max_response_time.txt')


if __name__ == '__main__':
    create_config()
