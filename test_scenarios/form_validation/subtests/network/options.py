from src.enum_types_constants import AlertModes
from src.values_presenters import NotEmptyString, AnyValue

options = {
    'id': 0,
    'test_values': {
        'settings': {
            'name': [12, '', '%%%', 'Network', 'Иямямямя'],
            'alert_mode': [
                'str', AlertModes.OFF, AlertModes.INHERIT, AlertModes.SPECIFY
            ],  # обязятельно последним SPECIFY
            'set_alert': ['asda', 'alert:0', 'alert:56'],
            'traffic_scale': [12, '', '%%%', 'nms', 'дескрипшон', 50001],
            'level_scale': [12, '', '%%%', 'nms', 'дескрипшон', 36],
        },
        'additional_setup': {
            'dev_password': ['a' * 15, '1234', 1234, ''],
        },
        'beams': {
            'beam1_file': ['', 'example.gxt', 'test_gxt'],
            'beam2_file': ['', 'example.gxt'],
            'beam3_file': ['', 'example.gxt'],
            'beam4_file': ['', 'example.gxt']
        }
    },
    'valid_values': {
        'settings': {
            'name': [12, '', '%%%', 'Network', 'Иямямямя'],
            'alert_mode': [
                'str', AlertModes.OFF, AlertModes.INHERIT, AlertModes.SPECIFY
            ],
            'set_alert': ['alert:0'],
            'traffic_scale': [12, ''],
            'level_scale': [12, ''],
        },
        'additional_setup': {
            'dev_password': ['1234', 1234, ''],
        },
        'beams': {
            'beam1_file': ['example.gxt', ''],
            'beam2_file': ['example.gxt', ''],
            'beam3_file': ['example.gxt', ''],
            'beam4_file': ['example.gxt', '']
        }
    },

}
