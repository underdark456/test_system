from src.enum_types_constants import Checkbox, LatitudeModes, LongitudeModes, StationModes, AlertModes, \
    SnmpModesStr, SnmpAuthStr, DhcpModesStr, RipModesStr, \
    LanCheckModesStr, McastModesStr, SntpModesStr, IpScreeningModesStr

system = {

}

options = {
    'star_station': {
        'general_settings': {  # NMS related
            'name': 'test_stn',
            'enable': Checkbox.ON,
            'mode': StationModes.STAR,
            'serial': 3233232,
            'rx_controller': f'controller:0',
            'alert_mode': AlertModes.OFF,
            'traffic_scale': 20000,
            'level_scale': 30,
        },
        'contact_information': {  # NMS related
            'customer': 'John Doe',
            'phone1': '+178348292',
            'phone2': '+172899228',
            'address': 'Milwaukee lane 8, 95-1, Massachusetts, USA',
            'email': 'jdoe@comtechtel.com',
            'comment': 'Do not mess with the client',
        },
        'extended_settings': {  # checked red_serial
            'red_serial': 11212314,
            'roaming': Checkbox.OFF,
            'no_balancing': Checkbox.OFF,
            'profile_set': f'profile_set:0',
            'scheduler': 'scheduler:0',
            'sw_load_id': 24,
        },
        'location': {  # NMS related
            'lat_deg': 23,
            'lat_min': 59,
            'lat_south': LatitudeModes.SOUTH,
            'lon_deg': 54,
            'lon_min': 22,
            'lon_west': LongitudeModes.WEST,
            'time_zone': -4,
        },
        'bandwidth_allocation': {  # checked
            'hub_shaper': 'shaper:0',
            'stn_shaper': 'shaper:1',
            'rq_profile': 4,
        },
        'realtime': {  # checked
            'rt_codec': 32654,
            'rt_threshold': 156,
            'rt_timeout': 152,
        },
        'hub_cn_limits': {
            'hub_low_cn': 1.5,
            'hub_high_cn': 25.4,
        },
        'stn_cn_limits': {
            'station_low_cn': 1.3,
            'station_high_cn': 25.3,
        },
        'ip_screening': {  # checked
            'ip_screening': IpScreeningModesStr.OFF,
        },
        'dns': {  # checked
            'dns_caching': Checkbox.ON,
            'dns_timeout': '33',
        },
        'arp': {  # checked
            'arp_timeout': '3',
            'proxy_arp': Checkbox.ON,
        },
        'tftp': {  # checked
            'tftp_server': '174.15.223.1',
            'tftp_vlan': '2009',
        },
        'mcast': {  # checked
            'mcast_mode': McastModesStr.IGMP,
            'mcast_timeout': '7',
        },
        'sntp': {  # checked
            'sntp_mode': SntpModesStr.CLIENT,
            'sntp_vlan': '2011',
            'sntp_server': '173.14.22.12',
        },
        'snmp': {  # checked
            'snmp_mode': SnmpModesStr.V3,
            'access1_ip': '197.12.45.3',
            'access2_ip': '193.56.23.9',
            'snmp_auth': SnmpAuthStr.AUTH_PRIV,
            'snmp_user': 'testUser2',
            'snmp_read': 'easy1235',
            'snmp_write': 'easy5321',
        },
        'dhcp': {  # checked
            'dhcp_mode': DhcpModesStr.ON,
            'dhcp_vlan': '207',
            'dhcp_ip_start': '172.16.0.2',
            'dhcp_ip_end': '172.16.255.254',
            'dhcp_mask': '/16',
            'dhcp_gateway': '172.16.0.1',
            'dhcp_dns': '192.16.113.8',
            'dhcp_timeout': '65234',
        },
        'nat': {  # checked
            'nat_enable': Checkbox.ON,
            'nat_ext_ip': '198.15.67.2',
            'nat_int_ip': '192.168.200.0',
            'nat_int_mask': '/24',
        },
        'rip': {  # checked
            'rip_mode': RipModesStr.ON,
            'rip_update': '46',
            'rip_timeout': '93',
            'rip_cost': '5',
            'rip_auth': '1',
            'rip_pass': 'qwerty999',
        },
        'tcpa': {  # checked
            'tcpa_enable': '1',
            # 'tcpa_version': TcpaVersionStr.V3_5,  # Currently not in the form
            'from_svlan': '1094',
            'to_svlan': '2095',
            'sessions': '98',
            'tcpa_mss': '1440',
            'max_rx_win': '30200',
            'rx_win_upd': '205',
            'buf_coef': '9',
            'max_pkts': '250',
            'max_qlen': '930',
            'retry_time': '11',
            'tcpa_retries': '13',
            'tcpa_timeout': '8',
            'ack_period': '77',
        },
        'service_monitoring': {  # checked
            'sm_enable': '1',
            'sm_interval': '13',
            'sm_losts': '3',
            'poll_enable1': '1',
            'poll_ip1': '127.0.0.1',
            'poll_vlan1': '3097',
            'chk_delay1': '1',
            'max_delay1': '1280',
            'poll_enable2': '1',
            'poll_ip2': '10.0.4.19',
            'poll_vlan2': '4001',
            'chk_delay2': '1',
            'max_delay2': '1320',
            'lan_rx_check': LanCheckModesStr.HIGHER,
            'rx_check_rate': '32128',
            'lan_tx_check': LanCheckModesStr.LOWER,
            'tx_check_rate': '9862',
            'bkp_enable': '1',
            'bkp_ip': '10.0.2.1',
            'auto_reboot': Checkbox.OFF,
            # 'reboot_delay': '182',
        },
        'queue': {  # checked
            'mod_queue1': '1987',
            'mod_queue2': '1612',
            'mod_queue3': '1311',
            'mod_queue4': '852',
            'mod_queue5': '452',
            'mod_queue6': '91',
            'mod_queue7': '53',
            'mod_que_ctl': '499',
        },
    }
}
