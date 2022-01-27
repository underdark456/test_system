from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.log_object import LogObject
from src.nms_entities.has_up_state_object import HasUpState
from src.nms_entities.paths_manager import PathsManager


class SrController(AbstractBasicObject, HasUpState, LogObject):
    """
    NMS Smart Redundancy Controller class.
    Can be used to either create a new Smart Redundancy Controller instance or manage an existing one.
    If sr_controller_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `network_id` and `sr_controller_id`

    >>> sr_ctrl = SrController(driver, 0, -1, params={'name': 'SR_CTRL'})
    >>> sr_ctrl.save()
    Instantiates a new SR controller named `SR_CTRL` in the Network ID 0.
    Applies the controller to NMS.

    >>> sr_ctrl = SrController(driver, 0, 3)
    Loads the parameters of Smart Redundancy Controller ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int network_id: ID of the parent network object
    :param int sr_controller_id: ID of the smart redundancy controller. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new smart redundancy controller is created.
                              Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the smart redundancy controller.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if smart redundancy controller ID is not found
    """

    # the parameters' names of checkboxes and dropdowns that change form
    _FIRST_QUEUE_FIELDS = [
        'check_stn',
        'check_cn',
        'check_sw_fails',
        'check_idle',
        'alert_mode',
    ]

    def __init__(self, driver: AbstractHttpDriver, network_id: int, sr_controller_id: int, params: dict = None):
        """
        Smart redundancy controller class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int network_id: ID of the parent network object
        :param int sr_controller_id: ID of the smart redundancy controller. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new smart redundancy controller is created.
                                  Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the smart redundancy controller.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if smart redundancy controller ID is not found
        """
        super().__init__(driver, network_id, sr_controller_id, params)
        self._state_fields = {
            'state': None,
            'num_state': None,

            # Controllers table
            'up_controllers': None,
            'down_tx': None,
            'down_rx': None,
            'fault_tx': None,
            'fault_rx': None,

            # Stations table
            'stn_up': None,
            'stn_down': None,
            'stn_ratio': None,
            'lowest_stn': None,
            'lowest_ctr': None,

            # Levels table
            'hub_cn_avg': None,
            'stn_cn_avg': None,
            'own_cn_avg': None,

            # Teleport table
            'cur_teleport': None,
            'tp_fail_code': None,
            'last_fail_code': None,
            'devices_up': None,
            'devices_down': None,
            'devices_idle': None,

            # Rest
            'warning': None,
            'error_code': None,
            'error_message': None,
        }

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new SR controller NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for creating a new SR controller NMS object
        """
        return PathsManager.sr_controller_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading an SR controller NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading an SR controller NMS object
        """
        return PathsManager.sr_controller_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating an SR controller NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating an SR controller NMS object
        """
        return PathsManager.sr_controller_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting an SR controller NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting an SR controller NMS object
        """
        return PathsManager.sr_controller_delete(self._driver.get_type(), self._object_id)

    def _get_log_path(self) -> str:
        """
        Private method that is used to get the path for SrController logs. The path is driver dependent.

        :returns str: full driver dependent path for getting SrController logs
        """
        return PathsManager.sr_controller_log(self._driver.get_type(), self._object_id)


    def _get_status_path(self):
        """
        Private method that returns the path for getting the status of an SrController NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the status of the existing SrController NMS object
        """
        return PathsManager.sr_controller_status(self._driver.get_type(), self._object_id)

    def get_state(self):
        """
        Get the current state of the SrController NMS object. The state parameters are the following:

            'state', 'num_state';
            'up_controllers', 'down_tx', 'down_rx', 'fault_tx', 'fault_rx';
            'stn_down', 'stn_up', 'stn_ratio', 'lowest_stn', 'lowest_ctr';
            'hub_cn_avg', 'stn_cn_avg', 'own_cn_avg';
            'cur_teleport', 'tp_fail_code', 'last_fail_code', 'devices_up', 'devices_down', 'devices_idle';
            'warning', 'error_code', 'error_message'.

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

    @classmethod
    def sr_controller_list(cls, driver: AbstractHttpDriver, network_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing SR controller ids of the network.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int network_id: the ID of the network
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the SR controllers
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.sr_controller_list(driver.get_type(), network_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get SR controllers list: error {_err}, error_code {_code}')
        _sr_ctrl_ids = set()
        for r in _res:
            _sr_ctrl_ids.add(r.get('%row'))
        return _sr_ctrl_ids

    def log_add_device_investigator(self):
        self._driver.set_path(self._get_log_path())
        self._driver.load_data()
        self._driver.add_device()

    def log_sync_add_investigator(self):
        self._driver.set_path(self._get_log_path())
        self._driver.load_data()
        self._driver.sync_add()
