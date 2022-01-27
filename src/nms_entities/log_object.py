import time
from abc import ABC, abstractmethod

from src.constants import NO_ERROR
from src.drivers.abstract_http_driver import API
from src.exceptions import NmsErrorResponseException, NotImplementedException


class LogObject(ABC):

    _driver = None

    def wait_log_message(self, obj, message=None, fault=True, info=True, warning=True, timeout=60, step_timeout=5):
        """
        Wait for log message to appear in logs

        :param AbstractBasicObject obj: an object that is expected to be referred in logs
        :param str message: log message that is expected to be logged. If None, any message is awaited. Default is None
        :param int timeout: timeout in seconds to await for the message. Default is 60 seconds
        :param int step_timeout: step in seconds between log queries. Default is 5 seconds
        :param bool fault: if True FAULT messages are included, otherwise not. Default is True
        :param bool info: if True INFO messages are included, otherwise not. Default is True
        :param bool warning: if True WARNING messages are included, otherwise not. Default is True

        :returns bool: log message if the expected log message is caught, otherwise False
        """

        if self._driver.get_type() != API:
            raise NotImplementedException('Method currently implemented only in API driver')
        path = self._get_log_path()
        start = round(float(time.time()), 3)
        end = start + timeout
        payload = {
            'start': start,
            'end': end,
            'fault': fault,
            'info': info,
            'warning': warning,
        }
        object_name = obj.get_param('name')
        while True:
            reply, error, error_code = self._driver.custom_post(path, payload=payload)
            if error_code == NO_ERROR and error == '':
                for rec in reply:
                    if rec['na'] == object_name:
                        if message is None:
                            return f'{rec["na"]} {rec["me"]}'
                        else:
                            if rec['me'] == message:
                                return f'{rec["na"]} {rec["me"]}'
            else:
                raise NmsErrorResponseException(f'Cannot get logs: error_code={error_code}, error={error}')
            t = int(time.time())
            if timeout < t - start:
                return False
            time.sleep(step_timeout)

    def get_raw_logs(self, start=None, end=None, fault=True, info=True, warning=True):
        """
        Get raw logs from object

        :param float start: number of ticks since epoch to get logs from. Default is the current time minus an hour
        :param float end: number of ticks since epoch to get logs to. Default is the current time
        :param bool fault: if True FAULT messages are included, otherwise not. Default is True
        :param bool info: if True INFO messages are included, otherwise not. Default is True
        :param bool warning: if True WARNING messages are included, otherwise not. Default is True

        :raises NotImplementedException: if the driver in use is not API
        :raises NmsErrorResponseException: if there is an error in the response
        :returns list reply: logs messages as a list of dictionaries
        """
        if self._driver.get_type() != API:
            raise NotImplementedException('Method currently implemented only in API driver')
        path = self._get_log_path()
        if end is None:
            # End of logs is the current time
            end = round(float(time.time()), 3)
        if start is None:
            # Start of logs is the current time minus 3600 seconds (one hour)
            start = end - 60 ** 2
        payload = {
            'start': start,
            'end': end,
            'fault': fault,
            'info': info,
            'warning': warning,
        }
        reply, error, error_code = self._driver.custom_post(path, payload=payload)
        if error_code == NO_ERROR and error == '':
            return reply
        else:
            raise NmsErrorResponseException(f'Cannot get logs: error_code={error_code}, error={error}')

    @abstractmethod
    def _get_log_path(self) -> str:
        pass
