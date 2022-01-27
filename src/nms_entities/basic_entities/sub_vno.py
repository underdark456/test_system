from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.log_object import LogObject
from src.nms_entities.paths_manager import PathsManager


class SubVno(AbstractBasicObject, LogObject):
    """
    NMS Sub-VNO class.
    Can be used to either create a new Sub-VNO instance or manage an existing one.
    If sub_vno_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `vno_id` and `sub_vno_id`.

    >>> sub_vno = SubVno(driver, 0, -1, params={'name': 'SUB_VNO'})
    >>> sub_vno.save()
    Instantiates a new Sub-VNO named `SUB_VNO` in the VNO ID 0.
    Applies the Sub-VNO to NMS.

    >>> sub_vno = SubVno(driver, 0, 3)
    Loads the parameters of Sub-VNO ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int vno_id: ID of the parent vno object
    :param int sub_vno_id: ID of the Sub-VNO. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new Sub-VNO is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the Sub-VNO.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if Sub-VNO ID is not found
    """

    # the parameters' names of checkboxes and dropdowns that change form
    _FIRST_QUEUE_FIELDS = [
        'alert_mode',
    ]

    def __init__(self, driver: AbstractHttpDriver, vno_id: int, sub_vno_id: int, params: dict = None):
        """
        Sub-VNO class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int vno_id: ID of the parent vno object
        :param int sub_vno_id: ID of the Sub-VNO. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new Sub-VNO is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the Sub-VNO.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if Sub-VNO ID is not found
        """
        super().__init__(driver, vno_id, sub_vno_id, params)
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

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new Sub-VNO NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new Sub-VNO NMS object
        """
        return PathsManager.sub_vno_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a Sub-VNO NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a Sub-VNO NMS object
        """
        return PathsManager.sub_vno_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a Sub-VNO NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a Sub-VNO NMS object
        """
        return PathsManager.sub_vno_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a Sub-VNO NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a Sub-VNO NMS object
        """
        return PathsManager.sub_vno_delete(self._driver.get_type(), self._object_id)

    def _get_log_path(self) -> str:
        """
        Private method that is used to get the path for SubVNO logs. The path is driver dependent.

        :returns str: full driver dependent path for getting SubVNO logs
        """
        return PathsManager.sub_vno_log(self._driver.get_type(), self._object_id)

    def _get_status_path(self):
        """
        Private method that returns the path for getting the status of a SubVNO NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the status of a SubVNO NMS object
        """
        return PathsManager.sub_vno_status(self._driver.get_type(), self._object_id)

    def _get_map_path(self):
        """
        Private method that returns the path for getting the map of a SubVNO NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for getting the map of the existing SubVNO NMS object
        """
        return PathsManager.sub_vno_map(self._driver.get_type(), self._object_id)

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