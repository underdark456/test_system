from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager


class ControllerRoute(AbstractBasicObject):
    """
    NMS Controller routing class.
    Can be used to either create a new Controller route instance or manage an existing one.
    If route_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `controller_id` and `route_id`

    >>> rt = ControllerRoute(driver, 0, -1, params={'type': 'Static_route', 'service': 'service:0'})
    >>> rt.save()
    Instantiates a new Controller route of type `Static_route` and service ID 0 for the Controller ID 0.
    The rest parameters are default. Applies the route to NMS.

    >>> rt = ControllerRoute(driver, 0, 3)
    Loads the parameters of Controller route ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int controller_id: ID of the parent controller object
    :param int route_id: ID of the route. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new controller route is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the controller route.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if controller route ID is not found
    """
    # the parameters' names of checkboxes and dropdowns that change form
    _FIRST_QUEUE_FIELDS = [
        'type',
        'override_vlan'
    ]

    def __init__(self, driver: AbstractHttpDriver, controller_id: int, route_id: int, params: dict = None):
        """
        Controller route class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int controller_id: ID of the parent controller object
        :param int route_id: ID of the route. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new controller route is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the controller route.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if controller route ID is not found
        """
        super().__init__(driver, controller_id, route_id, params)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new controller route NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for creating a new controller route NMS object
        """
        return PathsManager.controller_route_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a controller route NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a controller route NMS object
        """
        return PathsManager.controller_route_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a controller route NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a controller route NMS object
        """
        return PathsManager.controller_route_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a controller route NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a controller route NMS object
        """
        return PathsManager.controller_route_delete(self._driver.get_type(), self._object_id)

    def _get_list_path(self) -> str:
        """
        Private method that returns the path for listing controller routes in a controller.
        The path is driver dependent.

        :returns str: full driver dependent path for listing controller routes
        """
        return PathsManager.controller_route_list(self._driver.get_type(), self._parent_id)

    @classmethod
    def controller_route_list(cls, driver: AbstractHttpDriver, controller_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing controller routes ids of the controller.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int controller_id: the ID of the controller
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the routes
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.controller_route_list(driver.get_type(), controller_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get controllers list: error {_err}, error_code {_code}')
        _routes_ids = set()
        for r in _res:
            _routes_ids.add(r.get('%row'))
        return _routes_ids
