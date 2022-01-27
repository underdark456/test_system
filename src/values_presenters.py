import ipaddress

import numpy


class NotEmptyString:
    """
    The class implements the dunder contains method that checks if a provided string is a non-empty string.
    item in NotEmptyString() >>> True for any item (str) having at least one character.
    Can be used in the form tests where the value must be a non-empty string.
    """

    def __contains__(self, item: str) -> bool:
        """
        Args:
        item (str) - a string to check.

        Returns:
        (bool) - True if the item is a non-empty string, otherwise False.
        """
        return 0 < len(item)


class NotEmpty:
    """
    The class implements the dunder contains method that checks if a passed object is either a non-empty string,
    or the object can be converted to a string with at least one character.
    item in NotEmptyString() >>> True for any item (str) or str(item) having at least one character.
    """

    def __contains__(self, item) -> bool:
        """
        Args:
        item (object) - an object to check.

        Returns:
        (bool) - True if the argument is either a non-empty string or can be converted to a non-empty string,
        otherwise False.
        """
        if str != type(item):
            return 0 < len(str(item))
        else:
            return 0 < len(item)


class AnyValue:
    """
    The class implements a dunder contains method that always returns True.
    item in AnyValue() >>> True for any item (object).
    Can be used in the form tests where the values themselves are irrelevant.
    """

    def __contains__(self, item) -> True:
        """
        Args:
        item (obj) - an object to check.

        Returns:
        True for any provided item.
        """
        return True


class UntypedIntRange:
    """
    Проверяет содержит ли переданный range значение переданное в виде int или str

    if '0' in UntypedIntRange(range(0,1)):
        True
    if 0 in UntypedIntRange(range(0,1)):
        True
    if '0a' in UntypedIntRange(range(0,1)):
        False
    """

    def __init__(self, rng: range):
        self._rng = rng

    def __contains__(self, item):
        try:
            val = int(item)
        except ValueError:
            return False
        return val in self._rng


class StrIntRange(object):
    """
    The class is initialized with the desired range.
    In order to check if an int or str value is in the set range:
        '0' in StrIntRange(range(0,1)) >>> True
         0 in StrIntRange(range(0,1)) >>> True
        '0a' in StrIntRange(range(0,1)) >>> False

    In order to unpack the set range:
        [ *StrIntRange(range(0,2)) ] >>> ['0','1']

    The range can be iterated in the following manner:
        for val in StrIntRange(range(0,2)):
            val - a string element of the range.

    """

    def __init__(self, rng):
        self._rng = rng
        self._i = None

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i >= len(self._rng):
            raise StopIteration
        val = self._rng[self._i]
        self._i += 1
        return str(val)

    def __contains__(self, item):
        """
        Args:
        item (object) - an object to check.

        Returns:
        (bool) - True if the passed object can be converted to an integer,
        and it is in range of the initialized instance of the class,
        otherwise False.
        """
        if bool == type(item):
            return False
        try:
            val = int(item)
        except ValueError:
            return False
        return val in self._rng


class StrFloatRange(object):
    def __init__(self, rng: numpy.arange, precision=1):
        """

        :param rng: `numpy.arange`
        :param precision: `int`
        """
        self._rng = rng
        self._i = None
        self._precision = precision

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i >= len(self._rng):
            raise StopIteration
        val = round(self._rng[self._i], self._precision)
        self._i += 1
        return str(val)

    def __contains__(self, item):
        if bool == type(item):
            return False
        try:
            val = round(float(item), self._precision)
        except ValueError:
            return False
        return val in self._rng


# Separate validation of IPv4 abd IPv6 addresses
class ValidIpAddr(object):
    """
    The class implements a dunder contains method that returns True if the passed item can be converted to
    a valid IP-address.
    item in ValidIpAddr() >>> True if item (object) is a valid IP-address.
    """

    def __contains__(self, item):
        """
        Args:
        item (object) - an object to check.

        Returns:
        (bool) - True if the passed object can be converted to a valid IP-address, otherwise False.
        """
        try:
            ipaddress.IPv4Address(item)
            return True
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            return False


class ValidIpv6Addr(object):
    """
    The class implements a dunder contains method that returns True if the passed item can be converted to
    a valid IPv6-address.
    item in ValidIpv6Addr() >>> True if item (object) is a valid IPv6-address.
    """

    def __contains__(self, item):
        """
        Args:
        item (object) - an object to check.

        Returns:
        (bool) - True if the passed object can be converted to a valid IPv6-address, otherwise False.
        """
        try:
            ipaddress.IPv6Address(item)
            return True
        except (ipaddress.AddressValueError, ipaddress.NetmaskValueError):
            return False


class ValidIpMask(object):
    """
    The class implements a dunder contains method that returns True if the passed item can be converted to
    a valid IP mask.
    The mask object should be passed as a string in one the following formats:
        '/num' - prefix style where int(num) is in range(0,33);
        'a.b.c.d' - netmask style.
    item in ValidIpMask() >>> True if item (str) is a valid IP mask;
    item in ValidIpMask() >>> False if either item (object) is not a string,
                                       or 'a.b.c.d' is not a valid IP address,
                                       or the prefix is not in range(0, 33).
    """

    def __contains__(self, item: str) -> bool:
        """
        Args:
        item (str) - a string to check IP mask validity.

        Returns:
        (bool) - True if the passed object is a string that can be converted to a corresponding IP mask,
        otherwise False.
        """
        if str != type(item):
            return False
        try:
            return item in ValidIpAddr() or \
                   int(item.lstrip('/')) in range(0, 33)
        except (AttributeError, ValueError):
            return False


class ValidIpv6Mask(object):
    """
    The class implements a dunder contains method that returns True if the passed item can be converted to
    a valid IPv6 mask.
    The mask object should be passed as a string in one the following formats:
        '/num' - prefix style where int(num) is in range(0,128);
        'a.b.c.d' - netmask style (NMS accepts netmask style, converting it to the prefix style).
    item in ValidIpv6Mask() >>> True if item (str) is a valid IP mask;
    item in ValidIpv6Mask() >>> False if either item (object) is not a string,
                                       or 'a.b.c.d' is not a valid IP address,
                                       or the prefix is not in range(0, 33).
    """

    def __contains__(self, item: str) -> bool:
        """
        Args:
        item (str) - a string to check IP mask validity.

        Returns:
        (bool) - True if the passed object is a string that can be converted to a corresponding IPv6 mask,
        otherwise False.
        """
        if str != type(item):
            return False
        try:
            return int(item.lstrip('/')) in range(0, 129)
        except (AttributeError, ValueError):
            return False


def get_mixed_values_list(min_val=0, max_val=17000):
    """
    The function is used to get a list of mixed values based on the passed minimum and maximum values,
    their derivatives in the form of min_val - 1, max_val + 1 etc., as well as some predetermined values,
    such as an empty string, -9999999999999, '0123123' etc.
    The types of the elements of the list are int and str.
    The resulting list can be used to check the range of valid values.

    Args:
    min_val (int) - the minimum value of the range.
    max_val (int) - the maximum value of the range.

    Returns:
    (list) - the resulting list.
    """
    return [
        -9999999999999,
        '-999999999999',
        min_val - 1,
        str(min_val),
        max_val,
        max_val + 1,
        min_val + ((max_val - min_val) / 2),
        str(min_val + ((max_val - min_val) / 3)),
        min_val + (((max_val - min_val) / 3) * 2),
        999999999999,
        '999999999999'
        '',
        '0xfffff',
        '0123123',
        'dsfhfjs',
        'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
    ]


TEXT_FIELD_TEST_VALUES = [
    '',
    'simple_text',
    'кириллица',
    '#$%@*(O_o)',
    1221,
    '-1221.09',
    'cat /dev/ass /dev/head',
]

IP_TEST_VALUES = ['1.1.1.1', '256.1.1.1', '1.1.1.1.1', '12.23.45', '1', '22', '192.300.22.1']
IP_MASK_TEST_VALUES = ['/24', '/32', '/33', '/5555555', 20, '255.255.256.0', '/-30', 'qwerty', '/16', '255.255.255.0']

CHECK_BOX_TEST_VALUES = [0, 1, '0', '1', 'text', True, False, '', 'none', 'sudo', '2', 5, None]
CHECK_BOX_VALID_VALUES = StrIntRange(range(0, 2))
CHECK_BOX_TEST_VALUES_ENABLE = [1, '1', True, 'c', 'ON', 'on']

IPV6_TEST_VALUES = [
    '2345:0425:2CA1:0000:0000:0567:5673:23b5',
    '2345:0425:2CA1::0567:5673:23b5',
    '2001:db8::1',
    '2001::0567:7829',
]

IPV6_PREFIX_TEST_VALUES = [
    '/64',
    '/128',
    'qwerty',
    '/0',
    '/333',
]