from time import time, sleep

from pysnmp.hlapi import SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, \
    OctetString, ObjectIdentity, cmdgen, Integer32, Gauge32

from src.exceptions import DriverInitException


class SnmpExecutor(object):
    def __init__(self, delay=0.100):
        """

        :param delay: delay between requests in seconds
        """
        self._delay = delay * 1000000
        self._last_request_time = 0
        self._error = None

    def set_delay(self, delay: float):
        self._delay = delay

    def get(self, ip, port, access, target):
        var_binds = self._execute(
            cmdgen.getCmd,
            CommunityData(access, mpModel=0),
            UdpTransportTarget((ip, port)),
            ObjectType(ObjectIdentity(target))
        )
        if self._error is None:
            return var_binds[0][1].prettyPrint()
        else:
            return None

    def set(self, ip, port, access, target, value, value_type=None):
        if value_type == 'gauge32':
            val = Gauge32(value)
        elif isinstance(value, int):
            val = Integer32(value)
        else:
            val = OctetString(value)
        self._execute(
            cmdgen.setCmd,
            CommunityData(access, mpModel=1),
            UdpTransportTarget((ip, port)),
            ObjectType(ObjectIdentity(target), val)
        )
        return self._error is None

    def _execute(self, cmd, community_data, transport, payload):
        self._error = None
        self._wait_timeout()
        error_indication, error_status, error_index, var_binds = next(
            cmd(
                SnmpEngine(),
                community_data,
                transport,
                ContextData(),
                payload
            )
        )
        self._last_request_time = self._get_time()
        if error_indication:
            self._error = error_indication
            return None
        elif error_status:
            self._error = '{} at {}'.format(
                error_status.prettyPrint(),
                error_index and var_binds[int(error_index) - 1][0] or '?'
            )
            return None
        return var_binds

    @staticmethod
    def _get_time():
        return int(round(time() * 1000000))

    def _wait_timeout(self):
        current_time = self._get_time()
        time_passed = current_time - self._last_request_time
        if self._delay > time_passed:
            delay = (self._delay - time_passed) / 1000000
            sleep(delay)

    def get_error(self):
        return self._error


if __name__ == '__main__':
    s = SnmpExecutor()
    print(s.set('10.0.2.156', 161, 'private', '.1.3.6.1.4.1.8000.22.1.3.0', 'modulator tx on'))

