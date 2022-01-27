from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager


class Server(AbstractBasicObject):
    """
    NMS Server class.
    Can be used to either create a new Server instance or manage an existing one.
    If server_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `network_id` and `server_id`

    >>> server = Server(driver, 0, -1, params={'name': 'TEST_SRV')
    >>> server.save()
    Instantiates a new Server named `TEST_SRVH` in the Network ID 0.
    Applies the server to NMS.

    >>> server = Server(driver, 0, 3)
    Loads the parameters of Server ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int nms_id: ID of the parent nms object
    :param int server_id: ID of the server. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new server is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the server.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if server ID is not found
    """

    def __init__(self, driver: AbstractHttpDriver, nms_id: int, server_id: int, params: dict = None):
        """
        Server class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int nms_id: ID of the parent nms object
        :param int server_id: ID of the server. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new server is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the server.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if server ID is not found
        """
        super().__init__(driver, nms_id, server_id, params)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new server NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new server NMS object
        """
        return PathsManager.server_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a server NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a server NMS object
        """
        return PathsManager.server_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a server NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a server NMS object
        """
        return PathsManager.server_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a server NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a server NMS object
        """
        return PathsManager.server_delete(self._driver.get_type(), self._object_id)

    @classmethod
    def server_list(cls, driver: AbstractHttpDriver, nms_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing server ids of the given parent object.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int nms_id: the ID of the parent object
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the servers
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.server_list(driver.get_type(), nms_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get server list: error {_err}, error_code {_code}')
        _server_ids = set()
        for r in _res:
            _server_ids.add(r.get('%row'))
        return _server_ids
