import base64
import json
from http import HTTPStatus
from json import JSONDecodeError
from pathlib import Path
from time import sleep

import requests

from src.constants import API_LOGIN_PATH, API_LOAD_CONFIG_COMMAND, API_SAVE_CONFIG_AS_COMMAND
from src.exceptions import DriverInitException, NmsDownloadException
from src.options_providers.options_provider import OptionsProvider, API_CONNECT


class BackupManager:

    def __init__(self, connection_options=None):
        if connection_options is None:
            connection_options = OptionsProvider.get_connection('global_options', API_CONNECT)
        self._address = connection_options['address']
        self._driver = requests
        self._cookies = None
        self._login(connection_options['username'], connection_options['password'])

    def create_backup(self, backup_name, local=True):
        """
        Create the backup of the current NMS configuration and optionally download it locally.

        :param str backup_name: the name of the backup to create
        :param bool local: if True (by default) the created backup is downloaded to nms_backups folder
        :raises NmsDownloadException: if the backup cannot be downloaded locally
        """
        if not len(backup_name):
            raise ValueError('file name can not be empty')
        old_backup_data = self._get_backup_data(backup_name)
        self._save_backup(backup_name)
        if self._wait_backup(backup_name, old_backup_data) and local:
            backup = self._download_backup(backup_name)
            _nms_backup_size = int(self._get_backup_data(backup_name).get('size'))
            # TODO: probably not needed, however it is better to know when the backup is not fully downloaded
            if len(backup) < _nms_backup_size:
                raise NmsDownloadException(f'Cannot download full backup from NMS: '
                                           f'downloaded size {len(backup)} bytes, actual size {_nms_backup_size} bytes')
            self._write_backup(backup_name, backup)

    def apply_backup(self, backup_name, local=True):
        """
        Apply a backup by its name

        :param str backup_name: the name of the backup to apply
        :param bool local: if True (by default) the backup is uploaded from a local machine in the first place
        """
        if local:
            self._upload_backup(backup_name)
        self._send_backup(backup_name)

    def _save_backup(self, backup_name):
        result, error = self._post(
            f'api/object/write/nms=0/command={API_SAVE_CONFIG_AS_COMMAND}', {'save_filename': backup_name}
        )
        if error is not None:
            raise Exception(error)

    def _get_backup_data(self, backup_name):
        result, error = self._post('api/fs/content/nms=0/path=/config/', {'dir': 'config'})
        if error is not None:
            raise ValueError(error)
        for backup_info in result:
            if 'name' in backup_info and backup_name == backup_info['name']:
                return backup_info

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

    def _wait_backup(self, backup_name, old_backup_data):
        """Wait for backup to be entirely saved in NMS"""
        _previous_size = -1
        _created = False
        counter = 0
        for i in range(1, 50):
            try:
                new_data = self._get_backup_data(backup_name)
                if new_data is not None:
                    if _created:
                        _size = new_data.get('size')
                        if _size != _previous_size:
                            _previous_size = _size
                        else:
                            counter += 1

                        if counter == 5:
                            return True
                    else:
                        if old_backup_data is not None:
                            if new_data['date'] != old_backup_data['date']:
                                _created = True
                        else:
                            if new_data is not None:
                                _created = True
            except ValueError:
                pass
            sleep(0.2)
        raise ValueError('backup not created')

    def _download_backup(self, backup_name):
        resp = self._driver.post(
            self._address + f'api/fs/download/nms=0/path=config&{backup_name}',
            data=json.dumps({'filename': F"config/{backup_name}"}),
            cookies=self._cookies,
        )
        if HTTPStatus.OK != resp.status_code:
            error = F"{resp.status_code} : {resp.reason}"
        elif 0 == len(resp.content):
            error = 'Empty response body'
        else:
            return resp.content
        raise ValueError(error)

    # noinspection PyMethodMayBeStatic
    def _write_backup(self, backup_name: str, backup):
        # newline='' to handle windows system default line endings
        with open(self._get_backup_dir(backup_name), mode='w+', newline='') as f:
            data = backup.decode('utf-8')
            f.write(data)

    def _upload_backup(self, backup_name):
        with open(self._get_backup_dir(backup_name), 'rb') as f:
            files = {'config': f}
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

    def _send_backup(self, backup_name):
        start_time = self._get_start_time()
        result, error = self._post(
            f'api/object/write/nms=0/command={API_LOAD_CONFIG_COMMAND}',
            {'load_filename': backup_name}
        )
        if error is not None:
            raise ValueError(error)
        for i in range(1, 50):
            sleep(0.5)
            try:
                new_time = self._get_start_time()
                if new_time and start_time != new_time:
                    return
            except ValueError:
                continue
        raise ValueError('Backup apply error')

    def _get_start_time(self):
        result = None
        try:
            resp = self._driver.get(self._address + 'api/object/dashboard/nms=0', cookies=self._cookies)
            error = None
            if HTTPStatus.OK != resp.status_code:
                error = F"{resp.status_code} : {resp.reason}"
                # Handle Access denied after loading backup
                # TODO: is resp.status_code != 200 better?
                if resp.status_code in (401, 403):
                    return None
            elif 0 == len(resp.content):
                error = 'Empty response body'
            else:
                try:
                    result_obj = json.loads(resp.content)
                    if 0 == result_obj['error_code']:
                        result = result_obj['reply']['load_time']
                    else:
                        error = result_obj['error_log']
                except JSONDecodeError:
                    error = 'Invalid json in response'
                except KeyError:
                    error = 'Not found error_code in response'
            if error is not None:
                raise ValueError(error)
        except requests.exceptions.ConnectionError:
            pass
        return result

    def _delete_backup(self, backup_name):
        result, error = self._post(
            f'api/fs/delete/nms=0/path=config&{backup_name}',
            {}
        )
        if error is not None:
            raise Exception(error)

    @staticmethod
    def _get_backup_dir(backup_name):
        return (Path(__file__).parent.parent / '../nms_backups' / backup_name).resolve()
