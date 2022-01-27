# Alternative api driver
import json
import requests
import base64
from json import JSONDecodeError
from time import sleep, time
from http import HTTPStatus

from src.constants import API_RESTART_COMMAND, API_LOAD_CONFIG_COMMAND, API_RETURN_ALL_COMMAND, \
    API_FORCE_CONFIG_CONTROLLER_COMMAND, API_FORCE_CONFIG_STATION_COMMAND
from src.exceptions import InvalidOptionsException, DriverInitException, ObjectNotCreatedException, \
    ObjectNotUpdatedException, NmsErrorResponseException
from pathlib import Path
from collections import namedtuple

from src.nms_entities.has_up_state_object import HasUpState

NO_AUTO_ABORT = False
AUTO_ABORT = True
_API_LOGIN_PATH = "api/tree/login/nms=0"
_API_OBJECT_CREATE = 'api/object/write/{}/new_item={}'
_API_OBJECT_READ = 'api/object/get/{}'
_API_OBJECT_UPDATE = 'api/object/write/{}'
_API_OBJECT_DELETE = 'api/object/delete/{}'
_API_LIST_ITEMS = 'api/list/get/{}/list_items={}'
_API_LOGOUT_PATH = "api/tree/logout/nms=0"
_API_OBJECT_LOG = 'api/log/get/{}'
_API_REALTIME = 'api/realtime/get/{}'

_NMS = 'nms'
_NETWORK = 'network'
_CONTROLLER = 'controller'
_SERVICE_ = 'service'
_VNO = 'vno'
_TELEPORT = 'teleport'
_POLICY = 'policy'
_RULE = 'polrule'
_STATION = 'station'
_PROFILE = 'profile_set'
_SHAPER = 'shaper'
_ALERT = 'alert'
_USER = 'user'
_GROUP = 'group'
_ROUTE = 'route'
_DASHBOARD = 'dashboard'
_BAL_CONTROLLER = 'bal_controller'
_SR_CONTROLLER = 'sr_controller'
_SR_LICENSE = 'sr_license'
_SR_TELEPORT = 'sr_teleport'
_DEVICE = 'device'
_SERVER = 'server'
_ACCESS = 'access'
_CAMERA = 'camera'
_PORT_MAP = 'port_map'
_SW_UPLOAD = 'sw_upload'
_RIP = 'rip_router'
_SCHEDULER = 'scheduler'
_SCH_RANGE = 'sch_range'
_SCH_SERVICE = 'sch_service'
_SCH_TASK = 'sch_task'

_valid_states_objects = (_NMS, _CONTROLLER, _STATION, _BAL_CONTROLLER, _SR_CONTROLLER, _SR_TELEPORT, _DEVICE, _SCHEDULER)
_get_realtime_commands = {
    # Interfaces section
    'lan': 'show int eth',
    'modulator': 'show int mod',
    'demodulator': 'show in dem',
    'demodulator2': 'show int 2dem',

    # Network section
    'network': 'show net',
    'stations': 'show stat',
    'stations rf': 'show st rf 0',
    'stations tr': 'show st tr 0',
    'mf tdma': 'show mf_tdma',
    'nms': 'show nms',

    # System section
    'system': 'show system',
    'profiles': 'show prof',
    'errors': 'show err',
    'bluescreen': 'bl',
    'options': 'unit key',
    'boot mode': 'show boot',
    'log': 'show log',
    'redundancy': 'show backup',

    # Protocols section
    'routing': 'show ip  ',
    'rip': 'show rip',
    'vlans': 'show vlans',
    'svlans': 'show svlans',
    'mac tbl': 'show mac',
    'rtp': 'show rtp',
    'arp': 'show arp',
    'snmp': 'show snmp',
    'tcpa': 'show acc all',
    'dhcp': 'show dhcp',
    'nat': 'show nat',
    'multicast': 'show mult',
    'shapers': 'show shapers',
    'tuning': 'show serv tun',
    'cotm': 'show serv cotm',
    'acm': 'show modcods',
}

_set_realtime_commands = {
    'save config': 'conf save',
    'clear counters': 'cle co all',
    'reboot': 'ds 1',
    'clear faults': 'cf',
    'exit telnet': 'exit',
    'run profile 1': 'prof 1 run',
}

# The following variables are global, their values are set to default at each `connect` function call
_default_timeout = 4
_auto_abort_on_error = True
_nms_ip_port = None
_cookies = None
_error_code = None
_error_log = None


def connect(url: str, username: str, password: str):
    """
    Connect to NMS using the passed URL and the credentials

    >>> connect('http://localhost:8000', 'admin', '12345')
    Login to NMS located at `localhost:8000` using username `admin` and password `12345`

    :param str url: NMS URL in the following format `http://<ip_address>:<port>`
    :param str username: NMS username
    :param str password: NMS password
    :returns None: this function returns None
    :raises requests.exceptions.ConnectTimeout: if there is no response from the server
    :raises DriverInitException: if Http status code is not 200
    """
    # Setting global variables to their default values at NMS connection
    global _cookies
    global _nms_ip_port
    global _auto_abort_on_error
    global _error_code
    global _error_log
    global _default_timeout
    _default_timeout = 3
    _error_code = None
    _error_log = None
    _auto_abort_on_error = True
    bytes_str = F"{username}:{password}".encode('ascii')
    bytes_b64 = base64.b64encode(bytes_str)
    token = bytes_b64.decode('ascii')
    headers = {
        'Authorization': F"Basic {token}"
    }
    if not url.endswith('/'):
        url += '/'
    _nms_ip_port = url
    resp = requests.get(_nms_ip_port + _API_LOGIN_PATH, headers=headers, timeout=_default_timeout)
    if HTTPStatus.OK != resp.status_code and _auto_abort_on_error:
        raise DriverInitException(f'Login unsuccessful: {resp.content}')
    _cookies = resp.cookies


def login(url: str, username: str, password: str):
    """
    Alias for `connect` function
    Login to NMS using the passed URL and the credentials

    >>> login('http://localhost:8000', 'admin', '12345')
    Login to NMS located at `localhost:8000` using username `admin` and password `12345`

    :param str url: NMS URL in the following format `http://<ip_address>:<port>`
    :param str username: NMS username
    :param str password: NMS password
    :returns None:
    :raises requests.exceptions.ConnectTimeout: if there is no response from the server
    :raises DriverInitException: if Http status code is not 200
    """
    connect(url, username, password)


def logout():
    """
    Disconnect from NMS

    :returns None:
    :raises requests.exceptions.ConnectTimeout: if there is no response from the server
    :raises DriverInitException: if Http status code is not 200
    """
    global _cookies
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    resp = requests.get(_nms_ip_port + _API_LOGOUT_PATH, timeout=_default_timeout)
    if HTTPStatus.OK != resp.status_code and _auto_abort_on_error:
        raise NmsErrorResponseException(f'Logout unsuccessful: {resp.content}')
    _cookies = None


def create(parent_table_row: str, new_item: str, params: dict):
    """
    Create new NMS object

    >>> create('network:0', 'vno', {'name': 'vno-0'})
    Create a new item `vno` in network ID 0


    :param str parent_table_row: describes parent object as `<parent_table>:<row>`
    :param str new_item: name of a new item to create
    :param dict params: parameters of the new item that are used to create it
    :returns str trow: the ID of the created item in the following format `<new_item_table>:<row>`
    :returns None: if auto_abort_on_error is off but there is an error upon creating an object
    :raises ObjectNotCreatedException: if auto_abort_on_error is on and there is an error upon creation an object
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Call `connect` function first')
    if len(parent_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong parent table row format')
    if not isinstance(params, dict) and _auto_abort_on_error:
        raise InvalidOptionsException('Parameters must be passed as a dictionary')
    reply = _post(_API_OBJECT_CREATE.format(parent_table_row.replace(':', '='), new_item), params)

    if _error_log != '' or _error_code:
        if _auto_abort_on_error:
            raise ObjectNotCreatedException(f'`{new_item}` is not created in `{parent_table_row}`. '
                                            f'Reason: error_code: `{_error_code}` error_log: `{_error_log}`')
        else:
            return None
    trow = f'{new_item}:{reply.get("%row")}'
    return trow


def update(object_table_row: str, params: dict):
    """
    Update NMS object

    >>> update('vno:0', {'name': 'vno-5'})
    Apply new name `vno-5` to vno ID 0

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :param dict params: parameters which are applied to the object
    :returns str object_table_row: if update is succeeded
    :returns None: if auto_abort_on_error is off but there is an error upon creating an object
    :raises ObjectNotUpdatedException: if auto_abort_on_error is on and there is an error upon creation an object
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    if not isinstance(params, dict) and _auto_abort_on_error:
        raise InvalidOptionsException('Parameters must be passed as a dictionary')
    _post(_API_OBJECT_UPDATE.format(object_table_row.replace(':', '=')), params)

    if _error_log != '' or _error_code:
        if _auto_abort_on_error:
            raise ObjectNotUpdatedException(f'`{object_table_row}` is not updated. '
                                            f'Reason: error_code: `{_error_code}` error_log: `{_error_log}`')
        else:
            return None
    return object_table_row


def read(object_table_row: str):
    """
    Read NMS object

    >>> read('station:0')
    Get station ID 0 parameters

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :returns None: if auto_abort_on_error is off but there is an error upon getting object data
    :returns dict reply: a dictionary containing parameters of the object
    :raises NmsErrorResponseException: if auto_abort_on_error is on and there is an error upon reading an object
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    reply = _post(_API_OBJECT_READ.format(object_table_row.replace(':', '=')), {})

    if _error_log != '' or _error_code:
        if _auto_abort_on_error:
            raise NmsErrorResponseException(f'`{object_table_row}` cannot be read. '
                                            f'Reason: error_code: `{_error_code}` error_log: `{_error_log}`')
        else:
            return None
    return reply


def delete(object_table_row: str, recursive: bool = False):
    """
    Delete NMS object

    >>> delete('network:0')
    Delete network ID 0

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :param bool recursive: True to apply recursive deletion, otherwise False
    :returns bool: True if deletion is succeeded, otherwise False
    :raises ObjectNotCreatedException: if auto_abort_on_error is on and there is an error upon creation an object
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    if recursive:
        params = {'recursive': 1}
    else:
        params = {}
    _post(_API_OBJECT_DELETE.format(object_table_row.replace(':', '=')), params)

    if _error_log != '' or _error_code:
        if _auto_abort_on_error:
            raise NmsErrorResponseException(f'`{object_table_row}` is not deleted. '
                                            f'Reason: error_code: `{_error_code}` error_log: `{_error_log}`')
        else:
            return False
    return True


def get_param(object_table_row: str, param_name: str) -> object:
    """
    Get the value of the passed parameter for the passed `table_row`

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :param str param_name: the name of the parameter to get the value from
    :returns:
        - param_value - the value of the parameter
        - None - if such parameter is not found
    :raises NmsErrorResponseException: if auto_abort_on_error is on and there is an error upon getting the parameter
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    reply = _post(_API_OBJECT_READ.format(object_table_row.replace(':', '=')), {})

    if _error_log != '' or _error_code:
        if _auto_abort_on_error:
            raise NmsErrorResponseException(f'`{object_table_row}` cannot be read. '
                                            f'Reason: error_code: `{_error_code}` error_log: `{_error_log}`')
        else:
            return None
    try:
        for key, value in reply.items():
            if key == param_name:
                return value
    except AttributeError:
        return None
    return None


def get_uprow(object_table_row: str):
    """
    Get the uprow of the object

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :returns:
        - uprow - the uprow of the object
        - None - if such parameter is not found
    :raises NmsErrorResponseException: if auto_abort_on_error is on and there is an error upon getting the uprow
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    reply = _post(_API_OBJECT_READ.format(object_table_row.replace(':', '=')), {})

    if _error_log != '' or _error_code:
        if _auto_abort_on_error:
            raise NmsErrorResponseException(f'`{object_table_row}` cannot be read. '
                                            f'Reason: error_code: `{_error_code}` error_log: `{_error_log}`')
        else:
            return None
    try:
        for key, value in reply.items():
            if key == 'uprow' and isinstance(value, str) and len(value.split()) > 1:
                return value.split()[0]
    except AttributeError:
        return None
    return None


def auto_abort_on_error(abort=True):
    """
    Set behavior of the API driver

    :param bool abort: if True no exceptions will be thrown upon CRUD operations
    """
    global _auto_abort_on_error
    if abort:
        _auto_abort_on_error = True
    else:
        _auto_abort_on_error = False


def get_next_error():
    global _error_code
    global _error_log
    if isinstance(_error_log, requests.exceptions.ConnectionError):
        error_log = str(_error_log)
    else:
        error_log = _error_log
    error_code = _error_code
    _error_log = None
    _error_code = None
    current_errors = namedtuple('errors', 'code log')
    return current_errors(error_code, error_log)


def load_config(config_name, local=True):
    """
    Load and apply config to NMS.

    >>> load_config('default_config.txt')
    Upload and apply config `default_config.txt` to NMS

    :param str config_name: the name of the config file to apply
    :param bool local: if True (by default) the backup is uploaded from a local machine in the first place
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Call `connect` function first')
    if local:
        _upload_config(config_name)
    _apply_config(config_name)


def search_by_name(parent_table_row: str, object_type: str, name: str):
    """
    Get an object table row by its name.

    :param str parent_table_row: the name of a table to perform search in
    :param str object_type: the type of the searched object
    :param str name: the name of an object to find
    :returns:
        - `object_table_row` - if the object with the passed name is found
        - None - if the object with the given name is not found
    """
    global _error_code
    global _error_log
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Call `connect` function first')
    if len(parent_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong parent table row format')
    parent_table_row = parent_table_row.replace(':', '=')
    resp = _post(_API_LIST_ITEMS.format(parent_table_row, object_type), {})
    if _error_log != '' or _error_code:
        if _auto_abort_on_error:
            raise NmsErrorResponseException(f'Cannot get list of `{name}` in `{parent_table_row}`'
                                            f'Reason: error_code: `{_error_code}` error_log: `{_error_log}`')
        else:
            return None
    try:
        for obj in resp:
            for inner_key, inner_value in obj.items():
                if inner_key == 'name' and inner_value == name:
                    object_table_row = f'{object_type}:{obj.get("%row", None)}'
                    return object_table_row
    except AttributeError:
        return None
    return None


def set_timeout(timeout=3):
    """
    Set requests driver global timeout

    :param int timeout: number of seconds to wait for both connection establishment and response
    """
    global _default_timeout
    _default_timeout = timeout


def _upload_config(config_name):
    """
    ! Private function - Do not call it directly! Upload a config `config_name` to NMS.

    :param str config_name: name of the config file to upload
    :raises JSONDecodeError: if there is any error upon applying the config or applying is timed out
    :raises FileNotFoundError: if the config file is not found
    """
    # Should not happen if the function is not called directly by the user
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Call `connect` function first')
    with open((Path(__file__).parent / '../nms_backups' / config_name).resolve(), 'rb') as f:
        files = {'config': f}
        resp = requests.post(
            _nms_ip_port + 'api/fs/upload/nms=0',
            files=files,
            cookies=_cookies
        )
        error = None
        if HTTPStatus.OK != resp.status_code:
            error = F"{resp.status_code} : {resp.reason}"
        elif 0 == len(resp.content):
            error = 'Empty response body'
        else:
            try:
                result_obj = json.loads(resp.content)
                if 0 != result_obj['error_code']:
                    error = result_obj['error_log']
            except JSONDecodeError:
                error = 'Invalid json in response'
            except KeyError:
                error = 'Not found error_code in response'
        if _auto_abort_on_error and error is not None:
            raise ValueError(error)


def _apply_config(config_name):
    """
    ! Private function - Do not call it directly! Apply the loaded config `config_name` to NMS.

    :param str config_name: name of the config file to apply
    :raises ValueError: if there is any error upon applying the config or applying is timed out
    """
    # Should not happen if the function is not called directly by the user
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Call `connect` function first')
    # global _error_log
    # global _error_code
    start_time = _get_start_time()
    _post(
        f'api/object/write/nms=0/command={API_LOAD_CONFIG_COMMAND}',
        {'load_filename': config_name}
    )
    if _error_log != '':
        raise ValueError(f'Cannot apply config. Reason: {_error_log}')
    sleep(2)
    for i in range(1, 50):
        sleep(0.5)
        # In some cases there is 403 after config load : Forbidden error, therefore, ignoring it
        try:
            new_time = _get_start_time()
            if new_time and start_time != new_time:
                return
        except ValueError:
            continue
    if _auto_abort_on_error:
        raise ValueError('Config load error')


def _post(path: str, data: dict):
    """
    ! Private function - Do not call it directly! Calls POST request with the passed parameters

    :param str path: relative path to execute POST request
    :param dict data: POST payload
    :returns tuple (result, error): the response to POST request and any errors
    :raises JSONDecodeError: if the response contains a non-valid JSON
    :raises KeyError: if there is no error_log in the response
    """
    # Should not happen if the function is not called directly by the user
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Call `connect` function first')
    # handling non-ascii characters in the payload
    data = json.dumps(data, ensure_ascii=False)
    encoded_data = data.encode('utf-8')
    reply = None
    global _error_code
    global _error_log
    _error_code = None
    _error_log = None

    try:
        resp = requests.post(
            _nms_ip_port + path,
            data=encoded_data,
            cookies=_cookies,
            timeout=_default_timeout
        )

        if HTTPStatus.OK != resp.status_code:
            _error_log = F"{resp.status_code} : {resp.reason}"
        elif 0 == len(resp.content):
            _error_log = 'Empty response body'
        else:
            try:
                result_obj = json.loads(resp.content)
                reply = result_obj.get('reply', None)
                if reply is None:
                    _error_log = 'Not found reply in response'
                _error_log = result_obj.get('error_log', None)
                if _error_log is None:
                    _error_log = 'Not found error_log in response'
                _error_code = result_obj.get('error_code', None)
                if _error_code is None:
                    _error_log = 'Not found error_code in response'
            except JSONDecodeError:
                _error_log = 'Invalid json in response'
    # If NMS does not respond to the POST request
    except requests.exceptions.ConnectionError as exc:
        _error_log = exc
    return reply


def _get_start_time():
    """
    ! Private function - Do not call it directly! Get `load_time` value of NMS

    :returns int result: Load time value of NMS
    :raises JSONDecodeError: if the response contains a non-valid JSON
    :raises KeyError: if there is no error_log in the response
    :raises ValueError: if there is any error in the response
    """
    result = None
    try:
        resp = requests.get(_nms_ip_port + 'api/object/dashboard/nms=0', cookies=_cookies, timeout=_default_timeout)
        error = None
        if HTTPStatus.OK != resp.status_code:
            error = F"{resp.status_code} : {resp.reason}"
            # Handle Access denied after loading backup
            if resp.status_code == 401:
                return None
        elif 0 == len(resp.content):
            error = 'Empty response body'
        else:
            try:
                result_obj = json.loads(resp.content)
                if 0 == result_obj['error_code']:
                    result = result_obj['reply']['load_time']
                else:
                    error = result_obj['error_log']
            except JSONDecodeError:
                error = 'Invalid json in response'
            except KeyError:
                error = 'Not found error_code in response'
        if error is not None and _auto_abort_on_error:
            raise ValueError(error)
    except requests.exceptions.ConnectionError:
        pass
    return result


def wait_state(object_table_row: str, state: str, *, timeout: int = 30, step_timeout: int = 5):
    """
    Wait for desired state (Up, Down etc.) The awaiting is blocking

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :param str state: the desired state to wait for
    :param int timeout: the amount of time in seconds to wait the UP state
    :param int step_timeout: the amount of time in seconds between queries of the state
    :returns bool: True if the UP state is reached, otherwise False
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    if object_table_row.split(':')[0] not in _valid_states_objects:
        raise InvalidOptionsException('Invalid object for awaiting state')
    if state not in HasUpState._valid_states:
        raise InvalidOptionsException('Invalid expected state is passed')
    begin = int(time())
    while True:
        if get_param(object_table_row, 'state') == state:
            return True
        t = int(time())
        if timeout < t - begin:
            return False
        sleep(step_timeout)


def wait_not_state(object_table_row: str, not_state: str, *, timeout: int = 30, step_timeout: int = 5):
    """
    Wait for a state (Up, Down etc.) to be ANY but not the passed one. The awaiting is blocking

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :param str not_state: the desired state that is not expected
    :param int timeout: the amount of time in seconds to wait for ANY but not the passed state
    :param int step_timeout: the amount of time in seconds between queries of the state
    :returns bool: True if ANY of the state is reached, otherwise False
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    if object_table_row.split(':')[0] not in _valid_states_objects:
        raise InvalidOptionsException('Invalid object for awaiting state')
    if not_state not in HasUpState._valid_states:
        raise InvalidOptionsException('Invalid expected state is passed')
    begin = int(time())
    while True:
        if get_param(object_table_row, 'state') != not_state:
            return True
        t = int(time())
        if timeout < t - begin:
            return False
        sleep(step_timeout)


def wait_states(object_table_row: str, states: list, *, timeout: int = 30, step_timeout: int = 5):
    """
    Wait for ANY of the desired states (Up, Down etc.) The awaiting is blocking

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :param list states: a list of desired states
    :param int timeout: the amount of time in seconds to wait for one of the states
    :param int step_timeout: the amount of time in seconds between queries of the state
    :returns bool: True if ANY of the passed state is reached, otherwise False
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    if object_table_row.split(':')[0] not in _valid_states_objects:
        raise InvalidOptionsException('Invalid object for awaiting state')
    for state in states:
        if state not in HasUpState._valid_states:
            raise InvalidOptionsException(f'Invalid expected state is passed: {state}')
    begin = int(time())
    while True:
        if get_param(object_table_row, 'state') in states:
            return True
        t = int(time())
        if timeout < t - begin:
            return False
        sleep(step_timeout)


def wait_not_states(object_table_row: str, states: list, *, timeout: int = 30, step_timeout: int = 5):
    """
    Wait for ANY state that is not passed (Up, Down etc.) The awaiting is blocking

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :param list states: a list of states to avoid
    :param int timeout: the amount of time in seconds to wait
    :param int step_timeout: the amount of time in seconds between queries of the state
    :returns bool: True if ANY state but passed is reached, otherwise False
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    if object_table_row.split(':')[0] not in _valid_states_objects:
        raise InvalidOptionsException('Invalid object for awaiting state')
    for state in states:
        if state not in HasUpState._valid_states:
            raise InvalidOptionsException(f'Invalid expected state is passed: {state}')
    begin = int(time())
    while True:
        if get_param(object_table_row, 'state') not in states:
            return True
        t = int(time())
        if timeout < t - begin:
            return False
        sleep(step_timeout)


def wait_up(object_table_row: str, timeout=30, step_timeout=5):
    """
    Wait for UP state. The awaiting is blocking

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :param int timeout: the amount of time in seconds to wait the UP state
    :param int step_timeout: the amount of time in seconds between queries of the state
    :returns bool: True if the UP state is reached, otherwise False
    """
    return wait_state(object_table_row, HasUpState.UP, timeout=timeout, step_timeout=step_timeout)


def wait_fault(object_table_row: str, timeout=30, step_timeout=5):
    """
    Wait for FAULT state. The awaiting is blocking

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :param int timeout: the amount of time in seconds to wait the UP state
    :param int step_timeout: the amount of time in seconds between queries of the state
    :returns bool: True if the UP state is reached, otherwise False
    """
    return wait_state(object_table_row, HasUpState.FAULT, timeout=timeout, step_timeout=step_timeout)


def restart(timeout=10):
    """
    Restart NMS. NMS will be instantly restarted

    :param int timeout: timeout in seconds to get NMS restarted
    :raises NmsErrorResponseException: if NMS does not respond after restart
    :returns True: if no exceptions are thrown
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    _path = f'{_API_OBJECT_UPDATE.format("nms=0")}/command={API_RESTART_COMMAND}'
    _post(_path, data={})
    if _error_log not in ('', None) or _error_code:
        if _auto_abort_on_error:
            raise NmsErrorResponseException(f'NMS restart command unsuccessful. '
                                            f'Reason: error_code: `{_error_code}` error_log: `{_error_log}`')
        else:
            return None

    sleep(timeout)

    _post('api/object/dashboard/nms=0', {})
    if _error_log not in ('', None) or _error_code:
        raise NmsErrorResponseException('NMS is restarted but does not respond')
    return True


def find_active_device(sr_controller_table_row: str):
    """
    Get table:row of active device in desired sr_controller

    :param str sr_controller_table_row: sr_controller table:row to find active device in
    :returns str device_table_row: active device table:row or None if no active device found
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Call `connect` function first')
    if len(sr_controller_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong sr_controller table row format')
    if sr_controller_table_row.split(':')[0] != 'sr_controller':
        raise InvalidOptionsException('Wrong table name, should be sr_controller')
    path = _API_LIST_ITEMS.format(sr_controller_table_row.replace(':', '='), 'sr_teleport')
    reply = _post(path, {})
    if _error_log not in ('', None) or _error_code:
        return None
    if reply is not None:
        for sr_tp in reply:
            path = _API_LIST_ITEMS.format(f'sr_teleport:{sr_tp.get("%row")}'.replace(':', '='), 'device')
            reply = _post(path, {})
            if reply is not None:
                for dev in reply:
                    if get_param(f'device:{dev.get("%row")}', 'state') == HasUpState.UP:
                        return f'device:{dev.get("%row")}'


def wait_log_message(
        object_table_row: str,
        message=None,
        fault=True,
        info=True,
        warning=True,
        start=None,
        end=None,
        timeout=60,
        step_timeout=5
):
    """
    Wait for log message to appear in logs. If 'start' is not set, current time is used.

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :param str message: log message that is expected to be logged. If None, any message is awaited. Default is None
    :param int timeout: timeout in seconds to await for the message. Default is 60 seconds
    :param int step_timeout: step in seconds between log queries. Default is 5 seconds
    :param bool fault: if True FAULT messages are included, otherwise not. Default is True
    :param bool info: if True INFO messages are included, otherwise not. Default is True
    :param bool warning: if True WARNING messages are included, otherwise not. Default is True
    :param int start: start time since epoch to obtain logs
    :param int end: send time since epoch to obtain logs
    :returns bool: log message if the expected log message is caught, otherwise False
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    path = _API_OBJECT_LOG.format(object_table_row.replace(':', '='))
    if start is None:
        start = round(float(time()), 3)
    if end is None:
        end = start + timeout
    payload = {
        'start': start,
        'end': end,
        'fault': fault,
        'info': info,
        'warning': warning,
    }
    object_name = get_param(object_table_row, 'name')
    while True:
        reply = _post(path, payload)
        if _error_log in ('', None) and _error_code == 0:
            for rec in reply:
                if rec['na'] == object_name:
                    if message is None:
                        return f'{rec["na"]} {rec["me"]}'
                    else:
                        if rec['me'].strip() == message:
                            return f'{rec["na"]} {rec["me"].strip()}'
        else:
            raise NmsErrorResponseException(f'Cannot get logs: error_code={_error_code}, error={_error_log}')
        t = int(time())
        if timeout < t - start:
            return False
        sleep(step_timeout)


def get_params(object_table_row):
    """
    Get all the parameters and their respective values of the NMS object

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :returns dict params: a dictionary of parameters and their values returned by NMS API for the object
    :raises NmsErrorResponseException: if auto_abort_on_error is on and there is an error upon getting the parameters
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    reply = _post(_API_OBJECT_READ.format(object_table_row.replace(':', '=')), {})

    if _error_log != '' or _error_code:
        if _auto_abort_on_error:
            raise NmsErrorResponseException(f'`{object_table_row}` cannot be read. '
                                            f'Reason: error_code: `{_error_code}` error_log: `{_error_log}`')
        else:
            return None
    if reply is not None or reply != '':
        return reply
    else:
        return {}


def wait_next_tick(timeout: int = 10, step_timeout: float = 0.1) -> bool:
    """
    Wait till the next NMS tick is in place to make sure that the config is sent to controllers.

    :param int timeout: the parameter is used to terminate the waiting cycle if tick number is not updated
    :param float step_timeout: the parameter indicates how often the tick number value is requested
    :return bool: True if the tick number value is incremented, False is returned upon timeout
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    begin = int(time())
    tick_number_init = get_param('nms:0', 'tick_number')
    while True:
        tick_number = get_param('nms:0', 'tick_number')
        if tick_number > tick_number_init:
            # sleep(1)  # Still has to wait a second in order to let UHP process the new config
            return True
        t = int(time())
        if timeout < t - begin:
            return False
        sleep(step_timeout)


def wait_ticks(number=1):
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if number not in range(1, 100):
        raise InvalidOptionsException(f'Number of ticks to wait must be in range 1 - 100')
    for _ in range(number):
        if not wait_next_tick():
            return False
    return True


def get_sr_license_options(sr_license_table_row: str):
    """
    Get sr_license options as a string
    Sample output:
        'OUTR INR DVB 16AP'

    :param str sr_license_table_row: sr_license table:row to get options from
    :returns str: a string representing sr_license options
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(sr_license_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    if sr_license_table_row.split(':')[0] != 'sr_license':
        raise InvalidOptionsException('Wrong table name, should be sr_license')
    _options = ' '.join(get_param(sr_license_table_row, 'options').split())
    return _options


def get_realtime(object_table_row: str, command: str):
    """
    Get output of realtime command of an NMS object

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :param str command: realtime command
    :returns str reply: output of the command
    :raises NmsErrorResponseException: if auto_abort_on_error is on and there is an error upon getting the output
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    if object_table_row.split(':')[0] not in (_CONTROLLER, _STATION, _DEVICE):
        raise InvalidOptionsException(f'Realtime available for {_CONTROLLER}, {_STATION} and {_DEVICE}')
    if not isinstance(command, str):
        raise InvalidOptionsException('Command must be passed as a string')
    if command.lower() in _get_realtime_commands.keys():
        command = _get_realtime_commands.get(command.lower())
    else:
        command = command.lower()
    reply = _post(_API_REALTIME.format(object_table_row.replace(':', '=')), {'command': command, 'control': 0})
    if _error_log != '' or _error_code:
        if _auto_abort_on_error:
            raise NmsErrorResponseException(f'`{object_table_row}` realtime {command} cannot be read. '
                                            f'Reason: error_code: `{_error_code}` error_log: `{_error_log}`')
        else:
            return None
    if reply is not None or reply != '':
        return reply
    else:
        return ''


def set_realtime(object_table_row: str, command: str):
    """
    Send realtime command to an NMS object

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :param str command: realtime command
    :returns str reply: output of the command
    :raises NmsErrorResponseException: if auto_abort_on_error is on and there is an error upon getting the output
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    if object_table_row.split(':')[0] not in (_CONTROLLER, _STATION, _DEVICE):
        raise InvalidOptionsException(f'Realtime available for {_CONTROLLER}, {_STATION} and {_DEVICE}')
    if not isinstance(command, str):
        raise InvalidOptionsException('Command must be passed as a string')
    if command.lower() in _set_realtime_commands.keys():
        command = _set_realtime_commands.get(command.lower())
    else:
        command = command.lower()
    reply = _post(_API_REALTIME.format(object_table_row.replace(':', '=')), {'command': command, 'control': 1})
    if _error_log != '' or _error_code:
        if _auto_abort_on_error:
            raise NmsErrorResponseException(f'`{object_table_row}` realtime {command} cannot be read. '
                                            f'Reason: error_code: `{_error_code}` error_log: `{_error_log}`')
        else:
            return None
    if reply is not None or reply != '':
        return reply
    else:
        return ''


def list_items(object_table_row: str, items: str):
    """
    List all items specific to a particular table, i.e. all NMS networks
    Sample usage:
    >>> list_items('nms:0', 'network')  # equals to `/api/list/get/nms=0/list_items=network` request

    :param str object_table_row: describes the object as `<object_table>:<row>`
    :param str items: items to be listed
    :returns list items: all objects found in the `table:row` format
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    _path = _API_LIST_ITEMS.format(object_table_row.replace(':', '='), items) + '?list_vars='
    reply = _post(_path, {})
    if _error_log != '' or _error_code:
        if _auto_abort_on_error:
            raise NmsErrorResponseException(f'Cannot get {_path}'
                                            f'Reason: error_code: `{_error_code}` error_log: `{_error_log}`')
        else:
            return None
    if reply is not None or reply != '':
        # Preparing reply as a tuple containing strings of `table:row`
        return [f'{items}:{i.get("%row")}' for i in reply]
    return []


def return_all(object_table_row: str):
    """
    Forced return of all stations to initial RX controllers
    Sample usage:
    >>> return_all('bal_controller:0')

    :param str object_table_row: describes bal_controller as `bal_controller:<row>`
    :raises InvalidOptionsException: if passed object_table_row is invalid
    :raises NmsErrorResponseException: if response error_code is not None, i.e. in case if bal_controller does not exist
    :returns bool: True if command is successful, otherwise False
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    if object_table_row.split(':')[0] != 'bal_controller' and _auto_abort_on_error:
        raise InvalidOptionsException('Return_all is supported for bal_controller only')
    _path = _API_OBJECT_UPDATE.format(object_table_row.replace(':', '=')) + f'/command={API_RETURN_ALL_COMMAND}'
    reply = _post(_path, {})
    if _error_log != '' or _error_code:
        if _auto_abort_on_error:
            raise NmsErrorResponseException(f'Cannot get {_path}'
                                            f'Reason: error_code: `{_error_code}` error_log: `{_error_log}`')
        else:
            return None
    if reply is not None or reply != '':
        return True
    return False


def force_config(object_table_row: str):
    """
    Send config forcibly; can cause profile restart
    Sample usage:
    >>> force_config('controller:0')

    :param str object_table_row: describes controller or station as `<object_table_row>:<row>`
    :raises InvalidOptionsException: if passed object_table_row is invalid
    :raises NmsErrorResponseException: if response error_code is not None, i.e. in case if object does not exist
    :returns bool: True if command is successful, otherwise False
    """
    if _auto_abort_on_error and (not _cookies or not _nms_ip_port):
        raise DriverInitException('Cookies are not received yet. Call `connect` function first')
    if len(object_table_row.split(':')) != 2 and _auto_abort_on_error:
        raise InvalidOptionsException('Wrong object table row format')
    if object_table_row.split(':')[0] not in ('controller', 'station') and _auto_abort_on_error:
        raise InvalidOptionsException('Force_config is supported for controller or station only')
    if object_table_row.split(':')[0] == 'controller':
        command = API_FORCE_CONFIG_CONTROLLER_COMMAND
    else:
        command = API_FORCE_CONFIG_STATION_COMMAND
    _path = _API_OBJECT_UPDATE.format(object_table_row.replace(':', '=')) + f'/command={command}'
    reply = _post(_path, {})
    if _error_log != '' or _error_code:
        if _auto_abort_on_error:
            raise NmsErrorResponseException(f'Cannot get {_path}'
                                            f'Reason: error_code: `{_error_code}` error_log: `{_error_log}`')
        else:
            return None
    if reply is not None or reply != '':
        return True
    return False


if __name__ == '__main__':
    connect('http://10.56.24.40:8000', 'admin', '12345')
    print(return_all('bal_controller:0'))
