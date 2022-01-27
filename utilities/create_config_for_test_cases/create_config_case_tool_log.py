import ipaddress

from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import StationModes, ControllerModes, Checkbox
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

__author__ = 'dkudryashov'
__version__ = '0.1'
backup_name = 'case_tool_log.txt'


def get_drivers():
    connection_options = OptionsProvider.get_connection('global_options', API_CONNECT)
    api = DriversProvider.get_driver_instance(connection_options)
    return api


def create_config(driver=None):
    backup = BackupManager()
    backup.apply_backup('default_config.txt')
    if driver is None:
        api = get_drivers()
    else:
        api = driver
    Network.create(api, 0, {'name': 'test_net'})
    Teleport.create(api, 0, {'name': 'test_tp', 'sat_name': 'test_sat'})
    vno = Vno.create(api, 0, {'name': 'test_vno'})
    ctrl_ips = ipaddress.IPv4Address('172.16.0.1')
    for i in range(512):
        ctrl = Controller.create(api, 0, {
            'name': f'ctrl-{i}',
            'mode': ControllerModes.MF_HUB,
            'teleport': 'teleport:0',
            'device_ip': str(ctrl_ips + i),
            'device_mask': '/16',
            'device_vlan': 666,
            'stn_number': 64,
        })
        for j in range(64):
            Station.create(api, vno.get_id(), {
                'name': f'stn-{64 * i + j}',
                'serial': 64 * i + j + 1,
                'enable': Checkbox.ON,
                'mode': StationModes.STAR,
                'rx_controller': f'controller:{ctrl.get_id()}',
            })

    backup.create_backup('case_tool_log.txt')


if __name__ == '__main__':
    create_config()
