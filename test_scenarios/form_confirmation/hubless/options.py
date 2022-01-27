from src.custom_logger import OK, LOGGING
from src.enum_types_constants import *

system = {
    LOGGING: OK,
}

options = {
    'models': {
        'uhp100': ModelTypes.UHP100,
        'uhp100x': ModelTypes.UHP100X,
        'uhp200': ModelTypes.UHP200,
        'uhp200x': ModelTypes.UHP200X,
        'uhp232': ModelTypes.UHP232,
    },
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
        'teleport': {
            'teleport': 'teleport:0',
            'tx_10m': '1',
            'tx_dc_power': Checkbox.OFF,  # make sure that the lab splitters config do not pass DC
            'rx_10m': '1',
            'rx_dc_power': Checkbox.OFF,  # make sure that the lab splitters config do not pass DC
            #  'rx_voltage': RxVoltage.DC13V,  # broken rx_dc_power checkbox in ver.4.0.0.7
        },
        # Modulator transmission control section
        'modulator': {
            'tx_on': Checkbox.ON,
            'tx_level': '20.1',
        },

        # TX automatic transmit level control section
        'tlc': {
            'tlc_enable': '1',
            'tlc_max_lvl': '29.2',
            'tlc_net_own': '6',
            'tlc_avg_min': '7',
            'tlc_cn_stn': '15.3',
            # Return channel TLC control section
            'tlc_cn_hub': '9.7',
        },
        # Demodulator 1 setup section
        'demodulator1': {
            'rx1_input': DemodulatorInputModesStr.RX2,
            'rx1_frq': '10950300',  # check RX2 LO to enter a valid value
            'rx1_sr': '6254',
            'check_rx': '1',
        },
        # Demodulator 2 setup section
        'demodulator2': {
            'rx2_input': DemodulatorInputModesStr.OFF,
            'rx2_frq': '11950200',  # check RX1 LO to enter a valid value
            'rx2_sr': '3908',
        },
        'own_cn': {
            # Acceptable own C/N levels range section
            'own_cn_low': '5.6',
            'own_cn_high': '37.1',
        },
        'tdma_prot': {
            # TDMA protocol setup section
            'stn_number': '5',
            'frame_length': '100',
            'slot_length': '10',
            #  'no_stn_check': '1',  #  removed from ver.4.0.0.7
            # TODO: roaming
        },

        # TDMA RF setup
        'tdma_rf': {
            'tdma_input': TdmaInputModesStr.RX1,
            'tdma_sr': '1952',  # make sure that the total symbol rate satisfies the upper bound
            'tdma_roll': RollofModesStr.R5,
            'mf1_en': '1',
            'mf1_tx': '14452000',
            'mf1_rx': '11750000',
            'mf2_en': '1',
            'mf2_tx': '14452100',
            'mf2_rx': '11750100',
            'mf3_en': '1',
            'mf3_tx': '14452200',
            'mf3_rx': '11750200',
            'mf4_en': '1',
            'mf4_tx': '14452300',
            'mf4_rx': '11750300',
            # TDMA channel coding section
            'tdma_mc': TdmaModcod._8PSK_3_4,
            'enh_tables': '1',
        },

        # TDMA bandwidth allocation section
        'tdma_bw': {
            'act_on_traf': '1',
            'mir_limit': '1',
            'opt_latency': '1',
            'rt_to_cir': '1',
            'bw_rq_scale': '101',
            'td_rq_act1': '128',
            'td_rq_act2': '129',
            'td_rq_act3': '130',
            'td_rq_act4': '131',
            'td_rq_idl1': '64',
            'td_rq_idl2': '65',
            'td_rq_idl3': '66',
            'td_rq_idl4': '67',
            'td_rq_dwn1': '32',
            'td_rq_dwn2': '33',
            'td_rq_dwn3': '34',
            'td_rq_dwn4': '35',
            'td_rq_tout1': '10',
            'td_rq_tout2': '11',
            'td_rq_tout3': '12',
            'td_rq_tout4': '13',
        },

        # Master settings section
        'master': {
            'hub_shaper': 'shaper:0',
            'rq_profile': '2',
            'rt_codec': '120',
            'rt_threshold': '7',
            'rt_timeout': '9',
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
    'modcod': {
        'BPSK 1/2': 0,
        'BPSK 2/3': 1,
        'BPSK 3/4': 2,
        'BPSK 5/6': 3,
        'QPSK 1/2': 4,
        'QPSK 2/3': 5,
        'QPSK 3/4': 6,
        'QPSK 5/6': 7,
        '8PSK 1/2': 8,
        '8PSK 2/3': 9,
        '8PSK 3/4': 10,
        '8PSK 5/6': 11,
        '16APSK 1/2': 12,
        '16APSK 2/3': 13,
        '16APSK 3/4': 14,
        '16APSK 5/6': 15
    }
}
