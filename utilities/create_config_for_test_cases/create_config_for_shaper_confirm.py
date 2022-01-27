import random
from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import StationModes, ControllerModes, Checkbox, ShaperUpQueue, CheckboxStr
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.station import Station
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
    """Config for WEB dropdowns case - maximum number of entities appearing in dynamic dropdowns"""
    backup = BackupManager()
    backup.apply_backup(backup_name)
    if driver is None:
        api = get_drivers()
    else:
        api = driver

    net = Network.create(api, 0, {'name': 'test_net', 'sat_name': 'test_sat'})
    tp = Teleport.create(api, net.get_id(), {
        'name': 'test_tp',
        'tx_lo': 0,
        'rx1_lo': 0,
        'rx2_lo': 0,
    })

    # Controller shapers block
    next_shp = Shaper.create(api, net.get_id(), {
        'name': 'ctrl_shp-0',
        'cir': 128,
    })
    for i in range(1, 10):
        next_shp = Shaper.create(api, next_shp.get_id(), {
            'name': f'ctrl_shp-{i}',
            'cir': 128 - i,
            'up_queue': random.choice([*ShaperUpQueue()]),
            'max_enable': random.choice([*CheckboxStr()]),
            'max_cir': 128 + 2 * i,
            'max_slope': random.randint(1, 16),
            'min_enable': random.choice([*CheckboxStr()]),
            'min_cir': 128 - 2 * i,
            'down_slope': random.randint(1, 16),
            'up_slope': random.randint(1, 16),
            'wfq_enable': random.choice([*CheckboxStr()]),
            'wfq1': 30,
            'wfq2': 15,
            'wfq3': 15,
            'wfq4': 20,
            'wfq5': 10,
            'wfq6': 10,
            'night_enable': random.choice([*CheckboxStr()]),
            'night_cir': 128 * i,
            'night_start': random.randint(0, 23),
            'night_end': random.randint(0, 23),
        },
            parent_type='shaper')
    # End of controller shapers block
    ctrl = Controller.create(api, net.get_id(), {
        'name': 'test_ctrl',
        'mode': ControllerModes.MF_HUB,
        'teleport': f'teleport:{tp.get_id()}',
        'tx_on': Checkbox.ON,
        'tx_level': 20,
        'hub_shaper': f'shaper:{next_shp.get_id()}'

    }
    )

    # VNO shapers block
    next_shp = Shaper.create(api, net.get_id(), {
        'name': 'vno_shp-0',
        'cir': 128,
    })
    for i in range(1, 10):
        next_shp = Shaper.create(api, next_shp.get_id(), {
            'name': f'vno_shp-{i}',
            'cir': 128 - i,
            'up_queue': random.choice([*ShaperUpQueue()]),
            'max_enable': random.choice([*CheckboxStr()]),
            'max_cir': 128 + 2 * i,
            'max_slope': random.randint(1, 16),
            'min_enable': random.choice([*CheckboxStr()]),
            'min_cir': 128 - 2 * i,
            'down_slope': random.randint(1, 16),
            'up_slope': random.randint(1, 16),
            'wfq_enable': random.choice([*CheckboxStr()]),
            'wfq1': 30,
            'wfq2': 15,
            'wfq3': 15,
            'wfq4': 20,
            'wfq5': 10,
            'wfq6': 10,
            'night_enable': random.choice([*CheckboxStr()]),
            'night_cir': 128 * i,
            'night_start': random.randint(0, 23),
            'night_end': random.randint(0, 23),
        },
            parent_type='shaper')
    vno = Vno.create(api, net.get_id(), {
        'name': 'test_vno',
        'hub_shaper': f'shaper:{next_shp.get_id()}',
        'stn_shaper': f'shaper:{next_shp.get_id()}',
    })
    # End of VNO shapers block

    # Stations shapers block
    for i in range(10):
        stn_shaper = Shaper.create(api, net.get_id(), {'name': f'stn_shp-{i}', 'cir': random.randint(64, 256)})
        if random.random() > 0.5:
            Station.create(api, vno.get_id(), {
                'name': f'stn-{i}',
                'serial': 10000 + i,
                'enable': Checkbox.ON,
                'mode': StationModes.STAR,
                'rx_controller': f'controller:{ctrl.get_id()}',
                'hub_shaper': f'shaper:{stn_shaper.get_id()}',
                'stn_shaper': f'shaper:{stn_shaper.get_id()}',
            })
        else:
            Station.create(api, vno.get_id(), {
                'name': f'stn-{i}',
                'serial': 10000 + i,
                'enable': Checkbox.ON,
                'mode': StationModes.STAR,
                'rx_controller': f'controller:{ctrl.get_id()}',
            })
    backup.create_backup('case_shaper_config_confirm.txt')


if __name__ == '__main__':
    create_config()
