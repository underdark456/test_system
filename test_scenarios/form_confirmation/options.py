# Don`t change this file!
# For overriding the file create local_options.py in the current folder with 'options' and/or 'system' dicts inside.

from src.enum_types_constants import AlertModes, ControllerModes, ControlModes

system = {

}

options = {
    'nms_id': 0,
    'network': {
        'name': 'TEST_TP_NET',
        'alert_mode': AlertModes.INHERIT,
        'dev_password': 'indeed',
    },
    'controller': {
        'settings': {
            'name': 'CTRL-1',
            'mode': ControllerModes.HUBLESS_MASTER,
            'control': ControlModes.FULL,
            'up_timeout': '44',
        },
        'teleport': {
            'teleport': 'teleport:0',
        },
        'device': {
            'name': 'UHP1',
        },
    }
}
