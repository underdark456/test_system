# The NMS tables are loaded fully (max number of nets etc.)
import random
import time

from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import StationModes, ControllerModes, RouteTypes, DeviceModes, RuleTypes, ActionTypes, \
    PriorityTypes, Checkbox, CheckTypes, QueueTypes, CheckboxStr
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
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

__author__ = 'dkudryashov'
__version__ = '0.1'


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

    # for i in range(1, 128):
    #     Network.create(api, 0, {'name': f'network-{i}'})

    # for i in range(1, 512):
    #     Controller.create(api, 0, {
    #         'name': f'controller-{i}',
    #         'mode': ControllerModes.MF_HUB,
    #         'teleport': 'teleport:0'
    #     })

    # for i in range(1, 32768):
    #     Station.create(api, 0, {
    #         'name': f'station-{i}',
    #         'serial': i,
    #         'mode': StationModes.STAR,
    #         'rx_controller': 'controller:0',
    #         'enable': CheckboxStr.ON,
    #     })

    # backup.create_backup('case_web_throughput.txt')


if __name__ == '__main__':
    create_config()
