import json

from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

options_path = 'test_scenarios.api.tools'
backup_name = 'default_config.txt'


class ApiFileToolCase(CustomTestCase):
    """File tool upload, download, and delete test case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 53  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, API_CONNECT)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.options = OptionsProvider.get_options(options_path)

        cls.nms_ip_port = cls.system_options.get(API_CONNECT).get('address')

    def test_get_dirs(self):
        """Get user available directories test"""
        path = PathsManager._API_FILE_GET.format('', )
        reply, error, error_code = self.driver.custom_get(path)
        self.assertEqual(NO_ERROR, error_code, msg=f'Method GET error_code {error_code}')
        self.assertEqual(7, len(reply), msg=f'Expected 7 dirs, {len(reply)} in response')
        names = set()
        for dir_data in reply:
            if dir_data.get('type') == 'dir':
                names.add(dir_data.get('name'))
        for dir_name in (self.options.get('dir_names')):
            self.assertTrue(dir_name in names, msg=f'Expected directory {dir_name} is not in the response')
            # Getting content of the directories
            path = PathsManager._API_FILE_GET.format(dir_name, )
            reply, error, error_code = self.driver.custom_get(path)
            self.assertEqual(NO_ERROR, error_code, msg=f'Get directory {dir_name} content error_code {error_code}')

    def test_invalid_path(self):
        """Get non-existing dirs test"""
        for dir_ in ('uhp', 'sudo reboot', '\n', '\r', 'cd /', 'cd ~'):
            path = PathsManager._API_FILE_GET.format(dir_, )
            reply, error, error_code = self.driver.custom_get(path)
            self.assertEqual(NO_ERROR, error_code, msg=f'Directory request {dir_}, error_code {error_code}')
            self.assertEqual(0, len(reply), msg=f'Directory request {dir_}, reply length {len(reply)}')

    def test_nms_paths(self):
        """Get directory content of the upper level"""
        for dir_ in ('..', '../nms_data', './core_data'):
            path = f'api/fs/content/nms=0/path={dir_}'
            reply, error, error_code = self.driver.custom_get(path)
            self.assertEqual(NO_ERROR, error_code, msg=f'Directory request {dir_} error code {error_code}')

    def test_upload_delete(self):
        """Make sure that files can be uploaded to all user dirs as well as deleted"""
        file_name = 'test_upload_file'
        file_content = 'Hello world!'
        with open(file_name, 'w') as file:
            file.write(file_content)
        for dir_ in (self.options.get('dir_names')):
            with open(file_name, 'rb') as file:
                files = {dir_: file}
                self.driver.driver.post(
                    self.nms_ip_port + 'api/fs/upload/nms=0',
                    files=files,
                    cookies=self.driver.get_cookies()
                )

                path = PathsManager._API_FILE_GET.format(dir_, )
                reply, error, error_code = self.driver.custom_get(path)
                for r in reply:
                    if r.get('name') == file_name:
                        self.assertEqual(
                            str(len(file_content)),
                            r.get('size'),
                            msg=f'Uploaded file size {r.get("size")}, expected {len(file_content)}')
                        break
                else:
                    self.fail(f'Test file is not uploaded to dir {dir_}')

                # Delete uploaded file
                path = PathsManager._API_FILE_DELETE.format(f'{dir_}&{file_name}')
                self.driver.custom_get(path)

                path = PathsManager._API_FILE_GET.format(dir_, )
                reply, error, error_code = self.driver.custom_get(path)
                for r in reply:
                    if r.get('name') == file_name:
                        self.fail(f'Test file is not deleted in directory {dir_}')

    def test_upload_to_invalid_dir(self):
        """Upload file to a non-existing dir"""
        file_name = 'test_upload_file'
        file_content = 'Hello world!'
        with open(file_name, 'w') as file:
            file.write(file_content)

        with open(file_name, 'rb') as file:
            files = {'sudo': file}
            resp = self.driver.driver.post(
                self.nms_ip_port + 'api/fs/upload/nms=0',
                files=files,
                cookies=self.driver.get_cookies()
            )
            try:
                result_obj = json.loads(resp.content)
                self.assertEqual(NO_ERROR, result_obj.get('error_code'))
            except Exception as exc:
                self.fail(f'Loading file to a non-existing dir failed: exception {exc}')

    def test_maximum_upload_file_size(self):
        """Make sure that the current maximum file size can be uploaded to NMS"""
        file_name = 'test_upload_file_size'
        for file_size in range(1048576, int(1048576 * self.options.get('max_file_size_mb')) + 1, 524288):
            file_content = '0' * (file_size - 1)
            with open(file_name, 'w') as file:
                file.write(file_content)

            with open(file_name, 'rb') as file:
                try:
                    files = {'config': file}
                    resp = self.driver.driver.post(
                        self.nms_ip_port + 'api/fs/upload/nms=0',
                        files=files,
                        cookies=self.driver.get_cookies()
                    )
                    result_obj = json.loads(resp.content)
                    self.assertEqual(NO_ERROR, result_obj.get('error_code'))
                    path = PathsManager._API_FILE_GET.format('config', )
                    reply, error, error_code = self.driver.custom_get(path)
                    for file_entry in reply:
                        if file_entry.get('name') == file_name:
                            self.assertEqual(
                                str(file_size - 1),
                                file_entry.get('size'),
                                msg=f'Uploaded file size {file_size - 1}, nms file size {file_entry.get("size")}'
                            )
                            break
                    else:
                        self.fail(f'File size {file_size - 1} has not been uploaded')

                except Exception as exc:
                    self.fail(f'Uploading file size {len(file_content)} failed: exception {exc}')

                # Downloading file
                try:
                    path = PathsManager._API_FILE_DOWNLOAD.format(f'config&{file_name}')
                    resp = self.driver.driver.post(
                        self.nms_ip_port + path,
                        cookies=self.driver.get_cookies(),
                    )
                    self.assertEqual(
                        file_size - 1,
                        len(resp.content),
                        msg=f'Downloaded file size {len(resp.content)}, expected {file_size - 1}'
                    )
                except Exception as exc:
                    self.fail(f'Cannot download file size {file_size - 1}: {exc}')

    def test_non_existing_file_download(self):
        """Downloading non-existing file (should trigger 404)"""
        path = PathsManager._API_FILE_DOWNLOAD.format(f'config&dummy_file_name')
        resp = self.driver.driver.post(
            self.nms_ip_port + path,
            cookies=self.driver.get_cookies(),
        )
        self.assertEqual(404, resp.status_code, msg=f'Non-existing file download http status code {resp.status_code}')

    def test_non_existing_file_delete(self):
        """Deleting non-existing file (probably should trigger something)"""
        path = PathsManager._API_FILE_DELETE.format(f'config&dummy_file_name')
        resp = self.driver.driver.post(
            self.nms_ip_port + path,
            data={},
            cookies=self.driver.get_cookies(),
        )
        self.assertEqual(200, resp.status_code, msg=f'Non-existing file delete http status code {resp.status_code}')
