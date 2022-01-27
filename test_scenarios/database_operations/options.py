from src.enum_types_constants import StationModes, RouteTypes, ExtGatewayModes

options = {
    'alert': {
        'name': 'ALERT'
    },
    'controller_minimal_options': {
        'name': "MF_HUB",
        'mode': 'MF_hub',
        'teleport': 'teleport:0',
    },
    'user': {
        'name': 'user-',
        'enabled': '',
        'email': 'email@domain.com',
        'first_name': 'USER_NAME',
        'last_name': 'USER_LASTNAME',
        'password': '',

    },
    'controller': {
        'network_id': 0,
        'controller_id': 0,
        'values': {
            'name': "MF_HUB",
            'mode': 'MF_hub',
            'teleport': 'teleport:0',
            'up_timeout': '100',
            'device_name': '191 modem',
            'device_ip': '10.0.2.191',
            'device_vlan': '12',
            'device_gateway': '10.0.2.1',
            'tx_frq': '1200000',
            'tx_sr': '1500',
            'tx_modcod': '7',
            'tx_on': '1',
            'tx_level': '25',
            'rx1_frq': '1200000',
            'rx1_sr': '1500',
            'net_id': '191',
            'rf_id': '191',
            'mf1_tx': '1100000',
            'mf1_rx': '1100000',
            'tdma_sr': '1000',
            'tdma_mc': '7',
        },

    },

    'station': {
        'vno_id': 0,
        'values': {
            'name': "station-",
            'mode': StationModes.STAR,
            'serial': '000',
            #'customer': 'азазазаза',
            #'phone1': '22222222',
            #'phone2': '33333333',
            #'email': 'wewewew',
            'comment': 'comment 1',
            'ext_gateway': ExtGatewayModes.OFF,
            'no_balancing': True,
            'sw_load_id': '10',
            'lat_deg': '35',
            'lat_min': '45',
            'lat_south': 'South',
            'lon_deg': '120',
            'lon_min': '60',
            'lon_west': 'East',
            'time_zone': '5',
            'rq_profile ': '2',
            'rt_codec': '100',
            'rt_threshold': '2',
            'rt_timeout': '10',
            # 'hub_cn_low': '1.0',
            # 'hub_cn_high': 24,
            # 'station_cn_low': '3.0',
            # 'station_cn_high': 24,
            'ip_screening': 'On',
        },

    },
    'station-02': {
        'vno_id': 0,
        'values': {
            'name': 'STATION-193',
            'mode': 'Star',
            'serial': '50135763',
            'rx_controller': 'controller:0',
            'enable': '1',

        },

    },

    'teleport': {
        'network_id': 0,
        'values': {
            'name': 'TELEPORT',
            'tx_lo': '0',
            'rx1_lo': '0',
            'rx2_lo': '0',
        },

    },
    'network': {
        'nms_id': 0,
        'name': 'NETWORK',
    },
    'vno': {
        'network_id': 0,
        'values': {
            'name': 'VNO',
        },

    },

    'shaper': {
        'network_id': 0,
        'values': {
            'name': 'test_shaper',
        },
    },
    'wait_options': {
        'timeout': 30,
        'step': 5,

    },
    'route': {
        'ip': '0.0.0.0',
        'type': RouteTypes.IP_ADDRESS,
        'service': 'service:0',

    }
}
