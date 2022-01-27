import random
from src.enum_types_constants import TdmaModcod, StationModes, Checkbox, ModcodModes, CheckboxStr, RollofModesStr, \
    AlertModes, StationModesStr, AlertModesStr, ModcodModesStr, RouteIds, RouteIdsStr
from utilities import utils


class RandomObjects:

    @staticmethod
    def get_group(group_id):
        params = {
            'name': f'group-{group_id}',
            'active': random.choice(['ON', 'OFF'])
        }
        return params

    @staticmethod
    def get_user(user_id):
        params = {
            'name': f'user-{user_id}',
            'enable': random.choice(['ON', 'OFF']),
            'email': f'user_0@group{user_id}.com',
            'first_name': f'user{user_id}',
            'last_name': f'{user_id}_user_{user_id}',
            'language': random.choice(['English', 'Russian']),
            'password': random.randint(10000, 100000)
        }
        return params

    @staticmethod
    def get_server(server_id):
        params = {
            'name': f'server-{server_id}',
            'ip': ".".join(map(str, (random.randint(1, 255) for _ in range(4)))),
            'enable': random.choice(['ON', 'OFF']),
            'replication': random.choice(['ON', 'OFF']),
            'location': ''.join([chr(random.randint(97, 122)) for _ in range(random.randint(5, 10))])
        }
        return params

    @staticmethod
    def get_alert(alert_id):
        sound = random.choice(['ON', 'OFF'])
        if sound == 'ON':
            file_name = 'alert.mp3'
            repeat_sound = random.choice(['ON', 'OFF'])
        else:
            file_name = ''
            repeat_sound = 'OFF'
        params = {
            'name': f'alert-{alert_id}',
            'priority': random.choice(['Low', 'Medium', 'High']),
            'popup': True,
            'sound': sound,
            'file_name': file_name,
            'repeat_sound': repeat_sound,
        }
        # script = random.choice(['ON', 'OFF'])
        script = 'OFF'
        if script == 'ON':
            script_file = 'log_to_text_file.sh'
            params['run_script'] = script
            params['script_file'] = script_file
        else:
            params['run_script'] = script
        return params

    @staticmethod
    def get_network(net_id, alert_id=None):
        params = {
            'name': f'net-{net_id}',
            'traffic_scale': random.randint(0, 50000),
            'level_scale': random.randint(0, 35),
            'dev_password': ''.join([chr(random.randint(97, 122)) for _ in range(random.randint(5, 10))]),
            'beam1_file': 'example.gxt',
            'beam2_file': 'example.gxt',
            'beam3_file': 'example.gxt',
            'beam4_file': 'example.gxt',
        }
        if alert_id is None:
            params['alert_mode'] = random.choice(['Inherit', 'Off'])
        else:
            params['alert_mode'] = 'Specify'
            params['set_alert'] = f'alert:{alert_id}'
        return params

    @staticmethod
    def get_teleport(tp_id):
        params = {
            'name': f'tp-{tp_id}',
            'sat_name': f'sat-{tp_id}',
            'sat_lon_deg': str(random.randint(-179, 179)),
            'sat_lon_min': random.randint(0, 59),
            'lat_deg': random.randint(0, 89),
            'lat_min': random.randint(0, 59),
            'lat_south': random.choice(['North', 'South']),
            'lon_deg': random.randint(0, 179),
            'lon_min': random.randint(0, 59),
            'lon_west': random.choice(['East', 'West']),
            'time_zone': str(random.randint(-12, 12)),
            'tx_lo': random.randint(0, 33000000),
            'tx_offset': str(random.randint(-10000, 10000)),
            'tx_spi': random.choice(['ON', 'OFF']),
            'rx1_lo': random.randint(0, 33000000),
            'rx1_offset': str(random.randint(-10000, 10000)),
            'rx1_spi': random.choice(['ON', 'OFF']),
            'rx2_lo': random.randint(0, 33000000),
            'rx2_offset': str(random.randint(-10000, 10000)),
            'rx2_spi': random.choice(['ON', 'OFF']),
            'dvb_search': random.randint(0, 10000),
            'tdma_search': random.choice(['bw6', 'bw12', 'bw24', 'bw40']),
        }
        return params

    @staticmethod
    def get_vno(vno_id, alert_id=None, hub_shaper_id=None, stn_shaper_id=None):
        if hub_shaper_id is None:
            hub_shaper = ''
        else:
            hub_shaper = hub_shaper_id
        if stn_shaper_id is None:
            stn_shaper = ''
        else:
            stn_shaper = stn_shaper_id

        params = {
            'name': f'vno-{vno_id}',
            'traffic_scale': random.randint(0, 50000),
            'level_scale': random.randint(0, 35),
            'hub_shaper': f'shaper:{hub_shaper}',
            'stn_shaper': f'shaper:{stn_shaper}',
        }
        if alert_id is None:
            params['alert_mode'] = random.choice(['Inherit', 'Off'])
        else:
            params['alert_mode'] = 'Specify'
            params['set_alert'] = f'alert:{alert_id}'
        return params

    @staticmethod
    def get_qos(qos_id, policy_id=None, shaper_id=None):
        if policy_id is None:
            priority_types = ['Low', 'P2', 'P3', 'Medium', 'P5', 'P6', 'High']
            priority = random.choice(priority_types)
            policy = ''
        else:
            priority = 'Policy'
            policy = policy_id
        if shaper_id is None:
            shaper = ''
        else:
            shaper = shaper_id
        params = {
            'name': f'qos-{qos_id}',
            'priority': priority,
            'policy': f'policy:{policy}',
            'shaper': f'shaper:{shaper}',
        }
        return params

    @staticmethod
    def get_service(service_id):
        params = {
            'name': f'ser-{service_id}',
            'hub_vlan': random.randint(0, 4095),
            'stn_vlan': random.randint(0, 4095),
            'ctr_normal': random.choice(['ON', 'OFF']),
            'ctr_gateway': random.choice(['ON', 'OFF']),
            'ctr_mesh': random.choice(['ON', 'OFF']),
            'stn_normal': random.choice(['ON', 'OFF']),
            'stn_gateway': random.choice(['ON', 'OFF']),
            'stn_mesh': random.choice(['ON', 'OFF']),
            'group_id': random.randint(0, 999),
            'mesh_routing': random.choice(['None', 'To_mesh_routes', 'To_gw_routes']),
            'nonlocal': random.choice(['ON', 'OFF']),
            'rip_announced': random.choice(['ON', 'OFF']),
        }
        return params

    @staticmethod
    def get_shaper(shaper_id):
        max_enable = random.choice(['ON', 'OFF'])
        if max_enable == 'ON':
            max_cir = random.randint(1, 250000)
            max_slope = random.randint(1, 16)
        else:
            max_cir = 64
            max_slope = 8

        min_enable = random.choice(['ON', 'OFF'])
        if min_enable == 'ON':
            min_cir = random.randint(1, 250000)
            down_slope = random.randint(1, 16)
            up_slope = random.randint(1, 16)
        else:
            min_cir = 32
            down_slope = 8
            up_slope = 8

        wfq_enable = random.choice(['ON', 'OFF'])
        # The sum must equal to 100
        if wfq_enable == 'ON':
            wfq6 = random.randint(5, 15)
            wfq5 = random.randint(5, 15)
            wfq4 = random.randint(5, 15)
            wfq3 = random.randint(5, 15)
            wfq2 = random.randint(5, 15)
            wfq1 = 100 - wfq6 - wfq5 - wfq4 - wfq3 - wfq2
        else:
            wfq1 = 50
            wfq2 = 10
            wfq3 = 10
            wfq4 = 10
            wfq5 = 10
            wfq6 = 10

        night_enable = random.choice(['ON', 'OFF'])
        if night_enable == 'ON':
            night_cir = random.randint(1, 250000)
            night_start = random.randint(0, 23)
            night_end = random.randint(0, 23)
        else:
            night_cir = 128
            night_start = 21
            night_end = 9

        params = {
            'name': f'shp-{shaper_id}',
            'template': random.choice(['ON', 'OFF']),
            'cir': random.randint(1, 250000),
            'up_queue': random.choice(['Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'QtoQ']),

            'max_enable': max_enable,
            'max_cir': max_cir,
            'max_slope': max_slope,

            'min_enable': min_enable,
            'min_cir': min_cir,
            'down_slope': down_slope,
            'up_slope': up_slope,

            'wfq_enable': wfq_enable,
            'wfq1': wfq1,
            'wfq2': wfq2,
            'wfq3': wfq3,
            'wfq4': wfq4,
            'wfq5': wfq5,
            'wfq6': wfq6,

            'night_enable': night_enable,
            'night_cir': night_cir,
            'night_start': night_start,
            'night_end': night_end,
        }
        return params

    @staticmethod
    # TODO: add the rest checks and actions
    def get_rule(sequence):
        type_ = random.choice(['Check', 'Action'])
        if type_ == 'Check':
            params = {
                'sequence': sequence,
                'type': type_,
                'check_type': 'VLAN',
                'not': random.choice(['ON', 'OFF']),
                'vlan_min': random.randint(0, 2000),
                'vlan_max': random.randint(2001, 4095),
                'goto_actions': random.choice(['ON', 'OFF']),
            }
        else:
            params = {
                'sequence': sequence,
                'type': type_,
                'action_type': random.choice(
                    [
                        'Drop',
                        'No_TCPA',
                        'Compress_RTP',
                        'No_screening',
                        'Drop_if_station_down',
                        'Compress_GTP',
                    ]
                ),
                'terminate': random.choice(['ON', 'OFF'])
            }
        return params

    @staticmethod
    def get_sr_controller(ctrl_id, alert_id=None):
        check_ctr = random.choice(['ON', 'OFF'])
        if check_ctr == 'ON':
            max_tx_down = random.randint(0, 200)
            max_rx_down = random.randint(0, 200)
            max_tx_fault = random.randint(0, 200)
            max_rx_fault = random.randint(0, 200)
            ctr_timeout = random.randint(10, 30000)
        else:
            max_tx_down = 0
            max_rx_down = 0
            max_tx_fault = 0
            max_rx_fault = 0
            ctr_timeout = 60
        check_stn = random.choice(['ON', 'OFF'])
        if check_stn == 'ON':
            min_stn_up = random.randint(0, 100)
            min_ctr_up = random.randint(0, 100)
            stn_timeout = random.randint(10, 30000)
        else:
            min_stn_up = 0
            min_ctr_up = 0
            stn_timeout = 60
        check_cn = random.choice(['ON', 'OFF'])
        if check_cn == 'ON':
            hub_cn_min = random.randint(0, 40)
            stn_cn_min = random.randint(0, 40)
            own_cn_min = random.randint(0, 40)
            cn_timeout = random.randint(10, 30000)
        else:
            hub_cn_min = 5
            stn_cn_min = 5
            own_cn_min = 5
            cn_timeout = 60
        check_sw_fails = random.choice(['ON', 'OFF'])
        if check_sw_fails == 'ON':
            max_sw_fails = random.randint(0, 1000)
        else:
            max_sw_fails = 0
        check_idle = random.choice(['ON', 'OFF'])
        if check_idle == 'ON':
            min_idle = random.randint(0, 200)
            idle_timeout = random.randint(10, 30000)
        else:
            min_idle = 0
            idle_timeout = 60
        params = {
            'name': f'sr_ctrl-{ctrl_id}',
            'enable': random.choice(['ON', 'OFF']),
            'tp_up_timeout': random.randint(10, 30000),
            'tp_down_timeout': random.randint(10, 30000),
            'check_ctr': check_ctr,
            'max_tx_down': max_tx_down,
            'max_rx_down': max_rx_down,
            'max_tx_fault': max_tx_fault,
            'max_rx_fault': max_rx_fault,
            'ctr_timeout': ctr_timeout,
            'check_stn': check_stn,
            'min_stn_up': min_stn_up,
            'min_ctr_up': min_ctr_up,
            'stn_timeout': stn_timeout,
            'check_cn': check_cn,
            'hub_cn_min': hub_cn_min,
            'stn_cn_min': stn_cn_min,
            'own_cn_min': own_cn_min,
            'cn_timeout': cn_timeout,
            'check_sw_fails': check_sw_fails,
            'max_sw_fails': max_sw_fails,
            'check_idle': check_idle,
            'min_idle': min_idle,
            'idle_timeout': idle_timeout,
        }
        if alert_id is None:
            params['alert_mode'] = random.choice(['Inherit', 'Off'])
        else:
            params['alert_mode'] = 'Specify'
            params['set_alert'] = f'alert:{alert_id}'
        return params

    @staticmethod
    def get_sr_teleport(sr_tp_id, tp_id, alert_id=None):
        params = {
            'name': f'sr_tp-{sr_tp_id}',
            'mode': random.choice(['In_service', 'Disabled']),
            'teleport': f'teleport:{tp_id}',
            'tx_10m': random.choice(['ON', 'OFF']),
            'tx_dc_power': random.choice(['ON', 'OFF']),
            'rx_10m': random.choice(['ON', 'OFF']),
            'rx_dc_power': random.choice(['ON', 'OFF']),
        }
        if alert_id is None:
            params['alert_mode'] = random.choice(['Inherit', 'Off'])
        else:
            params['alert_mode'] = 'Specify'
            params['set_alert'] = f'alert:{alert_id}'
        return params

    @staticmethod
    def get_sr_license(sr_lic_id):
        params = {
            'name': f'sr_lic-{sr_lic_id}',
            'license_key': ''.join([chr(random.randint(97, 122)) for _ in range(random.randint(5, 10))]),
            'enable': random.choice(['ON', 'OFF']),
            'group1': random.choice(['ON', 'OFF']),
            'group2': random.choice(['ON', 'OFF']),
            'group3': random.choice(['ON', 'OFF']),
            'group4': random.choice(['ON', 'OFF']),
            'group5': random.choice(['ON', 'OFF']),
            'group6': random.choice(['ON', 'OFF']),
            'group7': random.choice(['ON', 'OFF']),
            'group8': random.choice(['ON', 'OFF']),
        }
        return params

    @staticmethod
    def get_device(device_id):
        dem1_connect = random.choice(['Teleport_RX', 'Outroute_sync', 'Disconnected'])
        if dem1_connect == 'Teleport_RX':
            dem1_power = random.choice(['isolated', 'passed'])
            dem1_ref = random.choice(['isolated', 'passed'])
        else:
            dem1_power = 'isolated'
            dem1_ref = 'isolated'
        dem2_connect = random.choice(['Teleport_RX', 'Outroute_sync', 'Disconnected'])
        if dem2_connect == 'Teleport_RX':
            dem2_power = random.choice(['isolated', 'passed'])
            dem2_ref = random.choice(['isolated', 'passed'])
        else:
            dem2_power = 'isolated'
            dem2_ref = 'isolated'
        params = {
            'name': f'dev-{device_id}',
            'mode': random.choice(['standby', 'no_access', 'used']),
            'ip': ".".join(map(str, (random.randint(1, 255) for _ in range(4)))),
            'mask': f'/{random.randint(4, 32)}',
            'vlan': random.randint(0, 4095),
            'gateway': ".".join(map(str, (random.randint(1, 255) for _ in range(4)))),
            'location': ''.join([chr(random.randint(97, 122)) for _ in range(random.randint(5, 10))]),
            'mod_connect': random.choice(['Teleport_TX', 'WB_modulator', 'Disconnected']),
            'mod_power': random.choice(['isolated', 'passed']),
            'mod_ref': random.choice(['isolated', 'passed']),
            'tx_level_adj': str(random.randint(-10, 10)),
            'dem1_connect': dem1_connect,
            'dem1_power': dem1_power,
            'dem1_ref': dem1_ref,
            'dem2_connect': dem2_connect,
            'dem2_power': dem2_power,
            'dem2_ref': dem2_ref,
        }
        return params

    @staticmethod
    def get_bal_controller(ctrl_id):
        free_down = random.choice(['ON', 'OFF'])
        if free_down == 'ON':
            free_fault = random.choice(['ON', 'OFF'])
            down_time = random.randint(10, 30000)
        else:
            free_fault = 'OFF'
            down_time = 120
        params = {
            'name': f'bal_ctrl-{ctrl_id}',
            'enable': random.choice(['ON', 'OFF']),
            'low_cn_time': random.randint(5, 30000),
            'bal_interval': random.randint(10, 30000),
            'free_down': free_down,
            'free_fault': free_fault,
            'down_time': down_time,
            'cn_lock_time': random.randint(10, 30000),
            'bal_lock_time': random.randint(10, 30000),
            'max_idle_bw': random.randint(1, 1000),
            'switch_down1': random.choice(['ON', 'OFF']),
            'switch_idle1': random.choice(['ON', 'OFF']),
            'load_lower1': random.randint(0, 50),
            'load_higher1': random.randint(51, 100),
            'switch_down2': random.choice(['ON', 'OFF']),
            'switch_idle2': random.choice(['ON', 'OFF']),
            'load_lower2': random.randint(0, 50),
            'load_higher2': random.randint(51, 100),
        }
        return params

    @staticmethod
    def get_camera(cam_id):
        params = {
            'name': f'cam-{cam_id}',
            'url': ".".join(map(str, (random.randint(1, 255) for _ in range(4)))),
        }
        return params

    @staticmethod
    def get_profile_set(set_id):
        params = {
            'name': f'pro-{set_id}',
        }
        for i in range(2, 9):
            mode = random.choice([
                'No_change',
                'None',
                'Star_station',
                'Mesh_station',
                'DAMA_station',
                'Hubless_station',
                'CrossPol_test',
            ])
            params[f'mode{i}'] = mode
            if mode in ('Star_station', 'Mesh_station', 'DAMA_station'):
                params[f'rx_frq{i}'] = random.randint(950000, 33000000)
                params[f'sym_rate{i}'] = random.randint(100, 200000)
                params[f'demod_power{i}'] = random.choice(['DC18V', 'DC13V'])
                params[f'lvl_offset{i}'] = str(random.randint(-12, 12))
            elif mode == 'Hubless_station':
                params[f'rx_frq{i}'] = random.randint(950000, 33000000)
                params[f'tx_frq{i}'] = random.randint(950000, 33000000)
                params[f'sym_rate{i}'] = random.randint(100, 200000)
                params[f'demod_power{i}'] = random.choice(['DC18V', 'DC13V'])
                params[f'lvl_offset{i}'] = str(random.randint(-12, 12))
                params[f'frame_len{i}'] = random.choice([i for i in range(16, 252, 4)])
                params[f'slot_len{i}'] = random.randint(2, 15)
                params[f'stn_number{i}'] = random.randint(1, 2040)
                params[f'modcod{i}'] = random.choice([*TdmaModcod()])
            elif mode == 'CrossPol_test':
                params[f'rx_frq{i}'] = random.randint(950000, 33000000)
                params[f'tx_frq{i}'] = random.randint(950000, 33000000)
                params[f'sym_rate{i}'] = random.randint(100, 200000)
                params[f'demod_power{i}'] = random.choice(['DC18V', 'DC13V'])
                params[f'lvl_offset{i}'] = str(random.randint(-12, 12))
        return params

    @classmethod
    def get_controller(cls, ctrl_id, alert_id=None, tp_id=None, sr_controller=None):
        # TODO: add more random values
        rx_dc_power = random.choice(['ON', 'OFF'])
        if rx_dc_power == 'ON':
            rx_voltage = random.choice(['DC18V', 'DC13V'])
        else:
            rx_voltage = 'DC18V'
        mode = 'MF_hub'
        if sr_controller is None:
            bindings = ['Static', 'Redundant_static']
            binding = random.choice(bindings)
        else:
            binding = random.choice(['Static', 'Redundant_static', 'Smart'])
        if tp_id is None:
            teleport = ''
        else:
            teleport = f'teleport:{tp_id}'

        dns_cashing = random.choice(['ON', 'OFF'])
        if dns_cashing == 'ON':
            dns_timeout = random.randint(1, 60)
        else:
            dns_timeout = 5

        ctl_protect = random.choice(['ON', 'OFF'])
        if ctl_protect == 'ON':
            ctl_key = random.randint(1, 256)
        else:
            ctl_key = 1

        params = {
            'name': f'ctrl-{ctrl_id}',
            'mode': mode,
            'control': 'Full',
            'up_timeout': random.randint(10, 250),
            'allow_local': random.choice(['ON', 'OFF']),
            'traffic_scale': random.randint(0, 50000),
            'level_scale': random.randint(0, 35),
            'binding': binding,
            # Teleport specific
            'teleport': teleport,
            'tx_10m': random.choice(['ON', 'OFF']),
            'tx_dc_power': random.choice(['ON', 'OFF']),
            'rx_10m': random.choice(['ON', 'OFF']),
            'rx_dc_power': rx_dc_power,
            'rx_voltage': rx_voltage,
            # Protocols section
            'ip_screening': random.choice(['Auto', 'On', 'Off']),
            'dns_caching': dns_cashing,
            'dns_timeout': dns_timeout,
            'arp_timeout': random.randint(1, 30),
            'proxy_arp': random.choice(['ON', 'OFF']),
            'tftp_server': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'tftp_vlan': random.randint(0, 4095),
            'mcast_mode': 'IGMP',
            'mcast_timeout': random.randint(1, 30),
            'sntp_mode': 'Both',
            'sntp_vlan': random.randint(0, 4095),
            'sntp_server': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'ctl_protect': ctl_protect,
            'ctl_key': ctl_key,
            # SNMP section
            'snmp_mode': 'V3',
            'access1_ip': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'access2_ip': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'snmp_auth': 'Auth_priv',
            'snmp_user': 'testUser2',
            'snmp_read': 'easy1235',
            'snmp_write': 'easy5321',
            # DHCP section
            'dhcp_mode': 'On',
            'dhcp_vlan': random.randint(0, 4095),
            'dhcp_ip_start': '172.16.0.2',
            'dhcp_ip_end': '172.16.255.254',
            'dhcp_mask': '/16',
            'dhcp_gateway': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'dhcp_dns': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'dhcp_timeout': random.randint(30, 86400),
            # NAT section
            'nat_enable': 'ON',
            'nat_ext_ip': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'nat_int_ip': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'nat_int_mask': '/24',
            # RIP section
            'rip_mode': 'On',
            'rip_update': random.randint(10, 250),
            'rip_timeout': random.randint(30, 3600),
            'rip_cost': random.randint(1, 16),
            'rip_auth': 'ON',
            'rip_pass': 'qwerty999',
            # TCPA section
            'tcpa_enable': 'ON',
            'tcpa_version': 'V3_5',
            'from_svlan': 1094,
            'to_svlan': 2095,
            'sessions': 98,
            'tcpa_mss': 1440,
            'max_rx_win': 30200,
            'rx_win_upd': 205,
            'buf_coef': 9,
            'max_pkts': 250,
            'max_qlen': 930,
            'retry_time': 11,
            'tcpa_retries': 13,
            'tcpa_timeout': 8,
            'ack_period': 77,
            # Service monitoring section
            'sm_enable': 'ON',
            'sm_interval': 13,
            'sm_losts': 3,
            'poll_enable1': 'ON',
            'poll_ip1': '127.0.0.1',
            'poll_vlan1': 3097,
            'chk_delay1': 'ON',
            'max_delay1': 1280,
            'poll_enable2': 'ON',
            'poll_ip2': '10.0.4.19',
            'poll_vlan2': 4001,
            'chk_delay2': 'ON',
            'max_delay2': 1320,
            'lan_rx_check': 'Higher',
            'rx_check_rate': 32128,
            'lan_tx_check': 'Lower',
            'tx_check_rate': 9862,
            'bkp_enable': 'ON',
            'bkp_ip': '10.0.2.1',
            'auto_reboot': 'ON',
            'reboot_delay': 182,
            # Modulator queues section
            'mod_queue1': random.randint(10, 3000),
            'mod_queue2': random.randint(10, 3000),
            'mod_queue3': random.randint(10, 2000),
            'mod_queue4': random.randint(10, 2000),
            'mod_queue5': random.randint(10, 1000),
            'mod_queue6': random.randint(10, 1000),
            'mod_queue7': random.randint(10, 500),
            'mod_que_ctl': random.randint(10, 1000),
        }
        if binding == str('Static'):
            params['net_id'] = 155
            params['device_ip'] = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
            params['device_mask'] = f'/{random.randint(4, 32)}'
            params['device_vlan'] = random.randint(0, 4095)
            params['device_gateway'] = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
        elif binding == str('Redundant_static'):
            params['net_id'] = 155
            params['device_ip'] = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
            params['device_mask'] = f'/{random.randint(4, 32)}'
            params['device_vlan'] = random.randint(0, 4095)
            params['device_gateway'] = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
            params['device_b_ip'] = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
            params['red_up_time'] = random.randint(20, 250)
            params['tx_level_adj'] = str(float(random.randint(-10, 10)))
        else:
            params['sr_controller'] = f'sr_controller:{sr_controller}'
            params['sr_priority'] = random.randint(0, 100)
            if mode not in ('Hubless_master', 'Inroute', 'Dama_inroute', 'Gateway'):
                params['net_id'] = random.randint(1, 255)
            dyn_license = random.choice(['ON', 'OFF'])
            params['dyn_license'] = dyn_license
            if dyn_license == 'ON':
                params['license_group'] = random.randint(1, 8)
        if alert_id is None:
            params['alert_mode'] = random.choice(['Inherit', 'Off'])
        else:
            params['alert_mode'] = 'Specify'
            params['set_alert'] = f'alert:{alert_id}'
        return params

    @staticmethod
    def get_route_ip_address(service_id, private=True):
        override_vlan = random.choice(['ON', 'OFF'])
        if override_vlan == 'ON':
            stn_vlan = random.randint(0, 4095)
        else:
            stn_vlan = 0
        params = {
            'type': 'IP_address',
            'service': f'service:{service_id}',
            'ip': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'mask': f'/{random.randint(4, 32)}',
            'override_vlan': override_vlan,
            'stn_vlan': stn_vlan,
        }
        if private:
            params['id'] = RouteIdsStr.PRIVATE
        else:
            params['id'] = random.choice([*RouteIdsStr()])
        return params

    @staticmethod
    def get_port_map():
        params = {
            'external_port': random.randint(0, 65535),
            'internal_ip': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'internal_port': random.randint(0, 65535),
        }
        return params

    @staticmethod
    def get_rip_router(service_id):
        params = {
            'service': f'service:{service_id}',
            'rip_next_hop': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'lan_rx': random.choice(['ON', 'OFF']),
            'lan_default': random.choice(['ON', 'OFF']),
            'sat_rx': random.choice(['ON', 'OFF']),
            'sat_default': random.choice(['ON', 'OFF']),
            'announce': random.choice(['ON', 'OFF']),
        }
        return params

    @staticmethod
    def get_access(group_id):
        params = {
            'group': f'group:{group_id}',
            'edit': random.choice(['ON', 'OFF']),
            'use': random.choice(['ON', 'OFF'])
        }
        return params

    @staticmethod
    def get_sw_upload(net_id):
        params = {
            'name': f'sw_up-{net_id}',
            'tx_controller': f'controller:{random.randint(net_id * 4, net_id * 4 + 3)}',
            'data_rate': random.randint(50, 1000),
            'start_in': random.randint(0, 24),
            'repeat_times': random.randint(1, 10),
            'interval': random.randint(1, 24),
        }
        return params

    @staticmethod
    def get_station_mesh(stn_num, rx_controller_id):
        params = {
            'name': f'stn-{stn_num}',
            'serial': stn_num + 1,
            'enable': 'ON',
            'mode': StationModesStr.MESH,
            'rx_controller': f'controller:{rx_controller_id}',
            'alert_mode': AlertModesStr.OFF,
            'traffic_scale': random.randint(0, 50000),
            'level_scale': random.randint(0, 35),
            'customer': utils.get_random_string(punctuation=False),
            'phone1': utils.get_random_string(punctuation=False, lower_case=False, upper_case=False),
            'phone2': utils.get_random_string(punctuation=False, lower_case=False, upper_case=False),
            'address': utils.get_random_string(punctuation=False),
            'email': utils.get_random_string(punctuation=False),
            'comment': utils.get_random_string(punctuation=False),
            'red_serial': random.randint(1, 10000),
            'roaming': random.choice(['ON', 'OFF']),
            'no_balancing': random.choice(['ON', 'OFF']),
            'fixed_location': 'ON',
            'lat_deg': random.randint(0, 89),
            'lat_min': random.randint(0, 59),
            'lat_south': random.choice(['North', 'South']),
            'lon_deg': random.randint(0, 179),
            'lon_min': random.randint(0, 59),
            'lon_west': random.choice(['East', 'West']),
            'time_zone': random.randint(-12, 12),
            'rq_profile': random.randint(1, 4),
            'rt_codec': random.randint(1, 65000),
            'rt_threshold': random.randint(1, 200),
            'rt_timeout': random.randint(1, 200),
            'hub_low_cn': random.randint(0, 12),
            'hub_high_cn': random.randint(13, 25),
            'station_low_cn': random.randint(0, 12),
            'station_high_cn': random.randint(13, 25),
            # Protocols section
            'ip_screening': random.choice(['Auto', 'ON', 'OFF']),
            'dns_caching': random.choice(['ON', 'OFF']),
            'dns_timeout': random.randint(1, 60),
            'arp_timeout': random.randint(1, 30),
            'proxy_arp': random.choice(['ON', 'OFF']),
            'tftp_server': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'tftp_vlan': random.randint(0, 4095),
            'mcast_mode': 'IGMP',
            'mcast_timeout': random.randint(1, 30),
            'sntp_mode': 'Both',
            'sntp_vlan': random.randint(0, 4095),
            'sntp_server': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            # SNMP section
            'snmp_mode': 'V3',
            'access1_ip': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'access2_ip': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'snmp_auth': 'Auth_priv',
            'snmp_user': 'testUser2',
            'snmp_read': 'easy1235',
            'snmp_write': 'easy5321',
            # DHCP section
            'dhcp_mode': 'ON',
            'dhcp_vlan': random.randint(0, 4095),
            'dhcp_ip_start': '172.16.0.2',
            'dhcp_ip_end': '172.16.255.254',
            'dhcp_mask': '/16',
            'dhcp_gateway': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'dhcp_dns': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'dhcp_timeout': random.randint(30, 86400),
            # NAT section
            'nat_enable': 'ON',
            'nat_ext_ip': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'nat_int_ip': ".".join(map(str, (random.randint(0, 255) for _ in range(4)))),
            'nat_int_mask': '/24',
            # RIP section
            'rip_mode': 'ON',
            'rip_update': random.randint(10, 250),
            'rip_timeout': random.randint(30, 3600),
            'rip_cost': random.randint(1, 16),
            'rip_auth': 'ON',
            'rip_pass': 'qwerty999',
            # TCPA section
            'tcpa_enable': 'ON',
            'from_svlan': 1094,
            'to_svlan': 2095,
            'sessions': 98,
            'tcpa_mss': 1440,
            'max_rx_win': 30200,
            'rx_win_upd': 205,
            'buf_coef': 9,
            'max_pkts': 250,
            'max_qlen': 930,
            'retry_time': 11,
            'tcpa_retries': 13,
            'tcpa_timeout': 8,
            'ack_period': 77,
            # Service monitoring section
            'sm_enable': 'ON',
            'sm_interval': 13,
            'sm_losts': 3,
            'poll_enable1': 'ON',
            'poll_ip1': '127.0.0.1',
            'poll_vlan1': 3097,
            'chk_delay1': 'ON',
            'max_delay1': 1280,
            'poll_enable2': 'ON',
            'poll_ip2': '10.0.4.19',
            'poll_vlan2': 4001,
            'chk_delay2': 'ON',
            'max_delay2': 1320,
            'lan_rx_check': 'Higher',
            'rx_check_rate': 32128,
            'lan_tx_check': 'Lower',
            'tx_check_rate': 9862,
            'bkp_enable': 'ON',
            'bkp_ip': '10.0.2.1',
            'auto_reboot': 'ON',
            'reboot_delay': 182,
            # Modulator queues section
            'mod_queue1': random.randint(10, 3000),
            'mod_queue2': random.randint(10, 3000),
            'mod_queue3': random.randint(10, 2000),
            'mod_queue4': random.randint(10, 1000),
            'mod_queue5': random.randint(10, 1000),
            'mod_queue6': random.randint(10, 1000),
            'mod_queue7': random.randint(10, 500),
            'mod_que_ctl': random.randint(10, 500),
        }
        return params

    @staticmethod
    def get_scheduler(net_id):
        params = {
            'name': f'scheduler-{net_id}',
        }
        return params

    @staticmethod
    def get_sch_range(scheduler_id):
        params = {
            'name': f'sch_range-{scheduler_id}',
            'start_frq': random.randint(950000, 33000000),
            'end_frq': random.randint(950000, 33000000)
        }
        return params

    @staticmethod
    def get_sch_service(sch_ser_id):
        params = {
            'name': f'sch_service-{sch_ser_id}',
            'tx_sr': random.randint(300, 200000),
            'tx_pilots': random.choice([*CheckboxStr()]),
            'tx_rolloff': random.choice([*RollofModesStr()]),
            'acm_enable': random.choice([*CheckboxStr()]),
            'tx_modcod': random.choice([*ModcodModes()]),
            'tx_level': random.randint(1, 46),
        }
        return params

    @staticmethod
    def get_dashboard(dash_id):
        params = {
            'name': f'dash-{dash_id}',
        }
        return params


if __name__ == '__main__':
    print(RandomObjects.get_rip_router(3))
    print(RandomObjects.get_access(3))
