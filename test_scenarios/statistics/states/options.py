from src.enum_types_constants import ControllerModes, ControlModes, DemodulatorInputModes, TdmaInputModes, TdmaModcod

system = {

}

options = {
    'network': {
        'name': 'net-0',
        'dev_password': 'indeed',
    },
    'teleport1': {
        'name': 'tp-1',
        'sat_name': 'sat_name',
        'tx_lo': 0,
        'rx1_lo': 0,
        'rx2_lo': 0,
    },
    'teleport2': {
        'name': 'tp-2',
        'sat_name': 'sat_name2',
    },
    'teleport3': {
        'name': 'tp-3',
        'sat_name': 'sat_name3',
        'tx_lo': 0,
        'rx1_lo': 0,
        'rx2_lo': 0,
    },
    'teleport4': {
        'name': 'tp-4',
        'sat_name': 'sat_name4',
        'tx_lo': 0,
        'rx1_lo': 0,
        'rx2_lo': 0,
    },
    'controller1': {
        'name': 'ctrl-1',
        'mode': ControllerModes.MF_HUB,
        'control': ControlModes.NO_ACCESS,
        'teleport': 'teleport:0',
        'rx1_input': DemodulatorInputModes.OFF,
        'tx_on': True,
        'tx_frq': 1100000,
        'rx1_frq': 1500000,
        'no_stn_check': True,
        'up_timeout': 250,
    },
    'controller2': {
        'name': 'ctrl-2',
        'mode': ControllerModes.MF_HUB,
        'control': ControlModes.NO_ACCESS,
        'teleport': 'teleport:1',
        'rx1_input': DemodulatorInputModes.OFF,
        'tx_on': True,
        'tx_frq': 1200000,
        'rx1_frq': 1600000,
        'no_stn_check': True,
        'up_timeout': 250,
    },
    'controller3': {
        'name': 'ctrl-3',
        'mode': ControllerModes.MF_HUB,
        'control': ControlModes.NO_ACCESS,
        'teleport': 'teleport:2',
        'rx1_input': DemodulatorInputModes.OFF,
        'tx_on': True,
        'tx_frq': 1300000,
        'rx1_frq': 1700000,
        'no_stn_check': True,
        'up_timeout': 250,
    },
    'controller4': {
        'name': 'ctrl-4',
        'mode': ControllerModes.MF_HUB,
        'control': ControlModes.NO_ACCESS,
        'teleport': 'teleport:3',
        'rx1_input': DemodulatorInputModes.OFF,
        'tx_on': True,
        'tx_level': 24,
        'stn_number': 10,
        'frame_length': 100,
        'slot_length': 10,
        'tdma_input': TdmaInputModes.RX1,
        'tdma_sr': 1000,
        'mf1_en': 'ON',
        'mf1_tx': 1400000,
        'mf1_rx': 1400000,
        'tdma_mc': TdmaModcod._8PSK_1_2,
    },
}
