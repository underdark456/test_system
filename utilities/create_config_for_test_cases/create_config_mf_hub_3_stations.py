import ipaddress

from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes, RouteTypes, RouteIds
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
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
    """Config which features an MF Hub and three stations"""
    backup = BackupManager()
    backup.apply_backup(backup_name)
    if driver is None:
        api = get_drivers()
    else:
        api = driver

    # Used in station routes
    ip_address = ipaddress.IPv4Address('127.0.0.1')

    net = Network.create(api, 0, {'name': f'test_net'})
    tp = Teleport.create(api, net.get_id(), {
        'name': f'test_tp',
        'sat_name': 'test_sat',
        'tx_lo': 0,
        'rx1_lo': 0,
        'rx2_lo': 0
    })
    mf_hub = Controller.create(
        api,
        net.get_id(),
        {'name': f'mf_hub', 'mode': ControllerModes.MF_HUB, 'teleport': f'teleport:{tp.get_id()}'})

    ser = Service.create(api, net.get_id(), {'name': f'stn_service'})
    vno = Vno.create(api, net.get_id(), {'name': f'test_vno'})
    for s in range(1, 4):
        stn = Station.create(
            api,
            vno.get_id(),
            {
                'name': f'test_stn{s}',
                'enable': True,
                'serial': s + 1,
                'mode': StationModes.STAR,
                'rx_controller': f'controller:{mf_hub.get_id()}'
            }
        )
    for s in range(1, 4):
        StationRoute.create(api, s - 1, {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': str(ip_address),
            'id': RouteIds.PRIVATE,
        })
        ip_address += 1

    for s in range(1, 4):
        StationRoute.create(
            api,
            s - 1,
            {
                'type': RouteTypes.STATIC_ROUTE,
                'service': f'service:{ser.get_id()}',
                'ip': '0.0.0.0',
                'mask': '/0',
                'gateway': str(ip_address),
                'id': RouteIds.PRIVATE,
            }
        )
        ip_address += 1

    backup.create_backup('mf_hub_3_stations.txt')


if __name__ == '__main__':
    create_config()
