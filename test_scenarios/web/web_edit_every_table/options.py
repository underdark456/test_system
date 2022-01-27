from src.options_providers.options_provider import CHROME_CONNECT, CONNECTION

system = {
    CONNECTION: CHROME_CONNECT,
    CHROME_CONNECT: {
        'no_gui': True,
        'window_size': (1920, 1080),
    },
}

options = {
    'number_of_access': 1024,  # added
    'number_of_alert': 2048,  # added
    'number_of_bal_controller': 32,  # added
    'number_of_camera': 64,  # added
    'number_of_controller': 512,  # added
    'number_of_dashboard': 256,  # added
    'number_of_device': 2048,  # added
    'number_of_group': 512,  # added
    'number_of_network': 128,  # added
    'number_of_policy': 512,  # added
    'number_of_polrule': 10000,  # added
    'number_of_port_map': 16000,  # added
    'number_of_profile_set': 128,  # added
    'number_of_rip_router': 256,  # added
    'number_of_route': 65000,  # added
    'number_of_server': 64,  # added
    'number_of_service': 512,  # added
    'number_of_shaper': 2048,  # added
    'number_of_sr_controller': 32,  # added
    'number_of_sr_license': 256,  # added
    'number_of_sr_teleport': 128,  # added
    'number_of_station': 32768,  # added
    'number_of_sw_upload': 32,  # added
    'number_of_teleport': 128,  # added
    'number_of_user': 512,  # added
    'number_of_vno': 512,  # added
    'number_of_scheduler': 64,  # added
    'number_of_sch_range': 64,  # added
    'number_of_sch_service': 128,  # added
}
