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
    'sidepanel_box_class': 'sidepanel__box',
    'resize_box': {
        'id': 'resizeBox',
        'buttons': [
            'Size to Fit',
            'Auto-Size',
            'Auto-Size (skip headers)',
        ],
    },
    'Filter': {
        'Info': 'infoCheckbox',
        'Warning': 'warningCheckbox',
        'Critical': 'criticalCheckbox',
        'Date': 'dateCheckbox',
        'Path': 'pathCheckbox',
    },
    'Last statistics': {
        '1h': 'oneHourButton',
        '3h': 'threeHoursButton',
        '1d': 'oneDayButton',
        '3d': 'threeDaysButton',
        '1W': 'oneWeekButton',
        '3W': 'threeWeeksButton',
        '1M': 'oneMonthButton',
    },
    'Range selection': {
        'From:': 'startDatePicker',
        'To:': 'endDatePicker',
        'Apply': 'applyPickerButton',
    },
    'Problem investigator': {
        'Add device': 'addDeviceButton',
        'Sync & Add': 'syncStorageButton',
    },
}
