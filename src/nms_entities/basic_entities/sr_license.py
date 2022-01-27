from src.drivers.abstract_http_driver import AbstractHttpDriver, API
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager


class SrLicense(AbstractBasicObject):
    """
    NMS Smart Redundancy License class.
    Can be used to either create a new Smart Redundancy License instance or manage an existing one.
    If sr_license_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `network_id` and `sr_license_id`

    >>> sr_lic = SrLicense(driver, 0, -1, params={'name': 'SR_LIC'})
    >>> sr_lic.save()
    Instantiates a new SR license named `SR_LIC` in the Network ID 0.
    Applies the license to NMS.

    >>> sr_lic = SrLicense(driver, 0, 3)
    Loads the parameters of Smart Redundancy License ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int network_id: ID of the parent network object
    :param int sr_license_id: ID of the smart redundancy license. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new smart redundancy license is created.
                              Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the smart redundancy license.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if smart redundancy license ID is not found
    """

    def __init__(self, driver: AbstractHttpDriver, network_id: int, sr_license_id: int, params: dict = None):
        """
        Smart redundancy license class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int network_id: ID of the parent network object
        :param int sr_license_id: ID of the smart redundancy license. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new smart redundancy license is created.
                                  Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the smart redundancy license.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if smart redundancy license ID is not found
        """
        super().__init__(driver, network_id, sr_license_id, params)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new SR license NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for creating a new SR license NMS object
        """
        return PathsManager.sr_license_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading an SR license NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading an SR license NMS object
        """
        return PathsManager.sr_license_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating an SR license NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating an SR license NMS object
        """
        return PathsManager.sr_license_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting an SR license NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting an SR license NMS object
        """
        return PathsManager.sr_license_delete(self._driver.get_type(), self._object_id)

    @classmethod
    def sr_license_list(cls, driver: AbstractHttpDriver, network_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing SR license ids of the network.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int network_id: the ID of the network
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the SR licenses
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.sr_license_list(driver.get_type(), network_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get SR licenses list: error {_err}, error_code {_code}')
        _sr_lic_ids = set()
        for r in _res:
            _sr_lic_ids.add(r.get('%row'))
        return _sr_lic_ids

    def get_options(self):
        self._driver.set_path(self._get_read_path())
        self._driver.load_data()
        if self._driver.get_type() == API:
            _options = ' '.join(self._driver.get_value('options').split())
            return _options
