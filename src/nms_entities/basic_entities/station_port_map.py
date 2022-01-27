from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager


class StationPortMap(AbstractBasicObject):
    """
    NMS Station Port map class.
    Can be used to either create a new Port map instance or manage an existing one.
    If port_map_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `parent_id` and `port_map_id`

    >>> pm = StationPortMap(driver, 0, -1, params={'external_port': 2048, 'internal_ip': '172.16.22.1', 'internal_port': 3675})
    >>> pm.save()
    Instantiates a new Port map for a Station ID 0.
    Applies the port map to NMS.

    >>> pm = StationPortMap(driver, 0, 3)
    Loads the parameters of Port Map ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int station_id: ID of the parent station object
    :param int port_map_id: ID of the map. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new port map is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the port map.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if port map ID is not found
    """

    def __init__(self, driver: AbstractHttpDriver, station_id: int, port_map_id: int, params: dict = None):
        """
        Port map class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int station_id: ID of the parent station object
        :param int port_map_id: ID of the map. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new port map is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the port map.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if port map ID is not found
        """
        super().__init__(driver, station_id, port_map_id, params)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new port map NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for creating a new port map NMS object
        """
        return PathsManager.station_port_map_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a port map NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a port map NMS object
        """
        return PathsManager.station_port_map_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a port map NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a port map NMS object
        """
        return PathsManager.station_port_map_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a controller route NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a controller route NMS object
        """
        return PathsManager.station_port_map_delete(self._driver.get_type(), self._object_id)

    def _get_list_path(self) -> str:
        """
        Private method that returns the path for listing controller routes in a controller.
        The path is driver dependent.

        :returns str: full driver dependent path for listing controller routes
        """
        return PathsManager.station_port_map_list(self._driver.get_type(), self._parent_id)

    @classmethod
    def port_map_list(cls, driver: AbstractHttpDriver, station_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing station port map ids of the station.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int station_id: the ID of the controller
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the routes
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.station_port_map_list(driver.get_type(), station_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get port map list: error {_err}, error_code {_code}')
        _map_ids = set()
        for r in _res:
            _map_ids.add(r.get('%row'))
        return _map_ids
