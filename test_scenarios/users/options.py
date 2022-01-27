from src.enum_types_constants import StationModes
from src.options_providers.options_provider import CONNECTION, API_CONNECT, CHROME_CONNECT

system = {
    CHROME_CONNECT: {
        'no_gui': True,
    },
    CONNECTION: API_CONNECT,
}

options = {
    'number_of_groups': 512,
    'number_of_users': 512,
    'users': {
        'user1': {
            'login': 'admin',
            'password': 12345
        },
        'user2': {
            'login': 'admin',
            'password': 12345
        },
        'user3': {
            'login': 'admin',
            'password': 12345
        },
        'user4': {
            'login': 'admin',
            'password': 12345
        },
    },
    'nms_objects': {
        'station': {
            'id': 0,
            'vno_id': 0,
            'params': {
                'name': 'default name',
                'mode': StationModes.STAR,
                'serial': '123123',
                'rx_controller': '0',
            },
            'rx_controllers': [
                'controller:0',
                'controller:1',
                'controller:2',
                'controller:3',
                'controller:4',
            ]
        }
    }
}
