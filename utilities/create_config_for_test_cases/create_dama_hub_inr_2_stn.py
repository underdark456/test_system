from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

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
    """DAMA network config: DAMA hub, DAMA inroute, two DAMA stations on hub chA, inr chB"""
    backup = BackupManager()
    backup.apply_backup(backup_name)
    if driver is None:
        api = get_drivers()
    else:
        api = driver

    options = get_options()
    net = Network.create(api, 0, options.get('network'))
    Teleport.create(api, net.get_id(), options.get('teleport'))
    vno = Vno.create(api, net.get_id(), options.get('vno'))
    dama_hub = Controller.create(api, net.get_id(), options.get('dama_hub'))
    dama_inroute = Controller.create(api, net.get_id(), options.get('dama_inroute'))
    dama_station_01 = Station.create(api, vno.get_id(), options.get('dama_station_01'))
    dama_station_02 = Station.create(api, vno.get_id(), options.get('dama_station_02'))
    service = Service.create(api, net.get_id(), options.get('service'))
    traffic_service = Service.create(api, net.get_id(), options.get('service_traffic-01'))
    station_01_ip = StationRoute.create(api, dama_station_01.get_id(), options.get('station01_ip'))
    station_02_ip = StationRoute.create(api, dama_station_02.get_id(), options.get('station02_ip'))
    station_01_gw = StationRoute.create(api, dama_station_01.get_id(), options.get('station01_gw'))
    station_02_gw = StationRoute.create(api, dama_station_02.get_id(), options.get('station02_gw'))

    backup.create_backup('dama_net_hub_inr_2_stn.txt')


if __name__ == '__main__':
    create_config()
