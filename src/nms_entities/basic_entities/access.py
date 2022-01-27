from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager
from src.drivers.abstract_http_driver import AbstractHttpDriver


class Access(AbstractBasicObject):
    """
    NMS Access class.
    Can be used to either create a new Access instance or manage an existing one.
    If access_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `parent_id` and 'access_id`.

    >>> acc = Access(driver, 0, -1, params={'name': 'TEST_ACC'}, parent_type='controller')
    >>> acc.save()
    Instantiates a new Access named `TEST_ACC` in Controller ID 0.
    Applies the Access to NMS.

    >>> acc = Access(driver, 0, 3)
    Load the parameters of Access ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int nms_id: ID of the parent NMS object
    :param int access_id: ID of the access. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new access is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the access.
                        Initial dictionary is not changed.
    :param str parent_type: type of the parent object
    :raises src.exceptions.ObjectNotFoundException:  if access ID is not found
    """
    def __init__(self, driver: AbstractHttpDriver, nms_id: int, access_id: int, params: dict = None, parent_type=None):
        """
        Access class constructor.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int nms_id: ID of the parent NMS object
    :param int access_id: ID of the access. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new access is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the access.
                        Initial dictionary is not changed.
    :param str parent_type: type of the parent object
    :raises src.exceptions.ObjectNotFoundException:  if access ID is not found
        """
        super().__init__(driver, nms_id, access_id, params, parent_type)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating an access NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new access NMS object
        """
        return PathsManager.access_create(self._driver.get_type(), self._parent_id, self._parent_type)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading an access NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading an access NMS object
        """
        return PathsManager.access_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating an access NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating an access NMS object
        """
        return PathsManager.access_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting an access NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting an access NMS object
        """
        return PathsManager.access_delete(self._driver.get_type(), self._object_id)

    @classmethod
    def access_list(cls, driver: AbstractHttpDriver, parent_id: int, parent_type=None, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing access ids of the given parent object.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int parent_id: the ID of the parent object
        :param parent_type: type of the parent object
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the accesses
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.access_list(driver.get_type(), parent_id, parent_type, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get access list: error {_err}, error_code {_code}')
        _acc_ids = set()
        for r in _res:
            _acc_ids.add(r.get('%row'))
        return _acc_ids
