from src.drivers.abstract_http_driver import CHROME
from src.options_providers.options_provider import CHROME_CONNECT, CONNECTION

system = {
    CHROME_CONNECT: {
        'type': CHROME,
        'no_gui': False,
        'maximize_window': True,
        # 'window_size': (1920, 1080),
    },
    CONNECTION: CHROME_CONNECT,
}

options = {
    'devices_graphs': {
        'UHP NMS': True,
        'test_network': True,
        'test_ctrl': True,
        'test_sr_ctrl': False,
        'test_sr_tp': False,
        'test_device': False,
        'test_bal_ctrl': False,
        'test_vno': True,
        'test_stn': True,
        'test_sw_up': False,
    },
    'graph_options_net': [
        'Levels',
        'Traffic summary',
        'TX traffic detailed',
        'RX traffic detailed',
        'Stations state',
        'Errors',
        'Controllers state',
    ],
    'graph_options_vno': [
        'Levels',
        'Traffic summary',
        'TX traffic detailed',
        'RX traffic detailed',
        'Stations state',
        'Errors',
    ],
    'graph_options_ctrl': [
        'Levels',
        'Traffic summary',
        'Levels detailed',
        'TX traffic detailed',
        'RX traffic detailed',
        'TDMA load',
        'Stations state',
        'Errors',
        'State',
    ],
    'graph_options_stn': [
        'Levels',
        'Traffic summary',
        'TX traffic detailed',
        'RX traffic detailed',
        'ACM',
        'TDMA load',
        'Errors',
    ],
}
