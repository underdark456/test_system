from src.custom_logger import LOGGING, DEBUG
from src.options_providers.options_provider import API_CONNECT, CONNECTION
from src.values_presenters import CHECK_BOX_TEST_VALUES, CHECK_BOX_VALID_VALUES, StrIntRange, \
    CHECK_BOX_TEST_VALUES_ENABLE

system = {
    CONNECTION: API_CONNECT,
    LOGGING: DEBUG,
}

options = {
    'depending_params': {
        'load_lower1': {'dep': 'load_higher1', 'lower': 'load_lower1', 'higher': 'load_higher1'},
        'load_higher1': {'dep': 'load_lower1', 'lower': 'load_lower1', 'higher': 'load_higher1'},
        'load_lower2': {'dep': 'load_higher2', 'lower': 'load_lower2', 'higher': 'load_higher2'},
        'load_higher2': {'dep': 'load_lower2', 'lower': 'load_lower2', 'higher': 'load_higher2'},

        'vlan_min': {'dep': 'vlan_max', 'lower': 'vlan_min'},
        'vlan_max': {'dep': 'vlan_min', 'lower': 'vlan_min'},
        'tos_min': {'dep': 'tos_max', 'lower': 'tos_min'},
        'tos_max': {'dep': 'tos_min', 'lower': 'tos_max'},
        'dscp_min': {'dep': 'dscp_max', 'lower': 'dscp_min'},
        'dscp_max': {'dep': 'dscp_min', 'lower': 'dscp_min'},
        'port_min': {'dep': 'port_max', 'lower': 'port_min'},
        'port_max': {'dep': 'port_min', 'lower': 'port_min'},

        'own_cn_low': {'dep': 'own_cn_high', 'lower': 'own_cn_low'},
        'own_cn_high': {'dep': 'own_cn_low', 'lower': 'own_cn_low'},
        'from_svlan': {'dep': 'to_svlan', 'lower': 'from_svlan'},
        'to_svlan': {'dep': 'from_svlan', 'lower': 'from_svlan'},

        'hub_low_cn': {'dep': 'hub_high_cn', 'lower': 'hub_low_cn'},
        'hub_high_cn': {'dep': 'hub_low_cn', 'lower': 'hub_low_cn'},
        'station_low_cn': {'dep': 'station_high_cn', 'lower': 'station_low_cn'},
        'station_high_cn': {'dep': 'station_low_cn', 'lower': 'station_low_cn'},
    },

    'checkbox_test_values': [0, 1, '0', '1', 'text', True, False, '', 'none', 'sudo', '2', 5, None],
    'checkbox_test_values_on': [1, '1', True, 'c', 'ON', 'on'],
    'checkbox_test_values_off': [0, '0', 'OFF', 'FF', ' F', 'off', False],
    'checkbox_response_on': ['ON ', 'ON', 'On ', 'On', 'on ', 'on'],
    'checkbox_response_off': ['OFF', 'Off', 'off'],

    'text_input_test_values': ['', 'qwerty', 'кириллица', '#$&^%@$#)(~', '   '],
    'pass_test_values': ['', 'qwerty', '#$&^%@$#)(~', ],
}
