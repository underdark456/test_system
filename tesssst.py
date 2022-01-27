import src
from src.custom_test_case import CustomTestCase
from src import nms_api, test_api

__author__ = 'ish'  # place your name in here
__version__ = '0.1'

from src.enum_types_constants import ControllerModes, StationModes, RouteTypes
from src.exceptions import ObjectNotCreatedException

options_path = ''
backup_name = 'default_config.txt'  # edit if needed


nms_options = test_api.get_nms()
nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))


