from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.has_faults_object import HasFaults
from src.nms_entities.has_up_state_object import HasUpState
from src.nms_entities.log_object import LogObject
from src.nms_entities.paths_manager import PathsManager


class Device(AbstractBasicObject, HasUpState, LogObject, HasFaults):
    """
    NMS Smart Redundancy Device class.
    Can be used to either create a new Smart Redundancy Device instance or manage an existing one.
    If device_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `sr_teleport_id` and `device_id`

    >>> dev = Device(driver, 0, -1, params={'name': 'DEV'})
    >>> dev.save()
    Instantiates a new SR device named `DEV` for SR Teeport ID 0.
    Applies the device to NMS.

    >>> dev = Device(driver, 0, 3)
    Loads the parameters of Smart Redundancy Device ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int sr_teleport_id: ID of the parent SR teleport object
    :param int device_id: ID of the smart redundancy device. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new smart redundancy device is created.
                              Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the smart redundancy device.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if smart redundancy device ID is not found
    """

    # the parameters' names of checkboxes and dropdowns that change form
    _FIRST_QUEUE_FIELDS = [
        'dem1_connect',
        'dem2_connect',
        'alert_mode',
    ]

    def __init__(self, driver: AbstractHttpDriver, sr_teleport_id: int, device_id: int, params: dict = None):
        """
        Smart redundancy device class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int sr_teleport_id: ID of the parent SR teleport object
        :param int device_id: ID of the smart redundancy device. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new smart redundancy device is created.
                                  Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the smart redundancy device.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if smart redundancy device ID is not found
        """
        super().__init__(driver, sr_teleport_id, device_id, params)
        self._state_fields = {
            'state': None,
            'num_state': None,

            'controller': None,
            'sr_priority': None,
            'faults': None,
            'clear_time': None,
            'last_up': None,
            'last_down': None,
            'down_times': None,
            'down_dur': None,
            'last_fault': None,
            'last_no_fault': None,
            'fault_times': None,
            'fault_dur': None,
            'last_reply': None,
            'last_lost': None,
            'lost_times': None,
            'lost_dur': None,
            
            'failed_times': None,
            'fail_time': None,
            'a_platform': None,
            'a_revision': None,
            'a_options': None,
            'a_serial': None,
            'a_old_pr_state': None,
            'a_profile_state': None,
            'a_sw_version': None,
            'a_cap_ready': None,
            'update': None,

        }

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new SR device object.
        The path is driver dependent.

        :returns str: full driver dependent path for creating a new SR device NMS object
        """
        return PathsManager.device_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading an SR device NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading an SR device NMS object
        """
        return PathsManager.device_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating an SR device NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating an SR device NMS object
        """
        return PathsManager.device_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting an SR device NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting an SR device NMS object
        """
        return PathsManager.device_delete(self._driver.get_type(), self._object_id)

    def _get_log_path(self) -> str:
        """
        Private method that is used to get the path for Device logs. The path is driver dependent.

        :returns str: full driver dependent path for getting Device logs
        """
        return PathsManager.device_log(self._driver.get_type(), self._object_id)

    def _get_status_path(self):
        """
        Private method that returns the path for getting the status of a Device NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the status of the existing Device NMS object
        """
        return PathsManager.device_status(self._driver.get_type(), self._object_id)

    def get_state(self):
        """
        Get the current state of the Device NMS object. The state parameters are the following:

            'state', 'num_state', 'controller', 'sr_priority', 'faults', 'clear_time', 'last_up', 'last_down',
            'down_times', 'down_dur', 'last_fault', 'last_no_fault', 'fault_times', 'fault_dur', 'last_reply',
            'last_lost', 'lost_times', 'lost_dur', 'failed_times', 'fail_time', 'a_platform', 'a_revision',
            'a_options', 'a_serial', 'a_old_pr_state', 'a_profile_state', 'a_sw_version', 'a_cap_ready', 'update'.

        :returns dict: a dictionary containing the key-value pairs of the Device state.
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
    def device_list(cls, driver: AbstractHttpDriver, sr_teleport_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing SR devices ids of the SR teleport.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int sr_teleport_id: the ID of the SR teleport
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the SR devices
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.device_list(driver.get_type(), sr_teleport_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get SR devices list: error {_err}, error_code {_code}')
        _dev_ids = set()
        for r in _res:
            _dev_ids.add(r.get('%row'))
        return _dev_ids

    def log_add_device_investigator(self):
        self._driver.set_path(self._get_log_path())
        self._driver.load_data()
        self._driver.add_device()

    def log_sync_add_investigator(self):
        self._driver.set_path(self._get_log_path())
        self._driver.load_data()
        self._driver.sync_add()