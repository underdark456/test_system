import ipaddress
import random

# from src.drivers.uhp import uhp_telnet_driver
from src.enum_types_constants import ModelTypes, ModelTypesStr
from src.exceptions import InvalidOptionsException


def get_model_from_serial(serial: int):
    """
    Get UHP hardware model based on the serial number

    :param int serial: serial number of UHP
    :returns str model: UHP model
    """
    last_five_digits = int(str(serial)[-5:])
    if last_five_digits in range(20000, 30000):
        return 'UHP1000'
    elif last_five_digits in range(40000, 42000):
        return ModelTypesStr.UHP100
    elif last_five_digits in range(42000, 45000):
        return ModelTypesStr.UHP100X
    elif last_five_digits in range(35000, 36200):
        return ModelTypesStr.UHP200
    elif last_five_digits in range(36200, 40000) or last_five_digits in range(90000, 91000):
        return ModelTypesStr.UHP200X
    else:
        return None


def get_default_gateway(ip_address, prefix=24):
    """
    Get default gateway (first host in the network) out of the provided IPv4 address and prefix

    :param str ip_address: IPv4 address
    :param Optional int prefix: prefix of the network, by default /24
    :raises InvalidOptionsException: if provided options are invalid
    :returns str: default gateway of the network

    """
    if prefix not in range(0, 33):
        raise InvalidOptionsException(f'passed IPv4 prefix {prefix} is not in a valid range 0-32')
    try:
        ipaddress.IPv4Network(ip_address)
    except ipaddress.AddressValueError:
        raise InvalidOptionsException(f'passed IPv4 address is not a valid IPv4 address: {ip_address}')
    _router_network = ipaddress.IPv4Network(f'{ip_address}/{prefix}', strict=False)
    _hosts = _router_network.hosts()
    try:
        _default_gateway = next(_hosts)
        return str(_default_gateway)
    except StopIteration:
        raise InvalidOptionsException(f'Cannot get default gateway out of the provided {ip_address}/{prefix}')


def get_random_string(length=10, random_length=False, lower_case=True, upper_case=True, digits=True, punctuation=True):
    """
    Get a random characters string

    :param int length: the desired length of the string
    :param bool random_length: if True the string length will be random ranged 1 - `length`
    :param bool lower_case: if True include lower case characters
    :param bool upper_case: if True include upper case characters
    :param bool digits: if True include digits
    :param bool punctuation: if Ture include other characters
    """
    _chars = ''
    if lower_case is True:
        _chars += 'abcdefghijklmnopqrstuvwxyz'
    if upper_case is True:
        _chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if digits is True:
        _chars += '0123456789'
    if punctuation is True:
        _chars += r"""!"#$%&'()*+,-.:;<=>?@[\]^_`{|}~"""

    if len(_chars) == 0:
        raise Exception('Character set is empty, please pass some of the char groups flags: '
                        '`lower_case`, `upper_case`, `digits`, `punctuation`')
    random_string = ''
    if random_length:
        for _ in range(random.randint(1, length)):
            random_string += _chars[random.randint(0, len(_chars) - 1)]
    else:
        for _ in range(length):
            random_string += _chars[random.randint(0, len(_chars) - 1)]
    return random_string


def serial_to_human_read(serial):
    """
    Transform UHP serial number representation, i.e. 50790707 to web-interface representation '3.7.1.33'

    :param int serial: NMS, SNMP representation of UHP serial number
    :returns str serial: web-interface representation of the UHP serial number
    """
    _octets = []
    _serial = hex(serial)[2:]
    for i in range(len(_serial) - 2, -3, -2):
        if i < 0:
            _octet = _serial[:i+2].lstrip('0')
            _octets.append(_octet)
        else:
            _octet = _serial[i:i+2].lstrip('0')
            _octets.append(_octet)
    _octets.reverse()
    return '.'.join(_octets)


def is_ipv4(uhp_ip_mask):
    try:
        ipaddress.IPv4Network(''.join(uhp_ip_mask.split()), strict=False)
        return True
    except ipaddress.AddressValueError:
        return False


def is_ipv6(uhp_ip_mask):
    try:
        ipaddress.IPv6Network(''.join(uhp_ip_mask.split()), strict=False)
        return True
    except ipaddress.AddressValueError:
        return False


# def prepare_default_config1(uhp_list):
#     """Reset all uhps listed in `uhp_list` to default. Save to Config1 and Config2"""
#     for uhp in uhp_list:
#         t = uhp_telnet_driver.UhpTelnetDriver(uhp)
#         res = t.default(vlan=12, default_gateway='10.56.12.1')
#         print(f'Default {uhp} result: {res}')
#         # res = t.send('conf save 1')
#         # print(f'Conf save 1 {uhp} result: {res.decode("utf-8")}')
#         t.close()


if __name__ == '__main__':
    pass
