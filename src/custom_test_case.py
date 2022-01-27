import datetime
import inspect
import logging
import os.path
import time
import traceback
import unittest
# noinspection PyUnresolvedReferences,PyProtectedMember
from unittest.case import _SubTest

from global_options.options import PROJECT_DIR
from src.custom_logger import CustomLogger, LOGGING, CONSOLE_LOGGING
from src.options_providers.options_provider import OptionsProvider


class CustomTestCase(unittest.TestCase):
    # Logs are placed in the following dir: `/logs/<NameOfTestCase>`
    datetime_now = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    log_dir = OptionsProvider.get_system_options("global_options").get("LOG_DIR")

    test_case_st_time = None
    logger = None
    console_logger = None
    class_logger = None
    class_file_handler = None

    # noinspection PyPep8Naming
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)

    # noinspection PyPep8Naming
    def _get_logger(self, methodName):
        """This is logger is used to log the test method"""
        # Getting absolute path of the test case in order to determine individual test case logging level
        case_abs_path = os.path.dirname(os.path.abspath(inspect.getsourcefile(self.__class__)))
        if case_abs_path is not None and case_abs_path.find(PROJECT_DIR) != -1:
            options_path = case_abs_path[len(PROJECT_DIR):].replace(os.sep, '.')
            system_options = OptionsProvider.get_system_options(options_path)
        else:
            system_options = OptionsProvider.get_system_options('global_options')

        self.logger = CustomLogger(methodName)
        self.logger.setLevel(system_options[LOGGING])

        if not os.path.isdir(f'{self.log_dir}{os.sep}{self.__class__.__name__}'):
            os.mkdir(f'{self.log_dir}{os.sep}{self.__class__.__name__}')

        # File logger setup block
        self.log_file_full_path = \
            f'{self.log_dir}{self.__class__.__name__}{os.sep}{self.datetime_now}_{self.__class__.__name__}.log'
        # setattr(self.__class__, 'log_file_full_path', self.log_file_full_path)
        self.file_handler = logging.FileHandler(
            self.log_file_full_path)
        file_format = logging.Formatter(
            fmt='%(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.file_handler.setFormatter(file_format)
        self.logger.addHandler(self.file_handler)

        # Console logger setup block
        self.console_logger = CustomLogger(f'{self.__class__.__name__}.{methodName}')
        self.console_logger.setLevel(system_options[CONSOLE_LOGGING])
        console_handler = logging.StreamHandler()
        console_format = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.console_logger.addHandler(console_handler)

    @classmethod
    def _get_class_logger(cls):
        """This logger is used to log test case in general: set_up_class and tear_down_class"""
        cls.class_logger = CustomLogger(cls.__name__)
        cls.class_logger.setLevel(logging.DEBUG)

        if not os.path.isdir(f'{cls.log_dir}{os.sep}{cls.__name__}'):
            os.mkdir(f'{cls.log_dir}{os.sep}{cls.__name__}')

        # Class File logger setup block
        log_file_full_path = \
            f'{cls.log_dir}{cls.__name__}{os.sep}{cls.datetime_now}_{cls.__name__}.log'
        cls.class_file_handler = logging.FileHandler(
            log_file_full_path)
        file_format = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        cls.class_file_handler.setFormatter(file_format)
        cls.class_logger.addHandler(cls.class_file_handler)

        # Console logger setup block
        console_handler = logging.StreamHandler()
        console_format = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        cls.class_logger.addHandler(console_handler)

    @classmethod
    def setUpClass(cls) -> None:
        cls.addClassCleanup(cls.case_execution_time)  # to get total test case execution time
        cls.test_case_st_time = time.perf_counter()
        set_up_class = getattr(cls, 'set_up_class', None)
        if set_up_class is not None:
            try:
                if cls.class_logger is None:
                    cls._get_class_logger()
                cls.class_logger.run(f'Initializing test case, running set_up_class...')
                set_up_class()
            except Exception as e:
                cls.class_logger.error(f'Exception in test case set up: {str(e)}')
                raise e

    def setUp(self) -> None:
        set_up = getattr(self, 'set_up', None)
        if set_up is not None:
            try:
                set_up()
            except Exception as e:
                self.logger.error(f'Exception in test set up: {str(e)}')
                raise e

    def tearDown(self) -> None:
        tear_down = getattr(self, 'tear_down', None)
        if tear_down is not None:
            try:
                tear_down()
            except Exception as e:
                self.logger.error(f'Exception in test tear down: {str(e)}')
                raise e

    @classmethod
    def tearDownClass(cls) -> None:
        tear_down_class = getattr(cls, 'tear_down_class', None)
        if tear_down_class is not None:
            try:
                if cls.class_logger is None:
                    cls._get_class_logger()
                cls.class_logger.run(f'Closing test case, running tear_down_class...')
                tear_down_class()
            except Exception as e:
                cls.class_logger.error(f'Exception in test case tear down: {str(e)}')
                raise e

    def dbg(self, msg, *args, **kwargs):
        if self.logger is not None:
            self.logger.debug(msg, *args, **kwargs)
        if self.console_logger is not None:
            self.console_logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        if self.logger is not None:
            self.logger.info(msg, *args, **kwargs)
        if self.console_logger is not None:
            self.console_logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.logger is not None:
            self.logger.warning(msg, *args, **kwargs)
        if self.console_logger is not None:
            self.console_logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.logger is not None:
            self.logger.error(msg, *args, **kwargs)
        if self.console_logger is not None:
            self.console_logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.logger is not None:
            self.logger.critical(msg, *args, **kwargs)
        if self.console_logger is not None:
            self.console_logger.critical(msg, *args, **kwargs)

    def _fail(self, msg, *args, **kwargs):
        if self.logger is not None:
            self.logger.fail(msg, *args, **kwargs)
        if self.console_logger is not None:
            self.console_logger.fail(msg, *args, **kwargs)

    def _run(self, msg, *args, **kwargs):
        if self.logger is not None:
            self.logger.run(msg, *args, **kwargs)
        if self.console_logger is not None:
            self.console_logger.run(msg, *args, **kwargs)

    def ok(self, msg, *args, **kwargs):
        if self.logger is not None:
            self.logger.ok(msg, *args, **kwargs)
        if self.console_logger is not None:
            self.console_logger.ok(msg, *args, **kwargs)

    def inter_res(self, msg, *args, **kwargs):
        if self.console_logger is not None:
            self.console_logger.inter_res(msg, *args, **kwargs)

    def skip(self, msg, *args, **kwargs):
        if self.logger is not None:
            self.logger.skip(msg, *args, **kwargs)
        if self.console_logger is not None:
            self.console_logger.skip(msg, *args, **kwargs)

    def run(self, result=None):
        self._get_logger(self._testMethodName)
        if result.testsRun:
            self.inter_res(
                f'\n    Tests run: {result.testsRun}'
                f'\n    Tests errors: {len(result.errors)}'
                f'\n    Tests failed: {len(result.failures)}'
                f'\n    Tests skipped: {len(result.skipped)}'
            )
        # Determining if test case or whole class is set to skip
        testMethod = getattr(self, self._testMethodName)
        _is_test_skipped = (getattr(self.__class__, "__unittest_skip__", False) or
                            getattr(testMethod, "__unittest_skip__", False))
        if _is_test_skipped:
            _is_test_skipped_why = (getattr(self.__class__, '__unittest_skip_why__', '') or
                                    getattr(testMethod, '__unittest_skip_why__', ''))
            self.skip(f'skipped, reason: {_is_test_skipped_why}')

        st_time = time.perf_counter()
        testMethod = getattr(self, self._testMethodName)
        if getattr(testMethod, "__runtest_rerun__", False) and \
                getattr(testMethod, "__runtest_rerun_retries__", False):
            rerun_attempts_left = testMethod.__runtest_rerun_retries__
        else:
            rerun_attempts_left = 0

        # Printing running test method only if it is not skipped
        if not _is_test_skipped:
            self._run('Running test method...')

        failures_before = len(result.failures)  # number of failed tests before starting

        super(CustomTestCase, self).run(result)

        # TODO: add rerun error if needed
        # TODO: do we need to add rerun failures to total failures?
        if rerun_attempts_left and failures_before < len(result.failures):  # If test if failed
            number_of_rerun_set = rerun_attempts_left
            while True:
                if rerun_attempts_left == 0:
                    self._fail(f'Test failed after {number_of_rerun_set} attempts')
                    break
                elif len(result.failures) == 0:
                    self.ok(f'Test OK after {number_of_rerun_set - rerun_attempts_left} attempts')
                    break
                else:
                    result.failures.pop(-1)  # Removing last failure result
                    self.info(f'Test failed but rerun is set: number of attempts left {rerun_attempts_left}')
                    rerun_attempts_left -= 1
                    super(CustomTestCase, self).run(result)

        # Printing test method execution time only if it is not skipped
        if not _is_test_skipped:
            self.info(f'test execution time is {round(time.perf_counter() - st_time, 2)} seconds')

        self.file_handler.close()
        self.logger.removeHandler(self.file_handler)

    def subTest(self, msg='', **params):
        if params.get('value', None) is None:
            self._run(f'subtest {msg}')
        else:
            self._run(f'subtest {msg} value {params["value"]}')
        return super(CustomTestCase, self).subTest(msg, **params)

    def _feedErrorsToResult(self, result, errors):
        ok = True
        for test, exc_info in errors:
            if isinstance(test, _SubTest):
                if exc_info is not None:
                    self._fail(test._subDescription() + ' ' + self._parse_error(exc_info))
                    ok = False
                else:
                    self.ok(test._subDescription())
                result.addSubTest(test.test_case, test, exc_info)
                result.testsRun += 1  # counting SubTests as well
            elif exc_info is not None:
                ok = False
                if issubclass(exc_info[0], self.failureException):
                    self._fail(self._parse_error(exc_info))
                    result.addFailure(test, exc_info)
                else:
                    self.error(self._parse_error(exc_info))
                    result.addError(test, exc_info)
        if ok:
            self.ok('OK')

    # noinspection PyMethodMayBeStatic
    def _parse_error(self, exc_info):
        exctype, value, tb = exc_info
        tb_e = traceback.TracebackException(
            exctype, value, tb, limit=0, capture_locals=False)
        return ('\n'.join(list(tb_e.format_exception_only()))).strip()

    @classmethod
    def case_execution_time(cls):
        if cls.test_case_st_time is not None:
            if cls.class_logger is None:
                cls._get_class_logger()
            cls.class_logger.info(f'Test case execution time is '
                                  f'{round(time.perf_counter() - cls.test_case_st_time, 2)} seconds\n')
            cls.class_file_handler.close()
            cls.class_logger.removeHandler(cls.class_file_handler)


def rerun(rerun_retries):
    """
    Rerun decorator that can be used to run test again if it is failed
    Example:
        @rerun(3)
        def test_sample(self):
            pass

    :param int rerun_retries: number of retries applied to a method if it fails
    """

    def decorator(test_item):
        if isinstance(rerun_retries, int) and rerun_retries > 1:
            test_item.__runtest_rerun__ = True
            test_item.__runtest_rerun_retries__ = rerun_retries
        return test_item

    return decorator
