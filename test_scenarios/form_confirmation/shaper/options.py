from src.enum_types_constants import ShaperUpQueueStr

system = {

}

options = {
    'vno_stn_shaper': {
        'name': 'vss',
        'template': 'ON',
        'cir': '234567',
        'up_queue': ShaperUpQueueStr.Q4,
        'max_enable': 'ON',
        'max_cir': '240800',
        'max_slope': '4',
        'min_enable': 'ON',
        'min_cir': '123456',
        'down_slope': '5',
        'up_slope': '6',
        'wfq_enable': 'ON',
        'wfq1': '50',
        'wfq2': '12',
        'wfq3': '11',
        'wfq4': '10',
        'wfq5': '9',
        'wfq6': '8',
        'night_enable': 'ON',
        'night_cir': '250000',
        'night_start': '22',
        'night_end': '7'
    },
    'stn_shaper': {
        'name': 'ss',
        'template': 'OFF',
        'cir': '1',
        'up_queue': ShaperUpQueueStr.Q7,
        'max_enable': 'ON',
        'max_cir': '1',
        'max_slope': '4',
        'min_enable': 'ON',
        'min_cir': '1',
        'down_slope': '1',
        'up_slope': '1',
        'wfq_enable': 'ON',
        'wfq1': '75',
        'wfq2': '5',
        'wfq3': '5',
        'wfq4': '5',
        'wfq5': '5',
        'wfq6': '5',
        'night_enable': 'ON',
        'night_cir': '1',
        'night_start': '0',
        'night_end': '0'
    },

}
