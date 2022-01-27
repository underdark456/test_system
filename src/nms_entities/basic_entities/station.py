import re
from ipaddress import IPv4Address

from scapy.layers.inet import IP, ICMP
from scapy.sendrecv import sr

from src.constants import STATION
from src.drivers.abstract_http_driver import AbstractHttpDriver, API
from src.enum_types_constants import RouteTypesStr
from src.exceptions import NmsErrorResponseException, NotImplementedException, InvalidOptionsException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.has_faults_object import HasFaults
from src.nms_entities.has_up_state_object import HasUpState
from src.nms_entities.log_object import LogObject
from src.nms_entities.paths_manager import PathsManager


class Station(AbstractBasicObject, HasUpState, LogObject, HasFaults):
    """
    NMS Station class.
    Can be used to either create a new Station instance or manage an existing one.
    If station_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `vno_id` and `station_id`.

    >>> stn = Station(driver, 0, -1, params={'name': 'TEST_STN', 'serial': '12345'})
    >>> stn.save()
    Instantiates a new Station named `TEST_STN` with the serial number `12345` in VNO ID 0.
    Applies the station to NMS.

    >>> stn = Station(driver, 0, 3)
    Load the parameters of Station ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int vno_id: ID of the parent VNO object
    :param int station_id: ID of the station. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new station is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the station.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if station ID is not found
    """
    # the parameters' names of checkboxes and dropdowns that change form
    _FIRST_QUEUE_FIELDS = [
        'mode',
        'alert_mode',
        'snmp_mode',  # changed in 4.0.0.7
        'snmp_auth',  # changed in 4.0.0.7
        'dhcp_mode',
        'dns_caching',
        'nat_enable',
        'rip_enable',
        'sntp_mode',
        'mcast_mode',
        'tcpa_enable',
        'sm_enable',
        'poll_enable1',
        'poll_enable2',
        'lan_rx_check',
        'lan_tx_check',
        'bkp_enable',
        'auto_reboot',
    ]

    _driver = None

    @classmethod
    def search_by_name(cls, driver: AbstractHttpDriver, parent_id: int, name: str):
        """
        Get a station NMS object by its name.

        >>> stn = Station.search_by_name(driver, 0, 'TEST_STN')
        Returns an instance of the station `TEST_STN` in the VNO ID 0.
        The parameters are loaded from NMS.

        :param AbstractHttpDriver driver: an instance of `src.drivers.abstract_http_driver.AbstractHttpDriver` class
        :param int parent_id: ID of the parent object
        :param str name: the name of a station to search
        :returns:
            - an instance of the found station NMS object.
            - None - if the station cannot be found
        """
        driver.set_path(PathsManager.station_list(driver.get_type(), parent_id))
        driver.load_data()
        result = driver.search_id_by_name({
            'web': "//a[contains(text(), '" + name + "')]",
            'api': name
        })
        station_id = None
        if result is None:
            return None

        elif isinstance(result, str):
            # TODO: make it driver independent
            if driver.get_type() == API:
                station_id = int(result)
            else:
                #exp = re.compile(r'.*vno=([\d]*),.*')
                exp = re.compile(r'.*group=([\d]*)')
                res = exp.search(result)
                if res is not None:
                    station_id = int(res.group(1))
        if station_id is not None:
            return Station(driver, parent_id, station_id)
        return None

    def __init__(self, driver: AbstractHttpDriver, vno_id: int, station_id: int, params: dict = None):
        """
        Station class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int vno_id: ID of the parent VNO object
        :param int station_id: ID of the station. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new station is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the station.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if station ID is not found
        """
        super().__init__(driver, vno_id, station_id, params)
        # The following dictionary contains the parameters of the station state
        # TODO: add the rest state fields
        self._state_fields = {
            'state': None,

            'station_cn': None,
            'cn_on_hub': None,
            'station_tx': None,
            'tx_margin': None,
            'station_2_cn': None,
            'bw_rq': None,
            'rx_errors': None,

            'forward_rate_all': None,
            'forward_rate1': None,
            'forward_rate2': None,
            'forward_rate3': None,
            'forward_rate4': None,
            'forward_rate5': None,
            'forward_rate6': None,
            'forward_rate7': None,

            'return_rate_all': None,
            'return_rate1': None,
            'return_rate2': None,
            'return_rate3': None,
            'return_rate4': None,
            'return_rate5': None,
            'return_rate6': None,
            'return_rate7': None,
        }

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new station NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new station NMS object
        """
        return PathsManager.station_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a station NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a station NMS object
        """
        return PathsManager.station_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a station NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a station NMS object
        """
        return PathsManager.station_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a station NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a station NMS object
        """
        return PathsManager.station_delete(self._driver.get_type(), self._object_id)

    def _get_log_path(self) -> str:
        """
        Private method that is used to get the path for Station logs. The path is driver dependent.

        :returns str: full driver dependent path for getting Station logs
        """
        return PathsManager.station_log(self._driver.get_type(), self._object_id)

    def _get_graph_path(self) -> str:
        """
        Private method that is used to get the path for Station graphs. The path is driver dependent.

        :returns str: full driver dependent path for getting Station graphs
        """
        return PathsManager.station_graph(self._driver.get_type(), self._object_id)

    def _get_status_path(self):
        """
        Private method that returns the path for getting the status of a station NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the status of a station NMS object
        """
        return PathsManager.station_status(self._driver.get_type(), self._object_id)

    def _get_realtime_path(self):
        """
        Private method that returns the path for getting the realtime monitor of a station NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the Realtime monitor of the existing station NMS object
        """
        return PathsManager.realtime(self._driver.get_type(), STATION, self._object_id)

    def _get_map_path(self):
        """
        Private method that returns the path for getting the map of a station NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the map of the existing station NMS object
        """
        return PathsManager.station_map(self._driver.get_type(), self._object_id)

    def get_map(self):
        """Get map of the station object

        :returns: None if a WEB driver is used,
                  otherwise a list of dictionaries containing objects and their coordinates
        """
        self._driver.set_path(self._get_map_path())
        self._driver.load_data()
        if self._driver.get_type() == API:
            return self._driver.get_value('list')

    def get_state(self):
        """
        Get the current state of the station NMS object. The state parameters are the following:

            'state';

            'station_cn', 'cn_on_hub', 'station_tx', 'tx_margin', 'station_2_cn', 'bw_rq', 'rx_errors';

            'forward_rate_all', 'forward_rate1', 'forward_rate2', 'forward_rate3', 'forward_rate4',
            'forward_rate5', 'forward_rate6', 'forward_rate7';

            'return_rate_all', 'return_rate1', 'return_rate2', 'return_rate3', 'return_rate4', 'return_rate5',
            'return_rate6', and 'return_rate7'.

        :returns dict: a dictionary containing the key-value pairs of the station state.
        """
        self._driver.set_path(self._get_status_path())
        self._driver.load_data()
        for field in self._state_fields.keys():
            state = self._driver.get_value(field)
            if str == type(state):
                self._state_fields[field] = state.strip()
            else:
                self._state_fields[field] = state
        return self._state_fields.copy()

    def check_station(self):
        if self.wait_up():
            if self.ping():
                return True
        return False

    def ping(self, stn_ip_address=None, requests=5):
        if stn_ip_address is None:
            for route in self.get_routes():
                if route.get('type') == RouteTypesStr.IP_ADDRESS:
                    stn_ip_address = route.get('ip')
                    break
            else:
                raise InvalidOptionsException('Station IP address neither provided nor cannot be determined')
        # Make sure that stn_ip_address is a valid IP address
        try:
            IPv4Address(stn_ip_address)
        except ValueError:
            raise InvalidOptionsException('Station IP address is not a valid IPv4 address')
        counter = 0
        for i in range(requests):
            ans, unans = sr(IP(dst=stn_ip_address) / ICMP(), timeout=2, verbose=False)
            if len(ans) == 1:
                counter += 1
        if counter == requests:
            return True
        return False

    def get_routes(self):
        """
        Get a list of station routes

        :raises NotImplementedException: if driver is not API
        :returns list _res: a list of dictionaries containing all station routes
        """
        if self._driver.get_type() != API:
            raise NotImplementedException('Method is currently implemented in API only')
        _path = PathsManager.station_route_list(self._driver.get_type(), self._object_id)
        _res, _err, _code = self._driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get station routes: error {_err}, error_code {_code}')
        return _res

    def get_realtime(self, command=None):
        """
        Get Realtime station data of the passed command from NMS.
        The commands correspond to the existing show commands in UHP.

        >>> stn.get_realtime('show system')
        Gets the `show system` output

        :param str command: the command that is executed for getting the Realtime station data
        :returns:
            - reply (:py:class:`str`) - a string containing the data of the response
            - None - if there is either an error or `No reply` response from NMS
        """
        self._driver.set_path(self._get_realtime_path())
        return self._driver.get_realtime(command)

    @classmethod
    def station_list(cls, driver: AbstractHttpDriver, vno_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing station ids of the given VNO.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int vno_id: the ID of the VNO
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the stations
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.station_list(driver.get_type(), vno_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get stations list: error {_err}, error_code {_code}')
        _st_ids = set()
        for r in _res:
            _st_ids.add(r.get('%row'))
        return _st_ids

    def log_add_device_investigator(self):
        self._driver.set_path(self._get_log_path())
        self._driver.load_data()
        self._driver.add_device()

    def log_sync_add_investigator(self):
        self._driver.set_path(self._get_log_path())
        self._driver.load_data()
        self._driver.sync_add()

    def graph_add_device_investigator(self):
        self._driver.set_path(self._get_graph_path())
        self._driver.load_data()
        self._driver.add_device()

    def graph_sync_add_investigator(self):
        self._driver.set_path(self._get_graph_path())
        self._driver.load_data()
        self._driver.sync_add()