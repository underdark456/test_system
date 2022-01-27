from src.drivers.abstract_http_driver import CHROME
from src.options_providers.options_provider import CHROME_CONNECT, CONNECTION

system = {
    CHROME_CONNECT: {
        'type': CHROME,
        'no_gui': True,
        'maximize_window': True,
        # 'window_size': (1920, 1080),
    },
    CONNECTION: CHROME_CONNECT,
}

options = {
    'buttons': {
        'toggle': 'toggleButton',
        'filters': 'openFiltersButton',
        'state': 'State',
        'setup': 'Setup',
        'levels': 'Levels',
        'traffic': 'Traffic',
        'tx_detailed': 'TX detailed',
        'rx_detailed': 'RX detailed',
        'sw': 'SW',
        'history': 'History',
        'refresh': 'refreshOnceButton',
    },

    'graph': {
        'graph_x_axis': 'graphXAxis',
        'graph_first': 'firstSelect',
        'graph_second': 'secondSelect',
    },
    'graph_x_options': [
        'Serial #',
        'Name',
        'RX number',
        'RX controller',
    ],
    'first_select_options': [
        'C/N on hub',
        'C/N on station',
        'TX level',
        'TX margin',
        'State',
        'Faults',
        'Hub RX errors',
        'return_rate_all',
        'forward_rate_all',
        'forward_rate2',
    ],
    'second_select_options': [
        'None',
        'C/N on hub',
        'C/N on station',
        'TX level',
        'TX margin',
        'State',
        'Faults',
        'Hub RX errors',
        'return_rate_all',
        'forward_rate_all',
        'forward_rate2',
    ],

    'checkboxes': {
        'State': 'state_checkbox',
        'Faults': 'faults_checkbox',
        'Serial': 'serial_checkbox',
        'Redundant serial': 'red_serial_checkbox',
        'Enable': 'enable_checkbox',
        'Mode': 'mode_checkbox',
        'RX controller': 'rx_controller_checkbox',
        'Cur. RX ctr.': 'rx_ctr_act_checkbox',
        'Rx number': 'rx_number_checkbox',
        'SW load ID': 'sw_load_id_checkbox',
        'Ext gateway': 'ext_gateway_checkbox',
        'Profile set': 'profile_set_checkbox',
        'SW version': 'sw_version_checkbox',
        'RX errors': 'rx_errors_checkbox',
        'RX level at hub': 'cn_on_hub_checkbox',
        'RX level at station': 'station_cn_checkbox',
        'RX2 level at station': 'station_2_cn_checkbox',
        'Station TX level': 'station_tx_checkbox',
        'Station TX margin': 'tx_margin_checkbox',
        'Forward MODCOD': 'forward_modcod_checkbox',
        'Return MODCOD': 'return_modcod_checkbox',
        'Gateway MODCOD': 'gateway_modcod_checkbox',
        'Station TX traffic': 'return_rate_all_checkbox',
        'Station RX traffic': 'forward_rate_all_checkbox',
        'Station RX2 traffic': 'tx2_speed_all_checkbox',
        'TX 1': 'return_rate1_checkbox',
        'TX 2': 'return_rate2_checkbox',
        'TX 3': 'return_rate3_checkbox',
        'TX 4': 'return_rate4_checkbox',
        'TX 5': 'return_rate5_checkbox',
        'TX 6': 'return_rate6_checkbox',
        'TX 7': 'return_rate7_checkbox',
        'RX 1': 'forward_rate1_checkbox',
        'RX 2': 'forward_rate2_checkbox',
        'RX 3': 'forward_rate3_checkbox',
        'RX 4': 'forward_rate4_checkbox',
        'RX 5': 'forward_rate5_checkbox',
        'RX 6': 'forward_rate6_checkbox',
        'RX 7': 'forward_rate7_checkbox',
        'BW request': 'bw_rq_checkbox',
        'Latitude deg.': 'cur_lat_deg_checkbox',
        'Latitude min.': 'cur_lat_min_checkbox',
        'Longitude deg.': 'cur_lon_deg_checkbox',
        'Longitude min.': 'cur_lon_min_checkbox',
        'Hub up shaper': 'hub_up_shaper_checkbox',
        'Station up shaper': 'stn_up_shaper_checkbox',
        'Last fault': 'last_fault_checkbox',
        'Last no fault': 'last_no_fault_checkbox',
        'Fault times': 'fault_times_checkbox',
        'Last up': 'last_up_checkbox',
        'Last down': 'last_down_checkbox',
        'Down times': 'down_times_checkbox',
        'Stats cleared': 'clear_time_checkbox',
    },
    'filters_apply': 'applyButton',
    'filters_close': 'closeButton'
}
