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
    'search_tool_unique_names': {
        'nms': 'reliable_nms',
        'server': 'amazing_server',
        'group': 'prominent_group',
        'user': 'renowned_user',
        'alert': 'shiny_alert',
        'dashboard': 'intelligent_dashboard',
        'network': 'brilliant_network',
        'teleport': 'beautiful_teleport',
        'controller': 'fashionable_controller',
        'vno': 'charming_vno',
        'service': 'elegant_service',
        'shaper': 'trustworthy_shaper',
        'policy': 'ambitious_policy',
        'sr_controller': 'lovely_sr_controller',
        'sr_teleport': 'agreeable_sr_teleport',
        'device': 'courteous_device',
        'sr_license': 'helpful_sr_license',
        'bal_controller': 'witty_bal_controller',
        'profile_set': 'gorgeous_profile_set',
        'sw_upload': 'supportive_sw_upload',
        'camera': 'faithful_camera',
        'scheduler': 'passionate_scheduler',
        'sch_range': 'sincere_sch_range',
        'sch_service': 'adorable_sch_service',
        'station': 'enthusiastic_station',
        'sch_task': 'seductive_sch_task',
        'qos': 'intelligent_qos',
    },
}
