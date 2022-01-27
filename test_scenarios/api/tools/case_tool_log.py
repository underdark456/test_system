import time
from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR, ACCESS_DENIED
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControlModes
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api.tools'


class ApiLogToolCase(CustomTestCase):
    """Test cases for log tool"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = 1800  # number of seconds to execute the test case
    __express__ = False

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.options = OptionsProvider.get_options(options_path)

        cls.nms = Nms(cls.driver, 0, 0)

    @skip('Temporary skip to check if it causes stat get hang')
    def test_log_tool_entities(self):
        """All NMS entities log requests both supported and unsupported"""
        self.backup.apply_backup('each_entity.txt')
        end = round(time.time(), 3)
        start = end - 3600
        for entity in self.options.get('dbeditor').keys():
            path = PathsManager._API_OBJECT_LOG.format(entity, 0)
            reply, error, error_code, http_status = self.driver.custom_post(
                path,
                http_status_code=True,
                payload={'start': start, 'end': end, 'info': 1, 'warning': 1, 'fault': 1}
            )
            if entity in ('buf_event', 'event'):
                self.assertEqual(ACCESS_DENIED, error_code, msg=f'{entity} get log does not trigger Access denied')
            elif entity in ('locktable', 'maxrow', 'module'):
                self.assertEqual(
                    f'404 : Not Found',
                    http_status,
                    msg=f'{entity} http status code {http_status}, expected 404 : Not Found',
                )
            else:
                self.assertEqual(NO_ERROR, error_code, msg=f'{entity} get log error_code {error_code}')

    def test_shown_logs_size(self):
        """Number of logs entries shown triggered by controllers"""
        expected_logs_number = 0
        self.backup.apply_backup('case_tool_log.txt')
        start = round(time.time(), 3)

        # The following cycle triggers new logs entries by switching controllers Off and On again
        for iter_num in range(self.options.get('test_shown_logs_iterations')):
            for i in range(512):
                ctrl = Controller(self.driver, 0, i)
                if not ctrl.wait_state('Unreachable'):
                    self.fail(f'Controller ID {i} unexpectedly is not Unreachable')
                ctrl.send_param('control', ControlModes.NO_ACCESS)
                expected_logs_number += 1
            for i in range(512):
                ctrl = Controller(self.driver, 0, i)
                if not ctrl.wait_state('Off'):
                    self.fail(f'Controller ID {i} unexpectedly is not Off')
                ctrl.send_param('control', ControlModes.FULL)
                expected_logs_number += 1
            for i in range(512):
                ctrl = Controller(self.driver, 0, i)
                if not ctrl.wait_state('Unreachable'):
                    self.fail(f'Controller ID {i} unexpectedly is not Unreachable')
        end = round(time.time(), 3)
        self.nms.wait_next_tick()
        self.nms.wait_next_tick()

        # Getting logs for whole NMS
        path = PathsManager._API_OBJECT_LOG.format('nms', 0)
        reply, error, error_code = self.driver.custom_post(path, payload={
            'start': start,
            'end': end,
            'info': 1,
            'warning': 1,
            'fault': 1,
        })
        with self.subTest(f'NMS logs expected entries number'):
            self.assertEqual(
                expected_logs_number,
                len(reply),
                f'NMS logs expected entries number {expected_logs_number} got {len(reply)}',
            )

        # Getting info logs for whole NMS
        path = PathsManager._API_OBJECT_LOG.format('nms', 0)
        reply, error, error_code = self.driver.custom_post(path, payload={
            'start': start,
            'end': end,
            'info': 1,
            'warning': 0,
            'fault': 0,
        })
        with self.subTest(f'NMS info logs expected entries number'):
            self.assertEqual(
                int(expected_logs_number / 2),
                len(reply),
                f'NMS info logs expected entries number {int(expected_logs_number / 2)} got {len(reply)}',
            )

        # Getting fault for whole NMS
        path = PathsManager._API_OBJECT_LOG.format('nms', 0)
        reply, error, error_code = self.driver.custom_post(path, payload={
            'start': start,
            'end': end,
            'info': 0,
            'warning': 0,
            'fault': 1,
        })
        with self.subTest(f'NMS fault logs expected entries number'):
            self.assertEqual(
                int(expected_logs_number / 2),
                len(reply),
                f'NMS fault logs expected entries number {int(expected_logs_number / 2)} got {len(reply)}',
            )

        # Getting logs without info, fault and warning for whole NMS
        path = PathsManager._API_OBJECT_LOG.format('nms', 0)
        reply, error, error_code = self.driver.custom_post(path, payload={
            'start': start,
            'end': end,
            'info': 0,
            'warning': 0,
            'fault': 0,
        })
        with self.subTest(f'NMS logs no info, fault, and warning expected entries number'):
            self.assertEqual(
                0,
                len(reply),
                f'NMS logs no info, fault, and warning '
                f'expected entries number 0, got {len(reply)}',
            )

        # Getting logs for whole Network
        path = PathsManager._API_OBJECT_LOG.format('network', 0)
        reply, error, error_code = self.driver.custom_post(path, payload={
            'start': start,
            'end': end,
            'info': 1,
            'warning': 1,
            'fault': 1,
        })
        with self.subTest(f'Network logs expected entries number'):
            self.assertEqual(
                expected_logs_number,
                len(reply),
                f'Network logs expected entries number {expected_logs_number} got {len(reply)}',
            )

        # Getting info logs for whole Network
        path = PathsManager._API_OBJECT_LOG.format('network', 0)
        reply, error, error_code = self.driver.custom_post(path, payload={
            'start': start,
            'end': end,
            'info': 1,
            'warning': 0,
            'fault': 0,
        })
        with self.subTest(f'Network info logs expected entries number'):
            self.assertEqual(
                int(expected_logs_number / 2),
                len(reply),
                f'Network info logs expected entries number {int(expected_logs_number / 2)} got {len(reply)}',
            )

        # Getting fault logs for whole Network
        path = PathsManager._API_OBJECT_LOG.format('nms', 0)
        reply, error, error_code = self.driver.custom_post(path, payload={
            'start': start,
            'end': end,
            'info': 0,
            'warning': 0,
            'fault': 1,
        })
        with self.subTest(f'Network fault logs expected entries number'):
            self.assertEqual(
                int(expected_logs_number / 2),
                len(reply),
                f'Network fault logs expected entries number {int(expected_logs_number / 2)} got {len(reply)}',
            )

        # Getting logs without info, fault and warning for whole Network
        path = PathsManager._API_OBJECT_LOG.format('network', 0)
        reply, error, error_code = self.driver.custom_post(path, payload={
            'start': start,
            'end': end,
            'info': 0,
            'warning': 0,
            'fault': 0,
        })
        with self.subTest(f'Network logs no info, fault, and warning expected entries number'):
            self.assertEqual(
                0,
                len(reply),
                f'Network logs no info, fault, and warning '
                f'expected entries number 0, got {len(reply)}',
            )

        for i in range(512):
            path = PathsManager._API_OBJECT_LOG.format('controller', i)
            reply, error, error_code = self.driver.custom_post(path, payload={
                'start': start,
                'end': end,
                'info': 1,
                'warning': 1,
                'fault': 1,
            })
            with self.subTest(f'Controller ID {i} logs expected entries number'):
                self.assertEqual(
                    self.options.get('test_shown_logs_iterations') * 2,
                    len(reply),
                    f'Controller ID {i} logs expected entries number '
                    f'{self.options.get("test_shown_logs_iterations") * 2}, got {len(reply)}',
                )

            path = PathsManager._API_OBJECT_LOG.format('controller', i)
            reply, error, error_code = self.driver.custom_post(path, payload={
                'start': start,
                'end': end,
                'info': 1,
                'warning': 0,
                'fault': 0,
            })
            with self.subTest(f'Controller ID {i} info logs expected entries number'):
                self.assertEqual(
                    self.options.get('test_shown_logs_iterations'),
                    len(reply),
                    f'Controller ID {i} info logs expected entries number '
                    f'{self.options.get("test_shown_logs_iterations")}, got {len(reply)}',
                )

            path = PathsManager._API_OBJECT_LOG.format('controller', i)
            reply, error, error_code = self.driver.custom_post(path, payload={
                'start': start,
                'end': end,
                'info': 0,
                'warning': 0,
                'fault': 1,
            })
            with self.subTest(f'Controller ID {i} fault logs expected entries number'):
                self.assertEqual(
                    self.options.get('test_shown_logs_iterations'),
                    len(reply),
                    f'Controller ID {i} fault logs expected entries number '
                    f'{self.options.get("test_shown_logs_iterations")}, got {len(reply)}',
                )

            # Getting logs without info, fault and warning for Controller
            path = PathsManager._API_OBJECT_LOG.format('controller', i)
            reply, error, error_code = self.driver.custom_post(path, payload={
                'start': start,
                'end': end,
                'info': 0,
                'warning': 0,
                'fault': 0,
            })
            with self.subTest(f'Controller ID {i} logs no info, fault, and warning expected entries number'):
                self.assertEqual(
                    0,
                    len(reply),
                    f'NMS logs no info, fault, and warning '
                    f'expected entries number 0, got {len(reply)}',
                )

    def test_logs_time_range(self):
        """Get logs with different start/end time range"""
        self.backup.apply_backup('case_tool_log.txt')
        self.nms.wait_next_tick()
        self.nms.wait_next_tick()

        # Logs requests from the past (even before epoch) up to 100 years
        _year_seconds = 60 * 60 * 24 * 365
        end = int(time.time())
        for start in range(int(end) - _year_seconds * 100, int(end), _year_seconds):
            path = PathsManager._API_OBJECT_LOG.format('nms', 0)
            reply, error, error_code = self.driver.custom_post(path, payload={
                'start': start,
                'end': end,
                'info': 1,
                'warning': 1,
                'fault': 1,
            })
            self.assertEqual(NO_ERROR, error_code, msg=f'Log request error_code {error_code} '
                                                       f'start time {start}, end time {end}')
            if start < 0:
                self.assertEqual(
                    0,
                    len(reply),
                    msg=f'Log request start time before epoch expected 0 entries, got {len(reply)}'
                )
            else:
                self.assertLessEqual(
                    0,
                    len(reply),
                    msg=f'Log request start time {start} expected >= 0 entries, got {len(reply)}'
                )

        # Logs requests from the future up to 100 years
        start = int(time.time())
        for end in range(start, int(end) + _year_seconds * 100, _year_seconds):
            path = PathsManager._API_OBJECT_LOG.format('nms', 0)
            reply, error, error_code = self.driver.custom_post(path, payload={
                'start': start,
                'end': end,
                'info': 1,
                'warning': 1,
                'fault': 1,
            })
            self.assertEqual(NO_ERROR, error_code, msg=f'Log request error_code {error_code} '
                                                       f'start time {start}, end time {end}')
            self.assertEqual(
                0,
                len(reply),
                msg=f'Log request start time now, end time {end} expected 0 entries, got {len(reply)}'
            )
