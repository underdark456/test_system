from src.drivers.abstract_http_driver import API, CHROME
from src.options_providers.options_provider import API_CONNECT, CONNECTION, CHROME_CONNECT

_nms_ip = 'http://10.56.33.9:8000/'  # redefine in local_options.py
_username = 'admin'  # redefine in local_options.py if needed
_password = '12345'  # # redefine in local_options.py if needed

system = {
    # For simplified API
    'nms_ip': _nms_ip,
    'username': _username,
    'password': _password,

    'uhp1_ip': '10.56.33.20',  # redefine in local options
    'uhp2_ip': '10.56.33.21',  # redefine in local options
    'uhp3_ip': '10.56.33.22',  # redefine in local options
    'uhp4_ip': '10.56.33.23',  # redefine in local options
    'uhp5_ip': None,  # redefine in local options
    'uhp6_ip': None,  # redefine in local options
    'uhp7_ip': None,  # redefine in local options
    'uhp8_ip': None,  # redefine in local options

    CHROME_CONNECT: {
        'type': CHROME,
        'no_gui': False,
        'driver_path': r"C:\\Users\\ish\\PycharmProjects\\test_system\\chromedriver",
        'address': _nms_ip,
        'username': _username,
        'password': _password,
        'maximize_window': True,  # if True the browser window is automatically maximized
        'window_size': None,  # set window size as a tuple. `window_size` has higher priority than `maximize_window`
        'auto_login': True,  # if set to True login is automatically performed after getting a driver instance
    },

    API_CONNECT: {
        'type': API,
        'address': _nms_ip,
        'username': _username,
        'password': _password,
        'auto_login': True,
    },

    # default connection
    CONNECTION: API_CONNECT,
}

options = {

}
