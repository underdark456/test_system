from src.enum_types_constants import ControllerModes, DemodulatorInputModes, TdmaModcod, StationModes, ModelTypes, \
    DemodulatorInputModesStr, TdmaInputModes, ModcodModes

options = {
    'network': {
        'name': 'net-0',
        'dev_password': 'indeed',
    },
    'teleport': {
        'name': 'tp-0',
        'sat_name': 'sat_name',
        'tx_lo': 0,
        'rx1_lo': 0,
        'rx2_lo': 0,
    },
    'controller_hbl': {
        'name': 'ctrl-0',
        'mode': ControllerModes.HUBLESS_MASTER,
        'teleport': 'teleport:0',
        'rx1_input': DemodulatorInputModesStr.OFF,
        'tx_on': 'OFF',
        'tx_level': 20,
        'stn_number': 2039,
        'frame_length': 100,
        'slot_length': 10,
        'tdma_input': TdmaInputModes.RX1,
        'tdma_sr': 1000,
        'mf1_en': 'ON',
        'mf1_tx': 1000000,
        'mf1_rx': 1100000,
        'tdma_mc': TdmaModcod._8PSK_1_2,
    },
    'controller_MF': {
        'name': f'test_ctrl',
        'mode': ControllerModes.MF_HUB,
        'teleport': f'teleport:0',
        'net_ID': '24',
        'uhp_model': ModelTypes.UHP200,
        'tx_frq': '960000',
        'tx_sr': '1500',
        'tx_modcod': ModcodModes.SF_QPSK_3_4,
        'tx_level': '42',
        'rx1_frq': '960000',
        'rx1_sr': '1500',
    },
    'station': {
        'name': 'stn-0',
        'enable': 'OFF',
        'mode': StationModes.HUBLESS,
        'serial': 10000,
        'rx_controller': 'controller:0'
    },
    'models': {
        'uhp100': ModelTypes.UHP100,
        'uhp100x': ModelTypes.UHP100X,
        'uhp200': ModelTypes.UHP200,
        'uhp200x': ModelTypes.UHP200X,
        'uhp232': ModelTypes.UHP232,
    }

}
