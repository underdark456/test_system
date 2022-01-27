from src.options_providers.options_provider import CONNECTION, API_CONNECT

system = {
    CONNECTION: API_CONNECT
}

options = {
    'hubless_master': {
        'device_ip': '10.56.24.11',
        'device_mask': '/24',
        'device_vlan': 0,
    },
    'hubless_station': {
        'device_ip': '10.56.24.12',
        'device_mask': '/24',
        'device_vlan': 0,
    },
    'MTU': 2000,
    'NUMBER_OF_PACKETS': 100,
    'PPS': 350,
}
