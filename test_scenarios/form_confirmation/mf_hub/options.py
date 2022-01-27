from src.custom_logger import LOGGING, INFO
from src.enum_types_constants import Checkbox, LanCheckModesStr, TcpaVersionStr, McastModesStr, SntpModesStr, \
    RipModesStr, DhcpModesStr, SnmpAuthStr, SnmpModesStr, IpScreeningModesStr, TdmaModcod, RollofModesStr, \
    TdmaInputModesStr, DemodulatorInputModesStr, ModcodModes, ControllerModes, ControlModes, TtsModesStr
from src.options_providers.options_provider import CHROME_CONNECT, CONNECTION

system = {
    LOGGING: INFO,
    CHROME_CONNECT: {
        'no_gui': False
    },
    CONNECTION: CHROME_CONNECT
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
            'mode': ControllerModes.MF_HUB,
            'control': ControlModes.FULL,
            'up_timeout': '57',
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
            'tx_on': Checkbox.OFF,
            'tx_level': '20.1',
        },
        'tdm_tx': {
            'tx_frq': 1178921,
            'tx_sr': 3419,
            'tx_pilots': Checkbox.ON,
            'tx_rolloff': RollofModesStr.R5,
            'tx_modcod': ModcodModes.SF_QPSK_2_3,
        },

        # TX automatic transmit level control section
        'tlc': {
            'tlc_enable': '1',
            'tlc_max_lvl': '29.2',
            'tlc_net_own': '6',
            'tlc_avg_min': '7',
            'tlc_cn_stn': '15.3',
            'tlc_cn_hub': '8.3',
        },
        # Demodulator 1 setup section
        'demodulator1': {
            'rx1_input': DemodulatorInputModesStr.RX1,
            'rx1_frq': '10950300',  # check RX2 LO to enter a valid value
            'rx1_sr': '6254',
            # 'check_rx': Checkbox.ON,
        },
        # Demodulator 2 setup section
        # 'demodulator2': {
        #     'rx2_input': DemodulatorInputModesStr.OFF,
        #     'rx2_frq': '11950200',  # check RX1 LO to enter a valid value
        #     'rx2_sr': '3908',
        # },
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
            'no_stn_check': Checkbox.ON,
        },
        'roaming': {
            'roaming_enable': Checkbox.ON,
            'roaming_slots': '8',
        },
        'timing': {
            'hub_tts_mode': TtsModesStr.VALUE,
            'tts_value': '0',
        },
        # TDMA RF setup
        'tdma_rf': {
            'tdma_input': TdmaInputModesStr.RX1,
            'tdma_sr': '1952',  # make sure that the total symbol rate satisfies the upper bound
            'tdma_roll': RollofModesStr.R5,
            'mf1_en': '1',
            'mf1_tx': '14400000',
            'mf1_rx': '11300000',
            'mf2_en': '1',
            'mf2_tx': '14401000',
            'mf2_rx': '11351000',
            'mf3_en': '1',
            'mf3_tx': '14402000',
            'mf3_rx': '11302000',
            'mf4_en': '1',
            'mf4_tx': '14403000',
            'mf4_rx': '11303000',
            'mf5_en': '1',
            'mf5_tx': '14404000',
            'mf5_rx': '11304000',
            'mf6_en': '1',
            'mf6_tx': '14405000',
            'mf6_rx': '11305000',
            'mf7_en': '1',
            'mf7_tx': '14406000',
            'mf7_rx': '11306000',
            'mf8_en': '1',
            'mf8_tx': '14407000',
            'mf8_rx': '11307000',
            'mf9_en': '1',
            'mf9_tx': '14408000',
            'mf9_rx': '11308000',
            'mf10_en': '1',
            'mf10_tx': '14409000',
            'mf10_rx': '11359000',
            'mf11_en': '1',
            'mf11_tx': '14410000',
            'mf11_rx': '11310000',
            'mf12_en': '1',
            'mf12_tx': '14411000',
            'mf12_rx': '11311000',
            'mf13_en': '1',
            'mf13_tx': '14412000',
            'mf13_rx': '11312000',
            'mf14_en': '1',
            'mf14_tx': '14413000',
            'mf14_rx': '11313000',
            'mf15_en': '1',
            'mf15_tx': '14414000',
            'mf15_rx': '11314000',
            'mf16_en': '1',
            'mf16_tx': '14415000',
            'mf16_rx': '11315000',

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
