from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

__author__ = 'Filipp Gaidanskiy'
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
    """
    DAMA network config: DAMA hub, DAMA station. Two services: one for management without ips,
    to not lose access to devices; one service for traffic with ip addresses.
    """
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
    dama_station_01 = Station.create(api, vno.get_id(), options.get('dama_station_01'))
    Service.create(api, net.get_id(), options.get('service'))
    Service.create(api, net.get_id(), options.get('service_traffic-01'))
    StationRoute.create(api, dama_station_01.get_id(), options.get('station01_ip'))
    StationRoute.create(api, dama_station_01.get_id(), options.get('station01_gw'))
    StationRoute.create(api, dama_station_01.get_id(), options.get('station01_traffic_ip'))
    ControllerRoute.create(api, dama_hub.get_id(), options.get('hub_traffic_ip'))

    backup.create_backup('dama_net_hub_stn.txt')


if __name__ == '__main__':
    create_config()
