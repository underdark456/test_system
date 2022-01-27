from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager
from src.drivers.abstract_http_driver import AbstractHttpDriver


class Alert(AbstractBasicObject):
    """
    NMS Alert class.
    Can be used to either create a new Alert instance or manage an existing one.
    If alert_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `nms_id` and 'alert_id`.

    >>> alrt = Alert(driver, 0, -1, params={'name': 'TEST_ALRT'})
    >>> alrt.save()
    Instantiates a new Alert named `TEST_ALRT` for NMS ID 0.
    Applies the Alert to NMS.

    >>> alrt = Alert(driver, 0, 3)
    Load the parameters of Alert ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int nms_id: ID of the parent NMS object
    :param int alert_id: ID of the alert. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new alert is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the alert.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if alert ID is not found
    """
    _FIRST_QUEUE_FIELDS = [
        'sound',
        'run_script',
    ]

    def __init__(self, driver: AbstractHttpDriver, nms_id: int, alert_id: int, params: dict = None):
        """
        Alert class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int nms_id: ID of the parent NMS object
        :param int alert_id: ID of the alert. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new alert is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the alert.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if alert ID is not found
        """
        super().__init__(driver, nms_id, alert_id, params)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating an alert NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new alert NMS object
        """
        return PathsManager.alert_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading an alert NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading an alert NMS object
        """
        return PathsManager.alert_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating an alert NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating an alert NMS object
        """
        return PathsManager.alert_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting an alert NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting an alert NMS object
        """
        return PathsManager.alert_delete(self._driver.get_type(), self._object_id)

    @classmethod
    def alert_list(cls, driver: AbstractHttpDriver, nms_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing alert ids of the given parent object.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int nms_id: the ID of the parent object
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the accesses
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.alert_list(driver.get_type(), nms_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get alert list: error {_err}, error_code {_code}')
        _alert_ids = set()
        for r in _res:
            _alert_ids.add(r.get('%row'))
        return _alert_ids
