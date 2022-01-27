NOT_FOUND_PAGE = 'notfound'
"""URL 404 страницы"""

WEB_LOGIN_PATH = "login"
WEB_LOGOUT_BUTTON = "logout"
WEB_LOGIN_BUTTON = "#submit"
# WEB_APPLY_BUTTON = "#submitSecond"
WEB_APPLY_BUTTON = "#submitFirst"
WEB_ERROR_SELECTOR = "div.errors"
WEB_FIELD_ERROR_SELECTOR = "{}_error"
"error container pattern. 'field id'_error"
WEB_ADD_DEVICE_BUTTON = "#addDeviceButton"
WEB_SYNC_ADD_BUTTON = "#syncStorageButton"

API_LOGIN_PATH = "api/tree/login/nms=0"
API_LOGOUT_PATH = "api/tree/logout/nms=0"
API_RESTART_COMMAND = 16777242
API_REBOOT_COMMAND = 16777243
API_FORCE_CONFIG_CONTROLLER_COMMAND = 6291483
API_FORCE_CONFIG_STATION_COMMAND = 35651604
API_SAVE_CONFIG_COMMAND = 16777235
API_SAVE_CONFIG_AS_COMMAND = 16777237
API_LOAD_CONFIG_COMMAND = 16777239
API_LOAD_BACKUP_COMMAND = 16777241
API_RETURN_ALL_COMMAND = 3145746

NEW_OBJECT_ID = -1

CONTROLLER = 'controller'
STATION = 'station'

# The following constants are used in Realtime monitor JSON payload as command values
SYSTEM = 'show system'
LAN = 'show int eth'
DEMODULATOR = 'show in dem'
DEMODULATOR2 = 'show int 2dem'
MODULATOR = 'show int mod'
NETWORK = 'show net'
STATIONS = 'show stat'
STATIONS_RF = 'show st rf'
STATIONS_TR = 'show st tr'
PROFILES = 'show prof'
ARP = 'show arp'
BLUESCREEN = 'bl'
ROUTING = 'show ip  '
SHAPERS = 'show shapers'
ERRORS = 'show err'
COTM = 'show serv cotm'
RTP = 'show rtp'
SNMP = 'show snmp'
DHCP = 'show dhcp'
MULTICAST = 'show mult'
TCPA = 'show acc all'
NAT = 'show nat'
REDUNDANCY = 'show backup'
MF_TDMA = 'show mf'
SCPC_TLC = 'show tlc'
NMS = 'show nms'
TUNING = 'show serv tun'
BOOT_MODE = 'show boot'

# NMS error codes
NO_ERROR = 0
NO_SUCH_TABLE = -1
NO_SUCH_ROW = -2
NO_SUCH_VARIABLE = -3
WRONG_VARIABLE_TYPE = -4
WRONG_VARIABLE_VALUE = -5
MULTIPLE_NAMES = -6
MULTIPLE_VALUES = -7
TABLE_FULL = -8
NO_HIERARCHY = -9
WRONG_OBJECT_SEQUENCE = -10
INTERNAL_SEARCH_FAILED = -11
OBJECT_EXISTS = -12
CANNOT_DELETE = -13
BAD_ARGUMENTS = -14
ACCESS_DENIED = -15
WRONG_SOURCE = -16
NO_SUCH_OBJECT = -17
STRING_TOO_LONG = -18
VALUE_TOO_HIGH = -19
VALUE_TOO_LOW = -20
ONE_TIME_SET = -21
