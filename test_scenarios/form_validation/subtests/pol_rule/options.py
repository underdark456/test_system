from src.enum_types_constants import QueueTypes
from src.values_presenters import IP_TEST_VALUES, IP_MASK_TEST_VALUES, ValidIpMask, ValidIpAddr

system = {

}

options = {
    'test_values': {
        '802_1q_priority': {
            'not': ['ON', 'OFF'],
            'prio_802': [*range(0, 8), 9, 'test', 'nousecryingoverspiltmilk'],
            'goto_actions': ['ON', 'OFF'],
        },
        'vlan': {
            'not': ['ON', 'OFF'],
            'goto_actions': ['ON', 'OFF'],
        },
        'tos': {
            'not': ['ON', 'OFF'],
            'goto_actions': ['ON', 'OFF'],
        },
        'dscp': {
            'not': ['ON', 'OFF'],
            'goto_actions': ['ON', 'OFF'],
        },
        'protocol': {
            'not': ['ON', 'OFF'],
            'protocol': [0, 255, 256, 652, 2550, 'test', 'nousecryingoverspiltmilk'],
            'goto_actions': ['ON', 'OFF'],
        },
        'src_net': {
            'not': ['ON', 'OFF'],
            'net_ip': IP_TEST_VALUES,
            'net_mask': IP_MASK_TEST_VALUES,
            'goto_actions': ['ON', 'OFF'],
        },
        'dst_net': {
            'not': ['ON', 'OFF'],
            'net_ip': IP_TEST_VALUES,
            'net_mask': IP_MASK_TEST_VALUES,
            'goto_actions': ['ON', 'OFF'],
        },
        'src_tcp_port': {
            'not': ['ON', 'OFF'],
            'goto_actions': ['ON', 'OFF'],
        },
        'dst_tcp_port': {
            'not': ['ON', 'OFF'],
            'goto_actions': ['ON', 'OFF'],
        },
        'src_udp_port': {
            'not': ['ON', 'OFF'],
            'goto_actions': ['ON', 'OFF'],
        },
        'dst_udp_port': {
            'not': ['ON', 'OFF'],
            'goto_actions': ['ON', 'OFF'],
        },
        'icmp_type': {
            'not': ['ON', 'OFF'],
            'icmp_type': [0, 8, 255, 256, 652, 2550, 'test', 'nousecryingoverspiltmilk'],
            'goto_actions': ['ON', 'OFF'],
        },
        'set_queue': {
            'terminate': ['ON', 'OFF'],
            'queue': ['Low', 'P2', 'P3', 'Medium', 'P5', 'P6', 'High', 'P7', 'a2', 18, 'qwerty']
        },
        'set_ts_ch': {
            'terminate': ['ON', 'OFF'],
            'shaper': [18, 'shaper:0', 'shaper:18', True]
        },
        'no_tcpa': {
            'terminate': ['ON', 'OFF'],
        },
        'compress_rtp': {
            'terminate': ['ON', 'OFF'],
        },
        'no_screening': {
            'terminate': ['ON', 'OFF'],
        },
        'set_acm_channel': {
            'terminate': ['ON', 'OFF'],
            'acm_channel': [0, 1, 5, 9, 10, 'qwerty', 22]
        },
        'drop_if_station_down': {
            'terminate': ['ON', 'OFF'],
        },
        'encrypt': {
            'key': [0, 1, 255, 256, 300, 100, 200, 'qwerty'],
            'terminate': ['ON', 'OFF'],
        },
        'set_tos': {
            'set_tos': [0, 255, 256, 300, 100, 'qwerty'],
            'terminate': ['ON', 'OFF'],
        },
        'set_dscp': {
            'set_dscp': [0, 63, 64, 100, 'qwerty'],
            'terminate': ['ON', 'OFF'],
        },
        'goto_policy': {
            'policy': ['policy:0', 'policy:1', 'qwerty'],
            'terminate': ['ON', 'OFF'],
        },
        'call_policy': {
            'policy': ['policy:0', 'policy:1', 'qwerty'],
            'terminate': ['ON', 'OFF'],
        },
        'compress_gtp': {
            'terminate': ['ON', 'OFF'],
        },
    },
    'valid_values': {
        '802_1q_priority': {
            'not': ['ON', 'OFF'],
            'prio_802': [*range(0, 8)],
            'goto_actions': ['ON', 'OFF'],
        },
        'vlan': {
            'not': ['ON', 'OFF'],
            'goto_actions': ['ON', 'OFF'],
            'vlan_min': [*range(0, 4096)],
            'vlan_max': [*range(0, 4096)],
        },
        'tos': {
            'not': ['ON', 'OFF'],
            'goto_actions': ['ON', 'OFF'],
            'tos_min': [*range(0, 256)],
            'tos_max': [*range(0, 256)],
        },
        'dscp': {
            'not': ['ON', 'OFF'],
            'goto_actions': ['ON', 'OFF'],
            'dscp_min': [*range(0, 64)],
            'dscp_max': [*range(0, 64)],
        },
        'protocol': {
            'not': ['ON', 'OFF'],
            'protocol': [*range(0, 256)],
            'goto_actions': ['ON', 'OFF'],
        },
        'src_net': {
            'not': ['ON', 'OFF'],
            'net_ip': ValidIpAddr(),
            'net_mask': ValidIpMask(),
            'goto_actions': ['ON', 'OFF'],
        },
        'dst_net': {
            'not': ['ON', 'OFF'],
            'net_ip': ValidIpAddr(),
            'net_mask': ValidIpMask(),
            'goto_actions': ['ON', 'OFF'],
        },
        'src_tcp_port': {
            'not': ['ON', 'OFF'],
            'goto_actions': ['ON', 'OFF'],
            'port_min': [*range(0, 65536)],
            'port_max': [*range(0, 65536)],
        },
        'dst_tcp_port': {
            'not': ['ON', 'OFF'],
            'goto_actions': ['ON', 'OFF'],
            'port_min': [*range(0, 65536)],
            'port_max': [*range(0, 65536)],
        },
        'src_udp_port': {
            'not': ['ON', 'OFF'],
            'goto_actions': ['ON', 'OFF'],
            'port_min': [*range(0, 65536)],
            'port_max': [*range(0, 65536)],
        },
        'dst_udp_port': {
            'not': ['ON', 'OFF'],
            'goto_actions': ['ON', 'OFF'],
            'port_min': [*range(0, 65536)],
            'port_max': [*range(0, 65536)],
        },
        'icmp_type': {
            'not': ['ON', 'OFF'],
            'icmp_type': [*range(0, 256)],
            'goto_actions': ['ON', 'OFF'],
        },
        'set_queue': {
            'terminate': ['ON', 'OFF'],
            'queue': ['Low', 'P2', 'P3', 'Medium', 'P5', 'P6', 'High']
        },
        'set_ts_ch': {
            'terminate': ['ON', 'OFF'],
            'shaper': ['shaper:0']
        },
        'no_tcpa': {
            'terminate': ['ON', 'OFF'],
        },
        'compress_rtp': {
            'terminate': ['ON', 'OFF'],
        },
        'no_screening': {
            'terminate': ['ON', 'OFF'],
        },
        'set_acm_channel': {
            'terminate': ['ON', 'OFF'],
            'acm_channel': [*range(1, 9)]
        },
        'drop_if_station_down': {
            'terminate': ['ON', 'OFF'],
        },
        'encrypt': {
            'key': [*range(1, 257)],
            'terminate': ['ON', 'OFF'],
        },
        'set_tos': {
            'set_tos': [*range(256)],
            'terminate': ['ON', 'OFF'],
        },
        'set_dscp': {
            'set_dscp': [*range(64)],
            'terminate': ['ON', 'OFF'],
        },
        'goto_policy': {
            'policy': ['policy:1', ],
            'terminate': ['ON', 'OFF'],
        },
        'call_policy': {
            'policy': ['policy:1', ],
            'terminate': ['ON', 'OFF'],
        },
        'compress_gtp': {
            'terminate': ['ON', 'OFF'],
        },
    },
    'first_values': {
        'vlan': {
            'vlan_min': [0, 4095, 4096, 10000, 1, 20, 3000, 'dadadadada', 2006, 56, 4000, 1000, 6000],
        },
        'tos': {
            'tos_min': [0, 255, 256, 10000, 1, 20, 'dadadadada', 97, 255, 0],
        },
        'dscp': {
            'dscp_min': [0, 63, 64, 10000, 1, 20, 'dadadadada', 34, 63, 0],
        },
        'src_tcp_port': {
            'port_min': [0, 65535, 65536, 10000, 1, 65534, 'dadadadada', 267, 34, 63, 0],
        },
        'dst_tcp_port': {
            'port_min': [0, 65535, 65536, 10000, 1, 65534, 'dadadadada', 267, 34, 63, 0],
        },
        'src_udp_port': {
            'port_min': [0, 65535, 65536, 10000, 1, 65534, 'dadadadada', 267, 34, 63, 0],
        },
        'dst_udp_port': {
            'port_min': [0, 65535, 65536, 10000, 1, 65534, 'dadadadada', 267, 34, 63, 0],
        },
    },
    'second_values': {
        'vlan': {
            'vlan_max': [0, 4095, 4096, 10000, 1, 20, 3000, 'dadadadada', 2006, 55, 3000, 5000, 3006],
        },
        'tos': {
            'tos_max': [0, 255, 256, 10000, 1, 20, 'dadadadada', 96, 0, 255],
        },
        'dscp': {
            'dscp_max': [0, 63, 64, 10000, 1, 20, 'dadadadada', 33, 0, 63],
        },
        'src_tcp_port': {
            'port_max': [0, 65535, 65536, 10000, 1, 65534, 'dadadadada', 'qwerty', 33, 0, 63],
        },
        'dst_tcp_port': {
            'port_max': [0, 65535, 65536, 10000, 1, 65534, 'dadadadada', 'qwerty', 33, 0, 63],
        },
        'src_udp_port': {
            'port_max': [0, 65535, 65536, 10000, 1, 65534, 'dadadadada', 'qwerty', 33, 0, 63],
        },
        'dst_udp_port': {
            'port_max': [0, 65535, 65536, 10000, 1, 65534, 'dadadadada', 'qwerty', 33, 0, 63],
        },
    },
}
