import re

from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager
from src.drivers.abstract_http_driver import AbstractHttpDriver, API


class Shaper(AbstractBasicObject):
    """
    NMS Shaper class.
    Can be used to either create a new Shaper instance or manage an existing one.
    If shaper_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `network_id` and `shaper_id`.

    >>> shpr = Shaper(driver, 0, -1, params={'name': 'TEST_SHPR'})
    >>> shpr.save()
    Instantiates a new Hubless controller named `TEST_SHPR` and using a Teleport ID 0 in the Network ID 0.
    Applies the shaper to NMS.

    >>> shpr = Shaper(driver, 0, 3)
    Loads the parameters of Shaper ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int network_id: ID of the parent network object
    :param int shaper_id: ID of the shaper. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new shaper is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the shaper.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if shaper ID is not found
    """

    @classmethod
    def search_by_name(cls, driver: AbstractHttpDriver, parent_id: int, name: str):
        """
        Get a shaper NMS object by its name.

        >>> shp = Shaper.search_by_name(driver, 0, 'TEST_SHP')
        Returns an instance of the shaper named `TEST_SHP` in the Network ID 0.
        The parameters are loaded from NMS.

        :param AbstractHttpDriver driver: an instance of `src.drivers.abstract_http_driver.AbstractHttpDriver` class
        :param int parent_id: ID of the parent object
        :param str name: the name of a shaper to search
        :returns:
            - an instance of the found shaper NMS object.
            - None - if the shaper cannot be found
        """
        driver.set_path(PathsManager.shaper_list(driver.get_type(), parent_id))
        driver.load_data()
        result = driver.search_id_by_name({
            'web': "//a[contains(text(), '" + name + "')]",
            'api': name
        })
        shaper_id = None
        if result is None:
            return None

        elif isinstance(result, str):
            # TODO: make it driver independent
            if driver.get_type() == API:
                shaper_id = int(result)
            else:
                #exp = re.compile(r'.*vno=([\d]*),.*')
                exp = re.compile(r'.*group=([\d]*)')
                res = exp.search(result)
                if res is not None:
                    shaper_id = int(res.group(1))
        if shaper_id is not None:
            return Shaper(driver, parent_id, shaper_id)
        return None

    def __init__(self, driver: AbstractHttpDriver, network_id: int, shaper_id: int, params: dict = None, parent_type=None):
        """
        Shaper class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int network_id: ID of the parent network object
        :param int shaper_id: ID of the shaper. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new shaper is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the shaper.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if shaper ID is not found
        """
        super().__init__(driver, network_id, shaper_id, params, parent_type)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new shaper NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new shaper NMS object
        """
        return PathsManager.shaper_create(self._driver.get_type(), self._parent_id, self._parent_type)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a shaper NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a shaper NMS object
        """
        return PathsManager.shaper_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a shaper NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a shaper NMS object
        """
        return PathsManager.shaper_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a shaper NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a shaper NMS object
        """
        return PathsManager.shaper_delete(self._driver.get_type(), self._object_id)

    @classmethod
    def shaper_list(cls, driver: AbstractHttpDriver, network_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing shaper ids of the network.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int network_id: the ID of the station
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all var
        :returns tuple: a tuple containing the IDs of the shapers
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.shaper_list(driver.get_type(), network_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get shapers list: error {_err}, error_code {_code}')
        _shaper_ids = set()
        for r in _res:
            _shaper_ids.add(r.get('%row'))
        return _shaper_ids
