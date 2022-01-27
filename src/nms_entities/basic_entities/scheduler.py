from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager


class Scheduler(AbstractBasicObject):
    """
    NMS Scheduler class.
    Can be used to either create a new Scheduler instance or manage an existing one.
    If scheduler_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `network_id` and `scheduler_id`

    >>> sch = Scheduler(driver, 0, -1, params={'name': 'TEST_SCH'})
    >>> sch.save()
    Instantiates a new Scheduler named `TEST_SCH` in the Network ID 0.
    Applies the scheduler to NMS.

    >>> sch = Scheduler(driver, 0, 3)
    Loads the Scheduler object ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int network_id: ID of the parent network object
    :param int scheduler_id: ID of the scheduler. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new scheduler is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the scheduler.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if scheduler ID is not found
    """

    def __init__(self, driver: AbstractHttpDriver, network_id: int, scheduler_id: int, params: dict = None):
        """
        Scheduler class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int network_id: ID of the parent network object
        :param int scheduler_id: ID of the scheduler. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new scheduler is created. Otherwise, the scheduler is loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the scheduler.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if scheduler ID is not found
        """
        super().__init__(driver, network_id, scheduler_id, params)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new scheduler NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new scheduler NMS object
        """
        return PathsManager.scheduler_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a scheduler NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a scheduler NMS object
        """
        return PathsManager.scheduler_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a scheduler NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a scheduler NMS object
        """
        return PathsManager.scheduler_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a scheduler NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a scheduler NMS object
        """
        return PathsManager.scheduler_delete(self._driver.get_type(), self._object_id)

    @classmethod
    def scheduler_list(cls, driver: AbstractHttpDriver, network_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing scheduler ids of the network.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int network_id: the ID of the network
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the schedulers
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.scheduler_list(driver.get_type(), network_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get schedulers list: error {_err}, error_code {_code}')
        _sch_ids = set()
        for r in _res:
            _sch_ids.add(r.get('%row'))
        return _sch_ids
