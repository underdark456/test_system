import re

from src.drivers.abstract_http_driver import AbstractHttpDriver, API
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager


class UserGroup(AbstractBasicObject):
    """
    NMS User groups class.
    Can be used to either create a new User groups instance or manage an existing one.
    If group_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `parent_id` and `group_id`

    >>> grp = UserGroup(driver, 0, -1, params={'name': 'TEST_GRP'}, parent_type='network')
    >>> grp.save()
    Instantiates a new UserGroup named `TEST_GRP` in Network ID 0.
    Applies the User group to NMS.

    >>> grp = UserGroup(driver, 0, 3)
    Loads the parameters of User group ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int nms_id: ID of the parent NMS object
    :param int group_id: ID of the group. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new User group is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the group.
                        Initial dictionary is not changed.
    :param str parent_type: type of the parent object
    :raises src.exceptions.ObjectNotFoundException:  if group ID is not found
    """

    @classmethod
    def search_by_name(cls, driver: AbstractHttpDriver, parent_id: int, name: str, parent_type='network'):
        """
        Get a user group NMS object by its name.

        >>> group = UserGroup.search_by_name(driver, 0, 'TEST_GROUP')
        Returns an instance of the user group named `TEST_GROUP` in the Network ID 0.
        The parameters are loaded from NMS.

        :param AbstractHttpDriver driver: an instance of `src.drivers.abstract_http_driver.AbstractHttpDriver` class
        :param int parent_id: ID of the parent object
        :param str name: the name of a user group to search
        :param str parent_type: type of the parent object
        :returns:
            - an instance of the found user group NMS object.
            - None - if the user group cannot be found
        """
        driver.set_path(PathsManager.group_list(driver.get_type(), parent_id, parent_type=parent_type))
        driver.load_data()
        result = driver.search_id_by_name({
            'web': "//a[contains(text(), '" + name + "')]",
            'api': name
        })
        group_id = None
        if result is None:
            return None

        elif isinstance(result, str):
            # TODO: make it driver independent
            if driver.get_type() == API:
                group_id = int(result)
            else:
                #exp = re.compile(r'.*vno=([\d]*),.*')
                exp = re.compile(r'.*group=([\d]*)')
                res = exp.search(result)
                if res is not None:
                    group_id = int(res.group(1))
        if group_id is not None:
            return UserGroup(driver, parent_id, group_id, parent_type=parent_type)
        return None

    def __init__(self, driver: AbstractHttpDriver, nms_id: int, group_id: int, params: dict = None, parent_type=None):
        """
        User group class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int nms_id: ID of the parent NMS object
        :param int group_id: ID of the group. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new User group is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the group.
                            Initial dictionary is not changed.
        :param str parent_type: type of the parent object
        :raises src.exceptions.ObjectNotFoundException:  if group ID is not found
        """
        super().__init__(driver, nms_id, group_id, params, parent_type)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new user group NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new user group NMS object
        """
        return PathsManager.group_create(self._driver.get_type(), self._parent_id, self._parent_type)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a user group NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a user group NMS object
        """
        return PathsManager.group_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a user group NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a user group NMS object
        """
        return PathsManager.group_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a user group NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a user group NMS object
        """
        return PathsManager.group_delete(self._driver.get_type(), self._object_id)

    @classmethod
    def user_group_list(cls, driver: AbstractHttpDriver, parent_id: int, parent_type=None, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing user group ids of the given parent object.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int parent_id: the ID of the parent object
        :param parent_type: type of the parent object
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all
        :returns tuple: a tuple containing the IDs of the user groups
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.group_list(driver.get_type(), parent_id, parent_type, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get user group list: error {_err}, error_code {_code}')
        _group_ids = set()
        for r in _res:
            _group_ids.add(r.get('%row'))
        return _group_ids

