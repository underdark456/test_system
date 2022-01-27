import asyncio
import importlib.util
import os
import random
import re
import time
from importlib import import_module
from typing import Optional, List

import aiohttp
from bs4 import BeautifulSoup

from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.enum_types_constants import ModelTypesStr
from src.exceptions import InvalidOptionsException, InvalidModeException
from utilities.utils import get_default_gateway, get_model_from_serial

_OPT = 'options'
_SYS = 'system'

API_CONNECT = '0'
CHROME_CONNECT = '1'
FIREFOX_CONNECT = '2'

CONNECTION = 'connection'


class OptionsProvider(object):
    """
    Default reader of configuration(options) files.


    Предоставляет доступ к иерархической структуре конфигурационных файлов.
    При чтении конфигурации из любого пакета, автоматически считывает глобальные файлы конфигурации
    из модуля global_options.

    Любой пакет может содержать файлы options.py и(или) local_options.py из которых будет прочитан словарь
    с именем options. Файл options.py контролируется системой контроля версий(СКВ), файл local_options.py СКВ
    игнорируется и применяется для локального переопределения параметров.

    Options are redefined in the following order:

    global_options.options -> global_options.local_options -> <your_packet>.options -> <your_packet>.local_options

    При слиянии все значения типа dict так же рекурсивно переопределяются

    Sample usage:

    default connection from the global options:

    >>> connection = OptionsProvider.get_connection()

    API connection:

    >>> connection = OptionsProvider.get_connection(API_CONNECT)
    """

    @classmethod
    def get_connection(cls, package_name: str = 'global_options', connection_type=None):
        """Get connection related parameters such as IP address of NMS, username and password as well as
        other driver dependant parameters.

        Upon calling with no parameters returns default connection parameters from the global options

        Can be redefined by setting `DRIVER` environmental variable:

            - `DRIVER=0` to set API connection
            - `DRIVER=1` to set CHROME connection
            - `DRIVER=2` to set FIREFOX connection

        For example, upon calling '`DRIVER=1 python -m unittest some.test.path`' the driver is CHROME

        :param str package_name: the package name to get connection data from
        :param str connection_type: the type of connection API_CONNECT | CHROME_CONNECT | FIREFOX_CONNECT
        :returns dict: a dictionary containing connection related parameters
        """
        if connection_type is None:
            env = os.environ.get('DRIVER', None)
            if env is None or env not in (API_CONNECT, CHROME_CONNECT, FIREFOX_CONNECT):
                connection_type = CONNECTION
            else:
                connection_type = env
        connection_data = cls.get_system_options(package_name)
        if connection_type == CONNECTION:
            return connection_data[connection_data[connection_type]]
        return connection_data[connection_type]

    @classmethod
    def get_system_options(cls, package_name: str, section=None) -> any:
        """
        Get a system options dictionary from the passed package name merged with the global system options.

        :param str package_name: the package name from which the system options dictionary is loaded
        :param Optional(str) section: the name of a parameter to get value of. If set, the value of the
        parameter is returned or None if such parameter is absent.
        :returns:
            - :py:class:`dict` - a dictionary of the system options
            - the value of the desired section
            - None - if the passed section is absent in the system options
        """

        return cls._load_config(_SYS, package_name, section)

    @classmethod
    def get_options(cls, package_name: str, section: str = None, options: dict = None) -> Optional[dict]:
        """
        Get a dictionary of options from the passed package name merged with the global options.

        :param str package_name: the package name from which the options dictionary is loaded
        :param Optional(str) section: the name of a parameter to get value of. If set, the value of the
        parameter is returned or None if such parameter is absent.
        :param dict options: optional dictionary to merge with the loaded options. Original dictionary is not changed.
        :returns:
            - :py:class:`dict` - a dictionary of the options
            - the value of the desired section
            - None - if the passed section is absent in the options
        """
        return cls._load_config(_OPT, package_name, section, options)

    @classmethod
    def get_uhp(cls, *, number=None, options_path=None, default=True) -> List[dict]:
        """
        Get a list of dictionaries of UHP modem options. Also set clear logs and load defaults to modems
        Sample output:
            [
                {
                    'device_ip': '10.56.24.11',
                    'device_vlan': 0,
                    'device_gateway': '10.56.24.1',
                    'serial': 50135501,
                    'model': 'UHP200',
                    'options': ()},
                },
                { ...
            ]

        :param int number: required number of UHP modems, if not set all available UHPs are included in the list
        :param str options_path: the package name from which the UHP options are loaded
        :param bool default: if True all found UHP modems are loaded to default, otherwise not
        :returns list _uhp_list: a list containing dictionaries of UHP modems options
        """
        if number is not None and number not in range(1, 100):
            raise InvalidOptionsException(f'Desired number of UHP must be in range 1 - 100')
        if options_path is None:
            options_path = 'global_options'
        _system_options = cls._load_config(_SYS, options_path)
        _uhp_list = []  # store dictionaries of available UHPs which will be returned
        _uhp_indices = {}  # store key-value pairs of UHP IP-addresses and indices, i.e. '10.56.24.11': 1

        # Getting a list of UHP IP-address from options
        for i in range(1, 100):
            # UHP IP-address section
            _next_ip = _system_options.get(f'uhp{i}_ip')
            if _next_ip is not None:
                _uhp_indices[_next_ip] = i

        # Getting a list of IP-addresses of available UHPs in the asynchronous loop, load default
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
        _available_uhp = _loop.run_until_complete(cls._get_uhps([*_uhp_indices.keys()], default=default))
        _loop.close()

        for uhp in _available_uhp:
            i = _uhp_indices.get(uhp)
            _uhp_list.append({f'device_ip': uhp, 'web_driver': UhpRequestsDriver(uhp, connect=False)})

            # UHP VLAN section
            _next_vlan = _system_options.get(f'uhp{i}_vlan')
            if _next_vlan is not None:
                _uhp_list[len(_uhp_list) - 1][f'device_vlan'] = _next_vlan
            else:
                _next_vlan = 0
                _uhp_list[len(_uhp_list) - 1][f'device_vlan'] = _next_vlan
            _uhp_list[len(_uhp_list) - 1]['web_driver'].vlan = _next_vlan

            # UHP gateway section
            _next_gw = _system_options.get(f'uhp{i}_gw')
            if _next_gw is not None:
                _uhp_list[len(_uhp_list) - 1]['device_gateway'] = _next_gw
            # If UHP gateway is not set in options it is calculated automatically for network prefix /24
            else:
                _uhp_list[len(_uhp_list) - 1]['device_gateway'] = get_default_gateway(uhp)

            # UHP serial number section
            _next_sn = _system_options.get(f'uhp{i}_sn')
            if _next_sn is not None:
                _uhp_list[len(_uhp_list) - 1]['serial'] = _next_sn
            # If UHP serial number is not set in options, getting it from UHP itself
            else:
                _next_sn = _uhp_list[len(_uhp_list) - 1]['web_driver'].get_serial_number()
                _uhp_list[len(_uhp_list) - 1]['serial'] = _next_sn
            _uhp_list[len(_uhp_list) - 1]['web_driver'].serial_number = _next_sn

            # UHP model section
            _next_md = _system_options.get(f'uhp{i}_md')
            if _next_md is not None:
                _uhp_list[len(_uhp_list) - 1]['model'] = _next_md
            # If UHP model is not set in options, getting it from UHP itself
            else:
                _uhp_list[len(_uhp_list) - 1]['model'] = get_model_from_serial(_next_sn)

            # UHP capabilities section
            _next_opt = _system_options.get(f'uhp{i}_options')
            if _next_opt is not None:
                _uhp_list[len(_uhp_list) - 1]['options'] = tuple(_next_opt)
            else:
                _uhp_list[len(_uhp_list) - 1]['options'] = tuple()

            # SW section
            _next_sw = _uhp_list[len(_uhp_list) - 1]['web_driver'].get_software_version()
            _uhp_list[len(_uhp_list) - 1]['sw'] = _next_sw

            # If the desired number of UHP is passed and all of them has been found - break
            if number is not None and len(_uhp_list) == number:
                return _uhp_list

        if number is not None and len(_uhp_list) < number:
            raise InvalidOptionsException(
                f'The number of the available UHP modems is {len(_uhp_list)}, required {number}')
        return _uhp_list

    @classmethod
    def get_uhp_by_model(cls, *args, number=None, options_path=None, default=True):
        """
        Get a list containing dictionaries of UHP modems with desired hardware models
        >>> OptionsProvider.get_uhp_by_model('UHP200', 'UHP200X')
        Sample output:
            [
                {
                    'device_ip': '10.56.24.11',
                    'device_vlan': 0,
                    'device_gateway': '10.56.24.1',
                    'serial': 50135501,
                    'model': 'UHP200',
                    'options': ()},
                },
                { ...
            ]

        :param args: desired UHP models in NMS format: `UHP100`, `UHP100X` etc.
        :param int number: required number of UHP modems
        :param str options_path: the package name from which the UHP options are loaded
        :param bool default: if True apply default to getting UHPs, otherwise just returns the data
        :returns list _uhp_list: a list containing dictionaries of UHP modems' options
        """
        if number is not None and number not in range(1, 100):
            raise InvalidOptionsException(f'Desired number of UHP must be in range 1 - 100')
        if 'any' in args or 'ANY' in args:
            models = [*ModelTypesStr()]
        else:
            models = []
            for model in args:
                if model not in [*ModelTypesStr()]:
                    raise InvalidOptionsException(f'Model {model} is not valid')
                models.append(model)
        _all_uhp_list = cls.get_uhp(options_path=options_path, default=default)
        _uhp_list = []
        for uhp in _all_uhp_list:
            for inner_key, inner_value in uhp.items():
                if inner_key == 'model' and inner_value in models:
                    _uhp_list.append(uhp)
                if number is not None and len(_uhp_list) == number:
                    break
        if number is not None and len(_uhp_list) < number:
            raise InvalidOptionsException(
                f'The number of the available UHP modems is {len(_uhp_list)}, required {number}')
        return _uhp_list

    @classmethod
    def get_uhp_controllers_stations(cls, ctrl_number: int, ctrl_model: list, stn_number: int, stn_model: list, *,
                                     options_path=None, default=True):
        """
        Get two lists containing UHP modems for controllers and stations
        Sample usage:
        >>> OptionsProvider.get_uhp_controllers_stations(2, ['UHP200', 'UHP200X'], 3, ['UHP200', 'UHP100'])
        Sample output:
        [
            {
                'device_ip': '10.56.24.11',
                ...
                'options': ()},
            },
            { ...
        ],
        [
            {
                'device_ip': '10.56.24.11',
                ...
                'options': ()},
            },
            { ...
        ]

        :param int ctrl_number: required number of UHP modems which are used as controllers
        :param list ctrl_model: a list of UHP models for controllers
        :param int stn_number: required number of UHP modems which are used as stations
        :param list stn_model: a list of UHP models for stations
        :param str options_path: the package name from which the UHP options are loaded
        :param bool default: if True apply default config to all UHPs, otherwise just returns the data
        :returns list _ctrl_list, _stn_list: two lists containing dictionaries of UHP modems
        """
        if ctrl_number not in range(1, 100):
            raise InvalidOptionsException(f'Controllers number must be passed as integer ranged 1 - 100')
        if not isinstance(ctrl_model, list):
            raise InvalidOptionsException(f'Controllers model must be passed as a list of strings')
        if 'any' in ctrl_model or 'ANY' in ctrl_model:
            ctrl_model = [*ModelTypesStr()]
        else:
            for model in ctrl_model:
                if model not in [*ModelTypesStr()]:
                    raise InvalidOptionsException(f'Passed controllers model {model} is not valid')
        if stn_number not in range(1, 100):
            raise InvalidOptionsException(f'Stations number must be passed as integer ranged 1 - 100')
        if not isinstance(stn_model, list):
            raise InvalidOptionsException(f'Stations model must be passed as a list of strings')
        if 'any' in stn_model or 'ANY' in stn_model:
            stn_model = [*ModelTypesStr()]
        else:
            for model in stn_model:
                if model not in [*ModelTypesStr()]:
                    raise InvalidOptionsException(f'Passed stations model {model} is not valid')

        _all_uhp_list = cls.get_uhp(options_path=options_path, default=default)
        _ctrl_list = []
        _stn_list = []
        # No worth trying to get UHP as the total requested number of modems is too high
        if len(_all_uhp_list) < ctrl_number + stn_number:
            raise InvalidOptionsException(
                f'The total number of the requested UHP modems is {ctrl_number + stn_number}, '
                f'the number of the available UHP modems is {len(_all_uhp_list)}')
        for uhp in _all_uhp_list:
            if uhp.get('model') in ctrl_model and len(_ctrl_list) < ctrl_number:
                _ctrl_list.append(uhp)
            elif uhp.get('model') in stn_model and len(_stn_list) < stn_number:
                _stn_list.append(uhp)
        if len(_ctrl_list) < ctrl_number:
            raise InvalidOptionsException(f'The number of the available UHP for controllers is {len(_ctrl_list)}, '
                                          f'the requested number is {ctrl_number}')
        if len(_stn_list) < stn_number:
            raise InvalidOptionsException(f'The number of the available UHP for stations is {len(_stn_list)}, '
                                          f'the requested number is {stn_number}')
        return _ctrl_list, _stn_list

    @classmethod
    def _load_config(cls, conf_name: str, package_name: str, section: str = None, options: dict = None):
        if options is None:
            options = {}
        _options = OptionsProvider._load_and_merge_options("global_options.options", conf_name, options)
        _options = OptionsProvider._load_and_merge_options("global_options.local_options", conf_name, _options)
        if package_name is not None and package_name != 'global_options':
            module_name = package_name + ".options"
            _options = OptionsProvider._load_and_merge_options(module_name, conf_name, _options)
            module_name = package_name + ".local_options"
            _options = OptionsProvider._load_and_merge_options(module_name, conf_name, _options)
        if section is not None:
            if section in _options:
                return _options[section]
            else:
                return None
        return _options

    @staticmethod
    def _load_and_merge_options(module_name: str, dict_name: str, options: dict):
        options_module = OptionsProvider._load_module(module_name)
        if options_module is not None and hasattr(options_module, dict_name):
            # NEW BLOCK - initial dictionary must be created from scratch without shallow copies
            if module_name == 'global_options.options':
                # print(dict_name, options_module.__getattribute__(dict_name))
                OptionsProvider._get_global_options(options, options_module.__getattribute__(dict_name))
            # END OF NEW BLOCK
            else:
                # print(dict_name, options_module.__getattribute__(dict_name))
                OptionsProvider._dict_merge(options, options_module.__getattribute__(dict_name))
        return options

    @staticmethod
    def _load_module(module_name: str):
        module = None
        if importlib.util.find_spec(module_name):
            module = import_module(module_name)
        return module

    @staticmethod
    def _get_global_options(dct: dict, merge_dct: dict):
        """ Recursive dict merge. Global options must be imported and put into a dictionary without shallow copies.

        :param dct: dict onto which the merge is executed
        :param merge_dct: dct merged into dct
        :returns: None
        """
        for k, v in merge_dct.items():
            if isinstance(merge_dct[k], dict):
                if k not in dct.keys():
                    dct[k] = {}
                OptionsProvider._get_global_options(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]

    @staticmethod
    def _dict_merge(dct: dict, merge_dct: dict):
        """Alternative approach to merging options in order to avoid shallow copies"""
        if isinstance(merge_dct, dict):
            for k, v in merge_dct.items():
                if isinstance(merge_dct[k], dict):
                    if k not in dct.keys():
                        dct[k] = {}
                    OptionsProvider._dict_merge(dct[k], merge_dct[k])
                elif isinstance(merge_dct[k], list):
                    if k not in dct.keys():
                        # Clearing list in the original dictionary
                        dct[k] = []
                    OptionsProvider._dict_merge(dct[k], merge_dct[k])
                else:
                    dct[k] = merge_dct[k]
        elif isinstance(merge_dct, list):
            for elem in merge_dct:
                dct.append(elem)

    @staticmethod
    def _dict_merge_old(dct: dict, merge_dct: dict):
        """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, dict_merge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
        ``dct``.
        :param dct: dict onto which the merge is executed
        :param merge_dct: dct merged into dct
        :returns: None
        """
        for k, v in merge_dct.items():
            if (k in dct and isinstance(dct[k], dict)
                    and isinstance(merge_dct[k], dict)):
                OptionsProvider._dict_merge_old(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]

    @classmethod
    async def _get_uhps(cls, _ips, default=True):
        """
        Asynchronously querying passed IP-addresses for responses.
        Clear logs and load config from bank 1 as well if default is set to True

        :param list _ips: a list of IP-addresses
        :param bool default: load default in all found UHPs
        :returns list _available_uhps: a list of strings containing IP-addresses of available UHP modems
        """
        _timeout = aiohttp.ClientTimeout(total=5)
        _available_uhps = []
        res = await asyncio.gather(*[cls._try_next_uhp(str(ip)) for ip in _ips])

        for i in range(len(res)):
            if res[i]:
                _available_uhps.append(str(_ips[i]))

        if default:
            # Setting NMS permissions to off
            await asyncio.gather(*[cls._nms_permissions(ip) for ip in _available_uhps])

        if default:
            # Running SCPC modem profile with both demodulators and modulator disabled
            await asyncio.gather(*[cls._load_scpc(ip) for ip in _available_uhps])

        # if default:
        #     # Sending lic clear network script command
        #     await asyncio.gather(*[cls._lic_clear(ip) for ip in _available_uhps])

        if default:
            # Clearing All Stats and Logs in ALL available UHPs
            await asyncio.gather(*[cls._clear_uhp_log(ip) for ip in _available_uhps])

        if default:
            # Loading Bank 1 config in ALL available UHPs, timeout is set to a higher value in order to wait for config
            await asyncio.gather(*[cls._load_uhp_default(ip) for ip in _available_uhps])

        if default:
            # Turning off Traffic generator as it is not switched off after calling config bank
            await asyncio.gather(*[cls._traffic_off(ip) for ip in _available_uhps])

        if default:
            # Getting again the list of available UHPs to handle possible unreachable state after loading default
            _available_uhps = []
            res = await asyncio.gather(*[cls._try_next_uhp(str(ip)) for ip in _ips])
            for i in range(len(res)):
                if res[i]:
                    _available_uhps.append(str(_ips[i]))
        return _available_uhps

    @classmethod
    async def _try_next_uhp(cls, ip):
        """
        Asynchronously querying UHP modem for response

        # :param aiohttp.ClientSession session: aiohttp session used to query UHP
        :param str ip: IP-address of the UHP modem
        :returns bool: True if UHP responds, otherwise False
        """
        # In order to perform requests slightly distributed in time
        # await asyncio.sleep(random.random())
        try:
            _timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=_timeout) as session:
                async with session.get(f'http://{ip}/ss37') as response:
                    await response.read()
                    # Just in case handling responses from other hosts
                    _text = await response.text()
                    if _text.find('State') != -1:
                        return True
                    return False
        except asyncio.exceptions.TimeoutError:
            return False
        except aiohttp.ClientConnectorError:
            return False

    @classmethod
    async def _nms_permissions(cls, ip):
        """
        Setting UHP NMS permissions to off.

        :param str ip: IP-address of the UHP modem
        :returns bool: True if request is successful, otherwise False
        """
        # In order to perform requests slightly distributed in time
        await asyncio.sleep(random.random())
        for _ in range(3):
            try:
                _timeout = aiohttp.ClientTimeout(total=5)
                async with aiohttp.ClientSession(timeout=_timeout) as session:
                    async with session.get(
                            f'http://{ip}/cw14?di=0&tb=&ih=0.0.0.0&if=0.0.0.0&ie=0.0.0.0&dk=0&dj=0&ta=Apply')\
                            as response:
                        await response.read()
                        return True
            except asyncio.exceptions.TimeoutError:
                print(f'{ip} set NMS permissions off TimeoutError, trying again...')
                await asyncio.sleep(1)
                continue
            except aiohttp.ClientConnectorError:
                print(f'{ip} set NMS permissions off ClientConnectionError, trying again...')
                await asyncio.sleep(1)
                continue
        return False

    @classmethod
    async def _clear_uhp_log(cls, ip, timeout=20):
        """
        Clear all stats&Logs in UHP. Asynchronously awaiting for `Log cleared` message in Logs

        :param str ip: IP-address of the UHP modem
        :param int timeout: timeout in seconds to wait for `Log cleared` message in Logs
        :returns bool: True if request is successful and there is `Log cleared` message, otherwise False
        """
        # In order to perform requests slightly distributed in time
        await asyncio.sleep(random.uniform(0, 2))
        for _ in range(3):
            try:
                _timeout = aiohttp.ClientTimeout(total=5)
                async with aiohttp.ClientSession(timeout=_timeout) as session:
                    async with session.get(f'http://{ip}/ss29?ta=Clear%C2%A0all%C2%A0stats%26Log') as response:
                        await response.read()

                await asyncio.sleep(1)
                st_time = time.perf_counter()
                while st_time + timeout > time.perf_counter():
                    _timeout = aiohttp.ClientTimeout(total=5)
                    async with aiohttp.ClientSession(timeout=_timeout) as session:
                        async with session.get(f'http://{ip}/ss52') as response:
                            res = await response.read()
                    soup = BeautifulSoup(res, 'html.parser')
                    tag = soup.find('pre')
                    if tag is None:
                        await asyncio.sleep(1)
                        continue
                    data = tag.text
                    if data.find('Log cleared') != -1:
                        return True
                    else:
                        await asyncio.sleep(1)
                print(f'{ip} Log cleared not found')
                return False
            except asyncio.exceptions.TimeoutError:
                print(f'{ip} clear log Timeout, trying again...')
                await asyncio.sleep(1)
                continue
            except aiohttp.ClientConnectorError:
                print(f'{ip} clear log ClientConnectionError, trying again...')
                await asyncio.sleep(1)
                continue
        return False

    @classmethod
    async def _load_uhp_default(cls, ip, timeout=20):
        """
        Load default config from Bank 1 in UHP. Asynchronously awaiting for `Config 1 loaded` message in Logs

        :param str ip: IP-address of the UHP modem
        :param int timeout: timeout in seconds to wait for `Config 1 loaded` message in Logs
        :returns bool: True if request is successful and there is `Config 1 loaded` message, otherwise False
        """
        # In order to perform requests slightly distributed in time
        await asyncio.sleep(random.uniform(0, 2))
        for _ in range(3):  # in some cases load config is unexpectedly not applied
            try:
                _timeout = aiohttp.ClientTimeout(total=5)
                async with aiohttp.ClientSession(timeout=_timeout) as session:
                    async with session.get(f'http://{ip}/cw1?da=1&tc=Load&tb=') as response:
                        await response.read()
            except asyncio.exceptions.TimeoutError:
                print(f'{ip} TimeoutError at send load default command')
                return False
            except aiohttp.ClientConnectorError:
                print(f'{ip} ClientConnectorError at send load default command')
                return False

            await asyncio.sleep(15)

            # Waiting for Config 1 loaded message in Logs
            st_time = time.perf_counter()
            while st_time + timeout > time.perf_counter():
                try:
                    _timeout = aiohttp.ClientTimeout(total=15)
                    async with aiohttp.ClientSession(timeout=_timeout) as session:
                        async with session.get(f'http://{ip}/ss52') as response:
                            res = await response.read()
                except asyncio.exceptions.TimeoutError:
                    print(f'{ip} TimeoutError at requesting logs to get Config 1 loaded message')
                    continue
                except aiohttp.ClientConnectorError:
                    print(f'{ip} ClientConnectorError at requesting to get Config 1 loaded message')
                    continue
                soup = BeautifulSoup(res, 'html.parser')
                tag = soup.find('pre')
                if tag is None:
                    await asyncio.sleep(1)
                    continue
                data = tag.text
                if data.find('Config 1 loaded') != -1:
                    return True
                else:
                    await asyncio.sleep(1)
            print(f'{ip} Config 1 loaded was not found, trying load again')
        return False

    @classmethod
    async def _load_scpc(cls, ip, timeout=20):
        # In order to perform requests slightly distributed in time
        await asyncio.sleep(random.random())
        try:
            _timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=_timeout) as session:
                async with session.get(f'http://{ip}/cB3?da=1&db=1&dd=1&de=40&ta=def&tf=Apply&df=2') as response:
                    await response.read()
                async with session.get(f'http://{ip}/cB3?da=1&db=1&dd=1&de=40&ta=def&tf=Apply&df=2') as response:
                    await response.read()
                async with session.get(
                        f'http://{ip}/cR3?dj=0&da=1&db=950000&dc=1000&dk=0&dh=952000&di=1000&dl=0&tf=Apply'
                ) as response:
                    await response.read()
                async with session.get(f'http://{ip}/ck3?da=1') as response:
                    await response.read()
        except asyncio.exceptions.TimeoutError:
            print(f'{ip} applying SCPC modem profile TimeoutError')
            return False
        except aiohttp.ClientConnectorError:
            print(f'{ip} applying SCPC modem profile ClientConnectorError')
            return False

        st_time = time.perf_counter()
        while st_time + timeout > time.perf_counter():
            try:
                _timeout = aiohttp.ClientTimeout(total=20)
                async with aiohttp.ClientSession(timeout=_timeout) as session:
                    async with session.get(f'http://{ip}/ss52') as response:
                        res = await response.read()
            except asyncio.exceptions.TimeoutError:
                print(f'{ip} get logs while checking Pro 1 manual run TimeoutError')
                return False
            except aiohttp.ClientConnectorError:
                print(f'{ip} get logs while checking Pro 1 manual run ClientConnectorError')
                return False
            soup = BeautifulSoup(res, 'html.parser')
            tag = soup.find('pre')
            if tag is None:
                await asyncio.sleep(1)
                continue
            data = tag.text
            if data.find('Pr1 manual run') != -1:
                return True
            else:
                await asyncio.sleep(1)
        print(f'{ip} SCPC modem profile Pr1 manual run is not found in logs')
        return False

    @classmethod
    async def _traffic_off(cls, ip):
        """
        Turn off Traffic Generator.

        :param str ip: IP-address of the UHP modem
        :returns bool: True if request is successful, otherwise False
        """
        # In order to perform requests slightly distributed in time
        await asyncio.sleep(random.random())
        for _ in range(3):
            try:
                _timeout = aiohttp.ClientTimeout(total=5)
                async with aiohttp.ClientSession(timeout=_timeout) as session:
                    async with session.get(
                            f'http://{ip}/cw43?ta=Apply') as response:
                        await response.read()
                        return True
            except asyncio.exceptions.TimeoutError:
                print(f'{ip} set Traffic Generator off TimeoutError, trying again...')
                await asyncio.sleep(1)
                continue
            except aiohttp.ClientConnectorError:
                print(f'{ip} set Traffic Generator off ClientConnectionError, trying again...')
                await asyncio.sleep(1)
                continue
        return False

    @classmethod
    async def _lic_clear(cls, ip):
        """
        Sending `lic clear` network command

        :param str ip: IP-address of the UHP modem
        :returns bool: True if request is successful, otherwise False
        """
        # In order to perform requests slightly distributed in time
        await asyncio.sleep(random.random())
        for _ in range(3):
            try:
                _timeout = aiohttp.ClientTimeout(total=5)
                async with aiohttp.ClientSession(timeout=_timeout) as session:
                    async with session.get(
                            f'http://{ip}/cw42?db=0&dc=0&aa=lic+clear&ta=Apply') as response:
                        await response.read()
            except asyncio.exceptions.TimeoutError:
                print(f'{ip} sending lic clear command TimeoutError, trying again...')
                await asyncio.sleep(1)
                continue
            except aiohttp.ClientConnectorError:
                print(f'{ip} sending lic clear ClientConnectionError, trying again...')
                await asyncio.sleep(1)
                continue
        return False

    @classmethod
    def upload_uhp_sw(cls, share_dir=None, sw_family='3.7', sw_version=None, uhp_list=None):
        """
        Upload either latest or chosen SW to all UHPs set in options or passed as a list

        Sample usage:
        >>> upload_uhp_sw(sw_family='3.7', sw_version='3.7.1.34 211019')

        :param str share_dir: shared directory to look up for software
        :param str sw_family: global UHP SW revision ('3.5', '3.6', '3.7'), by default '3.7'
        :param str sw_version: desired UHP SW version to load, if None the latest one is loaded
        :param list uhp_list: list of UHP IP-addresses to load SW to, if None all the available UHPs will be chosen
        :returns None:
        """
        if share_dir is None:
            share_dir = cls.get_system_options('global_options').get('UHP_SW_DIR')

            if share_dir is None:
                raise InvalidOptionsException(
                    'Directory to look up for UHP SW should be either passed or set in options'
                )
        if sw_family not in ('3.5', '3.6', '3.7'):
            raise InvalidOptionsException('UHP SW family should be either 3.5, or 3.6, or 3.7')

        share_dir = f'{share_dir}{os.sep}{sw_family}{os.sep}Development'
        _content = os.listdir(share_dir)

        # Getting the last available SW version based on its number and date
        if sw_version is None:
            sw_version = cls._get_latest_sw_dir_name(share_dir, _content)
            share_dir = f'{share_dir}{os.sep}{sw_version}'
        elif sw_version not in _content:
            raise InvalidOptionsException(f'Cannot locate desired SW version {sw_version}')
        else:
            share_dir = f'{share_dir}{os.sep}{sw_version}'

        _regex = re.search(r'[0-9]+.[0-9]+.[0-9]+.[0-9]+', sw_version)
        pure_sw_version = _regex.group(0)  # UHP SW in pure format, i.e. '3.7.1.34'

        _content = os.listdir(share_dir)  # file names inside the directory

        # Getting list of UHP IP-addresses from options
        if uhp_list is None:
            uhps = cls.get_uhp(default=False)
        # Or from the passed list
        else:
            uhps = []
            for u in uhp_list:
                web_driver = UhpRequestsDriver(u)
                serial = web_driver.get_serial_number()
                uhps.append({
                    'device_ip': u,
                    'serial': serial,
                    'model': get_model_from_serial(serial),
                    'sw': web_driver.get_software_version()
                })
        print(share_dir)
        # print(_content)
        # print(uhps)

        for uhp in uhps:
            device_ip = uhp.get('device_ip')
            current_sw = uhp.get('sw')
            if current_sw is not None:
                current_sw = current_sw.split()[0]
            else:  # if current UHP SW cannot be determined. Probably better raise exception
                current_sw = '0.0.0.0'
            if current_sw == pure_sw_version:
                print(f'SW {current_sw} is up to date')
            elif current_sw > pure_sw_version:
                print(f'Unexpectedly current UHP sw ver {current_sw} is newer than the latest {pure_sw_version}')
            else:
                print(f'Current UHP SW ver {current_sw} is older than the latest version {pure_sw_version}.'
                      f' Can be upgraded')
                sw_name = cls._get_sw_name(uhp.get('model'))
                print(device_ip, sw_name)

    @staticmethod
    def _get_latest_sw_dir_name(path, dirs):
        """Get the latest SW version based on revision number and folder creation date"""
        name = ''
        latest = 0
        for i in range(len(dirs)):
            # Skip `OLD` and similar dirs
            if not dirs[i].startswith('3.'):
                continue
            parts = dirs[i].split()  # splitting directory name to get base version number
            if parts[0] >= name and os.stat(f'{path}{os.sep}{dirs[i]}').st_mtime > latest:
                name = dirs[i]
                latest = os.stat(f'{path}{os.sep}{dirs[i]}').st_mtime
        return name

    @staticmethod
    def _get_sw_name(model):
        if model == 'UHP200':
            sw_name = 'uhp-soft.240'
        elif model == 'UHP200X':
            sw_name = 'uhp-200.S2X'
        elif model in ('UHP100', 'UHP100X'):
            sw_name = 'uhp-soft.100'
        else:
            raise InvalidModeException(f'Cannot find software for model {model}')
        return sw_name


if __name__ == '__main__':
    st_time = time.perf_counter()
    ctrls, stns = OptionsProvider.get_uhp_controllers_stations(3, ['UHP200', ], 5, ['ANY'], default=False)
    print(round(time.perf_counter() - st_time, 2))
    print(f'Total number of UHPs {len(ctrls) + len(stns)} ')
