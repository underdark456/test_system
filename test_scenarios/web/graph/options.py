from src.drivers.abstract_http_driver import CHROME
from src.options_providers.options_provider import CHROME_CONNECT, CONNECTION

system = {
    CHROME_CONNECT: {
        'type': CHROME,
        'no_gui': True,
        'maximize_window': True,
    },
    CONNECTION: CHROME_CONNECT,
}

options = {
    'sidepanel_box_class': 'sidepanel__box',  # Sidepanel element class (where all control elements are located)
    'graph_title_class': 'graph__title',  # Graph title element class
    'last_statistics': {
        'thirtyMinutesButton': '30m',
        'oneHourButton': '1h',
        'threeHoursButton': '3h',
        'oneDayButton': '1d',
        'threeDaysButton': '3d',
        'oneWeekButton': '1w',
        'threeWeeksButton': '3w',
        'oneMonthButton': '1m',
    },
    'range_selection': {
        'applyPickerButton': 'Apply',
        'endDatePicker': 'To:',
        'startDatePicker': 'From:',
    },
    'storage': {
        'addDeviceButton': 'Add device',
        'syncStorageButton': 'Sync & Add'
    },
    'first_selector_options_net': [
        'Levels',
        'Traffic summary',
        'TX traffic detailed',
        'RX traffic detailed',
        'Stations state',
        'Errors',
        'Controllers state',
    ],
    'second_selector_options_net': [
        'None',
        'Levels',
        'Traffic summary',
        'TX traffic detailed',
        'RX traffic detailed',
        'Stations state',
        'Errors',
        'Controllers state',
    ],
    'first_selector_options_vno': [
        'Levels',
        'Traffic summary',
        'TX traffic detailed',
        'RX traffic detailed',
        'Stations state',
        'Errors',
    ],
    'second_selector_options_vno': [
        'None',
        'Levels',
        'Traffic summary',
        'TX traffic detailed',
        'RX traffic detailed',
        'Stations state',
        'Errors',
    ],
    'first_selector_options_ctrl': [
        'Levels',
        'Traffic summary',
        'Levels detailed',
        'TX traffic detailed',
        'RX traffic detailed',
        'TDMA load',
        'Stations state',
        'Errors',
        'State',
    ],
    'second_selector_options_ctrl': [
        'None',
        'Levels',
        'Traffic summary',
        'Levels detailed',
        'TX traffic detailed',
        'RX traffic detailed',
        'TDMA load',
        'Stations state',
        'Errors',
        'State',
    ],
    'first_selector_options_stn': [
        'Levels',
        'Traffic summary',
        'TX traffic detailed',
        'RX traffic detailed',
        'ACM',
        'TDMA load',
        'Errors',
    ],
    'second_selector_options_stn': [
        'None',
        'Levels',
        'Traffic summary',
        'TX traffic detailed',
        'RX traffic detailed',
        'ACM',
        'TDMA load',
        'Errors',
    ],

}
