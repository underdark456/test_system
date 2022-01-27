from src.enum_types_constants import SnmpModes, SnmpAuth
from src.options_providers.options_provider import CONNECTION, CHROME_CONNECT

system = {
    CONNECTION: CHROME_CONNECT,  # for NMS 3.x login and password interaction
}

options = {
    'ip_address': 'localhost',  # please redefine in local options
    'ip_address2': 'localhost',  # please redefine in local options
    'nms_ip_address': 'localhost',  # please redefine in local options
    'nms_token': '12345',  # please redefine in local options
    'nms_username': 'admin',  # please redefine in local options if needed
    'nms_password': '12345',  # please redefine in local options if needed
    'controller_values': [
        'tdmrf_rxfreq_0',
        'tdmrf_txfreq_0',
        'tdmrf_rxfreq_1',
        'tdmrf_txfreq_1',
        'modulator_txlvl',
        'tdmaproto_slotsnum',
        'modulator_txon',
        'modem_id',
        'enabled'
    ],
    'satellite_values': [
        'id',
        'name',
        'longitude',
        'longitude_deg',
        'longitude_min',
        'longitude_dir',
    ],
    'snmp': {
        'snmp_mode': SnmpModes.V1_V2C,
        'snmp_user': 'none',
        'snmp_auth': SnmpAuth.NO_AUTH,
        'snmp_read': 'public',
        'snmp_write': 'private',
        'access1_ip': '255.255.255.255',
        'access2_ip': '255.255.255.255'
    },
    'expected_state_codes': {
        '0': 'off',
        '1': 'init',
        '2': 'noConfig',
        '3': 'useConfig',
        '4': 'redundant',
        '5': 'startRX',
        '6': 'cotmPointing',
        '7': 'startHubTX',
        '8': 'noRX',
        '9': 'identify',
        '10': 'getNetConfig',
        '11': 'calcDelays',
        '12': 'startTDMA',
        '13': 'startTX',
        '14': 'acquisition',
        '15': 'adjustment',
        '16': 'noStations',
        '17': 'operation',
    },
    'expected_alarm_codes': {
        '0x001': 'service monitoring local warning (LWRN)',
        '0x002': 'service monitoring local alarm (LFLT)',
        '0x004': 'service monitoring network warning (NWRN)',
        '0x008': 'service monitoring network alarm (NFLT)',
        '0x010': 'system fault (SYST)',
        '0x020': 'reboot fault (REBT)',
        '0x040': 'LAN down (LAN)',
        '0x080': 'RX1 offset fault (OFFS)',
        '0x100': 'CRC RX1 errors (CRC)',
        '0x200': 'TLC fault (TLC)',
        '0x400': 'RX2 offset fault (OFFS)',
        '0x800': 'CRC RX2 errors (CRC)',
        '0x1000': 'CRC BD errors(CRC)',
    }
}
