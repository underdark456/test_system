from src.custom_logger import LOGGING, INFO

system = {
    LOGGING: INFO,
}

options = {
    'nms_entities': {
        'network': 128,
        'server': 64,
        'group': 512,  # one group already exists in default config
        'user': 512,  # one user already exists in default config
        'alert': 2048,
        'access_net0': 512,  # have to split into two
        'access_net1': 511,
        'dashboard': 256,
        'teleport': 128,
        'controller': 512,
        'vno': 512,
        'service': 512,
        'shaper': 2048,
        'policy': 512,
        'sr_controller': 32,
        'sr_teleport': 128,
        'device': 2048,
        'polrule': 10000,
        'sr_license': 256,
        'bal_controller': 32,
        'profile_set': 128,
        'sw_upload': 32,
        'camera': 64,
        'scheduler': 64,
        'sch_range': 64,
        'sch_service': 128,
        'route': 65000,
        'rip_router': 256,
        'port_map': 16000,
        'station': 32768,
        'sch_task': 512,
        'qos': 1024,
    },
    'creation_time': {
        'network_exp_time': 1.2,
        'server_exp_time': 0.6,
        'group_exp_time': 5,
        'user_exp_time': 18.6,
        'alert_exp_time': 15.6,
        'access_net0_exp_time': 4.5,
        'access_net1_exp_time': 4.5,
        'dashboard_exp_time': 2,
        'teleport_exp_time': 1,
        'controller_exp_time': 6.2,
        'vno_exp_time': 4.1,
        'service_exp_time': 4,
        'shaper_exp_time': 16.5,
        'policy_exp_time': 4.1,
        'polrule_exp_time': 88.5,
        'sr_controller_exp_time': 0.5,
        'sr_teleport_exp_time': 1,
        'device_exp_time': 18.5,
        'sr_license_exp_time': 2.5,
        'bal_controller_exp_time': 0.5,
        'profile_set_exp_time': 1,
        'sw_upload_exp_time': 0.5,
        'camera_exp_time': 0.5,
        'scheduler_exp_time': 0.5,
        'sch_range_exp_time': 0.5,
        'sch_service_exp_time': 1,
        'route_exp_time': 810,
        'rip_router_exp_time': 2,
        'port_map_exp_time': 139,
        'station_exp_time': 700,
        'sch_task_exp_time': 4,
        'qos_exp_time': 8,
    },
    'deletion_time': {
        'network_del_time': 1,
        'server_del_time': 0.5,
        'group_del_time': 3,
        'user_del_time': 3,
        'alert_del_time': 47,
        'access_net0_del_time': 3,
        'access_net1_del_time': 3,
        'dashboard_del_time': 2,
        'teleport_del_time': 1,
        'controller_del_time': 12,
        'vno_del_time': 3,
        'service_del_time': 4,
        'shaper_del_time': 48,
        'policy_del_time': 3,
        'polrule_del_time': 48,
        'sr_controller_del_time': 0.5,
        'sr_teleport_del_time': 1,
        'device_del_time': 12,
        'sr_license_del_time': 1.5,
        'bal_controller_del_time': 0.5,
        'profile_set_del_time': 3,
        'sw_upload_del_time': 0.5,
        'camera_del_time': 0.5,
        'scheduler_del_time': 1.5,
        'sch_range_del_time': 0.5,
        'sch_service_del_time': 1,
        'route_del_time': 440,
        'rip_router_del_time': 2,
        'port_map_del_time': 74,
        'station_del_time': 16790,
        'sch_task_del_time': 3,
        'qos_del_time': 0.1,
    },
    'expected_list_time': {
        'network': 0.1,
        'server': 0.1,
        'group': 0.1,
        'user': 0.1,
        'alert': 0.15,
        'access_net0': 0.1,
        'access_net1': 0.1,
        'dashboard': 0.2,
        'teleport': 0.1,
        'controller': 1,
        'vno': 0.3,
        'service': 0.1,
        'shaper': 0.15,
        'policy': 0.1,
        'polrule': 0.3,
        'sr_controller': 0.1,
        'sr_teleport': 0.1,
        'device': 0.4,
        'sr_license': 0.1,
        'bal_controller': 0.1,
        'profile_set': 0.1,
        'sw_upload': 0.1,
        'camera': 0.1,
        'scheduler': 0.1,
        'sch_range': 0.1,
        'sch_service': 0.1,
        'route': 3.5,
        'rip_router': 0.1,
        'port_map': 0.3,
        'station': 2,
        'sch_task': 0.1,
        'qos': 0.1,
    },
    'names': {
        'network': 'net',
        'server': 'serv',
        'group': 'grp',
        'user': 'usr',
        'alert': 'alr',
        'dashboard': 'dash',
        'teleport': 'tel',
        'controller': 'ctrl',
        'vno': 'vno',
        'service': 'service',
        'shaper': 'shp',
        'policy': 'pol',
        'sr_controller': 'sr_ctr',
        'sr_teleport': 'sr_tp',
        'device': 'dev',
        'sr_license': 'sr_lic',
        'bal_controller': 'bal_ctr',
        'profile_set': 'pro',
        'sw_upload': 'sw',
        'camera': 'cam',
        'scheduler': 'sched',
        'sch_range': 'sch_r',
        'sch_service': 'sch_s',
        'station': 'stn',
        'sch_task': 'sch_t',
        'qos': 'qos',
    },
    'deletion_order': [
        'sch_task',
        'station',
        'port_map',
        'rip_router',
        'route',
        'sch_service',
        'sch_range',
        'scheduler',
        'camera',
        'sw_upload',
        'profile_set',
        'bal_controller',
        'sr_license',
        'polrule',
        'device',
        'sr_teleport',
        'sr_controller',
        'policy',
        'shaper',
        'vno',
        'controller',
        'teleport',
        'dashboard',
        'access_net0',
        'access_net1',
        'alert',
        'user',
        'group',
        'server',
        'service',
        'qos',
        'network',
    ],

    'expected_search_time': 0.8,
    'expected_delete_time': 0.1,
    'expected_station_delete_time': 0.7,
    'expected_edit_time': 0.1,
}
