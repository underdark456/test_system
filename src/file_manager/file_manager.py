import base64
import json
import os
import requests
from http import HTTPStatus
from json import JSONDecodeError
from pathlib import Path
from src.constants import API_LOGIN_PATH
from src.exceptions import DriverInitException, InvalidOptionsException, NmsErrorResponseException
from src.options_providers.options_provider import OptionsProvider, API_CONNECT


class FileManager:

    def __init__(self, connection_options=None):
        if connection_options is None:
            connection_options = OptionsProvider.get_connection('global_options', API_CONNECT)
        self._address = connection_options['address']
        self._driver = requests
        self._cookies = None
        self._login(connection_options['username'], connection_options['password'])

    def upload_beam(self, beam_name: str):
        """
        Upload a beam file from test system to NMS. The file must be located in `beams` directory

        :param str beam_name: the full name of the beam file including the extension
        :raises InvalidOptionsException: if file does not exist
        :raises ValueError: if there is any sort of error in the NMS response
        """
        _full_path = self._get_dir('beams', beam_name)
        if not os.path.isfile(_full_path):
            raise InvalidOptionsException(f'Beam file named {beam_name} cannot be located in the test system')
        self._upload_file(_full_path, 'footprints')

    def delete_beam(self, beam_name: str):
        """
        Delete a beam file from NMS

        :param str beam_name: the name of the file to delete
        :raises NmsErrorResponseException: if there is any sort of error in NMS response
        """
        self._delete_file('footprints', beam_name)

    def upload_uhp_software(self, sw_file: str):
        """
        Upload a UHP software file from test system to NMS. The file must be located in `uhp_soft3` directory

        :param str sw_file: the full name of the beam file including the extension
        :raises InvalidOptionsException: if file does not exist
        :raises ValueError: if there is any sort of error in the NMS response
        """
        _full_path = self._get_dir('uhp_soft3', sw_file)
        if not os.path.isfile(_full_path):
            raise InvalidOptionsException(f'UHP sw file named {sw_file} cannot be located in the test system')
        self._upload_file(_full_path, 'software')

    def delete_uhp_software(self, sw_file: str):
        """
        Delete a software file from NMS

        :param str sw_file: the name of the file to delete
        :raises NmsErrorResponseException: if there is any sort of error in NMS response
        """
        self._delete_file('software', sw_file)

    def _upload_file(self, _full_path, nms_dir):
        with open(_full_path, 'rb') as f:
            files = {nms_dir: f}
            resp = self._driver.post(
                self._address + 'api/fs/upload/nms=0',
                files=files,
                cookies=self._cookies
            )
            error = None
            if HTTPStatus.OK != resp.status_code:
                error = F"{resp.status_code} : {resp.reason}"
            elif 0 == len(resp.content):
                error = 'Empty response body'
            else:
                try:
                    result_obj = json.loads(resp.content)
                    if 0 != result_obj['error_code']:
                        error = result_obj['error_log']
                except JSONDecodeError:
                    error = 'Invalid json in response'
                except KeyError:
                    error = 'Not found error_code in response'
            if error is not None:
                raise ValueError(error)

    def _post(self, path: str, data: dict):
        resp = self._driver.post(
            self._address + path,
            data=json.dumps(data),
            cookies=self._cookies
        )
        result = None
        error = None
        if HTTPStatus.OK != resp.status_code:
            error = F"{resp.status_code} : {resp.reason}"
        elif 0 == len(resp.content):
            error = 'Empty response body'
        else:
            try:
                result_obj = json.loads(resp.content)
                if 0 == result_obj['error_code']:
                    result = result_obj['reply']
                else:
                    error = result_obj['error_log']
            except JSONDecodeError:
                error = 'Invalid json in response'
            except KeyError:
                error = 'Not found error_code in response'
        return result, error

    def _login(self, username, password):
        bytes_str = F"{username}:{password}".encode('ascii')
        bytes_b64 = base64.b64encode(bytes_str)
        token = bytes_b64.decode('ascii')
        headers = {
            'Authorization': F"Basic {token}"
        }
        resp = self._driver.get(self._address + API_LOGIN_PATH, headers=headers)
        if HTTPStatus.OK != resp.status_code:
            raise DriverInitException(resp.content)
        self._cookies = resp.cookies

    def _delete_file(self, dir_name, file_name):
        result, error = self._post(
            f'api/fs/delete/nms=0/path={dir_name}&{file_name}',
            {}
        )
        if error is not None:
            raise NmsErrorResponseException(error)

    @staticmethod
    def _get_dir(dir_name, file_name):
        return (Path(__file__).parent.parent / f'..{os.sep}{dir_name}' / file_name).resolve()
