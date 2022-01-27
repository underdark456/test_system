import math
from abc import ABC
from time import time

_DEFAULT_STEPS = 10

_GET_CALL = 1
_SET_CALL = 2


class InvalidStepsException(Exception):
    pass


class InvalidCallException(Exception):
    pass


class AbstractUhpSnmp(ABC):
    GET_AVG = 1
    """ Average of `steps`"""
    GET_MAX = 2
    """ Max of `steps`"""
    GET_MIN = 3
    """ Min of `steps`"""
    GET_MIN_AVG_MAX = 4
    """ Cortege (`min`, `avg`, `max`) of `steps`"""
    GET_AS_SPEED = 5

    def __init__(self, executor, ip, public='public', private='private', port=161):
        self._ip = ip
        self._executor = executor
        self._public = public
        self._private = private
        self._port = port

    def _call(self, call_type, oid, value=None, request_type=None, steps=_DEFAULT_STEPS):

        if _SET_CALL == call_type:
            return self._executor.set(self._ip, self._port, self._private, oid, value)
        elif _GET_CALL == call_type:
            if request_type is None:
                return self._executor.get(self._ip, self._port, self._public, oid)
            else:
                start_time = time()
                values = self._exec_combine_get(oid, steps)
                if values is None:
                    return None
                end_time = time()
                time_lapse = end_time - start_time

            if self.GET_AVG == request_type:
                return math.ceil(sum(values) / len(values))
            elif self.GET_MAX == request_type:
                return max(values)
            elif self.GET_MIN == request_type:
                return min(values)
            elif self.GET_MIN_AVG_MAX == request_type:
                min_val = min(values)
                avg_val = math.ceil(sum(values) / len(values))
                max_val = max(values)
                return min_val, avg_val, max_val
            elif self.GET_AS_SPEED == request_type:
                prev = 0
                bytes_acc = []
                for bytes_num in values:
                    if prev > bytes_num:
                        bytes_num = 0xFFFFFFFF - prev + bytes_num
                    if 0 == prev:
                        prev = bytes_num
                        continue
                    bytes_acc.append(bytes_num - prev)
                    prev = bytes_num
                return math.ceil(sum(bytes_acc) / time_lapse * 8)  # bit per second
        else:
            raise InvalidCallException

    def _exec_combine_get(self, oid, steps):
        steps = self._prepare_steps(steps)
        values = []
        for i in range(0, steps):
            res = self._executor.get(self._ip, self._port, self._public, oid)
            if res is None:
                return None
            else:
                values.append(int(res))
        return values

    @staticmethod
    def _prepare_steps(steps):
        if not steps:
            steps = _DEFAULT_STEPS
        elif not isinstance(steps, int) or 0 >= steps:
            raise InvalidStepsException
        return steps

    def get_error(self):
        return self._executor.get_error()
