from src.custom_logger import LOGGING, OK
from src.enum_types_constants import RouteTypes

system = {
    LOGGING: OK,
}

options = {

    'route_values': {
        'controller_id': 0,
        'station_id': 0,
        'IP_address': {
            'type': RouteTypes.IP_ADDRESS,
            'service': 'service:0',
            'id': 'Normal',
            'ip': '100.101.102.103',
            'mask': '/24',
            'override_vlan': False,
        },
        'Static_route': {
            'type': RouteTypes.STATIC_ROUTE,
            'service': 'service:0',
            'id': 'Normal',
            'ip': '2.2.2.2',
            'mask': '/24',
            'gateway': '100.101.102.1',
            'override_vlan': False,
        },
        'Route_to_hub': {
            'type': RouteTypes.ROUTE_TO_HUB,
            'service': 'service:0',
            'ip': '5.5.5.5',
            'mask': '/24',
            'override_vlan': False,
        },
        'Network_TX': {
            'type': RouteTypes.NETWORK_TX,
            'service': 'service:1',
            'ip': '6.6.6.6',
            'mask': '/24',
            'override_vlan': False,
        },
        'Network_RX': {
            'type': RouteTypes.NETWORK_RX,
            'service': 'service:1',
            'override_vlan': False,
        },
        'L2_bridge': {
            'type': RouteTypes.L2_BRIDGE,
            'service': 'service:0',
            'override_vlan': False,
        },
        'IPv6_address': {
            'type': RouteTypes.IPV6_ADDRESS,
            'service': 'service:0',
            'id': 'Normal',
            'V6_ip': '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
            'V6_mask': '/120',
            'override_vlan': False,
        },
        'IPv6_route': {
            'type': RouteTypes.IPV6_ROUTE,
            'service': 'service:0',
            'id': 'Normal',
            'V6_ip': '2001:0db8:85a3:0001::',
            'V6_mask': '/120',
            'override_vlan': False,
            'v6_gateway': '2001:0db8:85a3:0000:0000:8a3e:0370:3354',
        },
        'IPv6_to_hub': {
            'type': RouteTypes.IPV6_TO_HUB,
            'service': 'service:0',
            'V6_ip': '2001:0db8:85a3:0001::',
            'V6_mask': '/120',
            'override_vlan': True,
            'stn_vlan': 3006
        },
        'IPv6_net_tx': {
            'type': RouteTypes.IPV6_NET_TX,
            'service': 'service:0',
            'V6_ip': '2001:0db8:85a3:0001::',
            'V6_mask': '/120',
            'override_vlan': True,
            'stn_vlan': 3006
        },
        'IPv6_net_rx': {
            'type': RouteTypes.IPV6_NET_RX,
            'service': 'service:0',
            'override_vlan': True,
            'stn_vlan': 3006
        },
    }
}
