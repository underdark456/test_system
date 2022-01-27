# !!! Don`t change this file !!!
# For overriding create in this directory file `local_options.py` with 'options' and/or 'system' dict inside
import os
import unittest

from runtest import TextTestRunner
from src.custom_logger import *
from src.drivers.abstract_http_driver import CHROME, API, FIREFOX
from src.options_providers.options_provider import API_CONNECT, CHROME_CONNECT, CONNECTION, FIREFOX_CONNECT

_nms_ip = 'http://localhost:8000/'  # redefine in local_options.py
_username = 'admin'  # redefine in local_options.py if needed
_password = '12345'  # # redefine in local_options.py if needed

PROJECT_DIR = F'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}{os.sep}'

LOG_DIR = 'LOG_DIR'
SCREENSHOT_DIR = 'SCREENSHOTS'
UHP_SW_DIR = 'uhp_sw_dir'

system = {
    # For simplified API
    'nms_ip': _nms_ip,
    'username': _username,
    'password': _password,

    # the following path is used to look up for UHP SW, i.e.
    # /home/dkudryashov/mnt/TECHNICAL/UHP/UHP-SOFT3/3.7/Development/3.7.1.36 211116
    UHP_SW_DIR: None,

    CHROME_CONNECT: {
        'type': CHROME,
        'no_gui': False,
        'driver_path': r"/usr/bin/chromedriver",
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
    FIREFOX_CONNECT: {
        'type': FIREFOX,
        'no_gui': False,
        'driver_path': r"/usr/bin/geckodriver",
        'address': _nms_ip,
        'username': _username,
        'password': _password,
        'maximize_window': True,  # if True the browser window is automatically maximized
        'window_size': None,  # set window size as a tuple. `window_size` has higher priority than `maximize_window`
        'auto_login': True,  # if set to True login is automatically performed after getting a driver instance
    },

    # default connection
    CONNECTION: API_CONNECT,

    'server_username': 'user',
    'server_password': '1',

    'loader': unittest.TestLoader(),
    'runner': TextTestRunner(
        verbosity=0,
        failfast=False,
        descriptions=False,
        buffer=False,
    ),
    'api_connection': API_CONNECT,

    LOGGING: INFO,
    CONSOLE_LOGGING: DEBUG,

    # the following path is used to store logs (/logs)
    LOG_DIR: F'{PROJECT_DIR}logs{os.sep}',

    # the following path is used to store logs (/logs)
    SCREENSHOT_DIR: F'{PROJECT_DIR}screenshots{os.sep}',

    # The following key-value pairs are used in tests where UHP are involved
    'uhp1_ip': None,  # redefine in local options
    'uhp2_ip': None,  # redefine in local options
    'uhp3_ip': None,  # redefine in local options
    'uhp4_ip': None,  # redefine in local options
    'uhp5_ip': None,  # redefine in local options
    'uhp6_ip': None,  # redefine in local options
    'uhp7_ip': None,  # redefine in local options
    'uhp8_ip': None,  # redefine in local options

    # UHP serial numbers should be integers
    'uhp1_sn': None,  # redefine in local options
    'uhp2_sn': None,  # redefine in local options
    'uhp3_sn': None,  # redefine in local options
    'uhp4_sn': None,  # redefine in local options
    'uhp5_sn': None,  # redefine in local options
    'uhp6_sn': None,  # redefine in local options
    'uhp7_sn': None,  # redefine in local options
    'uhp8_sn': None,  # redefine in local options

    # UHP VLAN should be integers
    'uhp1_vlan': 0,  # redefine in local options if needed
    'uhp2_vlan': 0,  # redefine in local options if needed
    'uhp3_vlan': 0,  # redefine in local options if needed
    'uhp4_vlan': 0,  # redefine in local options if needed
    'uhp5_vlan': 0,  # redefine in local options if needed
    'uhp6_vlan': 0,  # redefine in local options if needed
    'uhp7_vlan': 0,  # redefine in local options if needed
    'uhp8_vlan': 0,  # redefine in local options if needed

    'uhp1_gw': None,  # redefine in local options if needed
    'uhp2_gw': None,  # redefine in local options if needed
    'uhp3_gw': None,  # redefine in local options if needed
    'uhp4_gw': None,  # redefine in local options if needed
    'uhp5_gw': None,  # redefine in local options if needed
    'uhp6_gw': None,  # redefine in local options if needed
    'uhp7_gw': None,  # redefine in local options if needed
    'uhp8_gw': None,  # redefine in local options if needed

    'net_id': 1,

}
options = {
    'tx_level': 36,  # tx_level used in the test stand, redefine if needed
    'stations_tx_lvl': 36,  # alias for tx_level, redefine if needed
}
