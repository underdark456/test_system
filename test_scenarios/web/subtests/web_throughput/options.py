from src.drivers.abstract_http_driver import API
from src.options_providers.options_provider import API_CONNECT, CONNECTION

system = {
    API_CONNECT: {
        'type': API,
        'address': "http://localhost:8000/",
        'username': "admin",
        'password': "12345",
        'auto_login': True,
    },
    CONNECTION: API_CONNECT,
}

options = {
    'number_of_users': 8,
    'ramp_up_period': 24,
    'number_of_get_requests': 5000,
    'number_of_post_requests': 30000,
    'static_urls': [
        'static/js/16.js',
        'static/js/17.js',
        'static/js/18.js',
        'static/js/19.js',
        'static/js/20.js',
    ],
    'get_urls': [
        'api/object/get/controller=0',
        'api/object/dashboard/network=0',
        'api/form/get/controller=0',
        'api/form/edit/controller=0',
        'api/log/get/network=0',
        'api/tree/get/nms=0',
        'api/station/list/network=0',
        'api/tree/problems/nms=0',
        'api/list/edit/network=0/list_items=controller',
        'api/search/get/controller=0',
    ],
    'post_urls': {
        # 'api/realtime/get/controller=0': {"command": "show int eth", "control": 0},
        'api/graph/get/network=0':
            {
                "start": 1626767518.281,
                "end": 1629359518.281,
                "dots": 400,
                "graphNumber": 2,
                "minmax": True,
                "faults": True
            },
        'api/map/both/network=0': {"marker_mode": "num_state"},
        'api/form/edit/controller=0': {'name': 'same_name'},
    }
}
