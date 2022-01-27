from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

__author__ = 'dkudryashov'
__version__ = '0.1'


options_path = 'utilities.create_all_entities'
backup_name = 'default_config.txt'


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

    User.create(api, 0, {'name': 'user-1'})
    User.create(api, 0, {'name': 'user-2'})
    User.create(api, 0, {'name': 'user-3'})
    Network.create(api, 0, {'name': 'test_net'})
    Teleport.create(api, 0, {'name': 'test_tp', 'sat_name': 'test_sat'})
    Controller.create(api, 0, {
        'name': 'test_ctrl',
        'mode': ControllerModes.MF_HUB,
        'teleport': 'teleport:0'
    })
    Controller.create(api, 0, {
        'name': 'test_ctrl2',
        'mode': ControllerModes.MF_HUB,
        'teleport': 'teleport:0'
    })
    Alert.create(api, 0, {'name': 'test_alert', 'popup': True})
    Vno.create(api, 0, {'name': 'test_vno'})

    backup.create_backup('case_simultaneous_access.txt')


if __name__ == '__main__':
    create_config()
