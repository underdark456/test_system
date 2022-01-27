from src.custom_logger import LOGGING, OK, INFO, FAIL

system = {
    LOGGING: FAIL,
}

options = {
    'number_of_sessions': 50,
    'number_of_requests': 10000,
    'api': [
        'api/object/write/{}={}/new_item={}',
        'api/object/get/{}={}',
        'api/object/write/{}={}',
        'api/object/delete/{}={}',
        'api/object/dashboard/{}',
        'api/object/new/{}={}/new_item={}'

        'api/form/get/{}={}',
        'api/form/edit/{}={}',
        'api/form/write/{}={}',
        'api/form/delete/{}={}',
        'api/form/new/{}={}/new_item={}',
        'api/map/both/{}={}',
        'api/log/get/{}={}',
        'api/graph/get/{}={}',
        'api/tree/get/{}={}',
        'api/{}/list/{}={}',
        'api/tree/problems/{}={}',
        'api/list/edit/{}={}/list_items={}',
        'api/realtime/get/{}={}',
        'api/search/get/{}={}',

    ],
    'api_list': [
        'api/list/get/{}={}/list_items={}/list_skip={}/list_max={}/list_vars={}',
    ],
    'web': [
        "form/new/{}={}/new_item={}",
        "form/edit/{}={}",
        "list/edit/{}={}/list_items={}",
        "object/dashboard/{}={}",
        "logs/get/{}={}",
        'realtime/get/{}={}',
    ],
    'entities': [
        'nms',
        'network',
        'controller',
        'service',
        'vno',
        'teleport',
        'policy',
        'polrule',
        'station',
        'profile_set',
        'shaper',
        'alert',
        # 'user',
        # 'group',
        'route',
        'dashboard',
        'bal_controller',
        'sr_controller',
        'sr_license',
        'sr_teleport',
        'device',
        'server',
        # 'access',
        'camera',
        'port_map',
        'sw_upload',
        'rip_router',
        'scheduler',
        'sch_range',
        'sch_service',
    ],

}
