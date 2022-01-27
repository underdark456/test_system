from src.enum_types_constants import ControllerModes, ModcodModes, TdmaInputModes, RollofModes, TdmaModcod, \
    CheckboxStr, ModelTypes

options = {
    'stations_tx_lvl': '40',
    'network': {
        'name': 'test_net',
        'dev_password': 'teste',
    },
    'teleport1': {
        'name': 'test_tp1',
        'tx_lo': '0',
        'rx1_lo': '0',
        'rx2_lo': '0',
    },
    'teleport2': {
        'name': 'test_tp2',
        'tx_lo': '0',
        'rx1_lo': '0',
        'rx2_lo': '0',
    },
    'mf_hub': {
        'name': f'test_ctrl',
        'mode': ControllerModes.MF_HUB,
        'teleport': f'teleport:0',
        'net_ID': '132',
        'uhp_model': ModelTypes.UHP200,
        'tx_frq': '960000',
        'tx_sr': '1500',
        'tx_modcod': ModcodModes.SF_QPSK_3_4,
        'tx_level': '40',
        'rx1_frq': '960000',
        'rx1_sr': '1500',
        'no_stn_check': '1',
        'tx_on': '1',
    },
    'inroute': {
        'name': f'test_ctrl_Inr',
        'inroute': '2',
        'mode': ControllerModes.INROUTE,
        'tx_controller': 'controller: 0',
        'teleport': f'teleport:0',
        'uhp_model': ModelTypes.UHP200,
        'stn_number': 5,
        'frame_length': 128,
        'slot_length': 10,
        'tdma_input': TdmaInputModes.RX1,
        'tdma_sr': 1000,
        'tdma_roll': RollofModes.R20,
        'mf1_rx': 1050000,
        'mf1_tx': 1050000,
        'tdma_mc': TdmaModcod._8PSK_2_3,
        'no_stn_check': '1',

    },
    'service': {
        'name': 'test_service'
    },
    'sr_controller': {
        'name': f'SR_test',
    },
    'sr_teleport1': {
        'name': f'SR_teleport1',
        'teleport': f'teleport:0',
    },
    'sr_teleport2': {
        'name': f'SR_teleport2',
        'teleport': f'teleport:1',
    },
    'device1': {
        'name': f'Device1',
        'mode': '2',
        'ip': '0.0.0.0',
        'mask': '/24',
        'gateway': '0.0.0.0',
        'dem2_connect': '1',
        'uhp_model': '2',
    },
    'device2': {
        'name': f'Device2',
        'mode': '2',
        'ip': '0.0.0.0',
        'mask': '/24',
        'gateway': '0.0.0.0',
        'dem2_connect': '1',
        'uhp_model': '2',
    },
    'device3': {
        'name': f'Device3',
        'mode': '2',
        'ip': '0.0.0.0',
        'mask': '/24',
        'gateway': '0.0.0.0',
        'dem2_connect': '1',
        'uhp_model': '2',
    },
    'device4': {
        'name': f'Device4',
        'mode': '2',
        'ip': '0.0.0.0',
        'mask': '/24',
        'gateway': '0.0.0.0',
        'dem2_connect': '1',
        'uhp_model': '2',
    },
    'lic_hub': {
        'name': 'lic_hub',
        'license_key': 'eyJvcHRpb25zIjoxNjMsInNpZ25hdHVyZSI6IjQ2QTFENzBFMDg0M0VCRDc5RjEyIn0=',
        'group1': '1',
    },
    'lic_inr': {
        'name': 'lic_inr',
        'license_key': 'eyJvcHRpb25zIjoyLCJzaWduYXR1cmUiOiJFQzgwQjVDNDg3RjlGN0I2OUU3MSJ9',
        'group2': '1',
    },
    'lic_hbl': {
        'name': 'lic_hbl',
        'license_key': 'eyJvcHRpb25zIjoyMDcyLCJzaWduYXR1cmUiOiJFREFEQTMxMkMxNDdGQkUzMTc4NyJ9',
        'group1': '1',
    },
    'service_ping': {
        'name': 'ping_service',
        'hub_vlan': 206,
        'stn_vlan': 306,
        'stn_normal': CheckboxStr.ON,
    }
}
