import random

from src.enum_types_constants import ControllerModes, ControlModes, Checkbox, RollofModesStr, ModcodModes, \
    IpScreeningModesStr, SnmpModesStr, SnmpAuthStr, DhcpModesStr, RipModesStr, SntpModesStr, McastModesStr, \
    TcpaVersionStr, LanCheckModesStr, RollofModes, DamaTx

system = {

}

options = {
    'teleport': {
        # settings section
        'name': 'MSK',
        # satellite_data section
        'sat_name': 'Eutelsat16A',
        'sat_lon_deg': '15',
        'sat_lon_min': '48',
        'tx_lo': '12800000',
        'rx1_lo': '10750000',
        'rx2_lo': '9750000',
    },
    'controller': {
        # Teleport and RF connection control section
        'settings': {
            'name': 'CTRL-1',
            'mode': ControllerModes.DAMA_HUB,
            'control': ControlModes.FULL,
            'up_timeout': random.randint(10, 250),
            'allow_local': Checkbox.OFF,
            'check_rx': Checkbox.ON,
        },
        'teleport': {
            'teleport': 'teleport:0',
            'tx_10m': '1',
            'tx_dc_power': Checkbox.OFF,
            'rx_10m': '1',
            'rx_dc_power': Checkbox.OFF,
        },
        # Modulator transmission control section
        'modulator': {
            'tx_on': Checkbox.ON,
            'tx_level': '29.7',
        },
        'tdm_tx': {
            'tx_frq': 1178921,
            'tx_sr': 3419,
            'tx_pilots': Checkbox.ON,
            'tx_rolloff': RollofModesStr.R5,
            'tx_modcod': ModcodModes.SF_QPSK_1_2,
        },
        # ACM settings
        'tdm_acm': {
            'acm_enable': 1,
            'acm_mc2': ModcodModes.SF_QPSK_2_3,
            'acm_mc3': ModcodModes.SF_QPSK_3_4,
            'acm_mc4': ModcodModes.SF_QPSK_4_5,
            'acm_mc5': ModcodModes.SF_QPSK_5_6,
            'acm_mc6': ModcodModes.SF_QPSK_8_9,
            'acm_thr': 2.6,
        },
        # TX automatic transmit level control section
        'tlc': {
            'tlc_enable': '1',
            'tlc_max_lvl': '29.2',
            'tlc_net_own': '6',
            'tlc_avg_min': '7',
            'tlc_cn_stn': '15.3',
        },
        # DAMA Return A
        'dama_return_a': {
            'a_dama_tx_frq': random.randint(950000, 2150000),
            'a_dama_rx_frq': random.randint(950000, 2150000),
            'a_dama_sr': random.randint(100, 65000),
            'a_dama_modcod': ModcodModes.SF_QPSK_3_4,
            'a_dama_pilots': Checkbox.ON,
            'a_dama_rolloff': RollofModes.R5,
            'a_dama_tx': DamaTx.ON,
            'a_dama_level': random.randint(1, 45) + 0.1,
            'a_dama_cn_hub': random.randint(0, 24) + 0.1,
        },
        'dama_return_b': {
            # DAMA Return B
            'b_dama_tx_frq': random.randint(950000, 2150000),
            'b_dama_rx_frq': random.randint(950000, 2150000),
            'b_dama_sr': random.randint(100, 65000),
            'b_dama_modcod': ModcodModes.SF_QPSK_5_6,
            'b_dama_pilots': Checkbox.OFF,
            'b_dama_rolloff': RollofModes.R20,
            'b_dama_tx': DamaTx.PURE,
            'b_dama_level': random.randint(1, 45) + 0.1,
            'b_dama_cn_hub': random.randint(0, 24) + 0.1,
        },
        # IP protocols setup section
        'ip_screening': {
            'ip_screening': IpScreeningModesStr.OFF,
        },

        # SNMP section
        'snmp': {
            'snmp_mode': SnmpModesStr.V3,
            'access1_ip': '197.12.45.3',
            'access2_ip': '193.56.23.9',
            'snmp_auth': SnmpAuthStr.AUTH_PRIV,
            'snmp_user': 'testUser2',
            'snmp_read': 'easy1235',
            'snmp_write': 'easy5321',
        },

        # DHCP section
        'dhcp': {
            'dhcp_mode': DhcpModesStr.ON,
            'dhcp_vlan': '207',
            'dhcp_ip_start': '172.16.0.2',
            'dhcp_ip_end': '172.16.255.254',
            'dhcp_mask': '/16',
            'dhcp_gateway': '172.16.0.1',
            'dhcp_dns': '192.16.113.8',
            'dhcp_timeout': '65234',
        },

        # DNS caching section
        'dns': {
            'dns_caching': '1',
            'dns_timeout': '33',
        },

        # ARP section
        'arp': {
            'arp_timeout': '3',
            'proxy_arp': '1',
        },

        # TFTP section
        'tftp': {
            'tftp_server': '174.15.223.1',
            'tftp_vlan': '2009',
        },

        # NAT section
        'nat': {
            'nat_enable': '1',
            'nat_ext_ip': '198.15.67.2',
            'nat_int_ip': '192.168.200.0',
            'nat_int_mask': '/24',
        },

        'rip': {
            'rip_mode': RipModesStr.ON,
            'rip_update': '46',
            'rip_timeout': '93',
            'rip_cost': '5',
            'rip_auth': '1',
            'rip_pass': 'qwerty999',
        },

        # SNTP section
        'sntp': {
            'sntp_mode': SntpModesStr.CLIENT,
            'sntp_vlan': '2011',
            'sntp_server': '173.14.22.12',
        },

        # Multicast section
        'mcast': {
            'mcast_mode': McastModesStr.IGMP,
            'mcast_timeout': '7',
        },

        # Traffic protection section
        'ctl': {
            'ctl_protect': '1',
            'ctl_key': '37',
        },

        'tcpa': {
            'tcpa_enable': '1',
            'tcpa_version': TcpaVersionStr.V3_5,
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
        'service_monitoring': {
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

        # Modulator queue lengths section
        'queue': {
            'mod_queue1': '1987',
            'mod_queue2': '1612',
            'mod_queue3': '1311',
            'mod_queue4': '852',
            'mod_queue5': '452',
            'mod_queue6': '91',
            'mod_queue7': '53',
            'mod_que_ctl': '476',
        },
    },
}
