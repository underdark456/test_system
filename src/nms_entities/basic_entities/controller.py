import re

from src.constants import CONTROLLER
from src.drivers.abstract_http_driver import AbstractHttpDriver, API
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.has_faults_object import HasFaults
from src.nms_entities.has_up_state_object import HasUpState
from src.nms_entities.log_object import LogObject
from src.nms_entities.paths_manager import PathsManager


class Controller(AbstractBasicObject, HasUpState, LogObject, HasFaults):
    """
    NMS Controller class.
    Can be used to either create a new Controller instance or manage an existing one.
    If controller_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `network_id` and `controller_id`

    >>> ctrl = Controller(driver, 0, -1, params={'name': 'TEST_CTRL', 'mode': 'Hubless_master', 'teleport': 'teleport:0'})
    >>> ctrl.save()
    Instantiates a new Hubless controller named `TEST_CTRL` and using a Teleport ID 0 in the Network ID 0.
    Applies the controller to NMS.

    >>> ctrl = Controller(driver, 0, 3)
    Loads the parameters of Controller ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int network_id: ID of the parent network object
    :param int controller_id: ID of the controller. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new controller is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the controller.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if controller ID is not found
    """

    # the parameters' names of checkboxes and dropdowns that change form
    _FIRST_QUEUE_FIELDS = [
        'mode',
        'teleport',
        'alert_mode',
        'binding',
        'acm_enable',
        'snmp_mode',  # changed in 4.0.0.7
        'snmp_auth',  # changed in 4.0.0.7
        'dhcp_mode',
        'dns_caching',
        'nat_enable',
        'rip_enable',
        'sntp_mode',
        'mcast_mode',
        'ctl_protect',
        'tcpa_enable',
        'sm_enable',
        'roaming_enable',
        'tdma_acm',
        'hub_tts_mode',
        'bal_enable'
    ]

    def __init__(self, driver: AbstractHttpDriver, network_id: int, controller_id: int, params: dict = None):
        """
        Controller class constructor.

        :param AbstractHttpDriver driver: an instance of `src.drivers.abstract_http_driver.AbstractHttpDriver` class
        :param int network_id: ID of the parent network object
        :param int controller_id: ID of the controller. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new controller is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the controller.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if controller ID is not found
        """
        super().__init__(driver, network_id, controller_id, params)
        # The following dictionary contains the parameters of the controller state
        # TODO: check all required state fields
        self._state_fields = {
            'state': None,
            'num_state': None,
            'a_profile_state': None,

            'stn_cn_avg': None,
            'hub_cn_avg': None,
            'rq_total': None,
            'rq_cir': None,
            'rq_for_rq': None,
            'tx_stn_cn_low': None,
            'tx_stn_cn_high': None,
            'mf_channels': None,
            'hub_own_cn': None,
            'hub_tx_level': None,
            'hub_rf_lvl': None,
            'rx_hub_cn_low': None,
            'rx_stn_cn_high': None,

            'tx_up_stations': None,
            'tx_down_stations': None,
            'tx_off_stations': None,
            'tx_fault_stations': None,

            'rx_up_stations': None,
            'rx_down_stations': None,
            'rx_off_stations': None,
            'rx_fault_stations': None,

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
    def search_by_name(cls, driver: AbstractHttpDriver, network_id: int, name: str):
        """
        Get a controller NMS object by its name.

        >>> ctrl = Controller.search_by_name(driver, 0, 'TEST_CTRL')
        Returns an instance of the controller named `TEST_CTRL` in the Network ID 0.
        The parameters are loaded from NMS.

        :param AbstractHttpDriver driver: an instance of `src.drivers.abstract_http_driver.AbstractHttpDriver` class
        :param int network_id: ID of the parent network object
        :param str name: the name of a controller to search
        :returns:
            - an instance of the found controller NMS object.
            - None - if the controller cannot be found
        """
        driver.set_path(PathsManager.controller_list(driver.get_type(), network_id))
        driver.load_data()
        result = driver.search_id_by_name({
            'web': "//a[contains(text(), '" + name + "')]",
            'api': name
        })
        controller_id = None
        if result is None:
            return None

        elif isinstance(result, str):
            # TODO: make it driver independent
            if driver.get_type() == API:
                controller_id = int(result)
            else:
                #exp = re.compile(r'.*controller=([\d]*),.*')
                exp = re.compile(r'.*controller=([\d]*)')
                res = exp.search(result)
                if res is not None:
                    controller_id = int(res.group(1))
        if controller_id is not None:
            return Controller(driver, network_id, controller_id)
        return None

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new controller NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new controller NMS object
        """
        return PathsManager.controller_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a controller NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a controller NMS object
        """
        return PathsManager.controller_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a controller NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a controller NMS object
        """
        return PathsManager.controller_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a controller NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a controller NMS object
        """
        return PathsManager.controller_delete(self._driver.get_type(), self._object_id)

    def _get_status_path(self):
        """
        Private method that returns the path for getting the status of a controller NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the status of the existing controller NMS object
        """
        return PathsManager.controller_status(self._driver.get_type(), self._object_id)

    def _get_log_path(self) -> str:
        """
        Private method that is used to get the path for Controller logs. The path is driver dependent.

        :returns str: full driver dependent path for getting Controller logs
        """
        return PathsManager.controller_log(self._driver.get_type(), self._object_id)

    def _get_graph_path(self) -> str:
        """
        Private method that is used to get the path for Controller graphs. The path is driver dependent.

        :returns str: full driver dependent path for getting Controller graphs
        """
        return PathsManager.controller_graph(self._driver.get_type(), self._object_id)

    def _get_realtime_path(self):
        """
        Private method that returns the path for getting the realtime monitor of a controller NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the Realtime monitor of the existing controller NMS object
        """
        return PathsManager.realtime(self._driver.get_type(), CONTROLLER, self._object_id)

    def _get_map_path(self):
        """
        Private method that returns the path for getting the map of a controller NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the map of the existing controller NMS object
        """
        return PathsManager.controller_map(self._driver.get_type(), self._object_id)

    def get_map(self):
        """Get map of the controller object

        :returns: None if a WEB driver is used,
                  otherwise a list of dictionaries containing objects and their coordinates
        """
        self._driver.set_path(self._get_map_path())
        self._driver.load_data()
        if self._driver.get_type() == API:
            return self._driver.get_value('list')

    def get_state(self):
        """
        Get the current state of the controller NMS object. The state parameters are the following:

            'state', 'num_state';

            'stn_cn_avg', 'hub_cn_avg', 'rq_total', 'rq_cir', 'rq_for_rq', 'tx_stn_cn_low', 'tx_stn_cn_high',
            'mf_channels', 'hub_own_cn', 'hub_tx_level', 'hub_rf_lvl', 'rx_hub_cn_low', 'rx_stn_cn_high';

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

    def get_realtime(self, command=None):
        """
        Get Realtime controller data of the passed command from NMS.
        The commands correspond to the existing show commands in UHP.

        >>> ctrl.get_realtime('show system')
        Gets the `show system` output

        :param str command: the command that is executed for getting the Realtime controller data
        :returns:
            - reply (:py:class:`str`) - a string containing the data of the response
            - None - if there is either an error or `No reply` response from NMS
        """
        self._driver.set_path(self._get_realtime_path())
        return self._driver.get_realtime(command)

    @classmethod
    def controller_list(cls, driver: AbstractHttpDriver, network_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing controllers ids of the networks.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int network_id: the ID of the network
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the controllers
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.controller_list(driver.get_type(), network_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get controllers list: error {_err}, error_code {_code}')
        _ctrl_ids = set()
        for r in _res:
            _ctrl_ids.add(r.get('%row'))
        return _ctrl_ids

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

    # def level_up_stations(self, tlc_cn_hub=15, timeout=30, step_timeout=3):
    #     """
    #     Adjust TX levels of all stations bound to the controller to get desired C/N level on the hub
    #     """
    #     ctrl_mode = self.get_param('mode')
    #     if ctrl_mode not in (
    #             ControllerModesStr.MF_HUB,
    #             ControllerModesStr.HUBLESS_MASTER,
    #             ControllerModesStr.INROUTE
    #     ):
    #         raise InvalidModeException(f'Controller mode {ctrl_mode} does not support leveling up stations')
    #     begin = int(time())
    #     while True:
    #         state = self.get_state()
    #         if state['state'] == self.UP:
    #             return True
    #         t = int(time())
    #         if timeout < t - begin:
    #             return False
    #         sleep(step_timeout)
