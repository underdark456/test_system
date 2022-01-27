import re
from time import time, sleep
from src.constants import NEW_OBJECT_ID, API_RESTART_COMMAND, NO_ERROR
from src.drivers.abstract_http_driver import AbstractHttpDriver, API
from src.exceptions import NotImplementedException, InvalidIdException, NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.log_object import LogObject
from src.nms_entities.paths_manager import PathsManager


class Nms(AbstractBasicObject, LogObject):
    """
    NMS global config class.
    Can be used to manage the settings of NMS.
    Note: NMS cannot be neither created nor deleted.

    >>> nms = Nms(driver, 0, 0)
    Loads the parameters of NMS ID 0 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int parent_id: the parameter value is irrelevant. Used for compability with the parent interface.
    :param int nms_id: ID of the NMS.
    :param dict params: a dictionary that contains the parameters of the controller.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if NMS ID is not found
    :raises src.exceptions.InvalidIdException: if nms_id < 0
    """
    _FIRST_QUEUE_FIELDS = [
        'redundancy',
        'licensing',
        'alert_mode',
    ]

    def __init__(self, driver: AbstractHttpDriver, parent_id: int, nms_id: int, params: dict = None):
        """
        NMS class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int parent_id: the parameter value is irrelevant. Used for compatibility with the parent interface.
        :param int nms_id: ID of the NMS.
        :param dict params: a dictionary that contains the parameters of the controller.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if NMS ID is not found
        :raises src.exceptions.InvalidIdException: if nms_id < 0
        """
        if NEW_OBJECT_ID >= nms_id:
            raise InvalidIdException
        super().__init__(driver, 0, nms_id, params)

    def _get_create_path(self) -> str:
        """
        Private method that is used for compatibility with the Base abstract class.

        :raises: src.exceptions.NotImplementedException
        """
        raise NotImplementedException

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading an NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading an NMS object
        """
        return PathsManager.nms_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating an NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating an NMS object
        """
        return PathsManager.nms_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that is used for compatibility with the Base abstract class.

        :raises: src.exceptions.NotImplementedException
        """
        raise NotImplementedException

    def _get_status_path(self) -> str:
        """
        Private method that returns the path for getting status of NMS. The path is driver dependent.

        :returns str: full driver dependent path for getting status of NMS
        """
        return PathsManager.nms_status(self._driver.get_type(), self._object_id)

    def _get_log_path(self) -> str:
        """
        Private method that is used to get the path for NMS logs. The path is driver dependent.

        :returns str: full driver dependent path for getting NMS logs
        """
        return PathsManager.nms_log(self._driver.get_type(), self._object_id)

    def _get_investigator_path(self) -> str:
        """
        Private method that is used to get the path for NMS investigator.

        :returns str: full driver dependent path for getting NMS investigator
        """
        return PathsManager.nms_investigator(self._driver.get_type(), self._object_id)

    def wait_next_tick(self, timeout: int = 10, step_timeout: float = 0.1) -> bool:
        """
        Wait till the next NMS tick is in place to make sure that the config is sent to controllers.
        Currently is supported only via API driver.

        :param int timeout: the parameter is used to terminate the waiting cycle if tick number is not updated
        :param float step_timeout: the parameter indicates how often the tick number value is requested
        :return bool: True if the tick number value is incremented, False is returned upon timeout
        """
        # TODO: implement in WEB driver
        if self._driver.get_type() != API:
            raise NotImplementedException('Method is implemented only in API driver')
        begin = int(time())
        self._driver.set_path(self._get_read_path())
        self._driver.load_data()
        tick_number_init = self._driver.get_value('tick_number')
        while True:
            self._driver.load_data()
            tick_number = self._driver.get_value('tick_number')
            if tick_number > tick_number_init:
                sleep(1)  # Still has to wait a second in order to let UHP process the new config
                return True
            t = int(time())
            if timeout < t - begin:
                return False
            sleep(step_timeout)

    def wait_ticks(self, number=1):
        """
        Wait for the desired number of ticks. Currently is supported only via API driver.

        :param int number: number of ticks to wait
        :return bool: True if the expected number of ticks passed, False if there was no tick increment on any step
        """
        for _ in range(number):
            if not self.wait_next_tick():
                return False
        return True

    def restart(self, timeout=10):
        """
        Restart NMS. NMS will be instantly restarted

        :param int timeout: timeout in seconds to get NMS restarted
        :raises NmsErrorResponseException: if NMS does not respond after restart
        :returns True: if no exceptions are thrown
        """
        _path = PathsManager.nms_update(self._driver.get_type(), self._object_id)
        reply, error, error_code = self._driver.custom_post(_path, payload={'command': API_RESTART_COMMAND})
        if error_code != NO_ERROR:
            raise ValueError(error_code)
        if error != '':
            raise ValueError(error)

        sleep(timeout)

        reply, error, error_code = self._driver.custom_get('api/object/dashboard/nms=0')
        if error != '' or error_code != NO_ERROR:
            raise NmsErrorResponseException('NMS is restarted but does not respond')
        return True

    def get_version(self):
        """Get NMS version in the following format <d.d.d.dd>"""
        if self._driver.get_type() == API:
            version = self.get_param('version')
            if version is not None:
                version = re.search(r'[0-9]+.[0-9]+.[0-9]+.[0-9]+', version)
                if version is not None:
                    return version.group()
        else:
            self._driver.set_path(self._get_status_path())
            self._driver.load_data()
            return self._driver.get_nms_version()

    def log_add_device_investigator(self):
        self._driver.set_path(self._get_log_path())
        self._driver.load_data()
        self._driver.add_device()

    def log_sync_add_investigator(self):
        self._driver.set_path(self._get_log_path())
        self._driver.load_data()
        self._driver.sync_add()

    def investigator(self):
        self._driver.set_path(self._get_investigator_path())
        self._driver.load_data()
