import random
import time

from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes, LatitudeModes, LongitudeModes
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
    Network.create(api, 0, params={'name': 'net1'})
    Vno.create(api, 0, params={'name': 'vno1'})
    Teleport.create(api, 0, params={'name': 'tp1', 'sat_name': 'sat1'})
    Controller.create(
        api,
        0,
        params={'name': 'ctrl1', 'mode': ControllerModes.HUBLESS_MASTER, 'teleport': f'teleport:0'}
    )
    st_time = time.perf_counter()
    for i in range(1, 32769):
        Station.create(api, 0, params={
            'name': f'stn-{i}',
            'mode': StationModes.HUBLESS,
            'enable': 'ON',
            'rx_controller': 'controller:0',
            'serial': i,
            'fixed_location': True,
            'lat_deg': random.randint(0, 89),
            'lat_min': random.randint(0, 59),
            'lat_south': random.choice([*LatitudeModes()]),
            'lon_deg': random.randint(0, 179),
            'lon_min': random.randint(0, 59),
            'lon_west': random.choice([*LongitudeModes()]),
            'time_zone': random.randint(-12, 12),
        })
    print(f'32768 stations creation time is {time.perf_counter() - st_time} seconds')
    stations1 = Station.station_list(api, 0, vars_=['name'], max_=15000)
    stations2 = Station.station_list(api, 0, vars_=['name'], skip=15000)
    if 32768 != len(stations1) + len(stations2):
        raise ObjectNotCreatedException(f'Expected 32768 stations created, got {len(stations1) + len(stations2)}')
    backup.create_backup('32768_stations_1_vno.txt')


if __name__ == '__main__':
    create_config()
