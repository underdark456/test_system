import time
import datetime

from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.api.tools'
backup_name = 'each_entity.txt'


class ApiGraphToolCase(CustomTestCase):
    """Graph tool test case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 50  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.web_driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT),
            driver_id='case_tool_graph',
            store_driver=False,
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.options = OptionsProvider.get_options(options_path)

    def test_graph(self):
        """Graph get for objects supported and not supported the tool"""
        path_api = PathsManager._API_OBJECT_GRAPH
        path_web = PathsManager._OBJECT_GRAPH
        for obj_name in self.options.get('valid_graph_objects'):
            end = round(time.time(), 3)
            start = end - 3600
            payload = {
                "start": start,
                "end": end,
                "dots": 400,
                "graphNumber": 2,
                "minmax": 0,
                "faults": 0
            }
            with self.subTest(f'Valid graph {obj_name} API'):
                reply, error, error_code = self.driver.custom_post(path_api.format(obj_name, 0), payload=payload)
                self.assertEqual(
                    NO_ERROR,
                    error_code,
                    msg=f'{obj_name} graph error_code {error_code}, expected {NO_ERROR}'
                )
                self.assertEqual(
                    '',
                    error,
                    msg=f'{obj_name} graph error {error}, expected empty error message'
                )
                self.assertEqual(
                    dict,
                    type(reply),
                    msg=f'{obj_name} graph reply type {type(reply)}, expected dictionary'
                )
            with self.subTest(f'Valid graph {obj_name} web form'):
                self.web_driver.load_data(path_web.format(obj_name, 0))
                self.assertEqual(
                    -1,
                    self.web_driver.driver.page_source.find('No graph for this object'),
                    msg=f'{path_web.format(obj_name, 0)} No graph for this object message on screen'
                )

        for obj_name in self.options.get('invalid_graph_objects'):
            end = round(time.time(), 3)
            start = end - 3600
            payload = {
                "start": start,
                "end": end,
                "dots": 400,
                "graphNumber": 2,
                "minmax": False,
                "faults": False
            }
            with self.subTest(f'Invalid graph {obj_name} API'):
                reply, error, error_code = self.driver.custom_post(path_api.format(obj_name, 0), payload=payload)
                self.assertEqual(
                    NO_ERROR,
                    error_code,
                    msg=f'{obj_name} graph error_code {error_code}, expected {NO_ERROR}'
                )
                self.assertEqual(
                    '',
                    error,
                    msg=f'{obj_name} graph error {error}, expected empty error message'
                )
                self.assertEqual(
                    dict,
                    type(reply),
                    msg=f'{obj_name} graph reply type {type(reply)}, expected None'
                )
            # Loading page of non-existing object graph should trigger 404 or No graph for this object message
            with self.subTest(f'Invalid graph {obj_name} web form'):
                self.web_driver.load_data(path_web.format(obj_name, 0))
                # self.assertNotEqual(
                #     -1,
                #     self.web_driver.driver.page_source.find('No graph for this object'),
                #     msg=f'{path_web.format(obj_name, 0)} is not 404 or No graph for this object message'
                # )

    def test_dots_number(self):
        """Number of dots in graph response test (up to 2000 dots)"""
        TICK_TIME = 5
        MAX_TEST_DOTS_NUM = 2000
        path_api = PathsManager._API_OBJECT_GRAPH
        for num in range(5, MAX_TEST_DOTS_NUM + TICK_TIME, 5):
            end = round(time.time(), 3)
            start = end - MAX_TEST_DOTS_NUM * TICK_TIME
            payload = {
                "start": start,
                "end": end,
                "dots": num,
                "graphNumber": 2,
                "minmax": False,
                "faults": False
            }
            reply, error, error_code = self.driver.custom_post(path_api.format('network', 0), payload=payload)
            self.assertEqual(
                NO_ERROR,
                error_code,
                msg=f'Network graph number of dots {num} error_code {error_code}, expected code {NO_ERROR}'
            )
            self.assertEqual(
                num,
                len(reply.get('dots')),
                msg=f'Number of dots in response {len(reply.get("dots"))}, expected {num}'
            )

    def test_valid_graph_number(self):
        """Valid graph number in graph request (data is not checked)"""
        path_api = PathsManager._API_OBJECT_GRAPH
        for i in range(2, 9):
            end = round(time.time(), 3)
            start = end - 3600
            payload = {
                "start": start,
                "end": end,
                "dots": 400,
                "graphNumber": i,
                "minmax": False,
                "faults": False
            }
            reply, error, error_code = self.driver.custom_post(path_api.format('network', 0), payload=payload)
            self.assertEqual(
                NO_ERROR,
                error_code,
                f'Valid graph number {i} error_code {error_code}, expected {NO_ERROR}'
            )
            self.assertEqual(
                400,
                len(reply.get('dots')),
                msg=f'Number of dots in response {len(reply.get("dots"))}, expected 400'
            )

    def test_invalid_graph_number(self):
        """Invalid graph number in graph request"""
        path_api = PathsManager._API_OBJECT_GRAPH
        for i in range(9, 20):
            end = round(time.time(), 3)
            start = end - 3600
            payload = {
                "start": start,
                "end": end,
                "dots": 400,
                "graphNumber": i,
                "minmax": False,
                "faults": False
            }
            reply, error, error_code = self.driver.custom_post(path_api.format('network', 0), payload=payload)
            self.assertEqual(
                NO_ERROR,
                error_code,
                f'Invalid graph number {i} error_code {error_code}, expected {NO_ERROR}'
            )
            self.assertEqual(
                0,
                len(reply),
                msg=f'Number of dots in response {len(reply)}, expected 0'
            )

    def test_start_end_range(self):
        """Start and end parameters in graph tool (up to 10 years ago)"""
        path_api = PathsManager._API_OBJECT_GRAPH
        end = round(time.time(), 3)
        seconds_day = 60 * 60 * 24
        for i in range(seconds_day, seconds_day * 365 * 10, seconds_day * 365):
            start = end - i
            payload = {
                "start": start,
                "end": end,
                "dots": 400,
                "graphNumber": 2,
                "minmax": False,
                "faults": False
            }
            d = datetime.datetime.fromtimestamp(start)
            with self.subTest(f'Graph tool start time {d.year}/{d.month}/{d.day}'):
                reply, error, error_code = self.driver.custom_post(path_api.format('network', 0), payload=payload)
                self.assertEqual(NO_ERROR, error_code)
                self.assertEqual(400, len(reply.get('dots')))

    def test_graph_faults_on(self):
        """Setting Faults on returns faults list in the response (data is not checked)"""
        path_api = PathsManager._API_OBJECT_GRAPH
        end = round(time.time(), 3)
        start = end - 3600
        payload = {
            "start": start,
            "end": end,
            "dots": 400,
            "graphNumber": 2,
            "minmax": False,
            "faults": True,
        }
        reply, error, error_code = self.driver.custom_post(path_api.format('network', 0), payload=payload)
        self.assertEqual(NO_ERROR, error_code)
        self.assertIsNotNone(reply.get('faults'))

    def test_short_range(self):
        """Start and end parameters in graph tool (range 1 hour, step 10 minutes)"""
        for _min in range(10, 70, 10):
            path_api = PathsManager._API_OBJECT_GRAPH
            end = round(time.time(), 3)  # now
            start = end - 60 * _min
            payload = {
                "start": start,
                "end": end,
                "dots": 400,
                "graphNumber": 2,
                "minmax": False,
                "faults": False,
            }
            reply, error, error_code = self.driver.custom_post(path_api.format('network', 0), payload=payload)
            self.assertEqual(NO_ERROR, error_code)
            expected_dots = _min * 12 + 1
            if expected_dots > 400:
                expected_dots = 400
            self.assertEqual(
                expected_dots,
                len(reply.get('dots')),
                msg=f'Got {len(reply.get("dots"))} dots in reply instead of {expected_dots}, '
                    f'graph range {_min} minutes from now'
            )
