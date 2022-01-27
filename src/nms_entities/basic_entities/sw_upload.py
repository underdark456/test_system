from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager


class SwUpload(AbstractBasicObject):
    """
    NMS SW upload class.
    Can be used to either create a new SW upload instance or manage an existing one.
    If sw_upload_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `network_id` and `sw_upload_id`.

    >>> sw = SwUpload(driver, 0, -1, params={'name': 'TEST_SW_UP'})
    >>> sw.save()
    Instantiates a new SwUpload named `TEST_SW_UP` in the Network ID 0.
    Applies the sw upload to NMS.

    >>> sw = SwUpload(driver, 0, 3)
    Loads the parameters of SW upload ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int network_id: ID of the parent network object
    :param int sw_upload_id: ID of the SW upload. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new sw upload is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the sw upload.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if sw upload ID is not found
    """

    _FIRST_QUEUE_FIELDS = []

    def __init__(self, driver: AbstractHttpDriver, network_id: int, sw_upload_id: int, params: dict = None):
        """
        SW upload class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int network_id: ID of the parent network object
        :param int sw_upload_id: ID of the SW upload. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new sw upload is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the sw upload.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if sw upload ID is not found
        """
        super().__init__(driver, network_id, sw_upload_id, params)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new sw upload NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new sw upload NMS object
        """
        return PathsManager.sw_upload_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading an sw upload NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading an sw upload NMS object
        """
        return PathsManager.sw_upload_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating an sw upload NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating an sw upload NMS object
        """
        return PathsManager.sw_upload_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting an sw upload NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting an sw upload NMS object
        """
        return PathsManager.sw_upload_delete(self._driver.get_type(), self._object_id)

    def _get_log_path(self) -> str:
        """
        Private method that is used to get the path for SW upload logs. The path is driver dependent.

        :returns str: full driver dependent path for getting SW upload logs
        """
        return PathsManager.sw_upload_log(self._driver.get_type(), self._object_id)

    @classmethod
    def sw_upload_list(cls, driver: AbstractHttpDriver, network_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing sw upload ids of the network.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int network_id: the ID of the network
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all var
        :returns tuple: a tuple containing the IDs of the sw uploads
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.sw_upload_list(driver.get_type(), network_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get sw upload list: error {_err}, error_code {_code}')
        _sw_ids = set()
        for r in _res:
            _sw_ids.add(r.get('%row'))
        return _sw_ids

    def log_add_device_investigator(self):
        self._driver.set_path(self._get_log_path())
        self._driver.load_data()
        self._driver.add_device()

    def log_sync_add_investigator(self):
        self._driver.set_path(self._get_log_path())
        self._driver.load_data()
        self._driver.sync_add()
