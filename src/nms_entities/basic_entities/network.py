import re

from src.drivers.abstract_http_driver import AbstractHttpDriver, API
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.log_object import LogObject
from src.nms_entities.paths_manager import PathsManager


class Network(AbstractBasicObject, LogObject):
    """
    NMS Network class.
    Can be used to either create a new Network instance or manage an existing one.
    If network_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `nms_id` and `network_id`.

    >>> net = Network(driver, 0, -1, params={'name': 'TEST_NET'})
    >>> net.save()
    Instantiates a new Network named `TEST_NET` and using for NMS ID 0.
    Applies the network to NMS.

    >>> net = Network(driver, 0, 3)
    Load the parameters of Network ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int nms_id: ID of the parent NMS object
    :param int network_id: ID of the network. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new network is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the network.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if network ID is not found
    """

    # id of a checkboxes and dropdown lists who change form
    _FIRST_QUEUE_FIELDS = [
        'alert_mode',
    ]

    def __init__(self, driver: AbstractHttpDriver, nms_id: int, network_id: int, params: dict = None):
        """
        Network class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int nms_id: ID of the parent NMS object
        :param int network_id: ID of the network. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new network is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the network.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if network ID is not found
        """
        super().__init__(driver, nms_id, network_id, params)
        self._state_fields = {
            'up_controllers': None,
            'off_controllers': None,
            'down_controllers': None,
            'fault_controllers': None,

            'up_stations': None,
            'off_stations': None,
            'down_stations': None,
            'fault_stations': None,
            'idle_stations': None,

            'up_devices': None,
            'down_devices': None,
            'idle_devices': None,

            'traffic_scale': None,
            'level_scale': None,
            'tx_errors': None,
            'rx_errors': None,
            'hub_cn_avg': None,
            'hub_low_cn': None,
            'hub_high_cn': None,
            'stn_cn_avg': None,
            'stn_cn_low': None,
            'stn_cn_high': None,

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

    @classmethod
    def search_by_name(cls, driver: AbstractHttpDriver, nms_id: int, name: str):
        """
        Get a controller NMS object by its name.

        >>> net = Network.search_by_name(driver, 0, 'TEST_NET')
        Returns an instance of the network named `TEST_NET` in NMS ID 0.
        The parameters are loaded from NMS.

        :param AbstractHttpDriver driver: an instance of `src.drivers.abstract_http_driver.AbstractHttpDriver` class
        :param int nms_id: ID of the parent NMS object
        :param str name: the name of a network to search
        :returns:
            - an instance of the found controller NMS object.
            - None - if the controller cannot be found
        """
        driver.set_path(PathsManager.network_list(driver.get_type(), nms_id))
        driver.load_data()
        result = driver.search_id_by_name({
            'web': "//a[contains(text(), '" + name + "')]",
            'api': name
        })
        network_id = None
        if result is None:
            return None

        elif isinstance(result, str):
            # TODO: make it driver independent
            if driver.get_type() == API:
                network_id = int(result)
            else:
                exp = re.compile(r'.*network=([\d]*)')
                res = exp.search(result)
                if res is not None:
                    network_id = int(res.group(1))
        if network_id is not None:
            return Network(driver, nms_id, network_id)
        return None

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new network NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new network NMS object
        """
        return PathsManager.network_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a network NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a network NMS object
        """
        return PathsManager.network_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a network NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a network NMS object
        """
        return PathsManager.network_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a network NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a network NMS object
        """
        return PathsManager.network_delete(self._driver.get_type(), self._object_id)

    def _get_log_path(self) -> str:
        """
        Private method that is used to get the path for Network logs. The path is driver dependent.

        :returns str: full driver dependent path for getting Network logs
        """
        return PathsManager.network_log(self._driver.get_type(), self._object_id)

    def _get_status_path(self):
        """
        Private method that returns the path for getting the status of a network NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the status of the existing network NMS object
        """
        return PathsManager.network_status(self._driver.get_type(), self._object_id)

    def _get_map_path(self):
        """
        Private method that returns the path for getting the map of a network NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the map of the existing network NMS object
        """
        return PathsManager.network_map(self._driver.get_type(), self._object_id)

    def _get_graph_path(self):
        """
        Private method that returns the path for getting the graph of a network NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the graph of the existing network NMS object
        """
        return PathsManager.network_graph(self._driver.get_type(), self._object_id)

    def get_map(self):
        """Get map of the network object

        :returns: None if a WEB driver is used,
                  otherwise a list of dictionaries containing objects and their coordinates
        """
        self._driver.set_path(self._get_map_path())
        self._driver.load_data()
        if self._driver.get_type() == API:
            return self._driver.get_value('list')

    def get_state(self):
        """
        Get the current state of the network NMS object. The state parameters are the following:

            'up_controllers', 'off_controllers', 'down_controllers', 'fault_controllers',
            'up_stations', 'off_stations', 'down_stations', 'fault_stations', 'idle_stations',
            'up_devices', 'down_devices', 'idle_devices',

            'traffic_scale', 'level_scale', 'tx_errors', 'rx_errors', 'hub_cn_avg', 'hub_low_cn',
            'hub_high_cn', 'stn_cn_avg', 'stn_cn_low', 'stn_cn_high',

            'forward_rate_all', 'forward_rate1', 'forward_rate2', 'forward_rate3', 'forward_rate4', 'forward_rate5';
            'forward_rate6', 'forward_rate7',

            'return_rate_all', 'return_rate1', 'return_rate2', 'return_rate3', 'return_rate4', 'return_rate5',
            'return_rate6', and 'return_rate7'.

        :returns dict: a dictionary containing the key-value pairs of the controller state.
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

    @classmethod
    def network_list(cls, driver: AbstractHttpDriver, nms_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing networks ids of the NMS.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int nms_id: the ID of the NMS (usually always 0)
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the networks
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.network_list(driver.get_type(), nms_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get networks list: error {_err}, error_code {_code}')
        _net_ids = set()
        for r in _res:
            _net_ids.add(r.get('%row'))
        return _net_ids

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
