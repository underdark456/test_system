from src.custom_logger import LOGGING, INFO

system = {
    LOGGING: INFO,
}

options = {
    'invalid_tables': [
        'adddaadda',
        ' ',
        2323322332,
        -1,
        'uhp'
    ],
    'invalid_rows': [
        65001,
        21908901221,
        -12121221,
        'qwerty',
        1000,
        '',
        '\r\n'
    ],
    'invalid_requests': [
        'api/list/get/',
        'api/adadda',
        'api',
        'api/ввавфыав',
        'api/object/write/',
        'api/object/delete/',
        'api/realtime/get/',
    ],
    'abbreviated_values': [
        'dev',
        'tx',
        'rx',
        'tlc',
        'tdma',
        'tftp',
        'rip',
        'mod'
    ],
    'get_paths': [
        'api/object/get/{}={}',
        'api/form/get/{}={}',
        'api/object/dashboard/{}={}',
        'api/object/delete/{}={}',
        'api/object/new/{}={}/new_item=new_item_table',
        'api/form/new/{}={}/new_item=new_item_table',
        'api/list/get/{}={}/list_items=network',
        'api/form/delete/{}={}',
        'api/log/get/{}={}',
        'api/realtime/get/{}={}',
        'api/map/list/{}={}',
        'api/object/dashboard/{}={}',
        'api/graph/get/{}={}',
        'api/station/list/{}={}',
        'api/tree/get/{}={}',
    ],
    'post_paths': [
        'api/object/write/{}={}',
        'api/object/write/{}={}/new_item=network',
    ],
}
