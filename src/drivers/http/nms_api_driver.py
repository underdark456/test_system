import base64
import json
from http import HTTPStatus
from json import JSONDecodeError
from typing import Optional
from src.class_logger import class_logger_decorator, debug
from src.constants import API_LOGIN_PATH
from src.drivers.abstract_http_driver import AbstractHttpDriver, DRIVER_NAMES
from src.exceptions import ObjectNotFoundException, DriverInitException, ObjectNotCreatedException, \
    ParameterNotPassedException, NotImplementedException, ObjectNotDeletedException

DEFAULT_TIMEOUT = 5


@class_logger_decorator
class NmsApiDriver(AbstractHttpDriver):

    def __init__(self, driver_type, driver):
        self._type = driver_type
        self._path = None
        self._current_path = None
        self._cookies = None
        self._values = {}
        self._errors = {}
        self._username = None
        self._password = None
        self.address = None
        self.driver = driver

    def get_type(self):
        return self._type

    def get_driver_name(self):
        return DRIVER_NAMES.get(self._type, None)

    def get_current_path(self):
        return self._current_path

    def load_data(self, path: str = None):
        if path is None:
            path = self._path
        self._current_path = path
        full_address = self.address + path
        debug(full_address)
        resp = self.driver.get(full_address, cookies=self._cookies)
        if HTTPStatus.OK != resp.status_code or 0 == len(resp.content):
            raise ObjectNotFoundException(F"{resp.status_code}:{full_address}: content | {resp.content}")
        debug(resp.content)
        self._values = json.loads(resp.content)['reply']

    def get_value(self, element_id: str):
        self._values[element_id] = None
        self.load_data()
        if element_id not in self._values:
            return None
        return self._values[element_id]

    def set_value(self, element_id: str, element_value: any):
        self._values[element_id] = element_value

    def send_value(self, element_id: str, element_value: any, sender_selector: str = None):
        self._values[element_id] = element_value
        result, error, obj_id = self._send_post()
        # if not result:
        if not result or error != '':
            self._errors[element_id] = error

    def create_object(self, sender_selector: str = None) -> Optional[int]:
        result, error, obj_id = self._send_post()
        if not result or error != '':
            raise ObjectNotCreatedException(error)
        return obj_id

    def delete_object(self, sender_selector: str = None) -> Optional[int]:
        result, error, obj_id = self._send_post()
        # result, error, obj_id = self._send_get()
        if not result or error != '':
            raise ObjectNotDeletedException(error)
        return obj_id

    def send_data(self, sender_selector: str = None):
        result, error, obj_id = self._send_post()
        if not result or error != '':
            self._set_errors(error)
            # TODO: decide what is the default behavior
            # raise ObjectNotUpdatedException(error)

    def _send_get(self):
        self._errors = {}
        obj_id = None
        result = False
        error = ''
        path = self._get_full_path()
        debug(path)
        resp = self.driver.get(
            path,
            timeout=DEFAULT_TIMEOUT,
            cookies=self._cookies
        )
        if HTTPStatus.OK != resp.status_code:
            error = F"{resp.status_code} : {resp.reason}"
        elif 0 == len(resp.content):
            error = 'Empty response body'
        else:
            try:
                result_obj = json.loads(resp.content)
                if 0 == result_obj['error_code']:
                    result = True
                    obj_id = result_obj['reply']['%row']
                else:
                    error = result_obj['error_log']
            except JSONDecodeError:
                error = 'Invalid json in response'
            except KeyError:
                error = 'Not found error_code in response'
        return result, error, obj_id

    def _send_post(self):
        self._errors = {}
        obj_id = None
        result = False
        error = ''
        path = self._get_full_path()
        debug(path)
        debug(self._values)

        # handling non-ascii characters in the payload
        data = json.dumps(self._values, ensure_ascii=False)
        encoded_data = data.encode('utf-8')
        resp = self.driver.post(
            path,
            encoded_data,
            timeout=DEFAULT_TIMEOUT,
            cookies=self._cookies
        )
        if HTTPStatus.OK != resp.status_code:
            error = F"{resp.status_code} : {resp.reason}"
        elif 0 == len(resp.content):
            error = 'Empty response body'
        else:
            try:
                result_obj = json.loads(resp.content)
                if 0 == result_obj['error_code']:
                    result = True
                    obj_id = result_obj['reply']['%row']
                else:
                    error = result_obj['error_log']
            except JSONDecodeError:
                error = 'Invalid json in response'
            except KeyError:
                error = 'Not found error_code in response'
        return result, error, obj_id

    def close(self):
        self.driver = None
        self._cookies = None

    def set_path(self, path: str):
        self._values = {}
        self._errors = {}
        self._path = path

    def has_param_error(self, element_id: str):
        return element_id in self._errors

    def search_id_by_name(self, search: dict):
        try:
            for obj in self._values:
                for inner_key, inner_value in obj.items():
                    if inner_key == 'name' and inner_value == search.get('api'):
                        return str(obj.get('%row', None))
        except AttributeError:
            return None
        return None

    def _get_full_path(self):
        return self.address + self._path

    def login(self, username, password):
        bytes_str = F"{username}:{password}".encode('ascii')
        bytes_b64 = base64.b64encode(bytes_str)
        token = bytes_b64.decode('ascii')
        headers = {
            'Authorization': F"Basic {token}"
        }
        resp = self.driver.get(self.address + API_LOGIN_PATH, headers=headers, timeout=DEFAULT_TIMEOUT)
        if HTTPStatus.OK != resp.status_code:
            raise DriverInitException(resp.content)
        self._cookies = resp.cookies
        self._username = username
        self._password = password

    def logout(self):
        self._cookies = None
        self._username = None
        self._password = None

    def _set_errors(self, error):
        for field in self._values.keys():
            if error.find(field) != -1:
                self._errors[field] = True

    def get_realtime(self, command=None, obj_id=0):
        if command is None:
            raise ParameterNotPassedException('Command must be passed as an argument')
        payload = {"command": command, "control": obj_id}
        error = ''
        reply = None
        resp = self.driver.post(
            self._get_full_path(),
            data=json.dumps(payload),
            timeout=DEFAULT_TIMEOUT * 10,  # the timeout must be big enough to handle 'No reply' response
            cookies=self._cookies
        )
        if HTTPStatus.OK != resp.status_code:
            error = F"{resp.status_code} : {resp.reason}"
        elif 0 == len(resp.content):
            error = 'Empty response body'
        else:
            try:
                result_obj = json.loads(resp.content)
                if 0 == result_obj['error_code']:
                    reply = result_obj['reply']
                else:
                    error = result_obj['error_log']
            except JSONDecodeError:
                error = 'Invalid json in response'
            except KeyError:
                error = 'Not found error_code in response'
        if not error and reply != 'No reply':
            return reply
        return None

    def custom_get(self, path, cookies=None, headers=None, timeout=None, http_status_code=False):
        """
        An entity independent GET request. Can be used to get API responses from NMS.
        If no cookies are provided, the current driver cookies are used.

        :param str path: a relative path of the request, i.e. `api/object/delete/network=100`
        :param cookies: optional alternative cookies
        :param dict headers: optional dictionary of headers
        :param int timeout: timeout in seconds before raising exception in case of non-response
        :param bool http_status_code: if True returns also http status code as the forth argument
        :raises requests.exceptions.ConnectTimeout: if there is no response during the timeout time
        """
        if headers is None:
            headers = {}
        if cookies is None:
            cookies = self._cookies
        if timeout is None:
            timeout = DEFAULT_TIMEOUT * 10
        reply = None
        error_code = None
        self._path = path
        resp = self.driver.get(
            self._get_full_path(),
            timeout=timeout,
            cookies=cookies,
            headers=headers
        )
        # TODO: Probably remove the following block
        if HTTPStatus.OK != resp.status_code:
            html_status = F"{resp.status_code} : {resp.reason}"
        else:
            html_status = 'OK'
        try:
            result_obj = json.loads(resp.content)
            reply = result_obj.get('reply', None)
            error_code = result_obj.get('error_code', None)
            error = result_obj.get('error_log', None)
        except JSONDecodeError:
            error = 'Invalid json in response'
        if http_status_code:
            return reply, error, error_code, html_status
        return reply, error, error_code

    def custom_post(self, path, cookies=None, payload=None, headers=None, timeout=None, http_status_code=False):
        """
        An entity independent POST request. Can be used to get API responses from NMS.
        If no cookies are provided, the current driver cookies are used.

        :param str path: a relative path of the request, i.e. `api/form/write/nms=0/new_item=network`
        :param cookies: optional alternative cookies
        :param dict payload: optional payload dictionary
        :param dict headers: optional dictionary of headers
        :param int timeout: timeout in seconds before raising exception in case of non-response
        :param bool http_status_code: if True returns also http status code as the forth argument
        :raises requests.exceptions.ConnectTimeout: if there is no response during the timeout time
        """
        if payload is None:
            payload = {}
        if headers is None:
            headers = {}
        if cookies is None:
            cookies = self._cookies
        if timeout is None:
            timeout = DEFAULT_TIMEOUT * 10
        reply = None
        error_code = None
        self._path = path

        # handling non-ascii characters in the payload
        data = json.dumps(payload, ensure_ascii=False)
        encoded_data = data.encode('utf-8')

        resp = self.driver.post(
            self._get_full_path(),
            encoded_data,
            timeout=timeout,
            cookies=cookies,
            headers=headers
        )
        # TODO: Probably remove the following block
        if HTTPStatus.OK != resp.status_code:
            html_status = F"{resp.status_code} : {resp.reason}"
        else:
            html_status = 'OK'
        try:
            result_obj = json.loads(resp.content)
            reply = result_obj.get('reply', None)
            error_code = result_obj.get('error_code', None)
            error = result_obj.get('error_log', None)
        except JSONDecodeError:
            error = 'Invalid json in response'
        if http_status_code:
            return reply, error, error_code, html_status
        return reply, error, error_code

    def get_cookies(self):
        return self._cookies

    def set_cookies(self, cookies):
        self._cookies = cookies

    def screenshot(self, screenshot_name):
        raise NotImplementedException('Screenshots can only be taken via WEB driver')

    def add_device(self):
        raise NotImplementedException('Add device is implemented only via WEB driver')

    def sync_add(self):
        raise NotImplementedException('Sync&Add is implemented only via WEB driver')
