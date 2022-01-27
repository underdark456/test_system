from abc import ABC, abstractmethod

from src.constants import NEW_OBJECT_ID
from src.drivers.abstract_http_driver import API, AbstractHttpDriver
from src.exceptions import InvalidIdException


class AbstractBasicObject(ABC):
    """
    Base class of NMS entities. Encapsulates CRUD operations for various drivers.
    Can be used to either create a new Entity instance or manage an existing one.
    If object_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `parent_id` and `object_id`

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int parent_id: ID of the parent object
    :param int object_id: ID of the object. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new object is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the object.
                        Initial dictionary is not changed.
    :param str parent_type: type of the parent object
    :raises src.exceptions.ObjectNotFoundException:  if object ID is not found
    """

    # ids of checkboxes and dropdowns that change form
    _FIRST_QUEUE_FIELDS = []

    def __init__(self, driver: AbstractHttpDriver, parent_id: int, object_id: int, params: dict = None, parent_type=None):
        """
        Base class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int parent_id: ID of the parent object
        :param int object_id: ID of the object. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new object is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the object.
                            Initial dictionary is not changed.
        :param str parent_type: type of the parent object
        :raises src.exceptions.ObjectNotFoundException:  if object ID is not found
        """
        self._driver = driver
        if params is None:
            _params = {}
        else:
            _params = params.copy()
        self._parent_id = parent_id
        self._parent_type = parent_type
        self._object_id = object_id
        self._params = _params
        if not self._is_new() and 0 != len(self._params):
            self.load()

    @classmethod
    def create(cls, driver: AbstractHttpDriver, parent_id: int, params: dict = None, parent_type=None):
        """
        Create a new object. Internally the class constructor is called,
        the parameters are sent to NMS, and the instance of object is returned.

        :param AbstractHttpDriver driver: an instance of `src.drivers.abstract_http_driver.AbstractHttpDriver` class
        :param int parent_id: ID of the parent object
        :param dict params: a dictionary that contains the parameters of the object
        :param str parent_type: type of the parent object
        :returns AbstractBasicObject obj: an instance of the class
        """
        return cls._apply_params(driver, parent_id, NEW_OBJECT_ID, params, parent_type)

    @classmethod
    def update(cls, driver: AbstractHttpDriver, parent_id: int, object_id: int, params: dict = None):
        """
        Update an existing object. Internally the parameters are sent to NMS,
        and the instance of object is returned.

        :param AbstractHttpDriver driver: an instance of `src.drivers.abstract_http_driver.AbstractHttpDriver` class
        :param int parent_id: ID of the parent object
        :param int object_id: ID of the object to update
        :param dict params: a dictionary that contains the parameters of the object
        :returns AbstractBasicObject obj: an instance of the class
        """
        # return cls._apply_params(driver, parent_id, object_id, params)
        # The above approach does not work as it loads the parameters from NMS and replaces the params
        # values with the loaded ones.

        # c = cls._apply_params(driver, parent_id, object_id, params)

        c = cls(driver, parent_id, object_id)
        c.send_params(params)
        return c

    @classmethod
    def _apply_params(cls, driver, parent_id, object_id, params, parent_type=None):
        """
        Private class method that is used to create or update objects. Do not call it directly, instead call `create`
        or `update` methods of the base class.

        :param AbstractHttpDriver driver: an instance of `src.drivers.abstract_http_driver.AbstractHttpDriver` class
        :param int parent_id: ID of the parent object
        :param int object_id: ID of the object
        :param dict params: a dictionary that contains the parameters of the object
        :returns AbstractBasicObject obj: an instance of the class
        """
        if API == driver.get_type():
            if params is None:
                params = {}
            # TODO: get rid of inconsistent number of arguments
            if parent_type is not None:
                c = cls(driver, parent_id, object_id, params, parent_type)
            else:
                c = cls(driver, parent_id, object_id, params)
            c.save()
        else:
            first_params, params = cls._prepare_fields(params)
            # TODO: get rid of inconsistent number of arguments
            if parent_type is not None:
                c = cls(driver, parent_id, object_id, params, parent_type)
            else:
                c = cls(driver, parent_id, object_id, params)
            for field, value in first_params.items():
                c.set_param(field, value)
            c.save()
        return c

    @classmethod
    def _prepare_fields(cls, params):
        """
        Private class method that is used to get the parameters that represent checkboxes and dropdowns
        in NMS WEB interface. Splits the parameters into two dictionaries. The first one is used by the web driver
        to check all the checkboxes and apply the dropdowns that add additional fields to the interface.

        :param dict params: the parameters passed upon creating or updating an object
        :returns tuple: the tuple contains two dictionaries `first_params` and `params`
        """
        first_params = {}
        if params is not None:
            params = params.copy()
        else:
            params = {}

        for field in cls._FIRST_QUEUE_FIELDS:
            if field in params:
                first_params[field] = params[field]
                del params[field]
        return first_params, params

    @abstractmethod
    def _get_create_path(self) -> str:
        """
        Abstract method that returns the path for creating an NMS object. The path is driver dependent.
        Redefine the method in the child class.
        """
        pass

    @abstractmethod
    def _get_update_path(self) -> str:
        """
        Abstract method that returns the path for updating an NMS object. The path is driver dependent.
        Redefine the method in the child class.
        """
        pass

    @abstractmethod
    def _get_read_path(self) -> str:
        """
        Abstract method that returns the path for reading an NMS object. The path is driver dependent.
        Redefine the method in the child class.
        """
        pass

    @abstractmethod
    def _get_delete_path(self) -> str:
        """
        Abstract method that returns the path for deleting an NMS object. The path is driver dependent.
        Redefine the method in the child class.
        """
        pass

    def get_id(self):
        """
        Get ID of the object.

        :returns:
            - self._object_id (:py:class:`int`) - object ID
            - None - if the controller cannot be found
        """
        if NEW_OBJECT_ID == self._object_id:
            return None
        return self._object_id

    def set_param(self, param_name: str, param_value: any):
        """
        Set the passed parameter value to the object.

        :param str param_name: the parameter name to set
        :param any param_value: the parameter value to set
        """
        self._params[param_name] = param_value
        self._set_send_context()
        self._driver.set_value(param_name, param_value)

    def set_params(self, params: dict):
        """
        Set the multiple passed parameter values to the object.

        :param dict params: a dictionary containing parameters and their respective values
        """
        self._set_send_context()
        for param_name, param_value in params.items():
            self._params[param_name] = param_value
            self._driver.set_value(param_name, param_value)

    def get_param(self, param_name: str):
        """
        Get a parameter value by its name.

        :param str param_name: the name of the parameter to get
        :returns:
            - param_value (str) - a corresponding value of the passed parameter
            - None - if the passed parameter does not exist for the given object
        """
        self._params[param_name] = None
        if self._get_read_path() != self._driver.get_current_path():
            self.load()
        else:
            for _param_name in self._params.keys():
                self.read_param(_param_name)
        return self._params[param_name]

    def send_param(self, param_name: str, param_value: any):
        """
        Method applies the passed parameter value to an object and sends it to NMS.
        Can be used to update the existing object.

        :param str param_name: the name of the parameter to apply
        :param any param_value: the value of the parameter to apply
         """
        self._params[param_name] = param_value
        self._set_send_context()
        self._driver.send_value(param_name, param_value)
        # Cleaning up the dict
        self._params = {}

    def send_params(self, params: dict):
        """
        Method applies the passed parameters to an object and sends them to NMS.
        Can be used to update the existing object.

        :param dict params: a dictionary of parameters to apply to the object
         """
        # TODO: probably uncomment if issue with different sent and returned values is fixed
        # self.set_params(params)
        # self.save()
        self._set_send_context()
        for name, value in params.items():
            self._driver.set_value(name, value)
        self._driver.send_data()

    def read_param(self, param_name: str):
        """
        Get the parameter value by its name.

        :returns:
            - (str) - value of the requested parameter
            - None - if there is no such parameter for the given object
        """
        self._driver.set_path(self._get_read_path())
        self._params[param_name] = self._driver.get_value(param_name)
        if param_name not in self._params:
            return None
        return self._params[param_name]

    def has_param_error(self, param_name: str):
        """
        Get the error status of the passed parameter.

        :returns:
            - (bool) - False if the parameter is not applied to the NMS object, otherwise True
        """
        return self._driver.has_param_error(param_name)

    def load(self):
        """
        Load the object from NMS. The parameters either passed to the class constructor or set via `set_param` or
        `set_params` are loaded.

        :raises InvalidIdException: if ID < 0
        """
        if self._is_new():
            raise InvalidIdException
        self._driver.set_path(self._get_read_path())
        self._driver.load_data()
        for param_name in self._params.keys():
            self.read_param(param_name)

    def save(self):
        """
        Send to NMS the parameters either passed to the constructor or set by calling
        `set_param` or `set_params`.

        :raises src.exceptions.ObjectNotCreatedException: if the object cannot be created
        """
        self._set_send_context()
        for name, value in self._params.items():
            self._driver.set_value(name, value)
        if self._is_new():
            self._object_id = self._driver.create_object()
        else:
            self._driver.send_data()
        self._params = {}

    def delete(self, recursively: bool = False):
        """
        Delete the existing object.

        :param bool recursively: True to apply recursive deletion, otherwise False
        """
        self._driver.set_path(self._get_delete_path())
        # TODO: use constants. Get rid of the driver dependent code.
        if API != self._driver.get_type():
            if self._get_delete_path() != self._driver.get_current_path():
                self._driver.load_data()
            self._driver.send_data("#deleteFirst")
            # TODO: is recursively still an option?
            if recursively:
                self._driver.send_data('#deleteRecursivelyCheckbox')
            # self._driver.send_data("#applyModalButton")
            self._driver.delete_object("#applyModalButton")
        else:
            if recursively:
                self._driver.set_value('recursive', 1)
            # self._driver.send_data()
            self._driver.delete_object()
        self._object_id = None

    def _set_send_context(self):
        """
        Private method that is used to set the driver dependent path for either creating a new object
        or updating the existing object. Do not call it directly.
        """
        if self._is_new():
            path = self._get_create_path()
        else:
            path = self._get_update_path()
        self._driver.set_path(path)
        if API != self._driver.get_type():
            if path != self._driver.get_current_path():
                self._driver.load_data()

    def _is_new(self):
        """
        Private method that is used to determine if a new object should be created. Do not call it directly.

        :returns bool: True if a new object should be created, otherwise False
        """
        return NEW_OBJECT_ID >= self._object_id

    def get_realtime(self):
        """
        Method is redefined for controller and station objects in order to get their Realtime stats.
        """
        pass

    def __del__(self):
        self._driver = None

    def get_uprow(self):
        """
        Get the uprow of the object.

        :returns:
            - uprow (str) - the uprow of the object in the following format `<object_table>:<row>`
            - None - if the uprow cannot be resolved
        """
        _uprow = self.read_param('uprow')
        if _uprow is not None and isinstance(_uprow, str) and len(_uprow.split()) > 1:
            return _uprow.split()[0]
        return None

    def log_add_device_investigator(self):
        pass

    def graph_add_device_investigator(self):
        pass

    def log_sync_add_investigator(self):
        pass

    def graph_sync_add_investigator(self):
        pass
