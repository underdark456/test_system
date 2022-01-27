from src.custom_logger import INFO, LOGGING
from src.enum_types_constants import StationModes, ControllerModes

system = {
    LOGGING: INFO,
}
options = {
    'hubless_master': {
        'network_id': 0,
        'values': {
            'name': 'HM',
            'mode': ControllerModes.HUBLESS_MASTER,
            'teleport': 'teleport:0',
            'up_timeout': 100,
        },
    },
    'alert': {
        'name': 'ALERT',
        'priority': 'Medium',
        'popup': True,
        'sound': True,
        'file_name': 'alert.mp3',
        'repeat_sound': True,
        'run_script': True,
        'script_file': 'log_to_text_file.sh',
    },
    'service': {
        'name': 'Service-01',

    },
    'user_group': {
        'name': 'U_Group_02',
        'active': True,
    },
    'user': {
        'name': 'User_01',
        'enable': True,
        'email': 'Mail_name',
        'first_name': 'Name',
        'last_name': 'LastName',
        'password': '12345'
    },
    'controller': {
        'network_id': 0,
        'values': {
            'name': "MF_HUB",
            'mode': ControllerModes.MF_HUB,
            'teleport': 'teleport:0',
            'up_timeout': 100,

        },
    },
    'controller_route': {
        'controller_id': 3,
        'route_values': {
            'type': 'IP_address',
            'service': 'service:0',
            'id': 'Normal',
            'ip': '100.101.102.103',
            'mask': '/24',
            'override_vlan': False,
        },
    },
    'station_route': {
        'station_id': 0,
        'route_values': {
            'type': 'IP_address',
            'service': 'service:0',
            'id': 'Normal',
            'ip': '100.101.100.103',
            'mask': '/24',
            'override_vlan': False,
        },
    },
    'controller_empty_name': {
        'network_id': 0,
        'values': {
            'name': "",
            'mode': ControllerModes.MF_HUB,
            'up_timeout': 100,

        },

    },
    'station': {
        'vno_id': 0,
        'values': {
            'name': "station_01",
            'mode': StationModes.STAR,
            'serial': 123,
            'rx_controller': 'controller:0',
            'enable': 1
        },

    },
    'station_empty_name': {
        'vno_id': 0,
        'values': {
            'name': "",
            'mode': StationModes.STAR,
            'serial': 123
        },

    },
    'teleport': {
        'network_id': 0,
        'values': {
            'name': 'TELEPORT',
        },

    },
    'network': {
        'nms_id': 0,
        'values': {
            'name': 'TEST_NET',
        },

    },
    'vno': {
        'network_id': 0,
        'values': {
            'name': 'VNO-',
        },

    },
    'vno_empty_name': {
        'network_id': 0,
        'values': {
            'name': '',
        },
    },
    'teleport_empty_name': {
        'network_id': 0,
        'values': {
            'name': '',
        },

    },
    'shaper': {
        'network_id': 0,
        'values': {
            'name': 'shp-89122',
        },
    },
    'number_of_test_cycle': 10,
    'number_of_access': 1024,
    'number_of_alert': 2048,
    'number_of_bal_controller': 32,  # not added yet
    'number_of_camera': 64,
    'number_of_controller': 512,
    'number_of_dashboard': 256,  # not added yet
    'number_of_device': 2048,  # not added yet
    'number_of_group': 512,
    'number_of_network': 128,
    'number_of_policy': 512,
    'number_of_polrule': 10000,
    'number_of_port_map': 16000,   # not added yet
    'number_of_profile_set': 128,
    'number_of_rip_router': 256,  # not added yet
    'number_of_route': 65000,
    'number_of_server': 64,
    'number_of_service': 512,
    'number_of_shaper': 2048,
    'number_of_sr_controller': 32,  # not added yet
    'number_of_sr_license': 256,  # not added yet
    'number_of_sr_teleport': 128,  # not added yet
    'number_of_station': 32768,
    'number_of_sw_upload': 32,  # not added yet
    'number_of_teleport': 128,
    'number_of_user': 512,
    'number_of_vno': 512,
}
