from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

options_path = 'utilities.create_typical_nms_config'
backup_name = 'default_config.txt'


def get_drivers():
    connection_options = OptionsProvider.get_connection('global_options', API_CONNECT)
    api = DriversProvider.get_driver_instance(connection_options)
    return api


def create_starblazer_config():
    options = OptionsProvider.get_options(options_path).get('starblazer')
    backup = BackupManager()
    backup.apply_backup(backup_name)

    api = get_drivers()

    for network_name in options.get('network_names'):
        Network.create(api, 0, {'name': network_name})

    for vno_name in options.get('AM7_vnos'):
        print(vno_name)
        Vno.create(api, 0, {'name': vno_name})

    for vno_name in options.get('AM8C_vnos'):
        Vno.create(api, 1, {'name': vno_name})

    for vno_name in options.get('Yamal 401_vnos'):
        Vno.create(api, 2, {'name': vno_name})

    for vno_name in options.get('AM5_vnos'):
        Vno.create(api, 3, {'name': vno_name})

    for vno_name in options.get('AM8_vnos'):
        Vno.create(api, 4, {'name': vno_name})


def stations_creation():
    """stations creation for Starblazer vno AM8C-Af"""
    options = OptionsProvider.get_options(options_path).get('starblazer')
    api = get_drivers()

    for i in range(1, 200):
        options['station']['values']['name'] = 'Опоп-' + str(i)
        options['station']['values']['serial'] = str(i)

        Station.create(
            api,
            options['station']['vno_id'],
            options['station']['values'],
        )


if __name__ == '__main__':
    stations_creation()
