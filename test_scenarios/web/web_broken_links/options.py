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
    'menu_main_class': 'menu__main',
    'menu_config_class': 'menu__configbody',
    'breadcrumb_items_class': 'breadcrumbs__item',
    'dashboard_id': 'mainbtn',

    'object_names': {
        'nms': 'UHP NMS',
        'network': 'test_network',
        'sr_controller': 'test_sr_ctrl',
        'sr_teleport': 'test_sr_tp',
        'device': 'test_device',
        'qos': 'test_qos',
    },

    'device_path': [
        "/form/edit/nms=0_|_UHP NMS",
        "/list/edit/nms=0/list_items=network_|_networks",
        "/form/edit/network=0_|_test_network",
        "/list/edit/network=0/list_items=sr_controller_|_sr_controllers",
        "/form/edit/sr_controller=0_|_test_sr_ctrl",
        "/list/edit/sr_controller=0/list_items=sr_teleport_|_sr_teleports",
        "/form/edit/sr_teleport=0_|_test_sr_tp",
        "/list/edit/sr_teleport=0/list_items=device_|_devices",
        "/form/edit/device=0_|_test_device",
    ],
    'device_path_dash': [
        "/object/dashboard/nms=0_|_UHP NMS",
        "/list/get/nms=0/list_items=network_|_networks",
        "/object/dashboard/network=0_|_test_network",
        "/list/get/network=0/list_items=sr_controller_|_sr_controllers",
        "/object/dashboard/sr_controller=0_|_test_sr_ctrl",
        "/list/get/sr_controller=0/list_items=sr_teleport_|_sr_teleports",
        "/object/dashboard/sr_teleport=0_|_test_sr_tp",
        "/list/get/sr_teleport=0/list_items=device_|_devices",
        "/object/dashboard/device=0_|_test_device",
    ]
}
