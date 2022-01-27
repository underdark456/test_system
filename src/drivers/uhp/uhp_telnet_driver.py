import ipaddress
import re
import socket
import telnetlib
import time

from src.class_logger import class_logger_decorator, debug
from src.drivers.uhp.constants import PRESS_SPACE_TO_CONTINUE
from src.exceptions import DriverInitException, InvalidOptionsException


@class_logger_decorator
class UhpTelnetDriver:
    """
    The class features methods to get data from UHP routers via Telnet as well as set parameters.
    The telnet connection must be closed.

    :param str router_address: UHP router IP address
    :param int timeout: telnet connection timeout value in seconds
    """

    def __init__(
            self,
            router_address: str = '127.0.0.1',
            vlan: int = 0,
            timeout: int = 5,
            connect=True,
    ):
        """
        Construct an instance of UhpTelnetDriver

        :param str router_address: UHP router local access IP address
        :param int vlan: UHP router local access VLAN
        :param int timeout: GET requests timeout value in seconds
        :param bool connect: if True connect to UHP via telnet upon initialization
        """
        self._router_address = router_address
        if not isinstance(vlan, int):
            raise DriverInitException(f'Passed VLAN value is not of int type: {type(vlan)}')
        elif vlan not in range(0, 4096):
            raise DriverInitException(f'VLAN value {vlan} is not in correct range 0 - 4095')
        self._vlan = vlan
        self._timeout = timeout
        if connect:
            self._connect()
        # atexit.register(self.close)

    def _connect(self, timeout=None):
        if timeout is None:
            timeout = self._timeout
        try:
            self._telnet = telnetlib.Telnet(self._router_address, timeout=timeout)
            result = self._telnet.read_until(b'#', timeout=timeout)
            if result.find(b'#') == -1:
                raise DriverInitException(f'UHP {self._router_address}: no hashtag in response')
        except Exception as exc:
            raise DriverInitException(f'Cannot connect to UHP {self._router_address} via telnet: {exc}')
        debug(f'Connected to {self._router_address} via telnet')

    def get_sw_version(self):
        show_system = self.get_raw_result('show system').decode()
        ver_index = show_system.find('Ver:')
        sn_index = show_system.find('SN:')
        if ver_index != -1 and sn_index != -1 and sn_index > ver_index:
            version = show_system[ver_index + 4:sn_index].lstrip().rstrip()
            return version.split()[0].rstrip()
        return None

    def show_arp(self):
        """
        Issue `show arp` command

        :returns dict results: a dictionary containing the following keys and their values:
        `free_entries`, `purge_interval`, `arp_requests`, and `arp_answers`
        """
        debug(f'{self._router_address}: issuing `show arp` command...')
        self._telnet.write(b'show arp\r')
        result_bytes = self._get_all_results()
        str_response = result_bytes.decode()

        free_entries_re = re.compile(r'Free entries:\s[0-9]+')
        free_entries = free_entries_re.search(str_response)
        if free_entries is not None:
            free_entries = free_entries.group()[13:]
        else:
            free_entries = None

        purge_interval_re = re.compile(r'Purge interval\s[0-9]+')
        purge_interval = purge_interval_re.search(str_response)
        if purge_interval is not None:
            purge_interval = purge_interval.group()[14:]
        else:
            purge_interval = None

        arp_requests_re = re.compile(r'ARP requests:\s[0-9]+')
        arp_requests = arp_requests_re.search(str_response)
        if arp_requests is not None:
            arp_requests = arp_requests.group()[14:]
        else:
            arp_requests = None

        arp_answers_re = re.compile(r'ARP answers:\s[0-9]+')
        arp_answers = arp_answers_re.search(str_response)
        if arp_answers is not None:
            arp_answers = arp_answers.group()[13:]
        else:
            arp_answers = None

        results = {
            'free_entries': free_entries,
            'purge_interval': purge_interval,
            'arp_requests': arp_requests,
            'arp_answers': arp_answers
        }
        return results

    def get_raw_result(self, command='help'):
        """
        Issue a specified telnet command. Get unprocessed results.

        :param str command: a command to execute
        :returns bytes results_bytes: resulting bytes
        """
        debug(f'{self._router_address}: issuing `{command}` command...')

        self._telnet.write(f'{command}\r'.encode('UTF-8'))
        result_bytes = self._get_all_results()
        return result_bytes

    def clear_arp(self):
        """
        Issue `clear arp` command.
        """
        debug(f'{self._router_address}: issuing clear arp command...')
        self._telnet.write(b'clear arp\r')

    def show_profile(self):
        pass

    def _get_all_results(self):
        """
        Get all results of the issued command. The method sends `space bar` key while there is
        'Press SPACE to continue Q to exit' message in the output.

        :returns bytes result_bytes: a byte string containing the whole output
        """
        result_bytes = b''
        # As a precaution instead of a while loop a long for loop is used
        for _ in range(1000):
            byte_response = self._telnet.read_until(PRESS_SPACE_TO_CONTINUE.encode('utf-8'), timeout=self._timeout)
            result_bytes += byte_response
            str_response = byte_response.decode()
            if str_response.find(PRESS_SPACE_TO_CONTINUE) != -1:
                self._telnet.write(b'\x20')
            else:
                break
        return result_bytes

    def wait_message(self, message=PRESS_SPACE_TO_CONTINUE, timeout=20):
        """Wait until a passed message appear in the console """
        st_time = time.perf_counter()
        byte_response = self._telnet.read_until(message.encode('utf-8'), timeout=timeout)
        debug(f'{message} wait time {time.perf_counter() - st_time} seconds')
        return byte_response

    def close(self):
        """
        Close current telnet connection.
        """
        self._telnet.write(b'exit\r')
        self._telnet.close()
        debug(f'{self._router_address} telnet connection is closed')

    def send(self, command='help'):
        """Alias for `get_raw_result` method. Issue a specified telnet command. Get unprocessed results.

        :param str command: a command to execute
        :returns bytes results_bytes: resulting bytes
        """
        return self.get_raw_result(command)

    def reboot(self):
        """Issue reboot telnet command and confirming it"""
        debug(f'{self._router_address}: issuing `reboot` command...')
        self._telnet.write(f'reboot\r'.encode('UTF-8'))
        self._telnet.read_until('(y/n)?'.encode('utf-8'), timeout=self._timeout)
        self._telnet.write(f'y\r'.encode('UTF-8'))

    def default(self, default_gateway=None, vlan=None, lic_clear=False, cl_in_eth=False):
        """
        Loading default UHP config

        :param str default_gateway: default gateway IPv4 address
        :param int vlan: vlan number to set UHP IPv4 address and default gateway
        :param bool lic_clear: if license clear is needed
        :param bool cl_in_eth: if interface ethernet clear is needed
        :raises InvalidOptionsException: if there are invalid default_gateway or vlan number passed
        :returns bool: True if default is successful
        """
        # Processing vlan parameter
        if vlan is None:
            vlan = self._vlan
        elif not isinstance(vlan, int):
            raise DriverInitException(f'Passed VLAN value is not of int type: {type(vlan)}')
        elif vlan not in range(0, 4096):
            raise DriverInitException(f'VLAN value {vlan} is not in correct range 0 - 4095')

        # Processing default_gateway parameter
        if default_gateway is not None:
            try:
                ipaddress.IPv4Network(default_gateway)
            except ipaddress.AddressValueError:
                raise InvalidOptionsException(f'passed default gateway is not a valid IPv4 address: {default_gateway}')
        # Setting default_gateway to the first valid address of a network {self._router_address}/24
        else:
            _hosts = ipaddress.IPv4Network(f'{self._router_address}/24', strict=False).hosts()
            default_gateway = str(next(_hosts))

        self.get_raw_result('ip update off')

        self._telnet.write(f'config load default all\r'.encode('UTF-8'))
        try:
            self.wait_message('Ethernet-1 UP')
        except EOFError:
            time.sleep(15)
            self._connect()

        if lic_clear:
            self.uhp_telnet.get_raw_result('lic clear')

        if cl_in_eth:
            self.get_raw_result('cl in eth')

        # Setting UHP IPv4 address to the address initialized during initialization
        _res = self.get_raw_result(f'ip address {self._router_address} /24 {vlan}')
        if _res.find(b'Parameter out of range') != -1:
            raise InvalidOptionsException('Cannot apply IP address in default() method')

        # Setting local oscillators to zero
        _res = self.get_raw_result('rf lo 0 0 0')
        if _res.find(b'Parameter out of range') != -1:
            raise InvalidOptionsException('Cannot apply IP address in default() method')

        # Setting default gateway either to the passed one or to the calculated one
        _res = self.get_raw_result(f'ip route 0.0.0.0 0.0.0.0 {default_gateway} {vlan}')
        if _res.find(b'Parameter out of range') != -1:
            raise InvalidOptionsException('Cannot apply IP address in default() method')

        self._telnet.write(f'conf save\r'.encode('UTF-8'))
        try:
            self.wait_message('saved')
        except EOFError:
            time.sleep(20)
            self._connect()

        self.reboot()
        self.close()

        st_time = time.perf_counter()
        # In some cases reboot can last up to 40 seconds, that is why timeout set to a high value
        self._connect(timeout=60)
        debug(f'reboot time {time.perf_counter() - st_time} seconds')
        time.sleep(10)
        self.get_raw_result('ip update on')
        return True

    def ping(self, ip_address=None, num=5, length=40, pps=1, vlan=0):
        """
        Issue ping command from UHP

        :param str ip_address: IPv4 destination address, if None set to UHP own IP address
        :param int num: number of ICMP echo requests to send, default is 5
        :param int length: length in bytes of every request
        :param int pps: ICMP echo requests per second
        :param int vlan: vlan used to issue requests
        :raises InvalidOptionsException: if passed parameters are not valid
        :returns bool: True if ALL echo requests are responded, otherwise False
        """
        if ip_address is None:
            ip_address = self._router_address
        else:
            try:
                ipaddress.IPv4Address(ip_address)
            except ipaddress.AddressValueError as exc:
                raise InvalidOptionsException(f'ip_address must a valid IPv4 address, passed value {ip_address}')
        if num not in range(1, 1000001):
            raise InvalidOptionsException(f'num must be in range 1-1000000, passed value {num}')
        if length not in range(40, 1501):
            raise InvalidOptionsException(f'length must be in range 40-1500, passed value {length}')
        if pps not in range(1, 10001):
            raise InvalidOptionsException(f'pps must be in range 1-10000, passed value {pps}')
        if vlan not in range(0, 4096):
            raise InvalidOptionsException(f'vlan must be in range 0-4095, passed value {vlan}')

        debug(f'{self._router_address}: issuing `ping {ip_address} {num} {length} {pps} {vlan}` command...')
        self._telnet.write(f'ping {ip_address} {num} {length} {pps * 1000} {vlan}\r'.encode('UTF-8'))
        res1 = self.wait_message(f'{num} packets transmitted', timeout=int(num * pps + 5))
        if res1.decode().find(f'{num} packets transmitted') == -1:
            return False
        result_bytes = self._get_all_results()
        if result_bytes.decode().find(f'0 packets lost (0%)') == -1:
            return False
        return True


if __name__ == '__main__':
    try:
        tn = telnetlib.Telnet('10.56.24.19', timeout=3)
    except socket.timeout:
        print('Socket timeout')