from numpy.ma import arange

from src.enum_types_constants import *
from src.values_presenters import *

options = {
    'test_values': {
        'settings': {  # TODO исправить
            'name': TEXT_FIELD_TEST_VALUES,
            'control': [*ControlModes(), '', 0, 1, 'test'],  # dropdown list (3 params)
            'up_timeout': get_mixed_values_list(10, 250),  # digit field (10 - 250)
            'allow_local': 1,  # checkbox
        },
        'alert_settings': {
            'alert_mode': [*AlertModes(), 'fake', '', '-123']
        },
        'device_binding': {
            'device_binding': [*BindingModes(), 'fake', '', '-123']
        },
        'device_a': {
            'device_name': TEXT_FIELD_TEST_VALUES,
            'device_ip': IP_TEST_VALUES,
            'device_mask': IP_MASK_TEST_VALUES,
            'device_vlan': get_mixed_values_list(0, 4095),
            'device_gateway': IP_TEST_VALUES
        },
        'teleport_and_rf': {
            'teleport': [],  # TODO
            'tx_10m': CHECK_BOX_TEST_VALUES,
            'tx_dc_power': CHECK_BOX_TEST_VALUES,
            'rx_10m': CHECK_BOX_TEST_VALUES,
            'rx_dc_power': CHECK_BOX_TEST_VALUES,
        },
        'modulator': {
            'tx_frq': get_mixed_values_list(950000, 33000000),
            'tx_sr': get_mixed_values_list(300, 200000),
            'tx_pilots': CHECK_BOX_TEST_VALUES,
            'tx_rolloff': [*RollofModes(), 'sdfsdf', -123143],
            'acm_enable': CHECK_BOX_TEST_VALUES,
            'tx_modcod': ['1', 124, 125, 'SF QPSK 1/2', 'fake', -2131313321323, 123534435345],
            'wbm_mode': [*WbmModes(), 'fake', -141234314, 234525345345345],
            'tx_on': CHECK_BOX_TEST_VALUES,
            'tx_level': get_mixed_values_list(1.0, 46.0)
        },
        'tlc': {
            'tlc_enable': CHECK_BOX_TEST_VALUES,
            'tlc_max_lvl': get_mixed_values_list(1.0, 46.0),
            'tlc_net_own': get_mixed_values_list(0, 16),
            'tlc_avg_min': get_mixed_values_list(0, 16),
            'tlc_cn_stn': get_mixed_values_list(0.0, 30.0),
            'tlc_cn_hub': get_mixed_values_list(0.0, 30.0),
        },
        'demodulator': {
            'rx1_input': [*DemodulatorInputModes(), 'fake', 2325355, -2114234],
            'rx1_frq': get_mixed_values_list(950000, 33000000),
            'rx1_sr': get_mixed_values_list(100, 200000),
            'check_rx': CHECK_BOX_TEST_VALUES,
            'rx2_input': [*DemodulatorInputModes(), 'fake', 2325355, -2114234],
            'rx2_frq': get_mixed_values_list(950000, 33000000),
            'rx2_sr': get_mixed_values_list(100, 200000),
        },
        'net_rf_id': {
            'net_id': get_mixed_values_list(1, 255),
            'rf_id': get_mixed_values_list(1, 255),
        },
        'tdma': {
            'stn_number': get_mixed_values_list(1, 2040),
            'frame_length': get_mixed_values_list(16, 252),
            'slot_length': get_mixed_values_list(2, 15),
            'no_stn_check': CHECK_BOX_TEST_VALUES,
            'roaming_enable': CHECK_BOX_TEST_VALUES,
            'tdma_input': [*TdmaInputModes(), 'fake', -1234],
            'tdma_sr': get_mixed_values_list(100, 11000),
            'tdma_roll': [*RollofModes(), 'fake', -123523]
        },

    },
    'valid_values': {
        'settings': {
            'name': NotEmpty(),
            'control': ControlModes(),
            'up_timeout': StrIntRange(range(10, 250)),
            'allow_local': 1,
        },
        'alert_settings': {
            'alert_mode': AlertModes()
        },
        'device_binding': {
        },
        'device_a': {
            'device_name': AnyValue(),
            'device_ip': ValidIpAddr(),
            'device_mask': ValidIpMask(),
            'device_vlan': StrIntRange(range(0, 4095)),
            'device_gateway': ValidIpAddr()
        },
        'teleport_and_rf': {
            'teleport': [],
            'tx_10m': CHECK_BOX_VALID_VALUES,
            'tx_dc_power': CHECK_BOX_VALID_VALUES,
            'rx_10m': CHECK_BOX_VALID_VALUES,
            'rx_dc_power': CHECK_BOX_VALID_VALUES,
        },
        'modulator': {
            'tx_frq': StrIntRange(range(950000, 33000001)),
            'tx_sr': StrIntRange(range(300, 200001)),
            'tx_pilots': CHECK_BOX_VALID_VALUES,
            'tx_rolloff': RollofModes(),
            'acm_enable': CHECK_BOX_VALID_VALUES,
            'tx_modcod': StrIntRange(range(1, 125)),
            'wbm_mode': WbmModes(),
            'tx_on': CHECK_BOX_VALID_VALUES,
            'tx_level': StrFloatRange(arange(1.0, 46.0))
        },
        'tlc': {
            'tlc_enable': CHECK_BOX_VALID_VALUES,
            'tlc_max_lvl': StrFloatRange(arange(1.0, 46.0)),
            'tlc_net_own': StrIntRange(range(0, 17)),
            'tlc_avg_min': StrIntRange(range(0, 17)),
            'tlc_cn_stn': StrFloatRange(arange(0.0, 30.0)),
            'tlc_cn_hub': StrFloatRange(arange(0.0, 30.0)),
        },
        'demodulator': {
            'rx1_input': DemodulatorInputModes(),
            'rx1_frq': StrIntRange(range(950000, 33000001)),
            'rx1_sr': StrIntRange(range(100, 200001)),
            'check_rx': CHECK_BOX_VALID_VALUES,
            'rx2_input': DemodulatorInputModes(),
            'rx2_frq': StrIntRange(range(950000, 33000001)),
            'rx2_sr': StrIntRange(range(100, 200001)),
        },
        'net_rf_id': {
            'net_id': StrIntRange(range(1, 256)),
            'rf_id': StrIntRange(range(1, 256)),
        },
        'tdma': {
            'stn_number': StrIntRange(range(1, 2041)),
            'frame_length': StrIntRange(range(16, 253)),
            'slot_length': StrIntRange(range(2, 16)),
            'no_stn_check': CHECK_BOX_VALID_VALUES,
            'roaming_enable': CHECK_BOX_VALID_VALUES,
            'tdma_input': TdmaInputModes(),
            'tdma_sr': StrIntRange(range(100, 11001)),
            'tdma_roll': RollofModes(),
        },
    },
}
