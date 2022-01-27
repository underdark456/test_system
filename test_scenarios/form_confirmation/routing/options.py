from src.enum_types_constants import CheckTypesStr

system = {

}

options = {
    'static_service': {
        'name': 'static',
        'hub_vlan': '500',
        'stn_vlan': '1500',
        'stn_normal': True,
    },
    'static_policy': {
        'name': 'static'
    },
    'static_polrule': {
        'sequence': 1,
        'check_type': CheckTypesStr.ICMP_TYPE,
        'not': 'ON',
        'icmp_type': '8',
        'goto_actions': 'OFF',
    },
    'static_shaper': {
        'name': 'static',
        'cir': '66554'
    },

    'rth_service': {
        'name': 'rth',
        'hub_vlan': '400',
        'stn_vlan': '1400',
    },
    'rth_policy': {
        'name': 'rth'
    },
    'rth_polrule': {
        'sequence': 1,
        'check_type': CheckTypesStr.DST_TCP_PORT,
        'not': 'OFF',
        'port_min': '9876',
        'port_max': '11223',
        'goto_actions': 'ON'
    },
    'rth_shaper': {
        'name': 'rth',
        'cir': '55443'
    },

    'network_rx_service': {
        'name': 'network_rx',
        'hub_vlan': '100',
        'stn_vlan': '1100',
    },
    'network_rx_policy': {
        'name': 'network_rx'
    },
    'network_rx_polrule': {
        'sequence': 1,
        'check_type': CheckTypesStr.SRC_TCP_PORT,
        'not': 'ON',
        'port_min': '12345',
        'port_max': '54321',
        'goto_actions': 'OFF'
    },
    'network_rx_shaper': {
        'name': 'network_rx',
        'cir': '123456'
    },

    'network_tx_service': {
        'name': 'network_tx',
        'hub_vlan': '200',
        'stn_vlan': '1200',
    },
    'network_tx_policy': {
        'name': 'network_tx'
    },
    'network_tx_polrule': {
        'sequence': 1,
        'check_type': CheckTypesStr.DST_TCP_PORT,
        'not': 'ON',
        'port_min': '23456',
        'port_max': '65432',
        'goto_actions': 'OFF'
    },
    'network_tx_shaper': {
        'name': 'network_tx',
        'cir': '234567'
    },

    'bridge_service': {
        'name': 'bridge',
        'hub_vlan': '300',
        'stn_vlan': '1300',
        'stn_normal': True,
    },
    'bridge_policy': {
        'name': 'bridge'
    },
    'bridge_polrule': {
        'sequence': 1,
        'check_type': CheckTypesStr.SRC_UDP_PORT,
        'not': 'ON',
        'port_min': '2983',
        'port_max': '3762',
        'goto_actions': 'ON'
    },
    'bridge_shaper': {
        'name': 'bridge',
        'cir': '112233'
    },


}
