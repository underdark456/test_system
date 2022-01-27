import logging

LOGGING = 'logging'
CONSOLE_LOGGING = 'console_logging'
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
# ERROR = logging.ERROR
ERROR = 55  # Errors should be always output
CRITICAL = logging.CRITICAL
FAIL = 60  # Fails should be always output
RUN = 15  # the value is low enough to let the logging level not to output run messages
SKIP = 45
OK = 25
INTER_RES = 26


class CustomLogger(logging.getLoggerClass()):
    """
    """

    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        logging.addLevelName(ERROR, 'ERROR')
        logging.addLevelName(FAIL, 'FAIL')
        logging.addLevelName(RUN, 'RUN')
        logging.addLevelName(OK, 'OK')
        logging.addLevelName(INTER_RES, 'INTERMEDIATE RESULTS')
        logging.addLevelName(SKIP, 'SKIP')

    def fail(self, msg, *args, **kwargs):
        if self.isEnabledFor(FAIL):
            self._log(FAIL, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(ERROR):
            self._log(ERROR, msg, args, **kwargs)

    def run(self, msg, *args, **kwargs):
        if self.isEnabledFor(RUN):
            self._log(RUN, msg, args, **kwargs)

    def ok(self, msg, *args, **kwargs):
        if self.isEnabledFor(OK):
            self._log(OK, msg, args, **kwargs)

    def inter_res(self, msg, *args, **kwargs):
        if self.isEnabledFor(INTER_RES):
            self._log(INTER_RES, msg, args, **kwargs)

    def skip(self, msg, *args, **kwargs):
        if self.isEnabledFor(SKIP):
            self._log(SKIP, msg, args, **kwargs)

    @staticmethod
    def get_console_logger() -> logging.Logger:
        """
        Get an instance of the Python Logger class.
        A file handler is added to the Logger instance.

        :returns logging.Logger logger: a Logger instance
        """
        logger = logging.getLogger('Global logger')
        logger.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_format = logging.Formatter(
            fmt='%(asctime)s : %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

        return logger
