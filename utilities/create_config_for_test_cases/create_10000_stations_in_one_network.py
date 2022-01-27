import ipaddress
import random
import time

from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, CheckboxStr, StationModes, LatitudeModes, LongitudeModes
from src.exceptions import ObjectNotCreatedException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.teleport import Teleport
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
    """Config 10000 stations in 1 network, 5 controllers with 2000 stations each"""
    backup = BackupManager()
    backup.apply_backup(backup_name)
    if driver is None:
        api = get_drivers()
    else:
        api = driver
    number_of_stations = 10000
    net = Network.create(api, 0, params={'name': 'net-0'})
    vno = Vno.create(api, 0, params={'name': 'vno-0'})
    tp = Teleport.create(api, net.get_id(), params={
        'name': 'tp-0',
        'sat_name': 'sat',
        'tx_lo': 0,
        'rx1_lo': 0,
        'rx2_lo': 0
    })
    st_time = time.perf_counter()
    for i in range(number_of_stations // 2000):
        ctrl = Controller.create(api, net.get_id(), params={
            'name': f'ctrl-{i}',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{tp.get_id()}',
            'device_ip': str(ipaddress.IPv4Address('127.0.0.1') + i),
            'stn_number': 2000,
            'tx_on': CheckboxStr.ON,
            'tx_level': 22
        })

        for j in range(2000):
            Station.create(api, vno.get_id(), params={
                'name': f'stn-{i * 2000 + j}',
                'serial': i * 2000 + j + 1,
                'mode': StationModes.STAR,
                'rx_controller': f'controller:{ctrl.get_id()}',
                'enable': 'ON',
                'fixed_location': True,
                'lat_deg': random.randint(0, 89),
                'lat_min': random.randint(0, 59),
                'lat_south': random.choice([*LatitudeModes()]),
                'lon_deg': random.randint(0, 179),
                'lon_min': random.randint(0, 59),
                'lon_west': random.choice([*LongitudeModes()]),
                'time_zone': random.randint(-12, 12),
            })
    print(f'{number_of_stations} stations creation time is {time.perf_counter() - st_time} seconds')
    stations = Station.station_list(api, 0, vars_=['name'])
    if number_of_stations != len(stations):
        raise ObjectNotCreatedException(f'Expected {number_of_stations} stations created, got {len(stations)}')
    backup.create_backup('10000_stations_in_1_network.txt')


if __name__ == '__main__':
    create_config()
