from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager


class User(AbstractBasicObject):
    """
    NMS User class.
    Can be used to either create a new User instance or manage an existing one.
    If user_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `group_id` and `user_id`

    >>> usr = User(driver, 0, -1, params={'name': 'TEST_USR'})
    >>> usr.save()
    Instantiates a new User named `TEST_USR` in the User group ID 0.
    Applies the user to NMS.

    >>> usr = User(driver, 0, 3)
    Loads the parameters of User ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int group_id: ID of the parent user group object
    :param int user_id: ID of the user. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new user is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the user.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if user ID is not found
    """

    def __init__(self, driver: AbstractHttpDriver, group_id: int, user_id: int, params: dict = None):
        """
        User class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int group_id: ID of the parent user group object
        :param int user_id: ID of the user. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new user is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the user.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if user ID is not found
        """
        super().__init__(driver, group_id, user_id, params)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new user NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new user NMS object
        """
        return PathsManager.user_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a user NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a user NMS object
        """
        return PathsManager.user_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a user NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a user NMS object
        """
        return PathsManager.user_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a user NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a user NMS object
        """
        return PathsManager.user_delete(self._driver.get_type(), self._object_id)

    @classmethod
    def user_list(cls, driver: AbstractHttpDriver, user_group_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing user ids of the user group.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int user_group_id: the ID of the user group
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the users
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.user_list(driver.get_type(), user_group_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get users list: error {_err}, error_code {_code}')
        _user_ids = set()
        for r in _res:
            _user_ids.add(r.get('%row'))
        return _user_ids

