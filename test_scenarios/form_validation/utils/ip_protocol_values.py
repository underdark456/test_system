from src.enum_types_constants import SntpModes, LanCheckModes, SnmpModes, SnmpAuth
from src.values_presenters import CHECK_BOX_TEST_VALUES, StrIntRange, CHECK_BOX_VALID_VALUES, AnyValue, \
    TEXT_FIELD_TEST_VALUES

# Общие для станций и контроллеров параметры
test_values = {
    'ip_screening': {
        'ip_screening': ['1', 'str', '0', 2, 4],
    },
    'snmp': {
        'snmp_mode': [
            '0', '2', '3', 2, 'str', '1', -1, 4, SnmpModes.OFF, SnmpModes.V1_V2C, SnmpModes.V3
        ],  # обязательно последним SnmpModes.V3
        'access1_ip': ['1.1.1.1.1', '1.1.1.1'],  # TODO сделать валидатор адресов
        'access2_ip': ['1.1.1.1.1', '1.1.1.1'],
        'snmp_auth': [
            '0', '2', '3', 2, 'str', '1', -1, 4, SnmpAuth.NO_AUTH, SnmpAuth.AUTH_NO_PRIV, SnmpAuth.AUTH_PRIV
        ],  # обязательно последним SnmpAuth.AUTH_PRIV
        'snmp_user': TEXT_FIELD_TEST_VALUES,
        'snmp_read': [12, '', '%%%', 'Read', 'sdfsdlgjslighsegiohsegoihsegosheguhsefgush'],
        'snmp_write': [12, '', '%%%', 'Write', 'sdfsdlgjslighsegiohsegoihsegosheguhsefgush'],
    },
    'dhcp': {
        'on': {
            'dhcp_vlan': ['0', 0, '4095', '4096', 4096, '-30', '20000000000000'],
            'dhcp_ip_start': ['1.1.1.1.1', '1.1.1.1'],
            'dhcp_ip_end': ['1.1.1.1.1', '1.1.1.1'],
            'dhcp_mask': ['/44', '/24'],
            'dhcp_gateway': ['1.1.1.1.1', '1.1.1.1'],
            'dhcp_dns': ['1.1.1.1.1', '1.1.1.1'],
            'dhcp_timeout': ['30', 30, '86400', 86400, '29', 29, '86401', 86401, '200'],
        },
        'relay': {
            'dhcp_vlan': ['0', 0, '4095', '4096', 4096, '-30', '20000000000000'],
            'dhcp_helper': ['1.1.1.1.1', '1.1.1.1'],
            'dhcp_local_ip': ['1.1.1.1.1', '1.1.1.1'],
        }
    },
    'dns': {
        'dns_timeout': ['1', 1, '60', 60, 'str', '61', 61, '0', 0, '20'],
    },
    'dns_with_api': {
        'dns_caching': [1, 4, '1', 'dfsf', 0]
    },
    'arp': {
        'arp_timeout': [-999999999999, -1, 1, '30', 31, '0', 'str', '200', 9999999999999],
        'proxy_arp': [0, 1],
    },
    'arp_with_api': {
        'proxy_arp': ['sdf', 'true', 'false', 'on', 'off', 1, 0, '1', '0'],
    },
    'tftp': {
        'tftp_server': ['1.1.1.1.1', '1.1.1.1'],
        'tftp_vlan': [-12312323, '0', 4095, '4096', 3453564375457, 'str', '200'],
    },
    'nat': {
        'nat_ext_ip': ['1.1.1.1.1', 2, '1.1.1.1'],
        'nat_int_ip': ['1.1.1.1.1', 2, '1.1.1.1'],
        'nat_int_mask': ['/44', 24, '/24', '255.255.255.0'],
    },
    'nat_with_api': {
        'nat_enable': CHECK_BOX_TEST_VALUES
    },
    'rip': {
        'rip_next_hop': ['1.1.1.1.1', 2, '1.1.1.1', 'sdfsddf'],
        'rip_omit_down': [0, 1],
        'rip_omit_sm': [0, 1],
        'rip_cost': [-99999999, -1, 0, '1', 16, '17', 0, '2', 999999999999999],
    },
    'rip_with_api': {
        'rip_enable': CHECK_BOX_TEST_VALUES,
        'rip_omit_down': CHECK_BOX_TEST_VALUES,
        'rip_omit_sm': CHECK_BOX_TEST_VALUES
    },
    'sntp': {
        'sntp_mode': [
            '0', '2', '3', 2, 'str', '1', -1, 4, SntpModes.SERVER, SntpModes.BOTH
        ],  # BOTH всегда последний
        'sntp_vlan': [
            -999999999999, -1, '0', 4095, '4096', 999999999999999, 'asdagfdsgdfgdgdfgdfgdfgfg', 'str', '200'
        ],
        'sntp_server': ['1.1.1.1.1', 2, '1.1.1.1'],
    },
    'mcast': {
        'mcast_mode': ['0', '3', 'str', '1', -1, 4, 2],  # 2 всегда последний
        'mcast_timeout': [-99999999, '-1', 0, 13, 30, 31, '31', 455, 999999999999, 'fsdfsdf', '123fdsfdf']
    },
    'acceleration': {
        'tcpa_enable': [0, 1],
        'from_svlan': [-99999999999, -1, '1', 64000, '0', 64001, '200', 99999999999],
        'to_svlan': [-99999999999, -1, '1', 64000, '0', 64001, '200', 99999999999],
        'sessions': [-99999999999, -1, '1', 64000, '0', 14000, 14001, '200', 99999999999],
    },
    'tcpa_with_api': {
        'tcpa_enable': CHECK_BOX_TEST_VALUES
    },
    'mtu': {
        'tcpa_mss': [-99999999999, -1, '1', 1500, '0', 1501, '200', 99999999999],
        'max_rx_win': [-99999999999, -1, '1', 9, 10, 65535, '0', 65536, '200', 99999999999, 'asdad', '123asfdsf'],
        'rx_win_upd': [-99999999999, -1, '50', 500, '49', 501, '200', 99999999999, 'asdad', '123asfdsf'],
    },
    'buffering': {
        'buf_coef': [-99999999999, -1, '4', 32, '3', 33, '20', 99999999999999, '123fhdgh', 'fsdgsgs'],
        'max_pkts': [
            -99999999999, -1, '4', 99, 100, '3', 33, '20', '65535', 65536, 99999999999999, '123fhdgh', 'fsdgsgs'
        ],
        'max_qlen': [
            -99999999999, -1, '4', 49, '50', '3', 33, '20', '500', 501, 99999999999999, '123fhdgh', 'fsdgsgs'
        ],
    },
    'retrying': {
        'retry_time': [-99999999999, -1, 0, '1', '255', '0', 256, '200', 600, 9999999999, 'sdfsdf', '23423fsgsrh'],
        'tcpa_retries': [-99999999999, -1, 0, '1', '255', '0', 256, '200', 600, 9999999999, 'sdfsdf', '23423sgsrh'],
        'tcpa_timeout': [-99999999999, -1, 0, '1', '255', '0', 256, '200', 600, 9999999999, 'sdfsdf', '23423sgsrh'],
        'ack_period': [-99999999999, -1, 0, '4', 500, '3', 501, '200', 9999999999999, '34sgdsg', 'fsghrh'],
    },
    'monitoring': {
        'sm_interval': [-99999999999, -1, '1', 60, '0', 61, '20', 99999999999999, 'sdfdsf', '123fsdgs'],
        'sm_losts': [-99999999999, -1, '1', '100' '0', 101, '20', 99999999999999, 'sdfdsf', '123fsdgs'],

        'poll_ip1': ['1.1.1.1.1', 2, '1.1.1.1'],
        'poll_vlan1': [-99999999999, -1, '0', 4095, 4096, 'str', '200', 999999999, '23fsefse'],

        'max_delay1': [-99999999999, -1, '0', '1', '32000', 32001, 'str', '200', 999999999, '23fsefse'],

        'poll_ip2': ['2.2.2.2.2', '2.2.2.2'],
        'poll_vlan2': [-99999999999, -1, '0', 4095, 4096, 'str', '200', 999999999, '23fsefse'],

        'max_delay2': [-99999999999, -1, '0', '1', '32000', 32001, 'str', '200', 999999999, '23fsefse'],

        'lan_rx_check': ['0', 1, '2', 3, '4', 'assas', LanCheckModes.LOWER],
        'rx_check_rate': [-99999999999, -1, '0', '1', '65000', 65001, 'str', '200', 999999999, '23fsefse'],

        'lan_tx_check': ['0', 1, '2', 3, '4', 'assas', LanCheckModes.HIGHER],
        'tx_check_rate': [-99999999999, -1, '0', '1', '65000', 65001, 'str', '200', 999999999, '23fsefse'],

        'bkp_ip': ['76.76.76.76.76', 2, '76.76.76.76'],

        'reboot_delay': [-99999999999, -1, 0, '3', '68', 250, '2', 251, 'str', '200fdfds', 99999999999999],
    },
    'monitoring_with_api': {
        'sm_enable': CHECK_BOX_TEST_VALUES,
        'poll_enable1': CHECK_BOX_TEST_VALUES,
        'chk_delay1': CHECK_BOX_TEST_VALUES,
        'poll_enable2': CHECK_BOX_TEST_VALUES,
        'chk_delay2': CHECK_BOX_TEST_VALUES,
        'bkp_enable': CHECK_BOX_TEST_VALUES,
        'auto_reboot': CHECK_BOX_TEST_VALUES,

    },
    'mod_queue': {
        'mod_queue1': [-999999999999, -1, 0, '10', 5000, '9', 5001, '200', 99999999999, '345fdsdg', '0xfff', 'dsf'],
        'mod_queue2': [-999999999999, -1, 0, '10', 5000, '9', 5001, '200', 99999999999, '345fdsdg', '0xfff', 'dsf'],
        'mod_queue3': [-999999999999, -1, 0, '10', 3000, '9', 3001, '200', 99999999999, '345fdsdg', '0xfff', 'dsf'],
        'mod_queue4': [-999999999999, -1, 0, '10', 3000, '9', 3001, '200', 99999999999, '345fdsdg', '0xfff', 'dsf'],
        'mod_queue5': [-999999999999, -1, 0, '10', 2000, '9', 2001, '200', 99999999999, '345fdsdg', '0xfff', 'dsf'],
        'mod_queue6': [-999999999999, -1, 0, '10', 1000, '9', 1001, '200', 99999999999, '345fdsdg', '0xfff', 'dsf'],
        'mod_queue7': [-999999999999, -1, 0, '10', 500, '9', 501, '200', 9999999999999, '345fdsdg', '0xfff', 'dsf'],
    },
}

valid_values = {
    'ip_screening': {
        'ip_screening': StrIntRange(range(0, 3)),
    },
    'snmp': {
        'snmp_mode': SnmpModes(),
        'access1_ip': ['1.1.1.1'],
        'access2_ip': ['1.1.1.1'],
        'snmp_auth': SnmpAuth(),
        'snmp_user': AnyValue(),
        'snmp_read': AnyValue(),
        'snmp_write': AnyValue(),
    },
    'dhcp': {
        'on': {
            'dhcp_vlan': StrIntRange(range(0, 4096)),
            'dhcp_ip_start': ['1.1.1.1'],
            'dhcp_ip_end': ['1.1.1.1'],
            'dhcp_mask': ['/24'],
            'dhcp_gateway': ['1.1.1.1'],
            'dhcp_dns': ['1.1.1.1'],
            'dhcp_timeout': StrIntRange(range(30, 86401)),
        },
        'relay': {
            'dhcp_vlan': StrIntRange(range(0, 4096)),
            'dhcp_helper': ['1.1.1.1'],
            'dhcp_local_ip': ['1.1.1.1'],
        },
    },
    'dns': {
        'dns_timeout': StrIntRange(range(1, 61)),
    },
    'dns_with_api': {
        'dns_caching': StrIntRange(range(0, 2)),
    },
    'arp': {
        'arp_timeout': StrIntRange(range(1, 31)),
        'proxy_arp': [0, 1],
    },
    'arp_with_api': {
        'proxy_arp': [0, 1],
    },
    'tftp': {
        'tftp_server': ['1.1.1.1'],
        'tftp_vlan': StrIntRange(range(0, 4096)),
    },
    'nat': {
        'nat_ext_ip': ['1.1.1.1'],
        'nat_int_ip': ['1.1.1.1'],
        'nat_int_mask': ['/24', '255.255.255.0'],
    },
    'nat_with_api': {
        'nat_enable': CHECK_BOX_VALID_VALUES
    },
    'rip': {
        'rip_next_hop': ['1.1.1.1'],
        'rip_omit_down': [0, 1],
        'rip_omit_sm': [0, 1],
        'rip_cost': StrIntRange(range(1, 17)),
    },
    'rip_with_api': {
        'rip_enable': CHECK_BOX_VALID_VALUES,
        'rip_omit_down': CHECK_BOX_VALID_VALUES,
        'rip_omit_sm': CHECK_BOX_VALID_VALUES
    },
    'sntp': {
        'sntp_mode': SntpModes(),
        'sntp_vlan': StrIntRange(range(0, 4096)),
        'sntp_server': ['1.1.1.1'],
    },
    'mcast': {
        'mcast_mode': StrIntRange(range(0, 3)),
        'mcast_timeout': StrIntRange(range(1, 31))
    },
    'acceleration': {
        'tcpa_enable': [0, 1],
        'from_svlan': StrIntRange(range(1, 64001)),
        'to_svlan': StrIntRange(range(1, 64001)),
        'sessions': StrIntRange(range(10, 14001)),
    },
    'tcpa_with_api': {
        'tcpa_enable': CHECK_BOX_VALID_VALUES
    },
    'mtu': {
        'tcpa_mss': StrIntRange(range(100, 1501)),
        'max_rx_win': StrIntRange(range(100, 65536)),
        'rx_win_upd': StrIntRange(range(50, 501)),
    },
    'buffering': {
        'buf_coef': StrIntRange(range(4, 33)),
        'max_pkts': StrIntRange(range(1, 5001)),
        'max_qlen': StrIntRange(range(5, 5001)),
    },
    'retrying': {
        'retry_time': StrIntRange(range(1, 256)),
        'tcpa_retries': StrIntRange(range(1, 256)),
        'tcpa_timeout': StrIntRange(range(1, 256)),
        'ack_period': StrIntRange(range(4, 501)),
    },
    'monitoring': {
        'sm_interval': StrIntRange(range(1, 61)),
        'sm_losts': StrIntRange(range(0, 101)),

        'poll_ip1': ['1.1.1.1'],
        'poll_vlan1': StrIntRange(range(0, 4096)),

        'max_delay1': StrIntRange(range(1, 32001)),

        'poll_ip2': ['2.2.2.2'],
        'poll_vlan2': StrIntRange(range(0, 4096)),

        'max_delay2': StrIntRange(range(1, 32001)),

        'lan_rx_check': LanCheckModes(),
        'rx_check_rate': StrIntRange(range(0, 65001)),

        'lan_tx_check': LanCheckModes(),
        'tx_check_rate': StrIntRange(range(0, 65001)),

        'bkp_ip': ['76.76.76.76'],

        'reboot_delay': StrIntRange(range(3, 251)),
    },
    'monitoring_with_api': {
        'sm_enable': CHECK_BOX_VALID_VALUES,
        'poll_enable1': CHECK_BOX_VALID_VALUES,
        'chk_delay1': CHECK_BOX_VALID_VALUES,
        'poll_enable2': CHECK_BOX_VALID_VALUES,
        'chk_delay2': CHECK_BOX_VALID_VALUES,
        'bkp_enable': CHECK_BOX_VALID_VALUES,
        'auto_reboot': CHECK_BOX_VALID_VALUES,

    },
    'mod_queue': {
        'mod_queue1': StrIntRange(range(10, 5001)),
        'mod_queue2': StrIntRange(range(10, 5001)),
        'mod_queue3': StrIntRange(range(10, 3001)),
        'mod_queue4': StrIntRange(range(10, 3001)),
        'mod_queue5': StrIntRange(range(10, 2001)),
        'mod_queue6': StrIntRange(range(10, 1001)),
        'mod_queue7': StrIntRange(range(10, 501)),
    },
}
