import re

from src.drivers.abstract_http_driver import AbstractHttpDriver, API
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager


class Qos(AbstractBasicObject):
    """
    NMS Qos class.
    Can be used to either create a new Qos instance or manage an existing one.
    If qos_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `network_id` and `qos_id`.

    >>> qos = Qos(driver, 0, -1, params={'name': 'test_qos'})
    Instantiates a new Qos named `test_qos` in Network ID 0.
    Applies the qos to NMS.

    >>> qos = Qos(driver, 0, 3)
    Loads the parameters of Qos ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int network_id: ID of the parent network object
    :param int qos_id: ID of the qos. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new qos is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the qos.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if qos ID is not found
    """

    _FIRST_QUEUE_FIELDS = [
        'priority',
    ]

    @classmethod
    def search_by_name(cls, driver: AbstractHttpDriver, parent_id: int, name: str):
        """
        Get a qos NMS object by its name.

        >>> qos = Qos.search_by_name(driver, 0, 'test_qos')
        Returns an instance of the qos `test_qos` in the Network ID 0.
        The parameters are loaded from NMS.

        :param AbstractHttpDriver driver: an instance of `src.drivers.abstract_http_driver.AbstractHttpDriver` class
        :param int parent_id: ID of the parent object
        :param str name: the name of a qos to search
        :returns:
            - an instance of the found qos NMS object.
            - None - if qos cannot be found
        """
        driver.set_path(PathsManager.qos_list(driver.get_type(), parent_id))
        driver.load_data()
        result = driver.search_id_by_name({
            'web': "//a[contains(text(), '" + name + "')]",
            'api': name
        })
        qos_id = None
        if result is None:
            return None

        elif isinstance(result, str):
            # TODO: make it driver independent
            if driver.get_type() == API:
                qos_id = int(result)
            else:
                #exp = re.compile(r'.*vno=([\d]*),.*')
                exp = re.compile(r'.*qos=([\d]*)')
                res = exp.search(result)
                if res is not None:
                    qos_id = int(res.group(1))
        if qos_id is not None:
            return Qos(driver, parent_id, qos_id)
        return None

    def __init__(self, driver: AbstractHttpDriver, network_id: int, qos_id: int, params: dict = None):
        """
        Qos class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int network_id: ID of the parent network object
        :param int qos_id: ID of the qos. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new qos is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the qos.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if qos ID is not found
        """
        super().__init__(driver, network_id, qos_id, params)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new qos NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new qos NMS object
        """
        return PathsManager.qos_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a qos NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a qos NMS object
        """
        return PathsManager.qos_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a qos NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a qos NMS object
        """
        return PathsManager.qos_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a qos NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a qos NMS object
        """
        return PathsManager.qos_delete(self._driver.get_type(), self._object_id)

    @classmethod
    def qos_list(cls, driver: AbstractHttpDriver, network_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing qos ids of the network.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int network_id: the ID of the network to get list from
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns set: a set containing the IDs of the qos
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.qos_list(driver.get_type(), network_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get network qos list: error {_err}, error_code {_code}')
        _qos_ids = set()
        for r in _res:
            _qos_ids.add(r.get('%row'))
        return _qos_ids
