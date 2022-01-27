from src.drivers.abstract_http_driver import CHROME
from src.options_providers.options_provider import CHROME_CONNECT

no_gui = True

system = {
    'first_user': {
        'type': CHROME,
        'no_gui': no_gui,
        'username': "user-1",
        'password': "12345",
        'maximize_window': True,  # if True the browser window is automatically maximized
        'window_size': None,  # set window size as a tuple. `window_size` has higher priority than `maximize_window`
        'auto_login': True,  # if set to True login is automatically performed after getting a driver instance
    },
    'second_user': {
        'type': CHROME,
        'no_gui': no_gui,
        'username': "user-2",
        'password': "12345",
        'maximize_window': True,  # if True the browser window is automatically maximized
        'window_size': None,  # set window size as a tuple. `window_size` has higher priority than `maximize_window`
        'auto_login': True,  # if set to True login is automatically performed after getting a driver instance
    },
    'third_user': {
        'type': CHROME,
        'no_gui': no_gui,
        'username': "user-3",
        'password': "12345",
        'maximize_window': True,  # if True the browser window is automatically maximized
        'window_size': None,  # set window size as a tuple. `window_size` has higher priority than `maximize_window`
        'auto_login': True,  # if set to True login is automatically performed after getting a driver instance
    },
}

options = {

}
