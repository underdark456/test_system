from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager


class SchTask(AbstractBasicObject):
    """
    NMS Scheduler Task class.
    Can be used to either create a new Scheduler Task instance or manage an existing one.
    If sch_task_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `station_id` and `sch_task_id`

    >>> sch_task = SchTask(driver, 0, -1, params={'name': 'TEST_SCH_TASK'})
    >>> sch_task.save()
    Instantiates a new Scheduler Task named `TEST_SCH_TASK` for the Station ID 0.
    Applies the scheduler task to NMS.

    >>> sch = SchTask(driver, 0, 3)
    Loads the Scheduler Task object ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int station_id: ID of the parent station object
    :param int sch_task_id: ID of the scheduler task. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new scheduler task is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the scheduler task.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if scheduler task ID is not found
    """

    def __init__(self, driver: AbstractHttpDriver, station_id: int, sch_task_id: int, params: dict = None):
        """
        Scheduler Task class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int station_id: ID of the parent station object
        :param int sch_task_id: ID of the scheduler task. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new scheduler task is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the scheduler task.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if scheduler task ID is not found
        """
        super().__init__(driver, station_id, sch_task_id, params)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new scheduler task NMS object.
        The path is driver dependent.

        :returns str: full driver dependent path for creating a new scheduler task NMS object
        """
        return PathsManager.sch_task_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a scheduler task NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a scheduler task NMS object
        """
        return PathsManager.sch_task_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a scheduler task NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a scheduler task NMS object
        """
        return PathsManager.sch_task_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a scheduler task NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a scheduler task NMS object
        """
        return PathsManager.sch_task_delete(self._driver.get_type(), self._object_id)

    @classmethod
    def scheduler_task_list(cls, driver: AbstractHttpDriver, station_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing scheduler task ids of the station.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int station_id: the ID of the station
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars
        :returns tuple: a tuple containing the IDs of the schedulers service
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.sch_task_list(driver.get_type(), station_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get schedulers task list: error {_err}, error_code {_code}')
        _sch_tsk_ids = set()
        for r in _res:
            _sch_tsk_ids.add(r.get('%row'))
        return _sch_tsk_ids
