import re

from src.drivers.abstract_http_driver import AbstractHttpDriver, API
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.log_object import LogObject
from src.nms_entities.paths_manager import PathsManager


class Vno(AbstractBasicObject, LogObject):
    """
    NMS VNO class.
    Can be used to either create a new VNO instance or manage an existing one.
    If vno_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `parent_id` and `vno_id`.

    >>> vno = Vno(driver, 0, -1, params={'name': 'TEST_VNO'}, parent_type='vno')
    >>> vno.save()
    Instantiates a new Sub-VNO named `TEST_VNO` in the VNO ID 0.
    Applies the VNO to NMS.

    >>> vno = Vno(driver, 0, 3)
    Loads the parameters of VNO ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int network_id: ID of the parent network object
    :param int vno_id: ID of the VNO. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new VNO is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the VNO.
                        Initial dictionary is not changed.
    :param str parent_type: type of the parent object
    :raises src.exceptions.ObjectNotFoundException:  if VNO ID is not found
    """

    # the parameters' names of checkboxes and dropdowns that change form
    _FIRST_QUEUE_FIELDS = [
        'alert_mode',
    ]

    def __init__(self, driver: AbstractHttpDriver, network_id: int, vno_id: int, params: dict = None, parent_type=None):
        """
        VNO class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int network_id: ID of the parent network object
        :param int vno_id: ID of the VNO. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new VNO is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the VNO.
                            Initial dictionary is not changed.
        :param str parent_type: type of the parent object
        :raises src.exceptions.ObjectNotFoundException:  if VNO ID is not found
        """
        super().__init__(driver, network_id, vno_id, params, parent_type)
        self._state_fields = {
            'up_stations': None,
            'off_stations': None,
            'down_stations': None,
            'fault_stations': None,
            'idle_stations': None,

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
    def search_by_name(cls, driver: AbstractHttpDriver, parent_id: int, name: str, parent_type='network'):
        """
        Get a vno NMS object by its name.

        >>> vno = Vno.search_by_name(driver, 0, 'TEST_VNO')
        Returns an instance of the vno named `TEST_VNO` in the Network ID 0.
        The parameters are loaded from NMS.

        :param AbstractHttpDriver driver: an instance of `src.drivers.abstract_http_driver.AbstractHttpDriver` class
        :param int parent_id: ID of the parent object
        :param str name: the name of a vno to search
        :param str parent_type: type of the parent object
        :returns:
            - an instance of the found vno NMS object.
            - None - if the vno cannot be found
        """
        driver.set_path(PathsManager.vno_list(driver.get_type(), parent_id, parent_type=parent_type))
        driver.load_data()
        result = driver.search_id_by_name({
            'web': "//a[contains(text(), '" + name + "')]",
            'api': name
        })
        vno_id = None
        if result is None:
            return None

        elif isinstance(result, str):
            # TODO: make it driver independent
            if driver.get_type() == API:
                vno_id = int(result)
            else:
                #exp = re.compile(r'.*vno=([\d]*),.*')
                exp = re.compile(r'.*vno=([\d]*)')
                res = exp.search(result)
                if res is not None:
                    vno_id = int(res.group(1))
        if vno_id is not None:
            return Vno(driver, parent_id, vno_id, parent_type=parent_type)
        return None

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new VNO NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new VNO NMS object
        """
        return PathsManager.vno_create(self._driver.get_type(), self._parent_id, self._parent_type)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a VNO NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a VNO NMS object
        """
        return PathsManager.vno_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a VNO NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a VNO NMS object
        """
        return PathsManager.vno_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a VNO NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a VNO NMS object
        """
        return PathsManager.vno_delete(self._driver.get_type(), self._object_id)

    def _get_log_path(self) -> str:
        """
        Private method that is used to get the path for Vno logs. The path is driver dependent.

        :returns str: full driver dependent path for getting vno logs
        """
        return PathsManager.vno_log(self._driver.get_type(), self._object_id)

    def _get_graph_path(self) -> str:
        """
        Private method that is used to get the path for Vno graphs. The path is driver dependent.

        :returns str: full driver dependent path for getting vno graphs
        """
        return PathsManager.vno_graph(self._driver.get_type(), self._object_id)

    def _get_status_path(self):
        """
        Private method that returns the path for getting the status of a VNO NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the status of a VNO NMS object
        """
        return PathsManager.vno_status(self._driver.get_type(), self._object_id)

    def _get_map_path(self):
        """
        Private method that returns the path for getting the map of a vno NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the map of the existing vno NMS object
        """
        return PathsManager.vno_map(self._driver.get_type(), self._object_id)

    def get_map(self):
        """Get map of the vno object

        :returns: None if a WEB driver is used,
                  otherwise a list of dictionaries containing objects and their coordinates
        """
        self._driver.set_path(self._get_map_path())
        self._driver.load_data()
        if self._driver.get_type() == API:
            return self._driver.get_value('list')

    def get_state(self):
        """
        Get the current state of the VNO NMS object. The state parameters are the following:

            'up_stations', 'off_stations', 'down_stations', 'fault_stations', 'idle_stations',
            'tx_errors', 'rx_errors', 'hub_cn_avg', 'hub_low_cn', 'hub_high_cn', 'stn_cn_avg', 'stn_cn_low',
            'stn_cn_high', 'forward_rate_all', 'forward_rate1', 'forward_rate2', 'forward_rate3', 'forward_rate4',
            'forward_rate5', 'forward_rate6', 'forward_rate7', 'return_rate_all', 'return_rate1', 'return_rate2',
            'return_rate3', 'return_rate4', 'return_rate5', 'return_rate6', 'return_rate7'.

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
    def vno_list(cls, driver: AbstractHttpDriver, parent_id: int,  parent_type=None, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing vno ids of the given network.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int parent_id: the ID of the VNO
        :param parent_type: type of the parent object
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the VNOs
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.vno_list(driver.get_type(), parent_id, parent_type, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get stations list: error {_err}, error_code {_code}')
        _vno_ids = set()
        for r in _res:
            _vno_ids.add(r.get('%row'))
        return _vno_ids

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