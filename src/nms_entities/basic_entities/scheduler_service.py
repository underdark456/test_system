from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager


class SchService(AbstractBasicObject):
    """
    NMS Scheduler Service class.
    Can be used to either create a new Scheduler Service instance or manage an existing one.
    If sch_service_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `scheduler_id` and `sch_service_id`

    >>> schser = SchService(driver, 0, -1, params={'name': 'TEST_SCH_SERVICE'})
    >>> schser.save()
    Instantiates a new Scheduler Service named `TEST_SCH_SERVICE` for the Scheduler ID 0.
    Applies the scheduler service to NMS.

    >>> sch = SchService(driver, 0, 3)
    Loads the Scheduler Service object ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int scheduler_id: ID of the parent scheduler object
    :param int sch_service_id: ID of the scheduler service. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new scheduler service is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the scheduler service.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if scheduler range ID is not found
    """

    def __init__(self, driver: AbstractHttpDriver, scheduler_id: int, sch_service_id: int, params: dict = None):
        """
        Scheduler Service class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int scheduler_id: ID of the parent network object
        :param int sch_service_id: ID of the scheduler service. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new scheduler service is created. Otherwise, the scheduler is loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the scheduler service.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if scheduler service ID is not found
        """
        super().__init__(driver, scheduler_id, sch_service_id, params)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new scheduler service NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for creating a new scheduler service NMS object
        """
        return PathsManager.sch_service_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a scheduler service NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a scheduler service NMS object
        """
        return PathsManager.sch_service_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a scheduler service NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a scheduler service NMS object
        """
        return PathsManager.sch_service_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a scheduler service NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a scheduler service NMS object
        """
        return PathsManager.sch_service_delete(self._driver.get_type(), self._object_id)

    @classmethod
    def scheduler_service_list(cls, driver: AbstractHttpDriver, scheduler_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing scheduler service ids of the scheduler.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int scheduler_id: the ID of the scheduler
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars
        :returns tuple: a tuple containing the IDs of the schedulers service
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.sch_service_list(driver.get_type(), scheduler_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get schedulers service list: error {_err}, error_code {_code}')
        _sch_ser_ids = set()
        for r in _res:
            _sch_ser_ids.add(r.get('%row'))
        return _sch_ser_ids
