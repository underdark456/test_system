from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.has_up_state_object import HasUpState
from src.nms_entities.log_object import LogObject
from src.nms_entities.paths_manager import PathsManager


class BalController(AbstractBasicObject, HasUpState, LogObject):
    """
    NMS Balance Controller class.
    Can be used to either create a new Balance Controller instance or manage an existing one.
    If bal_controller_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `network_id` and `bal_controller_id`

    >>> bal_ctrl = BalController(driver, 0, -1, params={'name': 'BAL_CTRL'})
    >>> bal_ctrl.save()
    Instantiates a new balance controller named `BAL_CTRL` in the Network ID 0.
    Applies the controller to NMS.

    >>> bal_ctrl = BalController(driver, 0, 3)
    Loads the parameters of Balance Controller ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int network_id: ID of the parent network object
    :param int bal_controller_id: ID of the balance controller. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new balance controller is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the balance controller.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if balance controller ID is not found
    """

    # the parameters' names of checkboxes and dropdowns that change form
    _FIRST_QUEUE_FIELDS = [
        'free_down'
    ]

    def __init__(self, driver: AbstractHttpDriver, network_id: int, bal_controller_id: int, params: dict = None):
        """
        Balance controller class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int network_id: ID of the parent network object
        :param int bal_controller_id: ID of the balance controller. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new balance controller is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the balance controller.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if balance controller ID is not found
        """
        super().__init__(driver, network_id, bal_controller_id, params)
        # The following dictionary contains the parameters of the controller state
        self._state_fields = {
            'state': None,
            'num_state': None,

            'cur_down_sw': None,
            'cur_level_sw': None,
            'cur_load_sw': None,
            'down_sw': None,
            'level_sw': None,
            'load_sw': None,
            'ch1_id': None,
            'ch2_id': None,
            'ch3_id': None,
            'ch4_id': None,
            'ch1_bw': None,
            'ch2_bw': None,
            'ch3_bw': None,
            'ch4_bw': None,
            'ch1_max': None,
            'ch2_max': None,
            'ch3_max': None,
            'ch4_max': None,
            'ch1_load': None,
            'ch2_load': None,
            'ch3_load': None,
            'ch4_load': None,
            'clear_time': None,
        }

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new balance controller NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for creating a new balance controller NMS object
        """
        return PathsManager.bal_controller_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a balance controller NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a controller NMS object
        """
        return PathsManager.bal_controller_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a BalController NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a BalController NMS object
        """
        return PathsManager.bal_controller_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a BalController NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a BalController NMS object
        """
        return PathsManager.bal_controller_delete(self._driver.get_type(), self._object_id)

    def _get_log_path(self) -> str:
        """
        Private method that is used to get the path for BalController logs. The path is driver dependent.

        :returns str: full driver dependent path for getting BalController logs
        """
        return PathsManager.bal_controller_log(self._driver.get_type(), self._object_id)

    def _get_status_path(self):
        """
        Private method that returns the path for getting the status of an BalController NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the status of the existing BalController NMS object
        """
        return PathsManager.bal_controller_status(self._driver.get_type(), self._object_id)

    @classmethod
    def bal_controller_list(cls, driver: AbstractHttpDriver, network_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing balance controller ids of the network.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int network_id: the ID of the network
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the balance controllers
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.bal_controller_list(driver.get_type(), network_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get balance controller list: error {_err}, error_code {_code}')
        _bal_ctrl_ids = set()
        for r in _res:
            _bal_ctrl_ids.add(r.get('%row'))
        return _bal_ctrl_ids

    def get_state(self):
        """
        Get the current state of the BalController NMS object. The state parameters are the following:

            'state';

            'cur_down_sw', 'cur_level_sw', 'cur_load_sw', 'down_sw', 'level_sw', 'load_sw',
            'ch1_id', 'ch2_id', 'ch3_id', 'ch4_id', 'ch1_bw', 'ch2_bw', 'ch3_bw', 'ch4_bw',
            'ch1_max', 'ch2_max', 'ch3_max', 'ch4_max', 'ch1_load', 'ch2_load', 'ch3_load', 'ch4_load', 'clear_time'

        :returns dict: a dictionary containing the key-value pairs of the SrController state.
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

    def log_add_device_investigator(self):
        self._driver.set_path(self._get_log_path())
        self._driver.load_data()
        self._driver.add_device()

    def log_sync_add_investigator(self):
        self._driver.set_path(self._get_log_path())
        self._driver.load_data()
        self._driver.sync_add()
