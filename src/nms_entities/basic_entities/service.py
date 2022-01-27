import re

from src.drivers.abstract_http_driver import AbstractHttpDriver, API
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager


class Service(AbstractBasicObject):
    """
    NMS Service class.
    Can be used to either create a new Service instance or manage an existing one.
    If service_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `network_id` and `service_id`.

    >>> srvc = Service(driver, 0, -1, params={'name': 'TEST_SRVC'})
    >>> srvc.save()
    Instantiates a new Service named `TEST_SRVC` the Network ID 0.
    Applies the service to NMS.

    >>> srvc = Service(driver, 0, 3)
    Loads the parameters of Service ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int network_id: ID of the parent network object
    :param int service_id: ID of the service. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new service is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the service.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if service ID is not found
    """

    @classmethod
    def search_by_name(cls, driver: AbstractHttpDriver, parent_id: int, name: str):
        """
        Get a service NMS object by its name.

        >>> ser = Service.search_by_name(driver, 0, 'TEST_SER')
        Returns an instance of the service `TEST_SER` in the Network ID 0.
        The parameters are loaded from NMS.

        :param AbstractHttpDriver driver: an instance of `src.drivers.abstract_http_driver.AbstractHttpDriver` class
        :param int parent_id: ID of the parent object
        :param str name: the name of a service to search
        :returns:
            - an instance of the found service NMS object.
            - None - if the service cannot be found
        """
        driver.set_path(PathsManager.service_list(driver.get_type(), parent_id))
        driver.load_data()
        result = driver.search_id_by_name({
            'web': "//a[contains(text(), '" + name + "')]",
            'api': name
        })
        service_id = None
        if result is None:
            return None

        elif isinstance(result, str):
            # TODO: make it driver independent
            if driver.get_type() == API:
                service_id = int(result)
            else:
                #exp = re.compile(r'.*vno=([\d]*),.*')
                exp = re.compile(r'.*service=([\d]*)')
                res = exp.search(result)
                if res is not None:
                    service_id = int(res.group(1))
        if service_id is not None:
            return Service(driver, parent_id, service_id)
        return None

    def __init__(self, driver: AbstractHttpDriver, network_id: int, service_id: int, params: dict = None):
        """
        Service class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int network_id: ID of the parent network object
        :param int service_id: ID of the service. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new service is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the service.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if service ID is not found
        """
        super().__init__(driver, network_id, service_id, params)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new service NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new service NMS object
        """
        return PathsManager.service_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a service NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a service NMS object
        """
        return PathsManager.service_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a service NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a service NMS object
        """
        return PathsManager.service_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a service NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a service NMS object
        """
        return PathsManager.service_delete(self._driver.get_type(), self._object_id)

    @classmethod
    def service_list(cls, driver: AbstractHttpDriver, network_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing service ids of the network.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int network_id: the ID of the network to get list from
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the services
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.service_list(driver.get_type(), network_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get network services list: error {_err}, error_code {_code}')
        _services_ids = set()
        for r in _res:
            _services_ids.add(r.get('%row'))
        return _services_ids
