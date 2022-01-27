"""Running tests"""
import datetime
import os
import sys
import time
import warnings
from collections import defaultdict
from unittest import result
from unittest.signals import registerResult
from src.options_providers.options_provider import OptionsProvider

__unittest = True


class _WritelnDecorator(object):
    """Used to decorate file-like objects with a handy 'writeln' method"""
    def __init__(self,stream):
        self.stream = stream

    def __getattr__(self, attr):
        if attr in ('stream', '__getstate__'):
            raise AttributeError(attr)
        return getattr(self.stream,attr)

    def writeln(self, arg=None):
        if arg:
            self.write(arg)
        self.write('\n') # text-mode streams translate to \r\n if needed


class TextTestResult(result.TestResult):
    """A test result class that can print formatted text results to a stream.

    Used by TextTestRunner.
    """
    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, stream, descriptions, verbosity, queue=None):
        super(TextTestResult, self).__init__(stream, descriptions, verbosity)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions
        self.queue = queue

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        if self.descriptions and doc_first_line:
            return '\n'.join((str(test), doc_first_line))
        else:
            return str(test)

    def startTest(self, test):
        # print(self.failures)
        # print(self.skipped)
        # print(self.errors)
        # print(self.queue)
        super(TextTestResult, self).startTest(test)
        pass

    def addSuccess(self, test):
        super(TextTestResult, self).addSuccess(test)
        pass

    def addError(self, test, err):
        super(TextTestResult, self).addError(test, err)
        pass

    def addFailure(self, test, err):
        super(TextTestResult, self).addFailure(test, err)
        pass

    def addSkip(self, test, reason):
        super(TextTestResult, self).addSkip(test, reason)
        pass

    def addExpectedFailure(self, test, err):
        super(TextTestResult, self).addExpectedFailure(test, err)
        pass

    def addUnexpectedSuccess(self, test):
        super(TextTestResult, self).addUnexpectedSuccess(test)
        pass

    def printErrors(self):
        pass

    def printErrorList(self, flavour, errors):
        pass


class TextTestRunner(object):
    """A test runner class that displays results in textual form.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """
    resultclass = TextTestResult

    def __init__(self, stream=None, descriptions=True, verbosity=0,
                 failfast=False, buffer=False, resultclass=None, warnings=None,
                 *, tb_locals=False):
        """Construct a TextTestRunner.

        Subclasses should accept **kwargs to ensure compatibility as the
        interface changes.
        """
        if stream is None:
            stream = sys.stderr
        self.stream = _WritelnDecorator(stream)
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = failfast
        self.buffer = buffer
        self.tb_locals = tb_locals
        self.warnings = warnings
        if resultclass is not None:
            self.resultclass = resultclass
        self.suite_name = None
        self.suite_st_time = time.perf_counter()
        self.queue = None

    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity, queue=self.queue)

    def run(self, test, **kwargs):
        self.suite_name = kwargs.get('suite_name')
        self.queue = kwargs.get('queue')
        result = self._makeResult()
        registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer
        result.tb_locals = self.tb_locals
        with warnings.catch_warnings():
            if self.warnings:
                # if self.warnings is set, use it to filter all the warnings
                warnings.simplefilter(self.warnings)
                # if the filter is 'default' or 'always', special-case the
                # warnings from the deprecated unittest methods to show them
                # no more than once per module, because they can be fairly
                # noisy.  The -Wd and -Wa flags can be used to bypass this
                # only when self.warnings is None.
                if self.warnings in ['default', 'always']:
                    warnings.filterwarnings('module',
                            category=DeprecationWarning,
                            message=r'Please use assert\w+ instead.')
            startTime = time.perf_counter()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()
            try:
                test(result)
            finally:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()
            stopTime = time.perf_counter()
        timeTaken = stopTime - startTime
        result.printErrors()
        if hasattr(result, 'separator2'):
            self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                             (run, run != 1 and "s" or "", timeTaken))
        self.stream.writeln()

        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
        except AttributeError:
            pass
        else:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        if not result.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = len(result.failures), len(result.errors)
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.write("OK")
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")
        self.logs_output(result)
        return result

    def logs_output(self, _result):
        number_of_run = _result.testsRun
        number_of_failures = len(_result.failures)
        number_of_errors = len(_result.errors)
        number_of_skip = len(_result.skipped)

        _failures = defaultdict(int)
        _errors = defaultdict(int)
        for fail in _result.failures:
            if fail[0].__class__.__name__ == '_SubTest':
                # _failures[fail[0].test_case.__class__.__name__] += 1
                _failures[fail[0].test_case] += 1
            else:
                _failures[fail[0]] += 1
        for error in _result.errors:
            if error[0].__class__.__name__ == '_SubTest':
                _errors[error[0].test_case.__class__.__name__] += 1
            elif error[0].__class__.__name__ == '_ErrorHolder':
                _errors[error[0].description] += 1
            else:
                _errors[error[0].__class__.__name__] += 1

        # Setting up logger
        datetime_now = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        system_options = OptionsProvider.get_system_options('global_options')
        log_dir = system_options["LOG_DIR"]
        if not os.path.isdir(log_dir):
            os.mkdir(f'{system_options["LOG_DIR"]}')

        # File logger setup block
        if self.suite_name is None:
            self.suite_name = 'test_suite'
        else:
            self.suite_name = self.suite_name.split('.')[0]

        with open(f'{log_dir}{self.suite_name}.log', 'w') as log_file:
            log_file.write(f'Test suite `{self.suite_name}` execution time '
                           f'{round(time.perf_counter() - self.suite_st_time, 2)} seconds:\n')
            log_file.write(f'RUN {number_of_run} test(s)\n')
            log_file.write(f'ERROR {number_of_errors} test(s)\n')
            log_file.write(f'FAIL {number_of_failures} test(s)\n')
            log_file.write(f'SKIP {number_of_skip} test(s)\n\n')

            if number_of_errors > 0:
                log_file.write('Tests errors:\n')
                for key, value in _errors.items():
                    log_file.write(f'{value} in {key}\n')
                log_file.write('\n')

            if number_of_failures > 0:
                log_file.write('Tests failures including subtests:\n')
                for key, value in _failures.items():
                    log_file.write(f'{value} in {key}\n')
                log_file.write('\n')

            if number_of_skip > 0:
                pass
