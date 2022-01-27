import ipaddress
import re
import time
import urllib
from typing import Dict

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

from src.drivers.uhp.constants import *
from src.drivers.uhp.uhp_getter import UhpGetter
from src.enum_types_constants import RollofModes, SnmpModes, SnmpAuth, TdmaInputModes, \
    SnmpModesStr, RipModesStr, SnmpAuthStr, CheckTypesStr, RuleTypesStr, CheckboxStr, TdmaSearchModes, LatitudeModes, \
    LongitudeModes
from src.exceptions import UhpResponseException, InvalidOptionsException

dF = 65534


class UhpRequestsDriver(UhpGetter):
    """
    The class features methods to get data from UHP routers as well as set parameters.

    :param str router_address: UHP router IP address
    :param Optional int vlan: UHP access protocols VLAN
    :param Optional int timeout: GET requests timeout value in seconds
    :param Optional int max_retries: number of GET requests retries
    :param Optional bool connect: if True tries to connect to UHP upon initialization
    :param Optional bool monitoring: if True sets NMS permission Monitoring to True upon initialization
    :param Optional bool control: if True sets NMS permission Control to True upon initialization
    :param Optional bool allow_local_config: if True sets NMS permission Allow local config to True upon initialization
    :param Optional str password: NMS permission password
    """

    def __init__(
            self,
            router_address: str = '127.0.0.1',
            vlan: int = 0,
            timeout: int = 5,
            max_retries: int = 2,
            connect=True,
            monitoring=False,
            control=False,
            allow_local_config=False,
            password='',
    ):
        """
        Construct an instance of UhpRequestsDriver

        :param str router_address: UHP router IP address
        :param int timeout: GET requests timeout value in seconds
        :param int max_retries: number of GET requests retries
        :param bool connect: if True automatically connect to UHP - can raise Exception if unreachable
        """
        self._router_address = router_address
        self._vlan = vlan
        self._serial_number = None
        self.uhp_software_version = None
        self._timeout = timeout
        self._max_retries = max_retries
        self._current_res = None
        if connect:
            self.connect()
        if monitoring is True or control is True or allow_local_config is True:
            self.set_nms_permission(
                vlan=vlan,
                password=password,
                monitoring=monitoring,
                control=control,
                allow_local_config=allow_local_config
            )

    @property
    def vlan(self):
        return self._vlan

    @vlan.setter
    def vlan(self, new_value):
        if new_value not in range(0, 4096):
            raise ValueError('VLAN must be ranged 0 - 4095')
        self._vlan = new_value

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, new_value):
        self._serial_number = new_value

    @staticmethod
    def _mask_to_prefix(mask=None):
        """
        Convert a netmask <xxx.xxx.xxx.xxx> to a corresponding prefix <xx>

        :param str mask: a network mask to convert
        :returns:
            - prefix (:py:class:'str') - corresponding prefix
            - None - if the netmask format is invalid
        """
        try:
            prefix = ipaddress.IPv4Network(f'0.0.0.0/{mask}').prefixlen
            return prefix
        except ipaddress.AddressValueError:
            return None

    def get_request(self, url, timeout=None):
        """
        Send a GET request using the passed URL, get a response

        :param str url: URL to get response from, i.e. `http://10.56.24.11/ss40`
        :param int timeout: timeout in seconds while waiting for response, if None instance timeout is used
        :returns Union[requests.Response, False]: requests.Response if reponse status code is 200, otherwise False
        :raises RequestException: if there is any of the requests exception (ConnectTimeout, ReadTimeout etc.)
        """
        if not timeout:
            timeout = self._timeout
        session = requests.Session()
        session.mount('http://', HTTPAdapter(max_retries=self._max_retries))
        for _ in range(3):
            try:
                r = session.get(url, timeout=timeout)
                self._current_res = r
                if r.status_code == 200:
                    session.close()
                    return r
                session.close()
                return False
            except requests.exceptions.RequestException as exc:
                # print(f'UHP web driver Exception: exc={exc}, url={url}')
                continue
        session.close()
        raise UhpResponseException(url)

    def _is_error(self):
        """Returns True if there is an error on the current page, otherwise False"""
        _error = None
        if self._current_res is not None:
            soup = BeautifulSoup(self._current_res.content, 'html.parser')
            # Error is indicated inside a font tag, having red color
            _error = soup.find(
                lambda tag: tag.name == 'font' and tag['color'] == 'red' and tag.contents[0].lower().find('error') != -1
            )
        if _error is None:
            return False
        return True

    def connect(self):
        """
        Send a GET request to the UHP using the IP-address provided during the class instantiation

        :returns: True if there is a response
        :raises UhpResponseException: if the target UHP does not respond
        """
        req = self.get_request(f'http://{self._router_address}')
        if not req:
            raise UhpResponseException(f'Cannot connect to UHP {self._router_address} at web driver init')
        return True

    def clear_log(self, timeout=10):
        req = self.get_request(f'http://{self._router_address}/ss52?ta=Clear log&db=0')
        if not req:
            return False
        st_time = time.perf_counter()
        while st_time + timeout > time.perf_counter():
            req = self.get_request(f'http://{self._router_address}/ss52')
            if not req:
                time.sleep(1)
                continue
            soup = BeautifulSoup(req.content, 'html.parser')
            tag = soup.find('pre')
            if tag is None:
                time.sleep(1)
                continue
            data = tag.text
            if data.find('Log cleared') != -1:
                return True
            else:
                time.sleep(1)
        return False

    def load_default(self, timeout=20):
        """Load Config 1 - default UHP config should be stored there"""
        if not self.clear_log():
            raise UhpResponseException(f'Cannot clear log to make sure that the config is loaded')

        req = self.get_request(f'http://{self._router_address}/cw1?da=1&tc=Load&tb=')
        if not req:
            raise UhpResponseException(f'Load Config 1 command unsuccessful')

        st_time = time.perf_counter()
        while st_time + timeout > time.perf_counter():
            req = self.get_request(f'http://{self._router_address}/ss52')
            if not req:
                time.sleep(1)
                continue
            soup = BeautifulSoup(req.content, 'html.parser')
            tag = soup.find('pre')
            if tag is None:
                time.sleep(1)
                continue
            data = tag.text
            if data.find('Config 1 loaded') != -1:
                return True
            else:
                time.sleep(1)
        return False

    def set_nms_permission(self, vlan=0, password='', monitoring=True, control=True, allow_local_config=False):
        """
        Set NMS permissions to the UHP and UHP redundancy. The parameters and their default values are the following:
            vlan=0, password='', monitoring=True, control=True, allow_local_config=False

        :param int vlan: VLAN ID to be used for access
        :param str password: password to be used for access
        :param bool monitoring: allow monitoring by NMS
        :param control: allow control by NMS
        :param allow_local_config: allow local config along with NMS
        :returns bool: True if the settings are set, otherwise False
        """
        current_params = self.get_stlc_nms_red_form()
        if current_params is None:
            return None
        current_params['vlan'] = vlan
        current_params['password'] = password
        current_params['monitoring'] = int(monitoring)
        current_params['control'] = int(control)
        current_params['allow_local_config'] = int(allow_local_config)
        payload = {}
        for key, value in scpc_tlc_red_mapping.items():
            payload[key] = current_params.get(value)
        payload = urllib.parse.urlencode(payload)
        res = self.get_request(f'http://{self._router_address}/cw14?{payload}')
        if not res:
            return False
        return True

    def get_nms_state(self):
        """
        Get UHP NMS state as a dictionary
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/ss14')
        if not req:
            return uhp_values
        else:
            data = req.text
        uhp_values['server_ip'] = self.get_support_info_value(
            regex=re.compile(r'serverip:\s[0-9]+.[0-9]+.[0-9]+.[0-9]+'), data=data
        )
        uhp_values['vlan'] = self.get_support_info_value(regex=re.compile(r'vlan:\s[0-9]+'), data=data)
        uhp_values['monitoring'] = self.get_support_info_value(regex=re.compile(r'mon:\s[a-z]+'), data=data)
        uhp_values['control'] = self.get_support_info_value(regex=re.compile(r'ctl:\s[a-z]+'), data=data)
        uhp_values['locked'] = self.get_support_info_value(regex=re.compile(r'locked:\s[a-z]+'), data=data)
        uhp_values['packets_in'] = self.get_support_info_value(regex=re.compile(r'packets_in:\s[0-9]+'), data=data)
        uhp_values['passwd_errs'] = self.get_support_info_value(regex=re.compile(r'passwd_errs:\s[0-9]+'), data=data)
        return uhp_values

    def wait_state(self, state='Operation', timeout=60, step=5) -> bool:
        """Wait for the desired state. The awaiting is blocking.

        :param str state: state that is awaited. Lowercased and uppercased strings are excepted
        :param int timeout: number of seconds to await the state
        :param int step: number of seconds between current state requests
        :return bool: True if the state is reached within timeout, otherwise False
        """
        st_time = time.time()
        while True:
            if self.get_state() == state.lower():
                return True
            if st_time + timeout < time.time():
                return False
            time.sleep(step)

    def wait_nms_controlled_mode(self, timeout=10):
        """
        Wait UHP to be in NMS controlled mode

        :param Optional int timeout: timeout in seconds to wait NMS controlled mode
        :returns bool: True if NMS is under NMS control, otherwise False
        """
        st_time = time.perf_counter()
        while True:
            req = self.get_request(f'http://{self._router_address}/cc2')
            if not req:
                return False
            if req.text.find('NMS controlled mode!') != -1:
                return True
            if time.perf_counter() - st_time > timeout:
                return False

    def set_profile_tlc(self, profile_number=1, params=None):
        """
        Alias for set_tlc method. Set TLC params for a profile.
        The parameters and their default values are the following:
            tlc_enable=0, tlc_max_lvl=1, tlc_net_own=0, tlc_avg_min=0,
            tlc_cn_stn=8.0, tlc_cn_hub=8.0.

        :param int profile_number: UHP profile number to set TLC (by default 1)
        :param dict params: parameters used to set TLC, if None default params are used (TLC disabled)
        :returns bool: True if parameters are set, otherwise False

        """
        return self.set_tlc(profile_number=profile_number, params=params)

    def set_tlc(self, profile_number=1, params=None):
        """
        Set TLC params for a profile. The parameters and their default values are the following:
            tlc_enable=0, tlc_max_lvl=1, tlc_net_own=0, tlc_avg_min=0,
            tlc_cn_stn=8.0, tlc_cn_hub=8.0.

        :param int profile_number: UHP profile number to set TLC (by default 1)
        :param dict params: parameters used to set TLC, if None default params are used (TLC disabled)
        :returns bool: True if parameters are set, otherwise False
        """
        if params is None:
            params = {}
        tlc_enable = params.get('tlc_enable')
        if tlc_enable is None or tlc_enable in (False, 0, '0', ''):
            tlc_enable = 0
        else:
            tlc_enable = 1

        tlc_cn_stn = params.get('tlc_cn_stn')
        if tlc_cn_stn is None or not isinstance(tlc_cn_stn, float):
            tlc_cn_stn_int = '8'
            tlc_cn_stn_float = '0'
        else:
            tlc_cn_stn_int, tlc_cn_stn_float = str(tlc_cn_stn).split('.')

        tlc_cn_hub = params.get('tlc_cn_hub')
        if tlc_cn_hub is None or not isinstance(tlc_cn_hub, float):
            tlc_cn_hub_int = '8'
            tlc_cn_hub_float = '0'
        else:
            tlc_cn_hub_int, tlc_cn_hub_float = str(tlc_cn_hub).split('.')

        payload = {
            TLC_ENABLE_ATTR_NAME: tlc_enable,
            TLC_MAX_LVL_ATTR_NAME: params.get('tlc_max_lvl', '1'),
            TLC_NET_OWN_ATTR_NAME: params.get('tlc_net_own', '0'),
            TLC_AVG_MIN_ATTR_NAME: params.get('tlc_avg_min', '0'),
            TLC_CN_STN_INT_ATTR_NAME: tlc_cn_stn_int,
            TLC_CN_STN_FLOAT_ATTR_NAME: tlc_cn_stn_float,
            TLC_CN_HUB_INT_ATTR_NAME: tlc_cn_hub_int,
            TLC_CN_HUB_FLOAT_ATTR_NAME: tlc_cn_hub_float,
        }
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cL3?da={profile_number}&{payload}&tf=Apply'
        res = self.get_request(url)
        if not res or self._is_error():
            return False
        return True

    def get_realtime_bw_form(self):
        """
        Get the data from the UHP TDMA Realtime BW allocation as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'rt_codec', 'rt_threshold', and 'rt_timeout'.
        The dictionary values are taken from the page unmodified.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cc16')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name = tag.get('name', None)
                if name is None:
                    continue
                elif name == RT_CODEC_ATTR_NAME:
                    uhp_values['rt_codec'] = tag.get('value', None)
                elif name == RT_THRESHOLD_ATTR_NAME:
                    uhp_values['rt_threshold'] = tag.get('value', None)
                elif name == RT_TIMEOUT_ATTR_NAME:
                    uhp_values['rt_timeout'] = tag.get('value', None)
        return uhp_values

    def get_station_edit_form(self, station_number=1):
        """
        Get the data from the UHP Advanced->Network->Stations->Station# page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'hub_shaper', 'rq_profile'.
        The dictionary values are taken from the page unmodified.

        :param int station_number: station number to get data from
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cc24?db={station_number}?dq=1')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('select')
            for tag in tags:
                name = tag.get('name', None)
                if name is None:
                    continue
                elif name == ST_EDIT_REQ_PR_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            try:
                                uhp_values['rq_profile'] = str(int(option.get('value', None)) + 1)
                            except TypeError:
                                pass
                            break
                elif name == ST_EDIT_SHAPER_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            value = option.get('value', None)
                            if value is None:
                                break
                            elif value != '0':
                                value = f'shaper:{int(value) - 1}'
                            uhp_values['hub_shaper'] = value
                            break
        return uhp_values

    def add_station(self, number=1, on=True, sn=12345, redundant_sn=0, shaper=0, req_pr=0, tcpa=False):
        """
        Add or replace station to UHP Advanced->Network->Stations->Station#.

        :param int number: station number in the table
        :param bool on: True if station ON, otherwise False
        :param int sn: station serial number
        :param int redundant_sn: redundant serial number
        :param int shaper: shaper number to use
        :param int req_pr: request profile number
        :param bool tcpa: TCP acceleration for this station
        :returns bool: True if station is added, otherwise False
        """
        payload = {
            STATION_NUMBER_ATTR_NAME: number,
            STATION_SN_ATTR_NAME: sn,
            STATION_RED_SN_ATTR_NAME: redundant_sn,
            STATION_SHAPER_ATTR_NAME: shaper,
            STATION_REQ_PR_ATTR_NAME: req_pr,
        }
        if on:
            payload[STATION_ON_ATTR_NAME] = 1
        if tcpa:
            payload[STATION_TCPA_ATTR_NAME] = 1
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cw24?{payload}&ta=Apply'
        req = self.get_request(url)
        if req:
            return True
        return False

    def get_demodulator_statistics(self, demodulator=1):
        """
        Get the data from the UHP Demodulator statistics page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        `rx_dc_power`, `rx_10m`, `rx{demodulator}_offset`, `dvb_search`, `rx{demodulator}_lo`, `rx{demodulator}_frq`,
        `rx{demodulator}_sr`, `rx{demodulator}_input`, `rx{demodulator}_spi`
        The rest are UHP specific:
        `rf_lvl`, `tx_spi`, `modcod`, `rolloff`, `cn`, `rx_offset`, and `fix_offset`.

        The dictionary values are taken from the page unmodified but lowercased.

        :param int demodulator: demodulator number to get statistics from
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        # TODO: add the rest values parsing
        if demodulator == 1:
            req = self.get_request(f'http://{self._router_address}/ss33')
        else:
            req = self.get_request(f'http://{self._router_address}/ss27')
        uhp_values = {}
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tag = soup.find('pre')
            if tag is None:
                return uhp_values
            else:
                data = tag.text
            uhp_values['rx_dc_power'] = self.get_support_info_value(re.compile(r'lnb-pwr:\s[0-9a-z]+'), data=data)
            uhp_values['rx_10m'] = self.get_support_info_value(re.compile(r't10m:\s[a-z]+'), data=data)
            uhp_values[f'rx{demodulator}_offset'] = self.get_support_info_value(re.compile(r'offset:\s[0-9]+'),
                                                                                data=data)
            uhp_values[f'dvb_search'] = self.get_support_info_value(re.compile(r'searchbw:\s[0-9]+'), data=data)
            uhp_values[f'rx{demodulator}_lo'] = self.get_support_info_value(re.compile(r'lo:\s[0-9]+'), data=data)
            uhp_values[f'rx{demodulator}_frq'] = self.get_support_info_value(re.compile(r'frq:\s[0-9]+'), data=data)
            uhp_values[f'rx{demodulator}_sr'] = self.get_support_info_value(re.compile(r'sr:\s[0-9]+'), data=data)
            uhp_values[f'rx{demodulator}_input'] = self.get_support_info_value(re.compile(r'input:[\s]+rx-[0-9]'),
                                                                               data=data)
            uhp_values[f'rx{demodulator}_spi'] = self.get_support_info_value(re.compile(r'spi:[\s]+[a-z]+'), data=data)
            lines = data.split('\n')
            for i in range(len(lines)):
                if lines[i - 1].find('InLvl') != -1 and lines[i - 1].find('SpI') != -1:
                    values = lines[i].rstrip('|').lstrip('|').split('|')
                    if len(values) < 7:
                        break
                    uhp_values[f'rf_lvl'] = values[0].rstrip().lstrip()
                    uhp_values[f'tx_spi'] = values[1].rstrip().lstrip()
                    uhp_values[f'modcod'] = values[2].rstrip().lstrip()
                    uhp_values[f'rolloff'] = values[3].rstrip().lstrip()
                    uhp_values[f'cn'] = values[4].rstrip().lstrip()
                    try:
                        uhp_values[f'rx_offset'] = values[5].split()[0].rstrip().lstrip()
                        uhp_values[f'fix_offset'] = values[6].split()[0].rstrip().lstrip()
                    except IndexError:
                        pass
        return uhp_values

    def get_stations_state(self):
        # TODO: make the rest stations parsing. Currently only 10 firsts are available
        """
        Get the data from the UHP Stations statistics page as a dictionary. The outer keys are the station numbers.
        The dictionary values are taken from the page lowercased.
        `bytes`, `crc`, `req`, `all`, `bdrx`, `rf`, `a1`, `strx`, `sttx`, `state`, `asterix`, and `not_defined`.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/ss24')
        if not req:
            return uhp_values
        soup = BeautifulSoup(req.content, 'html.parser')
        tag = soup.find('pre')
        if tag is None:
            return uhp_values
        else:
            data = tag.text
        lines = data.split('\n')
        for line in lines:
            try:
                if line[0].isdigit():
                    values = line.split('|')
                    if len(values) < 6:
                        break
                    stn_num = values[0].rstrip()
                    uhp_values[stn_num] = {}
                    if len(values[1].split()) == 2:
                        uhp_values[stn_num]['bytes'], uhp_values[stn_num]['crc'] = values[1].split()
                    if len(values[2].split()) == 2:
                        uhp_values[stn_num]['req'], uhp_values[stn_num]['all'] = values[2].split()
                    if len(values[3].split()) == 3:
                        uhp_values[stn_num]['bdrx'], uhp_values[stn_num]['rf'], uhp_values[stn_num]['a'] = values[3]. \
                            split()
                    elif len(values[3].split()) == 2:
                        uhp_values[stn_num]['bdrx'], uhp_values[stn_num]['rf'] = values[3]. \
                            split()
                        uhp_values[stn_num]['a1'] = None
                    if len(values[4].split()) == 3:
                        uhp_values[stn_num]['strx'], uhp_values[stn_num]['sttx'], \
                        uhp_values[stn_num]['a2'] = values[4].split()
                    if len(values[5].split()) == 3:
                        uhp_values[stn_num]['state'], uhp_values['asterix'], uhp_values[stn_num]['not_defined'] \
                            = values[5].rstrip('\r').split()
                    elif len(values[5].split()) == 2:
                        uhp_values[stn_num]['state'], uhp_values['not_defined'] = values[5].rstrip('\r').split()
                        uhp_values['asterix'] = None
            except IndexError:
                continue
        return uhp_values

    def get_stations_byprio(self) -> Dict[str, Dict[str, str]]:
        """
        Get the data from the UHP Stations ByPrio statistics page as a dictionary. All the stations are retrieved.
        The outer keys are the station numbers. The inner keys are the following:
            'p1_bytes', 'p2_bytes', 'p3_bytes', 'p4_bytes', 'p5_bytes', 'p6_bytes', 'p7_bytes'.

        :returns Dict[str, Dict] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        next_30_link = f'http://{self._router_address}/ss24?da=1&db=3'
        last_next_30_link = next_30_link  # If the current Next 30 link equals to the last Next 30 link, break the cycle
        for i in range(68):  # Maximum number of stations are 2040, therefore it is possible to get 68 * 30 pages max
            req = self.get_request(next_30_link)
            if not req:
                return uhp_values
            soup = BeautifulSoup(req.content, 'html.parser')
            tag = soup.find('pre')
            if tag is None:
                return uhp_values
            else:
                data = tag.text.rstrip('\n\r')
            lines = data[data.find('Stn'):].split('\n')
            for line in lines[1:]:
                p = re.compile('\d+\s+\|')
                if p.search(line) is not None:
                    values = line.split('|')
                    if values[0].strip() not in uhp_values.keys():
                        uhp_values[values[0].strip()] = {f'p{i+1}_bytes': values[1].split()[i] for i in range(7)}
                else:
                    break
            # Finding next 30 link
            a_tags = soup.find_all('a')
            for a_tag in a_tags:
                if a_tag.contents[0] == 'Next 30':
                    next_30_link = f'http://{self._router_address}/{a_tag["href"]}'
                    break
            if next_30_link == last_next_30_link:
                break
            else:
                last_next_30_link = next_30_link
        return uhp_values

    def get_ip_routing_stats(self):
        """
        Get the data from the UHP IP routing statistics page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'ip_screening'.
        The dictionary values are taken from the page using regular expressions.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/ss4')
        if req:
            value = re.compile(r'ip scr:[\s]*[a-z]+').search(req.text.lower())
            if value is not None:
                uhp_values['ip_screening'] = value.group().split()[-1]
        return uhp_values

    def get_snmp_stats(self):
        """
        Get the data from the UHP SNMP statistics page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'snmp_mode', 'snmp_user', 'snmp_auth', 'snmp_user', 'snmp_read', 'snmp_write', 'access1_ip', and 'access2_ip'.
        The dictionary values are taken from the page using regular expressions.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/ss9')
        if req:
            version = re.compile(r'version - [^\s]+').search(req.text.lower())
            if version is not None:
                version = version.group().split('-')[-1].strip()
                if version == 'snmpv3':
                    uhp_values['snmp_mode'] = SnmpModes.V3
                elif version == 'snmpv1/v2c':
                    uhp_values['snmp_mode'] = SnmpModes.V1_V2C
            username = re.compile(r'Username - [^\n]+').search(req.text)
            if username is not None:
                uhp_values['snmp_user'] = username.group().split('-')[-1].strip().rstrip()

            privacy_mode = re.compile(r'privacy mode - [^\n]+').search(req.text.lower())
            if privacy_mode is not None:
                privacy_mode = privacy_mode.group().split('-')[-1].strip().rstrip()
                if privacy_mode == 'no auth,no priv':
                    uhp_values['snmp_auth'] = SnmpAuth.NO_AUTH
                elif privacy_mode == 'auth,no priv':
                    uhp_values['snmp_auth'] = SnmpAuth.AUTH_NO_PRIV
                elif privacy_mode == 'auth,priv':
                    uhp_values['snmp_auth'] = SnmpAuth.AUTH_PRIV

            # TODO: NMS currently does not have 'auth_password' and 'priv_password' fields
            auth_password = re.compile(r'Auth password - [^\n]+').search(req.text)
            if auth_password is not None:
                uhp_values['auth_password'] = auth_password.group().split('-')[-1].strip().rstrip()

            priv_password = re.compile(r'Priv password - [^\n]+').search(req.text)
            if priv_password is not None:
                uhp_values['priv_password'] = priv_password.group().split('-')[-1].strip().rstrip()

            comm_read = re.compile(r'read community[\s]*-[\s]*[^\s]+').search(req.text.lower())
            if comm_read is not None:
                uhp_values['snmp_read'] = comm_read.group().split('-')[-1].strip()
            comm_write = re.compile(r'wrt\. community[\s]*-[\s]*[^\s]+').search(req.text.lower())
            if comm_write is not None:
                uhp_values['snmp_write'] = comm_write.group()[len('wrt. community - '):]
            access_ip1 = re.compile(r'ip permitted 1 - [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+').search(req.text.lower())
            if access_ip1 is not None:
                uhp_values['access1_ip'] = access_ip1.group()[len('ip permitted 1 - '):]
            access_ip2 = re.compile(r'ip permitted 2 - [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+').search(req.text.lower())
            if access_ip2 is not None:
                uhp_values['access2_ip'] = access_ip2.group()[len('ip permitted 2 - '):]
        return uhp_values

    def get_dhcp_stats(self):
        """
        Get the data from the UHP DHCP statistics page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'dhcp_mode', 'dhcp_vlan', 'dhcp_ip_start', 'dhcp_ip_end',
        'dhcp_mask', 'dhcp_gateway', 'dhcp_dns', and 'dhcp_timeout'.
        The dictionary values are taken from the page using regular expressions.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/ss8')
        if req:
            mode_re = re.compile(r'mode:\s*[a-z]+').search(req.text.lower())
            if mode_re is not None:
                uhp_values['dhcp_mode'] = mode_re.group().split()[-1]
            vlan_re = re.compile(r'vlan:\s*[0-9]+').search(req.text.lower())
            if vlan_re is not None:
                uhp_values['dhcp_vlan'] = vlan_re.group().split()[-1]
            ip_start_re = re.compile(r'range:\s*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+').search(req.text.lower())
            if ip_start_re is not None:
                uhp_values['dhcp_ip_start'] = ip_start_re.group()[len('range: '):].split()[-1]
            ip_end_re = re.compile(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+-[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+') \
                .search(req.text.lower())
            if ip_end_re is not None:
                uhp_values['dhcp_ip_end'] = ip_end_re.group().split('-')[-1]
            mask_re = re.compile(r'mask:\s*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+').search(req.text.lower())
            if mask_re is not None:
                # Converting netmask into the prefix format
                uhp_values['dhcp_mask'] = f'/{self._mask_to_prefix(mask_re.group().split()[-1])}'
            gateway_re = re.compile(r'gateway\(local relay ip\):\s*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+') \
                .search(req.text.lower())
            if gateway_re is not None:
                uhp_values['dhcp_gateway'] = gateway_re.group().split()[-1]
            dns_re = re.compile(r'dns\(relay\):\s*[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+').search(req.text.lower())
            if dns_re is not None:
                uhp_values['dhcp_dns'] = dns_re.group().split()[-1]
            timeout_re = re.compile(r'lease:\s*[0-9]+').search(req.text.lower())
            if timeout_re is not None:
                uhp_values['dhcp_timeout'] = timeout_re.group().split()[-1]
        return uhp_values

    def get_dns_stats(self):
        """
        Get the data from the UHP DNS statistics page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'dns_caching', and 'dns_timeout'.
        The dictionary values are taken from the page using regular expressions.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/ss59')
        if req:
            dns_caching_re = re.compile(r'mode:\s*[a-z]+').search(req.text.lower())
            if dns_caching_re is not None:
                if dns_caching_re.group().split()[-1] == 'on':
                    uhp_values['dns_caching'] = '1'
                else:
                    uhp_values['dns_caching'] = '0'
            dns_timeout_re = re.compile(r'clear timeout:\s*[0-9]+').search(req.text.lower())
            if dns_timeout_re is not None:
                uhp_values['dns_timeout'] = dns_timeout_re.group().split()[-1]
        return uhp_values

    def get_snmp_form(self):
        """
        Get the data from the UHP SNMP form page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'snmp_mode', 'snmp_user', 'snmp_auth', 'snmp_user', 'comm_read', 'comm_write', 'access1_ip', and 'access2_ip'.
        The dictionary values are taken from the page using regular expressions.
        All the values are lowercased.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cc9')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name = tag.get('name', None)
                value = tag.get('value', None)
                if name is None or value is None:
                    continue
                elif name == SNMP_ACCESS_IP1_ATTR_NAME:
                    uhp_values['access1_ip'] = value
                elif name == SNMP_ACCESS_IP2_ATTR_NAME:
                    uhp_values['access2_ip'] = value
                elif name == SNMP_READ_COMMUNITY_ATTR_NAME:
                    uhp_values['snmp_read'] = value.lower()
                elif name == SNMP_WRITE_COMMUNITY_ATTR_NAME:
                    uhp_values['snmp_write'] = value.lower()
                elif name == SNMP_USERNAME_ATTR_NAME:
                    uhp_values['snmp_user'] = value.lower()
                elif name == SNMP_AUTH_PASS_ATTR_NAME:
                    uhp_values['snmp_auth_pass'] = value.lower()
                elif name == SNMP_PRIV_PASS_ATTR_NAME:
                    uhp_values['snmp_priv_pass'] = value.lower()
            tags = soup.find_all('select')
            for tag in tags:
                name = tag.get('name', None)
                if name is None:
                    continue
                elif name == SNMP_VERSION_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            if option.get('value', None) == '0':
                                uhp_values['snmp_mode'] = SnmpModesStr.V1_V2C.lower()
                            elif option.get('value', None) == '1':
                                uhp_values['snmp_mode'] = SnmpModesStr.V3.lower()
                elif name == SNMP_PRIV_MODE_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            value = option.get('value', None)
                            if value == '0':
                                uhp_values['snmp_auth'] = SnmpAuthStr.NO_AUTH.lower()
                            elif value == '1':
                                uhp_values['snmp_auth'] = SnmpAuthStr.AUTH_NO_PRIV.lower()
                            elif value == '2':
                                uhp_values['snmp_auth'] = SnmpAuthStr.AUTH_PRIV.lower()
                            break
        return uhp_values

    def get_arp_form(self):
        """
        Get the data from the UHP ARP settings page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'arp_timeout', and 'proxy_arp'.
        The dictionary values are taken from the page unmodified except for 'proxy_arp' which is either '1' or '0'.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cc23')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                if tag['name'] == ARP_TABLE_CLEAR_ATTR_NAME:
                    uhp_values['arp_timeout'] = tag.get('value', None)
                elif tag['name'] == PROXY_ARP_ENABLE_ATTR_NAME:
                    if tag.get('checked') is not None:
                        uhp_values['proxy_arp'] = '1'
                    else:
                        uhp_values['proxy_arp'] = '0'
        return uhp_values

    def set_arp_form(self, params=None):
        """
        Set the data to the UHP ARP settings page.
        The dictionary keys correspond to the NMS naming convention:
        'arp_timeout', and 'proxy_arp'.
        The dictionary values are taken from the page unmodified except for 'proxy_arp' which is either '1' or '0'.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        if params is None:
            raise InvalidOptionsException('Parameters to set ARP settings are not passed')
        payload = {
            ARP_TABLE_CLEAR_ATTR_NAME: params.get('arp_timeout', 5),
            PROXY_ARP_ENABLE_ATTR_NAME: params.get('proxy_arp', 0),
        }
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cw23?{payload}&ta=Apply'
        req = self.get_request(url)
        if req:
            return True
        return False

    def get_tftp_form(self):
        """
        Get the data from the UHP TFTP settings page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'tftp_server', 'tftp_vlan'.
        The dictionary values are taken from the page unmodified.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cc21')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                if tag['name'] == TFTP_SERVER_IP_ATTR_NAME:
                    uhp_values['tftp_server'] = tag.get('value', None)
                elif tag['name'] == TFTP_VLAN_ATTR_NAME:
                    uhp_values['tftp_vlan'] = tag.get('value', None)
        return uhp_values

    def get_nat_form(self):
        """
        Get the data from the UHP NAT settings page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'nat_enable', 'nat_ext_ip', 'nat_int_ip', 'nat_int_mask'.
        The dictionary values are taken from the page unmodified, except for the internal mask
        that is converted to the prefix format.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {'port_map': []}
        req = self.get_request(f'http://{self._router_address}/cc7')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                if tag['name'] == NAT_ENABLE_ATTR_NAME:
                    if tag.get('checked') is not None:
                        uhp_values['nat_enable'] = '1'
                    else:
                        uhp_values['nat_enable'] = '0'
                elif tag['name'] == NAT_EXTERNAL_IP_ATTR_NAME:
                    uhp_values['nat_ext_ip'] = tag.get('value', None)
                elif tag['name'] == NAT_INTERNAL_NETWORK_ATTR_NAME:
                    uhp_values['nat_int_ip'] = tag.get('value', None)
                elif tag['name'] == NAT_INTERNAL_MASK_ATTR_NAME:
                    uhp_values['nat_int_mask'] = f'/{self._mask_to_prefix(tag.get("value", None))}'

            # Getting port mappings
            soup = BeautifulSoup(req.content, 'lxml')
            tables = soup.find_all('table')
            rows = tables[-1].find_all('tr')
            for i in range(len(rows)):
                row_data = rows[i].find_all('td')
                data = [td.text for td in row_data if td.text not in ('Del', '', ' ')]
                if len(data) == 3:
                    uhp_values['port_map'].append({
                        'external_port': data[0], 'internal_ip': data[1], 'internal_port': data[2]
                    })
        return uhp_values

    def get_rip_form(self):
        """
        Get the data from the UHP RIPv2 settings page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'rip_mode', 'rip_update', 'rip_timeout', 'rip_cost', 'rip_auth', 'rip_pass'.
        The dictionary values are taken from the page unmodified.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cc10')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name = tag.get('name', None)
                value = tag.get('value', None)
                if name is None or value is None:
                    continue
                elif name == RIP_UPDATE_ATTR_NAME:
                    uhp_values['rip_update'] = value
                elif name == RIP_TIMEOUT_ATTR_NAME:
                    uhp_values['rip_timeout'] = value
                elif name == RIP_COST_ATTR_NAME:
                    uhp_values['rip_cost'] = value
                elif name == RIP_PASS_AUTH_NAME:
                    uhp_values['rip_pass'] = value
                # TODO: NMS contains three modes in comparision with UHP
                elif name == RIP_ENABLE_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['rip_mode'] = RipModesStr.ON.lower()
                    else:
                        uhp_values['rip_mode'] = RipModesStr.OFF.lower()
                elif name == RIP_AUTH_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['rip_auth'] = '1'
                    else:
                        uhp_values['rip_auth'] = '0'
        return uhp_values

    def get_sntp_form(self):
        """
        Get the data from the UHP SNTP settings page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'sntp_mode', 'sntp_server', 'sntp_vlan'.
        The dictionary values are taken from the page unmodified, except for the sntp_mode
        that is converted to the corresponding NMS value.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cc11')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                if tag['name'] == SNTP_SERVER_IP_ATTR_NAME:
                    uhp_values['sntp_server'] = tag.get('value', None)
                elif tag['name'] == SNTP_VLAN_ATTR_NAME:
                    uhp_values['sntp_vlan'] = tag.get('value', None)
            tags = soup.find_all('select')
            for tag in tags:
                if tag['name'] == SNTP_MODE_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            mode = option.contents[0].lower()
                            if mode == 'client+server':
                                mode = 'both'
                            uhp_values['sntp_mode'] = mode
                            break
        return uhp_values

    def get_multicast_form(self):
        """
        Get the data from the UHP Multicast settings page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'mcast_mode', 'mcast_timeout'.
        The dictionary values are taken from the page unmodified.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cc39')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                if tag['name'] == MULTICAST_TIMEOUT_ATTR_NAME:
                    uhp_values['mcast_timeout'] = tag.get('value', None)
                    break
            tags = soup.find_all('select')
            for tag in tags:
                if tag['name'] == MULTICAST_MODE_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            uhp_values['mcast_mode'] = option.contents[0].lower()
        return uhp_values

    def get_security_form(self):
        """
        Get the data from the UHP Security system settings page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'ctl_protect', 'ctl_key'.
        The dictionary values are taken from the page unmodified, except for ctl_protect
        that is converted to either '1' or '0' depending on the mode.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cc58')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                if tag['name'] == ENCRYPTION_KEY_ATTR_NAME:
                    uhp_values['ctl_key'] = tag.get('value', None)
                    break
            tags = soup.find_all('select')
            for tag in tags:
                if tag['name'] == ENCRYPTION_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            mode = option.contents[0].lower()
                            if mode == 'on':
                                uhp_values['ctl_protect'] = '1'
                            else:
                                uhp_values['ctl_protect'] = '0'
        return uhp_values

    def get_tcpa_form(self):
        """
        Get the data from the UHP TCP Acceleration settings page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'tcpa_enable', 'from_svlan', 'to_svlan', 'tcpa_mss', 'max_rx_win',
        'rx_win_upd', 'sessions', 'buf_coef', 'max_pkts', 'max_qlen',
        'retry_time', 'tcpa_retries', 'tcpa_timeout', and 'ack_period'.
        The dictionary values are taken from the page unmodified, except for tcpa_version
        that is converted to the corresponding NMS value.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cc12')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                if tag['name'] == TCPA_ENABLE_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['tcpa_enable'] = '1'
                    else:
                        uhp_values['tcpa_enable'] = '0'
                elif tag['name'] == TCPA_FROM_SVLAN_ATTR_NAME:
                    uhp_values['from_svlan'] = tag.get('value', None)
                elif tag['name'] == TCPA_TO_SVLAN_ATTR_NAME:
                    uhp_values['to_svlan'] = tag.get('value', None)
                elif tag['name'] == TCPA_MSS_ATTR_NAME:
                    uhp_values['tcpa_mss'] = tag.get('value', None)
                elif tag['name'] == TCPA_MAX_WINDOW_ATTR_NAME:
                    uhp_values['max_rx_win'] = tag.get('value', None)
                elif tag['name'] == TCPA_WINDOW_UPDATE_ATTR_NAME:
                    uhp_values['rx_win_upd'] = tag.get('value', None)
                elif tag['name'] == TCPA_SESSIONS_ATTR_NAME:
                    uhp_values['sessions'] = tag.get('value', None)
                elif tag['name'] == TCPA_BUF_COEF_ATTR_NAME:
                    uhp_values['buf_coef'] = tag.get('value', None)
                elif tag['name'] == TCPA_MAX_PKTS_ATTR_NAME:
                    uhp_values['max_pkts'] = tag.get('value', None)
                elif tag['name'] == TCPA_MAX_QLEN_ATTR_NAME:
                    uhp_values['max_qlen'] = tag.get('value', None)
                elif tag['name'] == TCPA_RETRY_TIME_ATTR_NAME:
                    uhp_values['retry_time'] = tag.get('value', None)
                elif tag['name'] == TCPA_RETRIES_ATTR_NAME:
                    uhp_values['tcpa_retries'] = tag.get('value', None)
                elif tag['name'] == TCPA_TIMEOUT_ATTR_NAME:
                    uhp_values['tcpa_timeout'] = tag.get('value', None)
                elif tag['name'] == TCPA_ACK_PERIOD_ATTR_NAME:
                    uhp_values['ack_period'] = tag.get('value', None)

            tags = soup.find_all('select')
            for tag in tags:
                if tag['name'] == TCPA_VERSION_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            uhp_values['tcpa_version'] = option.contents[0].lower().replace('.', '_')
                            break
        return uhp_values

    def get_service_monitoring_form(self):
        """
        Get the data from the UHP Service monitoring page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'sm_enable', 'sm_interval', 'sm_losts', 'poll_enable1', 'poll_ip1',
        'poll_vlan1', 'chk_delay1', 'max_delay1', 'poll_enable2', 'poll_ip2',
        'poll_vlan2', 'chk_delay2', 'max_delay2', and 'rx_check_rate',
        'tx_check_rate', 'bkp_enable', 'bkp_ip', 'auto_reboot', 'reboot_delay',
        'lan_rx_check', and 'lan_tx_check'.
        The dictionary values are taken from the page unmodified, except for tcpa_version
        that is converted to the corresponding NMS value.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cc15')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                if tag['name'] == SM_ENABLE_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['sm_enable'] = '1'
                    else:
                        uhp_values['sm_enable'] = '0'
                elif tag['name'] == SM_INTERVAL_ATTR_NAME:
                    uhp_values['sm_interval'] = tag.get('value', None)
                elif tag['name'] == SM_LOSTS_ATTR_NAME:
                    uhp_values['sm_losts'] = tag.get('value', None)
                elif tag['name'] == SM_POLL_ENABLE1_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['poll_enable1'] = '1'
                    else:
                        uhp_values['poll_enable1'] = '0'
                elif tag['name'] == SM_POLL_IP1_ATTR_NAME:
                    uhp_values['poll_ip1'] = tag.get('value', None)
                elif tag['name'] == SM_POLL_VLAN1_ATTR_NAME:
                    uhp_values['poll_vlan1'] = tag.get('value', None)
                elif tag['name'] == SM_CHK_DELAY1_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['chk_delay1'] = '1'
                    else:
                        uhp_values['chk_delay1'] = '0'
                elif tag['name'] == SM_MAX_DELAY1_ATTR_NAME:
                    uhp_values['max_delay1'] = tag.get('value', None)

                elif tag['name'] == SM_POLL_ENABLE2_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['poll_enable2'] = '1'
                    else:
                        uhp_values['poll_enable2'] = '0'
                elif tag['name'] == SM_POLL_IP2_ATTR_NAME:
                    uhp_values['poll_ip2'] = tag.get('value', None)
                elif tag['name'] == SM_POLL_VLAN2_ATTR_NAME:
                    uhp_values['poll_vlan2'] = tag.get('value', None)
                elif tag['name'] == SM_CHK_DELAY2_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['chk_delay2'] = '1'
                    else:
                        uhp_values['chk_delay2'] = '0'
                elif tag['name'] == SM_MAX_DELAY2_ATTR_NAME:
                    uhp_values['max_delay2'] = tag.get('value', None)

                elif tag['name'] == SM_RX_CHECK_RATE_ATTR_NAME:
                    uhp_values['rx_check_rate'] = tag.get('value', None)
                elif tag['name'] == SM_TX_CHECK_RATE_ATTR_NAME:
                    uhp_values['tx_check_rate'] = tag.get('value', None)
                elif tag['name'] == SM_BACKUP_ENABLE_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['bkp_enable'] = '1'
                    else:
                        uhp_values['bkp_enable'] = '0'
                elif tag['name'] == SM_BACKUP_IP_ATTR_NAME:
                    uhp_values['bkp_ip'] = tag.get('value', None)

                elif tag['name'] == SM_AUTO_REBOOT_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['auto_reboot'] = '1'
                    else:
                        uhp_values['auto_reboot'] = '0'
                elif tag['name'] == SM_REBOOT_DELAY_ATTR_NAME:
                    uhp_values['reboot_delay'] = tag.get('value', None)

            tags = soup.find_all('select')
            for tag in tags:
                if tag['name'] == SM_LAN_RX_CHECK_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            uhp_values['lan_rx_check'] = option.contents[0].lower()
                elif tag['name'] == SM_LAN_TX_CHECK_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            uhp_values['lan_tx_check'] = option.contents[0].lower()
            return uhp_values

    def get_interfaces_form(self):
        # TODO: add the rest of the elements.
        """
        Get the data from the UHP Interfaces page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'mod_queue1', 'mod_queue2', 'mod_queue3', 'mod_queue4', 'mod_queue5',
        'mod_queue6', 'mod_queue7', 'mod_que_ctl'.
        The dictionary values are taken from the page unmodified.

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cc18')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name = tag.get('name', None)
                value = tag.get('value', None)
                if name is None and value is None:
                    continue
                elif name == P1_ATTR_NAME:
                    uhp_values['mod_queue1'] = value
                elif name == P2_ATTR_NAME:
                    uhp_values['mod_queue2'] = value
                elif name == P3_ATTR_NAME:
                    uhp_values['mod_queue3'] = value
                elif name == P4_ATTR_NAME:
                    uhp_values['mod_queue4'] = value
                elif name == P5_ATTR_NAME:
                    uhp_values['mod_queue5'] = value
                elif name == P6_ATTR_NAME:
                    uhp_values['mod_queue6'] = value
                elif name == P7_ATTR_NAME:
                    uhp_values['mod_queue7'] = value
                elif name == CTRL_ATTR_NAME:
                    uhp_values['mod_que_ctl'] = value
        return uhp_values

    def get_stations(self):
        # TODO: find a better way to get the data
        """
        Get the data from the UHP Stations page as a dictionary of dictionaries.
        The outer key is the station number.
        The inner dictionary keys correspond to the NMS naming convention:
        `enable`, `serial`, `red_serial`, `stn_shaper`, `rq_profile`, `tcpa_enable`.

        :returns Dict[str, Dict] uhp_values: a dictionary of dictionaries.
        """
        uhp_values = {}
        dq = 1
        last_number = None
        # each stations page contains max 20 entries, increment by 20 on each cycle
        while dq <= 2041:
            req = self.get_request(f'http://{self._router_address}/cc24?dq={dq}')
            if req:
                soup = BeautifulSoup(req.content, 'html.parser')
                anchor_tags = soup.find_all('a')
                number = None
                for tag in anchor_tags:
                    href = tag.get('href', None)
                    if href is None:
                        continue
                    elif href.startswith('cc24?db='):
                        number = tag.contents[0]
                        if number is None:
                            continue
                        uhp_values[number] = {
                            'enable': None,
                            'serial': None,
                            'red_serial': None,
                            'stn_shaper': None,
                            'rq_profile': None,
                            'tcpa_enable': None,
                        }

                        st_req = self.get_request(f'http://{self._router_address}/{href}')
                        if not st_req:
                            continue

                        soup_st = BeautifulSoup(st_req.content, 'html.parser')
                        input_tags = soup_st.find_all('input')
                        select_tags = soup_st.find_all('select')
                        for input_tag in input_tags:
                            name = input_tag.get('name', None)
                            value = input_tag.get('value', None)
                            if name is None or value is None:
                                continue
                            elif name == STATION_ON_ATTR_NAME:
                                if input_tag.get('checked', None) is not None:
                                    # noinspection PyTypeChecker
                                    uhp_values[number]['enable'] = '1'
                                else:
                                    # noinspection PyTypeChecker
                                    uhp_values[number]['enable'] = '0'
                            elif name == STATION_SN_ATTR_NAME:
                                uhp_values[number]['serial'] = value
                            elif name == STATION_RED_SN_ATTR_NAME:
                                uhp_values[number]['red_serial'] = value
                            elif name == STATION_TCPA_ATTR_NAME:
                                if input_tag.get('checked', None) is not None:
                                    # noinspection PyTypeChecker
                                    uhp_values[number]['tcpa_enable'] = '1'
                                else:
                                    # noinspection PyTypeChecker
                                    uhp_values[number]['tcpa_enable'] = '0'
                        for select_tag in select_tags:
                            name = select_tag.get('name', None)
                            if name is None:
                                continue
                            options = select_tag.find_all('option')
                            for option in options:
                                value = option.get('value', None)
                                if value is None:
                                    continue
                                elif option.get('selected') is not None:
                                    if name == STATION_SHAPER_ATTR_NAME:
                                        uhp_values[number]['stn_shaper'] = value
                                    elif name == STATION_REQ_PR_ATTR_NAME:
                                        uhp_values[number]['rq_profile'] = value
                if last_number == number:
                    break
                dq += 20
                last_number = number
        return uhp_values

    def set_profile_basic(self, profile_number=1, params=None):
        """
        Set Profile basic parameters. The parameters' keys and their default values are the following:
            valid=1, autorun=1, mode=0, timeout=40, title='script'

        :param int profile_number: profile number to write config to
        :param dict params: a dictionary of parameters to apply
        :returns bool: True if request to UHP is successful, otherwise False
        """
        if params is None:
            params = {}
        if params.get('autorun') is not None and not params.get('autorun'):
            autorun = 0
        else:
            autorun = 1
        payload = {
            # TODO: mode validation
            PROFILE_MODE_ATTR_NAME: params.get('mode', 0),
            PROFILE_TIMEOUT_ATTR_NAME: params.get('timeout', 40),
            PROFILE_TITLE_ATTR_NAME: params.get('title', 'script'),
            PROFILE_AUTORUN_ATTR_NAME: autorun,
        }
        url = f'http://{self._router_address}/cB3?{PROFILE_NUMBER_ATTR_NAME}={profile_number}&'
        valid = params.get('valid', None)
        if valid is not None and not valid:
            pass
        else:
            url += f'{PROFILE_VALID_ATTR_NAME}=1&'
        url += f'{urllib.parse.urlencode(payload)}&tf=Apply&df=1'
        self.get_request(url)
        # Have to apply settings twice to make sure that `autorun` and/or `valid` is applied
        req = self.get_request(url)
        if req:
            return True
        return False

    def set_profile_tdm_rx(self, profile_number=1, params=None):
        """
        Set Profile TDM/SCPC RX parameters. The parameters' keys and their default values are the following:
            check_rx=0, input_gain=0, rx1_enable=1, rx1_input=0, rx1_frq=960000, rx1_sr=1600,
            rx2_enable=0, rx2_input=0, rx2_frq=970000, rx2_sr=1000, rx_voltage=0

        :param int profile_number: profile number to write config to
        :param dict params: a dictionary of parameters to apply
        :returns bool: True if request to UHP is successful, otherwise False
        """
        if params is None:
            params = {}
        payload = {
            DEM_CHECK_RX_ATTR_NAME: params.get('check_rx', 0),
            DEM_INPUT_GAIN_ATTR_NAME: params.get('input_gain', 0),
            DEM_RX1_ENABLE_ATTR_NAME: params.get('rx1_enable', 1),
            DEM_RX1_INPUT_ATTR_NAME: params.get('rx1_input', 0),
            DEM_RX1_FREQ_ATTR_NAME: params.get('rx1_frq', 960000),
            DEM_RX1_SR_ATTR_NAME: params.get('rx1_sr', 1600),
            DEM_RX2_ENABLE_ATTR_NAME: params.get('rx2_enable', 0),
            DEM_RX2_INPUT_ATTR_NAME: params.get('rx2_input', 0),
            DEM_RX2_FREQ_ATTR_NAME: params.get('rx2_frq', 970000),
            DEM_RX2_SR_ATTR_NAME: params.get('rx2_sr', 1000),
            DEM_RX_VOLTAGE_ATTR_NAME: params.get('rx_voltage', 0)
        }
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cR3?do=0&da={profile_number}&de=1&{payload}&tf=Apply'
        res = self.get_request(url)
        if not res or self._is_error():
            return False
        return True

    def set_profile_tdm_tx(self, profile_number=1, params=None):
        """
        Set Profile TDM/SCPC TX parameters. The parameters' keys and their default values are the following:
            tx_frq=950000, tx_sr=1000, tx_modcod=4, tx_pilots=0, tx_rolloff=0

        :param int profile_number: profile number to write config to
        :param dict params: a dictionary of parameters to apply
        :returns bool: True if request to UHP is successful, otherwise False
        """
        if params is None:
            params = {}
        payload = {
            TDM_TX_FREQ_ATTR_NAME: params.get('tx_frq', 950000),
            TDM_TX_SR_ATTR_NAME: params.get('tx_sr', 1000),
            TDM_TX_MODCOD_ATTR_NAME: params.get('tx_modcod', 4),
            TDM_TX_PILOTS_ATTR_NAME: params.get('tx_pilots', 0),
            TDM_TX_ROLLOFF_ATTR_NAME: params.get('tx_rolloff', 0)
        }
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cT3?da={profile_number}&{payload}&tf=Apply'
        req = self.get_request(url)
        if req:
            return True
        return False

    def set_profile_tdma_prot(self, profile_number=1, params=None):
        """
        Set Profile TDMA prot parameters. The parameters' keys and their default values are the following:
            stn_number=10, frame_length=64, slot_length=8, no_stn_check=1, rec_all_traffic=0

        :param int profile_number: profile number to write config to
        :param dict params: a dictionary of parameters to apply
        :returns bool: True if request to UHP is successful, otherwise False
        """
        if params is None:
            params = {}
        payload = {
            TDMA_PROT_STN_NUMBER_ATTR_NAME: params.get('stn_number', 10),
            TDMA_PROT_FRAME_LENGTH_ATTR_NAME: params.get('frame_length', 64),
            TDMA_PROT_SLOT_LENGTH_ATTR_NAME: params.get('slot_length', 8),
            TDMA_PROT_NO_STN_CHECK_ATTR_NAME: params.get('no_stn_check', 1),
            TDMA_PROT_REC_ALL_TRAF_ATTR_NAME: params.get('rec_all_traffic', 0)
        }
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cP3?da={profile_number}&de=1&{payload}&tf=Apply&df=1'
        req = self.get_request(url)
        if req:
            return True
        return False

    def set_profile_tdma_rf(self, profile_number=1, params=None):
        """
        Set Profile TDMA RF parameters. The parameters' keys and their default values are the following:
            tdma_sr=1000, tdma_mc=9, 'tdma_roll'=0, enh_tables=0, mf1_rx=1000000, mf1_tx=1000000,
            mf2_en=0, mf2_rx=962000, mf2_tx=962000,
            mf3_en=0, mf3_rx=964000, mf3_tx=964000,
            mf4_en=0, mf4_rx=966000, mf4_tx=966000,


        :param int profile_number: profile number to write config to (default is 1)
        :param dict params: a dictionary of parameters to apply, by default modulator is ON with tx_level=20.0
        :returns bool: True if request to UHP is successful, otherwise False
        """
        if params is None:
            params = {}
        tdma_input = params.get('tdma_input', None)
        if tdma_input is not None:
            if tdma_input == TdmaInputModes.RX1:
                tdma_input = 0
            else:
                tdma_input = 1
        else:
            tdma_input = 0
        rolloff = params.get('tdma_roll', None)
        if rolloff is not None:
            if rolloff == RollofModes.R20:
                rolloff = 0
            else:
                rolloff = 1
        else:
            rolloff = 0
        payload = {
            TDMA_RF_INPUT_ATTR_NAME: tdma_input,
            TDMA_RF_SR_ATTR_NAME: params.get('tdma_sr', 1000),
            TDMA_RF_MODCOD_ATTR_NAME: params.get('tdma_mc', 9),
            TDMA_RF_ROLL_ATTR_NAME: rolloff,
            TDMA_RF_ENH_TABLE_ATTR_NAME: params.get('enh_tables', 0),
            TDMA_RF_RX1_ATTR_NAME: params.get('mf1_rx', 1000000),
            TDMA_RF_TX1_ATTR_NAME: params.get('mf1_tx', 1000000),
            TDMA_RF_RX2_ATTR_NAME: params.get('mf2_rx', 962000),
            TDMA_RF_TX2_ATTR_NAME: params.get('mf2_tx', 962000),
            TDMA_RF_RX3_ATTR_NAME: params.get('mf3_rx', 964000),
            TDMA_RF_TX3_ATTR_NAME: params.get('mf3_tx', 964000),
            TDMA_RF_RX4_ATTR_NAME: params.get('mf4_rx', 966000),
            TDMA_RF_TX4_ATTR_NAME: params.get('mf4_tx', 966000),
            TDMA_RF_ENABLE2_ATTR_NAME: params.get('mf2_en', 0),
            TDMA_RF_ENABLE3_ATTR_NAME: params.get('mf3_en', 0),
            TDMA_RF_ENABLE4_ATTR_NAME: params.get('mf4_en', 0),
        }
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cD3?da={profile_number}&de=1&{payload}&ta=Apply'
        req = self.get_request(url)
        if req:
            return True
        return False

    def set_profile_tdma_acm(self, profile_number=1, params=None):
        """
        Set Profile TDMA ACM parameters. The parameters' keys and their default values are the following:
            acm_enable=0, mode=0, mesh_mc=0, hub_rx_mesh=0, bpsk1_2=0, bpsk2_3=0, bpsk3_4=0, bpsk5_6=0,
            qpsk1_2=0, qpsk2_3=0, qpsk3_4=0, qpsk5_6=0, epsk1_2=0, epsk2_3=0, epsk3_4=0, epsk5_6=0,
            apsk1_2=0, apsk2_3=0, apsk3_4=0, apsk5_6=0, t_bpsk1_2=0.0, t_bpsk2_3=0.3, t_bpsk3_4=1.2, t_bpsk5_6=2.2,
            t_qpsk1_2=2.8, t_qpsk2_3=4.1, t_qpsk3_4=5.1, t_qpsk5_6=6.4, t_epsk1_2=9.3, t_epsk2_3=9.3, t_epsk3_4=9.8,
            t_epsk5_6=11.2, t_apsk1_2=13.6, t_apsk2_3=13.6, t_apsk3_4=13.6, t_apsk5_6=14.6
        :param int profile_number: profile number to write config to
        :param dict params: a dictionary of parameters to apply
        :returns bool: True if request to UHP is successful, otherwise False
        """
        if params is None:
            params = {}
        payload = {
            TDMA_ACM_ENABLE_ATTR_NAME: params.get('acm_enable', 0),
            TDMA_ACM_MODE_ATTR_NAME: params.get('mode', 0),
            TDMA_MESH_MODCOD_ATTR_NAME: params.get('mesh_mc', 0),
            TDMA_RECEIVE_MESH_ATTR_NAME: params.get('hub_rx_mesh', 0),
            TDMA_ACM_ACTIVE_BPSK_1_2_ATTR_NAME: params.get('bpsk1_2', 0),
            TDMA_ACM_ACTIVE_BPSK_2_3_ATTR_NAME: params.get('bpsk2_3', 0),
            TDMA_ACM_ACTIVE_BPSK_3_4_ATTR_NAME: params.get('bpsk3_4', 0),
            TDMA_ACM_ACTIVE_BPSK_5_6_ATTR_NAME: params.get('bpsk5_6', 0),
            TDMA_ACM_ACTIVE_QPSK_1_2_ATTR_NAME: params.get('qpsk1_2', 0),
            TDMA_ACM_ACTIVE_QPSK_2_3_ATTR_NAME: params.get('qpsk2_3', 0),
            TDMA_ACM_ACTIVE_QPSK_3_4_ATTR_NAME: params.get('qpsk3_4', 0),
            TDMA_ACM_ACTIVE_QPSK_5_6_ATTR_NAME: params.get('qpsk5_6', 0),
            TDMA_ACM_ACTIVE_8PSK_1_2_ATTR_NAME: params.get('epsk1_2', 0),
            TDMA_ACM_ACTIVE_8PSK_2_3_ATTR_NAME: params.get('epsk2_3', 0),
            TDMA_ACM_ACTIVE_8PSK_3_4_ATTR_NAME: params.get('epsk3_4', 0),
            TDMA_ACM_ACTIVE_8PSK_5_6_ATTR_NAME: params.get('epsk5_6', 0),
            TDMA_ACM_ACTIVE_16APSK_1_2_ATTR_NAME: params.get('apsk1_2', 0),
            TDMA_ACM_ACTIVE_16APSK_2_3_ATTR_NAME: params.get('apsk2_3', 0),
            TDMA_ACM_ACTIVE_16APSK_3_4_ATTR_NAME: params.get('apsk3_4', 0),
            TDMA_ACM_ACTIVE_16APSK_5_6_ATTR_NAME: params.get('apsk5_6', 0),
            TDMA_ACM_THRESH_BPSK_1_2_ATTR_NAME: params.get('t_bpsk1_2', 0.0),
            TDMA_ACM_THRESH_BPSK_2_3_ATTR_NAME: params.get('t_bpsk2_3', 0.3),
            TDMA_ACM_THRESH_BPSK_3_4_ATTR_NAME: params.get('t_bpsk3_4', 1.2),
            TDMA_ACM_THRESH_BPSK_5_6_ATTR_NAME: params.get('t_bpsk5_6', 2.2),
            TDMA_ACM_THRESH_QPSK_1_2_ATTR_NAME: params.get('t_qpsk1_2', 2.8),
            TDMA_ACM_THRESH_QPSK_2_3_ATTR_NAME: params.get('t_qpsk2_3', 4.1),
            TDMA_ACM_THRESH_QPSK_3_4_ATTR_NAME: params.get('t_qpsk3_4', 5.1),
            TDMA_ACM_THRESH_QPSK_5_6_ATTR_NAME: params.get('t_qpsk5_6', 6.4),
            TDMA_ACM_THRESH_8PSK_1_2_ATTR_NAME: params.get('t_epsk1_2', 9.3),
            TDMA_ACM_THRESH_8PSK_2_3_ATTR_NAME: params.get('t_epsk2_3', 9.3),
            TDMA_ACM_THRESH_8PSK_3_4_ATTR_NAME: params.get('t_epsk3_4', 9.8),
            TDMA_ACM_THRESH_8PSK_5_6_ATTR_NAME: params.get('t_epsk5_6', 11.2),
            TDMA_ACM_THRESH_16APSK_1_2_ATTR_NAME: params.get('t_apsk1_2', 13.6),
            TDMA_ACM_THRESH_16APSK_2_3_ATTR_NAME: params.get('t_apsk2_3', 13.6),
            TDMA_ACM_THRESH_16APSK_3_4_ATTR_NAME: params.get('t_apsk3_4', 13.6),
            TDMA_ACM_THRESH_16APSK_5_6_ATTR_NAME: params.get('t_apsk5_6', 14.6),
        }
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cG3?da={profile_number}&de=1&{payload}&tq=Apply'
        req = self.get_request(url)
        if req:
            return True
        return False

    def set_profile_modulator(self, profile_number=1, params=None):
        """
        Set Profile Modulator parameters. The parameters' keys and their default values are the following:
            tx_on=1, tx_level not changed if not passed

        :param int profile_number: profile number to write config to (default is 1)
        :param dict params: a dictionary of parameters to apply, by default modulator is ON with tx_level=20.0
        :returns bool: True if request to UHP is successful, otherwise False
        """
        if params is None:
            params = {}
        tx_on = params.get('tx_on')
        if tx_on is None or tx_on:
            tx_on = 1
        else:
            tx_on = 0
        tx_level = params.get('tx_level')
        if tx_level is not None:
            try:
                tx_level = str(float(tx_level)).split('.')
            except TypeError:
                tx_level = ['20', '0']
        else:
            # Getting current modulator level in order to leave it untouched
            cur_lvl = self.get_modulator_form(profile_number=profile_number).get('tx_level')
            if cur_lvl is not None:
                cur_lvl = cur_lvl.split('.')
                tx_level = [cur_lvl[0], cur_lvl[1]]
            else:
                tx_level = ['20', '0']
        payload = {
            MOD_TX_ON_ATTR_NAME: tx_on,
            MOD_TX_LEVEL_INT_ATTR_NAME: tx_level[0],
            MOD_TX_LEVEL_FLOAT_ATTR_NAME: tx_level[1],
        }
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cM3?da={profile_number}&de=1&{payload}&tf=Apply'
        req = self.get_request(url)
        if req:
            return True
        return False

    def set_snmp(self, params=None):
        """
        Set SNMP settings in the UHP SNMP form page according to the passed parameters.
        The dictionary keys and their values must correspond to the NMS naming convention:
        'snmp_mode', 'snmp_user', 'snmp_auth', 'snmp_read', 'snmp_write', 'access1_ip', and 'access2_ip'.
        NMS4 uses 'snmp_read', 'snmp_write' as Auth password and Privacy password in the corresponding modes.

        :returns bool: True if the settings are applied, otherwise False
        """
        if params is None:
            params = {}
        # Convert NMS `snmp_mode` string value to UHP integer value
        snmp_mode = params.get('snmp_mode', None)
        if snmp_mode is None or snmp_mode == SnmpModes.OFF or snmp_mode == SnmpModes.V1_V2C:
            snmp_mode = 0
        else:
            snmp_mode = 1
        # Convert NMS 'snmp_auth' string value to UHP integer value
        snmp_auth = params.get('snmp_auth', None)
        if snmp_auth is None or snmp_auth == SnmpAuth.NO_AUTH:
            snmp_auth = 0
        elif snmp_auth == SnmpAuth.AUTH_NO_PRIV:
            snmp_auth = 1
        else:
            snmp_auth = 2
        payload = {
            SNMP_VERSION_ATTR_NAME: snmp_mode,
            SNMP_PRIV_MODE_ATTR_NAME: snmp_auth,
            SNMP_ACCESS_IP1_ATTR_NAME: params.get('access1_ip', '0.0.0.0'),
            SNMP_ACCESS_IP2_ATTR_NAME: params.get('access2_ip', '0.0.0.0'),
            SNMP_READ_COMMUNITY_ATTR_NAME: params.get('snmp_read', 'public'),
            SNMP_WRITE_COMMUNITY_ATTR_NAME: params.get('snmp_write', 'private'),
            SNMP_USERNAME_ATTR_NAME: params.get('snmp_user', ''),
            SNMP_AUTH_PASS_ATTR_NAME: params.get('snmp_read', 'public'),
            SNMP_PRIV_PASS_ATTR_NAME: params.get('snmp_write', 'private')
        }
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cw9?{payload}&ta=Apply'
        req = self.get_request(url)
        if req and req.text.find('ERROR!') == -1:
            return True
        return False

    def run_profile(self, profile_number=1):
        url = f'http://{self._router_address}/ck3?da={profile_number}'
        req = self.get_request(url)
        if req and req.text.find('ERROR!') == -1:
            return True
        return False

    def wait_active_profile(self, timeout=10, profile_number=8):
        while timeout > 0:
            if self.get_current_profile_number() == str(profile_number):
                return True
            timeout -= 1
            time.sleep(1)
        else:
            return False

    def wait_operation_state(self, timeout=30):
        while timeout > 0:
            if self.get_support_info_value(regex=re.compile(r'state:\s[a-z]+')) == 'operation':
                return True
            timeout -= 1
            time.sleep(1)
        else:
            return False

    def reboot(self):
        """Reboot UHP"""
        self.get_request(f'http://{self._router_address}/cw51?ta=Reboot')

    def wait_reboot(self, timeout=30):
        self.get_request(f'http://{self._router_address}/cw51?ta=Reboot')
        time.sleep(3)
        while timeout > 0:
            try:
                self.get_request(f'http://{self._router_address}')
                return True
            except UhpResponseException:
                pass
            timeout -= 1
            time.sleep(1)
        else:
            return False

    def clear_all_stats_log(self):
        req = self.get_request(f'http://{self._router_address}/ss29?ta=Clear%C2%A0all%C2%A0stats%26Log')
        if req:
            return True
        return False

    def set_cotm_amip(self, params=None):
        """
        Set COTM/AMIP settings in the UHP COTM/AMIP form page according to the passed parameters.

        The dictionary keys and their values are the following:
        'location_source' (0 - site setup(default), 1 - network, 2 - console);
        'tx_control' (0 - local(default), 1 - network, 2 - RXD_pin);
        'report_location' (0 - False(default), 1 - True); 'enable' (0 - False(default), 1 - True), 'peer_ip';
        'tcp_port'; 'vlan'; 'mode' (0 - off(default), 1 - Auto); 'use_amip' (0 - False(default), 1 - True);
        'antenna_setup_timeout'

        :returns bool: True if the settings are applied, otherwise False
        """
        if params is None:
            params = {}
        payload = {
            COTM_AMIP_LOCATION_SOURCE_ATTR_NAME: params.get('location_source', 0),
            COTM_AMIP_TX_CONTROL_ATTR_NAME: params.get('tx_control', 0),
            COTM_AMIP_REPORT_LOCATION_TO_HUB_ATTR_NAME: params.get('report_location', 0),
            COTM_AMIP_ENABLE_ATTR_NAME: params.get('enable', 0),
            COTM_AMIP_PEER_IP_ATTR_NAME: params.get('peer_ip', '0.0.0.0'),
            COTM_AMIP_TCP_PORT_ATTR_NAME: params.get('tcp_port', 0),
            COTM_AMIP_VLAN_ATTR_NAME: params.get('vlan', 0),
            COTM_AMIP_MODE_ATTR_NAME: params.get('mode', 0),
            COTM_AMIP_USE_AMIP_ATTR_NAME: params.get('use_amip', 0),
            COTM_AMIP_ANTENNA_SETUP_TIMEOUT_ATTR_NAME: params.get('antenna_setup_timeout', 0)
        }
        # http://10.56.24.11/cw17?da=1&dh=1&dn=1&di=1&ik=0.0.0.0&dl=33&dm=22&db=0&dc=1&dd=0&ta=Apply
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cw17?{payload}&ta=Apply'
        req = self.get_request(url)
        if req and req.text.find('ERROR!') == -1:
            return True
        return False

    def set_modulator_on_off(self, tx_on: bool = True, tx_level=None):
        """
        Set active profile modulator on/off

        :param bool tx_on: set modulator of the active profile ON/OFF. Default is True
        :param float tx_level: set modulator tx_level. Default is 20.0
        :raises UhpResponseException: if cannot get active profile number or active profile mode is None
        :returns bool: True if modulator is set, otherwise False
        """
        active_profile = self.get_current_profile_number()
        if active_profile is None:
            raise UhpResponseException('Cannot get active profile number')
        if self.get_basic_form(profile_number=active_profile).get('mode') == NONE:
            raise UhpResponseException('Active profile mode is None. Set modulator ON/OFF will have no effect')
        return self.set_profile_modulator(profile_number=active_profile, params={'tx_on': tx_on, 'tx_level': tx_level})

    # TODO: Probably move to a separate file
    def get_policy_rule(self, policy=1, polrule=0):
        rule = {}
        req = self.get_request(f'http://{self._router_address}/cr5?da={policy}&db={polrule}&dt=0&dF={dF}')
        if not req:
            return rule
        soup = BeautifulSoup(req.content, 'html.parser')
        # Checking radio buttons
        tags = soup.find_all('input')
        # print(tags)
        for tag in tags:
            if tag.get('name') == POLICY_RADIO_BUTTON_ATTR_NAME \
                    and tag.get('type') == 'radio' and tag.get('checked') is not None:
                current_rule = policy_mapping.get(tag.get('value'))
                if current_rule is None:
                    return rule
                elif current_rule in CheckTypesStr():
                    rule['type'] = RuleTypesStr.CHECK
                    rule['check_type'] = current_rule
                    if tag.get('value') == POLICY_PRIORITY_802_1Q_VALUE:
                        vtag = soup.find(lambda tag2: tag2.get('name') == POLICY_PRIORITY_802_1Q_ATTR_NAME)
                        if vtag is not None:
                            rule['prio_802'] = vtag.get('value')
                    elif tag.get('value') == POLICY_VLAN_VALUE:
                        vtag1 = soup.find(lambda tag2: tag2.get('name') == POLICY_VLAN_MIN_ATTR_NAME)
                        if vtag1 is not None:
                            rule['vlan_min'] = vtag1.get('value')
                        vtag2 = soup.find(lambda tag2: tag2.get('name') == POLICY_VLAN_MAX_ATTR_NAME)
                        if vtag2 is not None:
                            rule['vlan_max'] = vtag2.get('value')
                    elif tag.get('value') == POLICY_TOS_VALUE:
                        vtag1 = soup.find(lambda tag2: tag2.get('name') == POLICY_TOS_MIN_ATTR_NAME)
                        if vtag1 is not None:
                            rule['tos_min'] = vtag1.get('value')
                        vtag2 = soup.find(lambda tag2: tag2.get('name') == POLICY_TOS_MAX_ATTR_NAME)
                        if vtag2 is not None:
                            rule['tos_max'] = vtag2.get('value')
                    elif tag.get('value') == POLICY_IP_PRECEDENCE_VALUE:
                        vtag1 = soup.find(lambda tag2: tag2.get('name') == POLICY_IP_PRECEDENCE_MIN_ATTR_NAME)
                        if vtag1 is not None:
                            rule['ip_precedence_min'] = vtag1.get('value')
                        vtag2 = soup.find(lambda tag2: tag2.get('name') == POLICY_IP_PRECEDENCE_MAX_ATTR_NAME)
                        if vtag2 is not None:
                            rule['ip_precedence_max'] = vtag2.get('value')
                    elif tag.get('value') == POLICY_DSCP_VALUE:
                        vtag1 = soup.find(lambda tag2: tag2.get('name') == POLICY_DSCP_MIN_ATTR_NAME)
                        if vtag1 is not None:
                            rule['dscp_min'] = vtag1.get('value')
                        vtag2 = soup.find(lambda tag2: tag2.get('name') == POLICY_DSCP_MAX_ATTR_NAME)
                        if vtag2 is not None:
                            rule['dscp_max'] = vtag2.get('value')
                    elif tag.get('value') == POLICY_ICMP_TYPE_VALUE:
                        vtag = soup.find(lambda tag2: tag2.get('name') == POLICY_ICMP_TYPE_ATTR_NAME)
                        if vtag is not None:
                            rule['icmp_type'] = vtag.get('value')
                    elif tag.get('value') == POLICY_PROTOCOL_VALUE:
                        vtag = soup.find(lambda tag2: tag2.get('name') == POLICY_PROTOCOL_ATTR_NAME)
                        if vtag is not None:
                            rule['protocol'] = vtag.get('value')
                    elif tag.get('value') == POLICY_SRC_NET_VALUE:
                        vtag1 = soup.find(lambda tag2: tag2.get('name') == POLICY_SRC_NET_IP_ATTR_NAME)
                        if vtag1 is not None:
                            rule['net_ip'] = vtag1.get('value')
                            vtag2 = soup.find(lambda tag2: tag2.get('name') == POLICY_SRC_NET_MASK_ATTR_NAME)
                            if vtag2 is not None:
                                # Converting to prefix
                                try:
                                    n = ipaddress.IPv4Network(f'0.0.0.0/{vtag2.get("value")}')
                                    rule['net_mask'] = f'/{n.prefixlen}'
                                except Exception:
                                    pass
                    elif tag.get('value') == POLICY_DST_NET_VALUE:
                        vtag1 = soup.find(lambda tag2: tag2.get('name') == POLICY_DST_NET_IP_ATTR_NAME)
                        if vtag1 is not None:
                            rule['net_ip'] = vtag1.get('value')
                            vtag2 = soup.find(lambda tag2: tag2.get('name') == POLICY_DST_NET_MASK_ATTR_NAME)
                            if vtag2 is not None:
                                # Converting to prefix
                                try:
                                    n = ipaddress.IPv4Network(f'0.0.0.0/{vtag2.get("value")}')
                                    rule['net_mask'] = f'/{n.prefixlen}'
                                except Exception as exc:
                                    print(exc)
                                    pass
                    elif tag.get('value') == POLICY_SRC_TCP_PORT_VALUE:
                        vtag1 = soup.find(lambda tag2: tag2.get('name') == POLICY_SRC_TCP_PORT_MIN_ATTR_NAME)
                        if vtag1 is not None:
                            rule['port_min'] = vtag1.get('value')
                        vtag2 = soup.find(lambda tag2: tag2.get('name') == POLICY_SRC_TCP_PORT_MAX_ATTR_NAME)
                        if vtag2 is not None:
                            rule['port_max'] = vtag2.get('value')
                    elif tag.get('value') == POLICY_DST_TCP_PORT_VALUE:
                        vtag1 = soup.find(lambda tag2: tag2.get('name') == POLICY_DST_TCP_PORT_MIN_ATTR_NAME)
                        if vtag1 is not None:
                            rule['port_min'] = vtag1.get('value')
                        vtag2 = soup.find(lambda tag2: tag2.get('name') == POLICY_DST_TCP_PORT_MAX_ATTR_NAME)
                        if vtag2 is not None:
                            rule['port_max'] = vtag2.get('value')
                    elif tag.get('value') == POLICY_SRC_UDP_PORT_VALUE:
                        vtag1 = soup.find(lambda tag2: tag2.get('name') == POLICY_SRC_UDP_PORT_MIN_ATTR_NAME)
                        if vtag1 is not None:
                            rule['port_min'] = vtag1.get('value')
                        vtag2 = soup.find(lambda tag2: tag2.get('name') == POLICY_SRC_UDP_PORT_MAX_ATTR_NAME)
                        if vtag2 is not None:
                            rule['port_max'] = vtag2.get('value')
                    elif tag.get('value') == POLICY_DST_UDP_PORT_VALUE:
                        vtag1 = soup.find(lambda tag2: tag2.get('name') == POLICY_DST_UDP_PORT_MIN_ATTR_NAME)
                        if vtag1 is not None:
                            rule['port_min'] = vtag1.get('value')
                        vtag2 = soup.find(lambda tag2: tag2.get('name') == POLICY_DST_UDP_PORT_MAX_ATTR_NAME)
                        if vtag2 is not None:
                            rule['port_max'] = vtag2.get('value')

                else:
                    rule['type'] = RuleTypesStr.ACTION
                    rule['action_type'] = current_rule
                    if tag.get('value') == POLICY_SET_TOS_VALUE:
                        vtag = soup.find(lambda tag2: tag2.get('name') == POLICY_SET_TOS_ATTR_NAME)
                        if vtag is not None:
                            rule['set_tos'] = vtag.get('value')
                    elif tag.get('value') == POLICY_GOTO_POLICY_VALUE:
                        vtag = soup.find(lambda tag2: tag2.get('name') == POLICY_GOTO_POLICY_ATTR_NAME)
                        if vtag is not None:
                            rule['policy'] = vtag.get('value')
                    elif tag.get('value') == POLICY_SET_DSCP_VALUE:
                        vtag = soup.find(lambda tag2: tag2.get('name') == POLICY_SET_DSCP_ATTR_NAME)
                        if vtag is not None:
                            rule['set_dscp'] = vtag.get('value')
                    elif tag.get('value') == POLICY_CALL_POLICY_VALUE:
                        vtag = soup.find(lambda tag2: tag2.get('name') == POLICY_CALL_POLICY_ATTR_NAME)
                        if vtag is not None:
                            rule['policy'] = vtag.get('value')
                    elif tag.get('value') == POLICY_ENCRYPT_VALUE:
                        vtag = soup.find(lambda tag2: tag2.get('name') == POLICY_ENCRYPT_ATTR_NAME)
                        if vtag is not None:
                            rule['key'] = vtag.get('value')
                break
        selectors = (ActionTypesStr.SET_QUEUE, ActionTypesStr.SET_TS_CH, ActionTypesStr.SET_ACM_CHANNEL)
        if rule.get('type') == RuleTypesStr.ACTION and rule.get('action_type') in selectors:
            tags = soup.find_all('select')
            for tag in tags:
                if rule.get('action_type') == ActionTypesStr.SET_QUEUE \
                        and tag['name'] == POLICY_SET_QUEUE_SELECTOR_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            queue = option.contents[0]
                            if queue in queues_mapping.keys():
                                rule['queue'] = queues_mapping[queue]
                            else:
                                rule['queue'] = option.contents[0]
                elif rule.get('action_type') == ActionTypesStr.SET_TS_CH \
                        and tag['name'] == POLICY_SET_TS_CHANNEL_SELECTOR_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            # rule['shaper'] = option.contents[0]
                            rule['shaper'] = option.get('value')
                elif rule.get('action_type') == ActionTypesStr.SET_ACM_CHANNEL \
                        and tag['name'] == POLICY_SET_ACM_CHANNEL_SELECTOR_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            rule['acm_channel'] = option.contents[0]
        # Checking checkboxes
        tags = soup.find_all('input')
        for tag in tags:
            if tag.get('type') == 'checkbox' and rule.get('type') == RuleTypesStr.CHECK:
                if tag.get('name') == POLICY_NOT_ATTR_NAME:
                    if tag.get('checked') is not None:
                        rule['not'] = CheckboxStr.ON
                    else:
                        rule['not'] = CheckboxStr.OFF
                elif tag.get('name') == POLICY_GOTO_ACTIONS_ATTR_NAME:
                    if tag.get('checked') is not None:
                        rule['goto_actions'] = CheckboxStr.ON
                    else:
                        rule['goto_actions'] = CheckboxStr.OFF
            elif tag.get('type') == 'checkbox' and rule.get('type') == RuleTypesStr.ACTION \
                    and tag.get('name') == POLICY_TERMINATE_AFTER_ACTION:
                if tag.get('checked') is not None:
                    rule['terminate'] = CheckboxStr.ON
                else:
                    rule['terminate'] = CheckboxStr.OFF
        return rule

    def set_profile_timing(self, profile_number=1, params=None):
        """
        Alias for set_timing_values. Set Profile Timing parameters.
        The parameters' keys and their default values are the following:
            sat_lon_deg=0, sat_lon_min=0, tts_mode=1, tts_value=0
        The satellite longitude degrees are passed in -180 +180 format

        :param int profile_number: profile number to write config to
        :param dict params: a dictionary of parameters to apply, by default tts_mode is Value, the rest are all 0
        :returns bool: True if request to UHP is successful, otherwise False
        """
        return self.set_timing_values(profile_number=profile_number, params=params)

    def set_timing_values(self, profile_number=1, params=None):
        """
        Set Profile Timing parameters. The parameters' keys and their default values are the following:
            sat_lon_deg=0, sat_lon_min=0, tts_mode=1, tts_value=0
        The satellite longitude degrees are passed in -180 +180 format

        :param int profile_number: profile number to write config to
        :param dict params: a dictionary of parameters to apply, by default tts_mode is Value, the rest are all 0
        :returns bool: True if request to UHP is successful, otherwise False
        """
        if params is None:
            params = {}
        if profile_number not in range(1, 9):
            raise InvalidOptionsException(f'Invalid profile number: you passed {profile_number} {type(profile_number)}')
        mode = params.get('tts_mode')
        if mode is not None:
            if mode.lower() == 'location':
                mode = 0
            elif mode.lower() == 'value':
                mode = 1
            elif mode.lower() == 'measure':
                mode = 2
            else:
                raise InvalidOptionsException(f'Unknown mode {mode} passed to the method')
        else:
            mode = 1
        sat_lon_deg = params.get('sat_lon_deg')
        if sat_lon_deg is None:
            sat_lon_deg = 0
            east_west = 0
        elif not isinstance(sat_lon_deg, int):
            raise InvalidOptionsException(f'sat_lon_deg must be an integer, you passed {type(sat_lon_deg)}')
        elif sat_lon_deg not in range(-181, 181):
            raise InvalidOptionsException(f'sat_lon_deg must be in range from -180 to +180 including')
        elif sat_lon_deg < 0:
            sat_lon_deg = abs(sat_lon_deg)
            east_west = 1
        else:
            east_west = 0
        sat_lon_min = params.get('sat_lon_min')
        if sat_lon_min is None:
            sat_lon_min = 0
        elif not isinstance(sat_lon_min, int):
            raise InvalidOptionsException(f'sat_lon_min must be an integer, you passed {type(sat_lon_min)}')
        elif sat_lon_min not in range(0, 60):
            raise InvalidOptionsException(f'sat_lon_min must be in range from 0 to 59 including')

        payload = {
            TIMING_MODE_ATTR_NAME: mode,
            TIMING_VALUE_ATTR_NAME: params.get('tts_value', 0),
            SAT_LON_DEG_ATTR_NAME: sat_lon_deg,
            SAT_LON_MIN_ATTR_NAME: sat_lon_min,
            SAT_EAST_WEST_ATTR_NAME: east_west
        }
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cI3?da={profile_number}&{payload}&ta=Apply'
        req = self.get_request(url)
        if req and req.text.find('ERROR!') == -1:
            return True
        return False

    def set_profile_tdm_acm(self, profile_number=1, params=None):
        """
        Set profile TDM ACM values. The parameters' keys and their default values are the following:
            acm_enable=0, max_modcod=6, acm_thr=1.0, acm_mc2=6, acm_mc3=6, acm_mc4=6, acm_mc5=6,
            acm_mc6=6, acm_mc7=6, acm_mc8=6

        :param int profile_number: profile number to write config to
        :param dict params: a dictionary of parameters to apply, if no params are provided, acm is off
        :returns bool: True if request to UHP is successful, otherwise False
        """
        if profile_number not in range(1, 9):
            raise InvalidOptionsException(f'Invalid profile number: you passed {profile_number} {type(profile_number)}')
        if params is None:
            params = {}
        if params.get('acm_enable') is not None \
                and params.get('acm_enable') not in (False, 0, '0', 'OFF', 'off', 'Off'):
            acm_enable = 1
        else:
            acm_enable = 0
        if params.get('acm_thr') is not None:
            try:
                acm_thr = float(params.get('acm_thr'))
                acm_thr_int = str(acm_thr).split('.')[0]
                acm_thr_float = str(acm_thr).split('.')[1]
            except ValueError:
                acm_thr_int = 1
                acm_thr_float = 0
        else:
            acm_thr_int = 1
            acm_thr_float = 0

        payload = {
            TDM_ACM_ENABLE_ATTR_NAME: acm_enable,
            TDM_ACM_MAX_MODCOD_ATTR_NAME: params.get('max_modcod', 0),
            TDM_ACM_MODCOD2_ATTR_NAME: params.get('acm_mc2', 6),
            TDM_ACM_MODCOD3_ATTR_NAME: params.get('acm_mc3', 6),
            TDM_ACM_MODCOD4_ATTR_NAME: params.get('acm_mc4', 6),
            TDM_ACM_MODCOD5_ATTR_NAME: params.get('acm_mc5', 6),
            TDM_ACM_MODCOD6_ATTR_NAME: params.get('acm_mc6', 6),
            TDM_ACM_MODCOD7_ATTR_NAME: params.get('acm_mc7', 6),
            TDM_ACM_MODCOD8_ATTR_NAME: params.get('acm_mc8', 6),
            TDM_ACM_CN_THRESHOLD_INT_ATTR_NAME: acm_thr_int,
            TDM_ACM_CN_THRESHOLD_FLOAT_ATTR_NAME: acm_thr_float,
        }
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cA3?da={profile_number}&{payload}&ta=Apply'
        req = self.get_request(url)
        if req and req.text.find('ERROR!') == -1:
            return True
        return False

    def set_profile_roaming(self, profile_number=1, params=None):
        """
        Set profile Roaming values. The parameters' keys and their default values are the following:
            roaming_enable=0, roaming_timeout=1

        :param int profile_number: profile number to write config to
        :param dict params: a dictionary of parameters to apply, if no params are provided, roaming is off
        :returns bool: True if request to UHP is successful, otherwise False
        """
        if profile_number not in range(1, 9):
            raise InvalidOptionsException(f'Invalid profile number: you passed {profile_number} {type(profile_number)}')
        if params is None:
            params = {}
        if params.get('roaming_enable') is not None \
                and params.get('roaming_enable') not in (False, 0, '0', 'OFF', 'off', 'Off'):
            roaming_enable = 1
        else:
            roaming_enable = 0
        payload = {
            ROAMING_ENABLE_ATTR_NAME: roaming_enable,
            ROAMING_TIMEOUT_ATTR_NAME: params.get('roaming_timeout', 1),
        }
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cO3?da={profile_number}&{payload}&ta=Apply'
        req = self.get_request(url)
        if req and req.text.find('ERROR!') == -1:
            return True
        return False

    def dama_station(self, profile_number=1, params=None, run_profile=True):
        """
        Set and run DAMA station profile. The available parameters' keys and their default values are the following:
            valid=1, autorun=1, timeout=40, title='script',
            input_gain=0, rx1_input=0, rx1_frq=960000, rx1_sr=1600,
            rx2_enable=0, rx2_input=0, rx2_frq=970000, rx2_sr=1000, rx_voltage=0,
            tlc_enable=0, tlc_max_lvl=1,
            acm_enable=0, max_modcod=6, acm_thr=1.0

        :param int profile_number: profile number to write config to
        :param dict params: a dictionary of parameters to apply
        :param bool run_profile: if True profile is run, otherwise not
        :returns bool: True if all requests to UHP are successful, otherwise False
        """
        if profile_number not in range(1, 9):
            raise InvalidOptionsException(f'Invalid profile number: you passed {profile_number} {type(profile_number)}')

        if params is not None and params.get('mode') != DAMA_STATION:
            params['mode'] = DAMA_STATION
        elif params is None:
            params = {'mode': DAMA_STATION}
        if not self.set_profile_basic(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tdm_rx(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tlc(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tdm_acm(profile_number=profile_number, params=params):
            return False

        if run_profile:
            if not self.run_profile(profile_number=profile_number):
                return False
        return True

    def star_station(self, profile_number=1, params=None, run_profile=True):
        """
        Set and run DAMA station profile. The available parameters' keys and their default values are the following:
            valid=1, autorun=1, timeout=40, title='script',
            input_gain=0, rx1_input=0, rx1_frq=960000, rx1_sr=1600,
            rx2_enable=0, rx2_input=0, rx2_frq=970000, rx2_sr=1000, rx_voltage=0,
            tx_on=1, tx_level=20.0,
            tts_mode=1, tts_value=0
            tlc_enable=0, tlc_max_lvl=1,
            roaming_enable=0, roaming_timeout=1

        :param int profile_number: Profile number to write config to
        :param dict params: a dictionary of parameters to apply
        :param bool run_profile: if True profile is run, otherwise not
        :returns bool: True if all requests to UHP are successful, otherwise False
        """
        if profile_number not in range(1, 9):
            raise InvalidOptionsException(f'Invalid profile number: you passed {profile_number} {type(profile_number)}')

        if params is not None and params.get('mode') != STAR_STATION:
            params['mode'] = STAR_STATION
        elif params is None:
            params = {'mode': STAR_STATION}
        if not self.set_profile_basic(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tdm_rx(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_modulator(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_timing(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tlc(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_roaming(profile_number=profile_number, params=params):
            return False

        if run_profile:
            if not self.run_profile(profile_number=profile_number):
                return False
        return True

    def hubless_station(self, profile_number=1, params=None, run_profile=True):
        """
        Set and run Hubless station profile. The available parameters' keys and their default values are the following:
            valid=1, autorun=1, timeout=40, title='script',
            input_gain=0, rx1_enable=1, rx1_input=0, rx1_frq=960000, rx1_sr=1600,
            rx2_enable=0, rx2_input=0, rx2_frq=970000, rx2_sr=1000, rx_voltage=0,
            tx_on=1, tx_level=20.0,
            tts_mode=1, tts_value=0
            tlc_enable=0, tlc_max_lvl=1,
            tdma_sr=1000, tdma_mc=9, 'tdma_roll'=0, enh_tables=0, mf1_rx=1000000, mf1_tx=1000000,
            mf2_en=0, mf2_rx=962000, mf2_tx=962000,
            mf3_en=0, mf3_rx=964000, mf3_tx=964000,
            mf4_en=0, mf4_rx=966000, mf4_tx=966000,
            stn_number=10, frame_length=64, slot_length=8

        :param int profile_number: Profile number to write config to
        :param dict params: a dictionary of parameters to apply
        :param bool run_profile: if True profile is run, otherwise not
        :returns bool: True if all requests to UHP are successful, otherwise False
        """
        if profile_number not in range(1, 9):
            raise InvalidOptionsException(f'Invalid profile number: you passed {profile_number} {type(profile_number)}')

        if params is not None and params.get('mode') != HUBLESS_STATION:
            params['mode'] = HUBLESS_STATION
        elif params is None:
            params = {'mode': HUBLESS_STATION}
        if not self.set_profile_basic(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tdm_rx(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_modulator(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_timing(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tlc(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tdma_rf(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tdma_prot(profile_number=profile_number, params=params):
            return False

        if run_profile:
            if not self.run_profile(profile_number=profile_number):
                return False
        return True

    def mesh_station(self, profile_number=1, params=None, run_profile=True):
        """
        Set and run Mesh station profile. The available parameters' keys and their default values are the following:
            valid=1, autorun=1, timeout=40, title='script',
            input_gain=0, rx1_input=0, rx1_frq=960000, rx1_sr=1600,
            rx2_enable=0, rx2_input=0, rx2_frq=970000, rx2_sr=1000, rx_voltage=0,
            tx_on=1, tx_level=20.0,
            tts_mode=1, tts_value=0
            tlc_enable=0, tlc_max_lvl=1,
            no_stn_check=1, rec_all_traffic=0,
            roaming_enable=0, roaming_timeout=1

        :param int profile_number: profile number to write config to
        :param dict params: a dictionary of parameters to apply
        :param bool run_profile: if True profile is run, otherwise not
        :returns bool: True if all requests to UHP are successful, otherwise False
        """
        if profile_number not in range(1, 9):
            raise InvalidOptionsException(f'Invalid profile number: you passed {profile_number} {type(profile_number)}')

        if params is not None and params.get('mode') != MESH_STATION:
            params['mode'] = MESH_STATION
        elif params is None:
            params = {'mode': MESH_STATION}
        if not self.set_profile_basic(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tdm_rx(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_modulator(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_timing(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tlc(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tdma_rf(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tdma_prot(profile_number=profile_number, params=params):
            return False

        if run_profile:
            if not self.run_profile(profile_number=profile_number):
                return False
        return True

    def traffic_generator(self, params=None):
        """
        Turn OFF/ON UHP Traffic Generator. The available parameters' keys and their default values are the following:
            enabled=0, mode=0, ipv4='0.0.0.0', ipv6='::', vlan=0, pps_from=1, pps_to=1, pkt_len_from=40, pkt_len_to=40

        Without params Traffic Generator is OFF. For IPv4 set mode to 0, for IPv6 set mode to 1.
        Sample usage:
            traffic_generator() turns OFF Traffic Generator
            traffic_generator({'enabled': 1, 'ipv4': '127.0.0.1', 'vlan': 206, 'pps_from': 20, 'pps_to': 20})
                turns ON Traffic Generator in VLAN 206 to IPv4 address 127.0.0.1 pps 20

        :param dict params: a dictionary containing key-value pairs to set up Traffic Generator
        :returns bool: True if request to UHP is successful, otherwise False
        """
        if params is None:
            params = {}
        payload = {
            TR_GEN_ENABLED_ATTR_NAME: params.get('enabled', 0),
            TR_GEN_MODE_ATTR_NAME: params.get('mode', 0),
            TR_GEN_IPV4_ATTR_NAME: params.get('ipv4', '0.0.0.0'),
            TR_GEN_IPV6_ATTR_NAME: params.get('ipv6', '::'),
            TR_GEN_VLAN_ATTR_NAME: params.get('vlan', 0),
            TR_GEN_PPS_FROM_ATTR_NAME: params.get('pps_from', 1),
            TR_GEN_PPS_TO_ATTR_NAME: params.get('pps_to', 1),
            TR_GEN_PKT_LEN_FROM_ATTR_NAME: params.get('pkt_len_from', 40),
            TR_GEN_PKT_LEN_TO_ATTR_NAME: params.get('pkt_len_to', 40),
        }
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cw43?{payload}&ta=Apply'
        req = self.get_request(url)
        if req and req.text.find('ERROR!') == -1:
            return True
        return False

    def scpc_modem(self, profile_number: int = 1, params: dict = None, run_profile: bool = True):
        """
        Set and run SCPC modem profile. The available parameters' keys and their default values are the following:
            valid=1, autorun=1, timeout=40, title='script',
            check_rx=0, input_gain=0, rx1_input=0, rx1_frq=960000, rx1_sr=1600,
            rx2_enable=0, rx2_input=0, rx2_frq=970000, rx2_sr=1000, rx_voltage=0,
            tx_frq=950000, tx_sr=1000, tx_modcod=4, tx_pilots=0, tx_rolloff=0,
            tx_on=1, tx_level=20.0,
            tlc_enable=0, tlc_max_lvl=1, tlc_cn_hub=8.0,
            acm_enable=0, max_modcod=6, acm_thr=1.0,

        :param int profile_number: Profile number to write config to
        :param dict params: a dictionary of parameters to apply
        :param bool run_profile: if True profile is run, otherwise not
        :returns bool: True if all requests to UHP are successful, otherwise False
        """
        if profile_number not in range(1, 9):
            raise InvalidOptionsException(f'Invalid profile number: you passed {profile_number} {type(profile_number)}')

        if params is not None and params.get('mode') != SCPC_MODEM:
            params['mode'] = SCPC_MODEM
        elif params is None:
            params = {'mode': SCPC_MODEM}
        if not self.set_profile_basic(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tdm_rx(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tdm_tx(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_modulator(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tlc(profile_number=profile_number, params=params):
            return False
        if not self.set_profile_tdm_acm(profile_number=profile_number, params=params):
            return False

        if run_profile:
            if not self.run_profile(profile_number=profile_number):
                return False
        return True

    def exit_telnet(self):
        """Send exit telnet command to UHP"""
        req = self.get_request(f'http://{self._router_address}/cw42?db=0&dc=0&aa=exit&ta=Apply')
        if not req:
            return False
        time.sleep(3)
        return True

    def network_script(self, local=True, broadcast=False, sn=None, command=None):
        """
        Send network script either locally or to a specific s/n or broadcast

        :param bool local: if True command will be send locally
        :param bool broadcast: if True command will be broadcast (local still has higher priority)
        :param int sn: UHP serial number to send command to
        :param str command: command to send to
        :returns bool: True if command sent, False if there is an error upon sending command
        """
        if local:
            _type = 0
        elif broadcast:
            _type = 2
        else:
            _type = 1
        if sn is None or not isinstance(sn, int):
            sn = 0
        if command is None or not isinstance(command, str):
            command = ''
        payload = {
            NET_SCRIPT_TYPE_ATTR_NAME: _type,
            NET_SCRIPT_SN_VALUE_ATTR_NAME: sn,
            NET_SCRIPT_COMMAND_ATTR_NAME: command,
        }
        payload = urllib.parse.urlencode(payload)
        url = f'http://{self._router_address}/cw42?{payload}&ta=Apply'
        req = self.get_request(url)
        if req and req.text.find('ERROR!') == -1 and req.text.find('Error=') == -1:
            return True
        return False

    def set_redundancy(self, params=None):
        """
        Set UHP redundancy using passed dictionary. The parameters' keys are the following:
            red_enable, red_remote_ip, red_local_ip, red_fault_timeout, red_link_timeout, red_ser_monitor

        :param dict params: a dictionary of parameters to apply for redundancy
        :returns bool: True if redundancy parameters are applied, otherwise False
        """
        current_params = self.get_stlc_nms_red_form()
        if current_params is None:
            return False
        payload = {}
        for key, value in scpc_tlc_red_mapping.items():
            if value in params.keys():
                if isinstance(params.get(value), bool):
                    payload[key] = int(params.get(value))
                else:
                    payload[key] = params.get(value)
            else:
                payload[key] = current_params[value]
        payload = urllib.parse.urlencode(payload)
        res = self.get_request(f'http://{self._router_address}/cw14?{payload}&ta=Apply')
        if not res or self._is_error():
            return False
        return True

    def set_site_setup(self, params=None):
        """Set parameters for Site Setup. The parameters are the following:
            site_name='', lat_deg=0, lat_min=0, lat_south=0, lon_deg=0, lon_min=0, lon_west=0,
            rx1_lo=0, rx_dc_power=0, rx_10m=0, rx1_spi=0, rx1_offset=0,
            rx2_lo=0, rx2_spi=0, rx2_offset=0, tx_lo=0, tx_dc_power=0, tx_10m=0, tx_spi=0, tx_offset=0,
            dvb_search=800, net_id=0, rf_id=0, tdma_search=4, far_end_cn=0

        :param dict params: a dictionary of parameters to apply
        """
        if params is None:
            params = {}
        payload = {}
        for key, value in site_setup_mapping.items():
            if params.get(value) is None and value == 'site_name':
                payload[key] = ''
            elif params.get(value) is None and value == 'dvb_search':
                payload[key] = 800
            elif params.get(value) is None and value == 'tdma_search':
                payload[key] = TdmaSearchModes.BW40
            elif params.get(value) is None and value == 'lat_south':
                payload[key] = LatitudeModes.NORTH
            elif params.get(value) is None and value == 'lon_west':
                payload[key] = LongitudeModes.EAST
            else:
                payload[key] = params.get(value, 0)
        payload = urllib.parse.urlencode(payload)
        res = self.get_request(f'http://{self._router_address}/cw2?{payload}&tf=Apply')
        if not res or self._is_error():
            return False
        return True


if __name__ == '__main__':
    uhp = UhpRequestsDriver(router_address='10.56.24.12')
    print(uhp.get_snmp_form())