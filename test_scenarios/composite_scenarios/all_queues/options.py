from src.enum_types_constants import ControllerModes, DemodulatorInputModes, TdmaInputModes, RollofModes, TdmaModcod, \
    StationModes, IpScreeningModes, ModcodModes, TtsModes

options = {
    'network': {
        'name': 'net-0',
        'dev_password': '',
    },
    'teleport': {
        'name': 'tp-0',
        'sat_name': 'dummy_sat',
        'tx_lo': 0,
        'rx1_lo': 0,
        'rx2_lo': 0,
    },
    'controller': {
        'name': 'HL_MAS',
        'device_ip': '127.0.0.1',
        'mode': ControllerModes.HUBLESS_MASTER,
        'teleport': 'teleport:0',  # default config must be loaded
        # 'stn_number': 2,
        # 'frame_length': 100,
        # 'slot_length': 10,
        'tdma_input': TdmaInputModes.RX1,
        'tdma_sr': 1000,
        'tdma_roll': RollofModes.R20,
        'mf1_rx': 1000000,
        'mf1_tx': 1000000,
        'tdma_mc': TdmaModcod._QPSK_1_2,
        'tx_on': 1,
        'tx_level': 20,
        'rx1_input': DemodulatorInputModes.OFF,
        'up_timeout': 60,
    },
    'vno': {
        'name': 'vno-0'
    },
    'station': {
        'name': 'HL_STN',
        'enable': 1,
        'serial': '40336453',
        'mode': StationModes.HUBLESS,
        'rx_controller': 'controller:0',
        'ip_screening': IpScreeningModes.AUTO,
    },
    'station_ip': {
        'device_ip': '127.0.0.2',
    },
    'test_ip': '172.16.111.3',
    'controller_star': {
        'name': 'MF_HUB',
        'device_ip': '127.0.0.1',
        'mode': ControllerModes.MF_HUB,
        'teleport': 'teleport:0',  # default config must be loaded
        # TDM section
        'tx_frq': 960000,
        'tx_sr': 3000,
        'tx_modcod': ModcodModes.SF_QPSK_3_4,
        'rx1_input': DemodulatorInputModes.RX1,
        'rx1_frq': 960000,
        'rx1_sr': 3000,
        'hub_tts_mode': TtsModes.VALUE,
        'tts_value': 0,
        'rx2_input': DemodulatorInputModes.OFF,
        # TDMA section
        'stn_number': 2,
        # 'frame_length': 100,
        # 'slot_length': 10,
        'tdma_input': TdmaInputModes.RX1,
        'tdma_sr': 1000,
        'tdma_roll': RollofModes.R20,
        'mf1_rx': 1000000,
        'mf1_tx': 1000000,
        'tdma_mc': TdmaModcod._QPSK_1_2,
        'tx_on': 1,
        'tx_level': 20,
        'up_timeout': 60,
    },
    'station_star': {
        'name': 'STAR_STN',
        'enable': 1,
        'serial': 1,
        'mode': StationModes.STAR,
        'rx_controller': 'controller:0',
    },
}
