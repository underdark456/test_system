from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.has_up_state_object import HasUpState
from src.nms_entities.log_object import LogObject
from src.nms_entities.paths_manager import PathsManager


class SrTeleport(AbstractBasicObject, HasUpState, LogObject):
    """
    NMS Smart Redundancy Teleport class.
    Can be used to either create a new Smart Redundancy Teleport instance or manage an existing one.
    If sr_tp_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `sr_controller_id` and `sr_tp_id`

    >>> sr_tp = SrTeleport(driver, 0, -1, params={'name': 'SR_TP'})
    >>> sr_tp.save()
    Instantiates a new SR teleport named `SR_TP` for SR controller ID 0.
    Applies the teleport to NMS.

    >>> sr_tp = SrController(driver, 0, 3)
    Loads the parameters of Smart Redundancy Teleport ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int sr_controller_id: ID of the parent SR controlelr object
    :param int sr_tp_id: ID of the smart redundancy teleport. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new smart redundancy teleport is created.
                              Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the smart redundancy teleport.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if smart redundancy teleport ID is not found
    """

    # the parameters' names of checkboxes and dropdowns that change form
    _FIRST_QUEUE_FIELDS = [
        'alert_mode',
    ]

    def __init__(self, driver: AbstractHttpDriver, sr_controller_id: int, sr_tp_id: int, params: dict = None):
        """
        Smart redundancy teleport class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int sr_controller_id: ID of the parent SR controlelr object
        :param int sr_tp_id: ID of the smart redundancy teleport. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new smart redundancy teleport is created.
                                  Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the smart redundancy teleport.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if smart redundancy teleport ID is not found
        """
        super().__init__(driver, sr_controller_id, sr_tp_id, params)
        self._state_fields = {
            'state': None,
            'num_state': None,

            'devices_up': None,
            'devices_down': None,
            'devices_idle': None,
            'sr_devices_down': None,
            'sr_devices_idle': None,
        }

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new SR teleport NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for creating a new SR teleport NMS object
        """
        return PathsManager.sr_teleport_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading an SR teleport NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading an SR teleport NMS object
        """
        return PathsManager.sr_teleport_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating an SR teleport NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating an SR teleport NMS object
        """
        return PathsManager.sr_teleport_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting an SR teleport NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting an SR teleport NMS object
        """
        return PathsManager.sr_teleport_delete(self._driver.get_type(), self._object_id)

    def _get_log_path(self) -> str:
        """
        Private method that is used to get the path for SrTeleport logs. The path is driver dependent.

        :returns str: full driver dependent path for getting SrTeleport logs
        """
        return PathsManager.sr_teleport_log(self._driver.get_type(), self._object_id)

    def _get_status_path(self):
        """
        Private method that returns the path for getting the status of an SrTeleport NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the status of the existing SrTeleport NMS object
        """
        return PathsManager.sr_teleport_status(self._driver.get_type(), self._object_id)

    def get_state(self):
        """
        Get the current state of the SrTeleport NMS object. The state parameters are the following:

            'state', 'num_state', 'devices_up', 'devices_down', 'devices_idle', 'sr_devices_down', 'sr_devices_idle'.

        :returns dict: a dictionary containing the key-value pairs of the SrTeleport state.
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
    def sr_teleport_list(cls, driver: AbstractHttpDriver, sr_controller_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing SR teleport ids of the SR cpntroller.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int sr_controller_id: the ID of the SR controller
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the SR teleports
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.sr_teleport_list(driver.get_type(), sr_controller_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get SR teleports list: error {_err}, error_code {_code}')
        _sr_tp_ids = set()
        for r in _res:
            _sr_tp_ids.add(r.get('%row'))
        return _sr_tp_ids

    def log_add_device_investigator(self):
        self._driver.set_path(self._get_log_path())
        self._driver.load_data()
        self._driver.add_device()

    def log_sync_add_investigator(self):
        self._driver.set_path(self._get_log_path())
        self._driver.load_data()
        self._driver.sync_add()
