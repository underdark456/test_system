import re
from typing import Union, Dict

from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from src.drivers.uhp.constants import *
from src.enum_types_constants import RollofModesStr
from src.exceptions import UhpResponseException, InvalidOptionsException
from utilities.utils import is_ipv4, is_ipv6


class UhpGetter(ABC):
    _router_address = None
    serial_number = None
    uhp_software_version = None

    @abstractmethod
    def get_request(self, address, timeout=None):
        pass

    def get_router_address(self):
        """
        :returns str: the UHP IP address passed into the class constructor
        """
        return self._router_address

    def get_serial_number(self):
        """
        Get serial number of UHP. The value is taken from the Support Info page.

        :returns str: UHP serial number
        """
        self.serial_number = self.get_support_info_value(regex=re.compile(r'sn:\s[0-9]+'))
        return self.serial_number

    def get_software_version(self, timeout=None):
        """
        Get the software version of the currently instantiated UHP. On success the software version
        is placed into an instance variable self.uhp_software_version

        :returns:
            - self.uhp_software_version (:py:class:'str') - the software version of the UHP
            - None - if the software version cannot be determined
        :raises UhpResponseException: if the router does not respond
        """
        req = self.get_request(f'http://{self._router_address}/ss30', timeout=timeout)
        if not req:
            raise UhpResponseException(f'Cannot connect to UHP {self._router_address} to get software version')
        ver_index = req.text.find('Ver:')
        sn_index = req.text.find('SN:')
        if ver_index == -1 or sn_index == -1:
            return None
        self.uhp_software_version = req.text[ver_index + 5:sn_index].lstrip().rstrip()
        return self.uhp_software_version

    def get_hw(self):
        """
        Get HW version of UHP. The value is taken from the Support Info page.

        :returns str: UHP HW version
        """
        hw = self.get_support_info_value(regex=re.compile(r'h/w\suhp-[a-z0-9]+\)'))
        return hw[:-1].replace('-', '')

    def get_platform_version(self):
        """
        Get the platform version of the currently instantiated UHP.

        :returns:
            - uhp_platform_version (:py:class:'str') - the platform version of UHP
            - None - if the software version cannot be determined
        :raises UhpResponseException: if the router does not respond
        """
        req = self.get_request(f'http://{self._router_address}/')
        if not req:
            raise UhpResponseException(f'Cannot connect to UHP {self._router_address} to get platform version')
        platform = re.search(r'platform: uhp-[0-9]+[a-z]*', req.text.lower())
        if platform is not None:
            return platform.group().split()[1]
        return None

    def get_state(self):
        """
        Get current UHP state

        :returns str: lowercased UHP state
        """
        res = self.get_request(f'http://{self._router_address}/ss30')
        if not res:
            return False
        regex = re.compile(r'state:\s+[a-z]+[ ]*[a-z]*[ ]*[a-z]*')
        state = regex.search(res.text.lower())
        if res is not None:
            return state.group()[len('state:'):].strip()

    def get_nms_controlled_mode(self):
        """
        Get the state of UHP NMS controlled mode.
        If there is a message 'NMS controlled mode!' in the site setup page,
        the modem is under the control

        :returns bool: True if UHP is under NMS control, otherwise False.
        """
        req = self.get_request(f'http://{self._router_address}/cc2')
        if not req:
            return False
        if req.text.find('NMS controlled mode!') == -1:
            return False
        return True

    def get_current_profile_number(self):
        """
        Get the current active UHP profile number

        :returns:
            - profile_number (:py:class:'str') - current active profile number
            - None - if the current profile number cannot be established
        """
        req = self.get_request(f'http://{self._router_address}/h')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('a')
            profile_link_re = re.compile(r'cb\d\?da=\d')
            for tag in tags:
                if profile_link_re.search(tag['href']) is not None:
                    profile_number = tag['href'][-1:]
                    return profile_number
        return None

    def get_active_profile_name(self):
        """
        Get the current active UHP profile name

        :returns:
            - active profile name(:py:class:'str') - current active profile name
            - None - if the current profile name cannot be established
        """
        act_pro_num = self.get_support_info_value(regex=re.compile(r'profile:\s[0-9]'))
        if act_pro_num is None:
            return None
        req = self.get_request(f'http://{self._router_address}/cc3')
        if not req:
            return None
        soup = BeautifulSoup(req.content, 'html.parser')
        tags = soup.find_all('a')
        for tag in tags:
            if tag.get('href') is not None and tag['href'] == f'cb3?da={act_pro_num}':
                return tag.text
        else:
            return None

    def get_support_info_value(self, regex=None, data=None) -> Union[str, None]:
        """
        Get a value from the UHP support info page. If value is found it is lowercased.

        Example:
        uhp.get_support_info( self, regex=re.compile(r'timezone:\s[0-9]+') ) returns the current set timezone.

        :param re.Pattern regex: a regular expression pattern to find
        :param Optional requests.models.Response data: requests response object
        :returns:
            - value (:py:class:'str')
            - None - if value cannot be find
        """
        if regex is None:
            return None
        if data is None:
            req = self.get_request(f'http://{self._router_address}/ss30')
            if not req:
                return None
            value = regex.search(req.text.lower())
        else:
            req = data
            value = regex.search(req.lower())
        if value is not None:
            return value.group().split()[-1]
        return None

    def get_site_setup(self):
        """
        Alias for get_teleport_values

        Get the teleport data from the corresponding UHP pages as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'name', 'lat_deg', 'lat_min', 'lon_deg', 'lon_min', 'rx1_lo', 'rx_dc_power',
        'rx_10m', 'rx1_spi', 'rx1_offset', 'rx2_lo', 'rx2_spi', 'rx2_offset', 'tx_lo',
        'tx_dc_power', 'tx_10m', 'tx_spi', 'tx_offset', 'dvb_search', 'net_id',
        'rf_id', 'lat_south', 'lon_west', 'tdma_search', 'time_zone', 'sat_lon_deg',
        and 'sat_lon_min'

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        return self.get_teleport_values()

    def get_teleport_values(self):
        # TODO: The method is too long. Split it.
        """
        Get the teleport data from the corresponding UHP pages as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'name', 'lat_deg', 'lat_min', 'lon_deg', 'lon_min', 'rx1_lo', 'rx_dc_power',
        'rx_10m', 'rx1_spi', 'rx1_offset', 'rx2_lo', 'rx2_spi', 'rx2_offset', 'tx_lo',
        'tx_dc_power', 'tx_10m', 'tx_spi', 'tx_offset', 'dvb_search', 'net_id',
        'rf_id', 'lat_south', 'lon_west', 'tdma_search', 'time_zone', 'sat_lon_deg',
        and 'sat_lon_min'

        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """

        # Mapping UHP latitude names to NMS
        latitude = {
            '0': 'North',
            '1': 'South'
        }
        # Mapping UHP longitude names to NMS
        longitude = {
            '0': 'East',
            '1': 'West'
        }
        # Mapping UHP TDMA search names to NMS
        tdma_search = {
            '0': 'bw6',
            '1': 'bw12',
            '2': 'bw24',
            '3': 'bw40'
        }
        # Mapping the rest UHP elements names to NMS
        names = {
            SS_SITE_NAME_ATTR_NAME: 'name',
            SS_LAT_DEG_ATTR_NAME: 'lat_deg',
            SS_LAT_MIN_ATTR_NAME: 'lat_min',
            SS_LON_DEG_ATTR_NAME: 'lon_deg',
            SS_LON_MIN_ATTR_NAME: 'lon_min',
            SS_RX1_LO_ATTR_NAME: 'rx1_lo',
            SS_RX_DC_POWER_ATTR_NAME: 'rx_dc_power',
            SS_RX_10M_ATTR_NAME: 'rx_10m',
            SS_RX1_SPI_ATTR_NAME: 'rx1_spi',
            SS_RX1_OFFSET_ATTR_NAME: 'rx1_offset',
            SS_RX2_LO_ATTR_NAME: 'rx2_lo',
            SS_RX2_SPI_ATTR_NAME: 'rx2_spi',
            SS_RX2_OFFSET_ATTR_NAME: 'rx2_offset',
            SS_TX_LO_ATTR_NAME: 'tx_lo',
            SS_TX_DC_POWER_ATTR_NAME: 'tx_dc_power',
            SS_TX_10M_ATTR_NAME: 'tx_10m',
            SS_TX_SPI_ATTR_NAME: 'tx_spi',
            SS_TX_OFFSET_ATTR_NAME: 'tx_offset',
            SS_DVB_SEARCH_ATTR_NAME: 'dvb_search',
            SS_NET_ID_ATTR_NAME: 'net_id',
            SS_RF_ID_ATTR_NAME: 'rf_id',
            SS_LAT_SOUTH_ATTR_NAME: 'lat_south',
            # TODO: which NMS param represents far end c/n
            SS_FAR_END_CN_ATTR_NAME: 'far_end_cn',
        }
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cc2')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name = tag.get('name')
                if name is None or name in (SS_FAR_END_CN_SET_ATTR_NAME, SS_SUBMIT_ATTR_NAME,):
                    continue
                elif name in (
                        SS_RX_DC_POWER_ATTR_NAME,
                        SS_TX_DC_POWER_ATTR_NAME,
                        SS_RX1_SPI_ATTR_NAME,
                        SS_RX2_SPI_ATTR_NAME,
                        SS_TX_SPI_ATTR_NAME,
                        SS_RX_10M_ATTR_NAME,
                        SS_TX_10M_ATTR_NAME,
                ):
                    if tag.get('checked') is not None:
                        uhp_values[names[name]] = '1'
                    else:
                        uhp_values[names[name]] = '0'
                else:
                    uhp_values[names[name]] = tag['value']
            # Getting the select elements values (latitude, longitude, tdma_search)
            tags = soup.find_all('select')
            for tag in tags:
                if tag['name'] == SS_LAT_SOUTH_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            uhp_values['lat_south'] = latitude.get(option.get('value'), None)
                            break
                elif tag['name'] == SS_LON_WEST_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            uhp_values['lon_west'] = longitude.get(option.get('value'), None)
                            break
                elif tag['name'] == SS_TDMA_SEARCH_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            uhp_values['tdma_search'] = tdma_search.get(option.get('value'), None)
                            break

        # Getting the timezone value from the support info page
        time_zone = self.get_support_info_value(regex=re.compile(r'timezone:\s[0-9]+'))
        if time_zone is not None:
            uhp_values['time_zone'] = time_zone
        # TODO: if UHP is not in the UP state, the support page shows obsolete satellite data

        # Getting the sat data from the current active profile timing page.
        active_profile = self.get_current_profile_number()
        if active_profile:
            uhp_values.update(self.get_timing_values(profile_number=active_profile))
        return uhp_values

    def get_basic_form(self, profile_number=1):
        """
        Get the data from the UHP TDM/SCPC TX page as a dictionary.
        The dictionary keys are the following:
        'valid', 'autorun', 'mode', 'timeout', and 'title'.

        :param int profile_number: UHP profile number. By default NMS uses profile number 1
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cb3?da={profile_number}')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name = tag.get('name', None)
                value = tag.get('value', None)
                if name is None or value is None:
                    continue
                elif name == PROFILE_VALID_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['valid'] = '1'
                    else:
                        uhp_values['valid'] = '0'
                elif name == PROFILE_AUTORUN_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['autorun'] = '1'
                    else:
                        uhp_values['autorun'] = '0'
                elif name == PROFILE_TIMEOUT_ATTR_NAME:
                    uhp_values['timeout'] = value
                elif name == PROFILE_TITLE_ATTR_NAME:
                    uhp_values['title'] = value
            tags = soup.find_all('select')
            for tag in tags:
                if tag['name'] == PROFILE_MODE_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            uhp_values['mode'] = option.get('value', None)
                            break
        return uhp_values

    def get_tdm_rx_form(self, profile_number=1):
        """Alias for get_demodulator_form() method"""
        return self.get_demodulator_form(profile_number)

    def get_demodulator_form(self, profile_number=1):
        """
        Get the data from the UHP TDM/SCPC RX page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'rx1_input', 'rx1_frq', 'rx1_sr', 'check_rx',
        'rx2_input', 'rx2_frq', 'rx2_sr', and 'rx_voltage'.
        The dictionary values are taken from the page unmodified, except for 'rx1_input' and 'rx2_input'

        :param int profile_number: UHP profile number. By default NMS uses profile number 1
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        rx1_enable, rx2_enable = False, False
        rx1_input, rx2_input = None, None
        req = self.get_request(f'http://{self._router_address}/cr3?da={profile_number}')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                if tag['name'] == DEM_CHECK_RX_ATTR_NAME:
                    uhp_values['check_rx'] = tag.get('value', None)
                elif tag['name'] == DEM_RX1_FREQ_ATTR_NAME:
                    uhp_values['rx1_frq'] = tag.get('value', None)
                elif tag['name'] == DEM_RX2_FREQ_ATTR_NAME:
                    uhp_values['rx2_frq'] = tag.get('value', None)
                elif tag['name'] == DEM_RX1_SR_ATTR_NAME:
                    uhp_values['rx1_sr'] = tag.get('value', None)
                elif tag['name'] == DEM_RX2_SR_ATTR_NAME:
                    uhp_values['rx2_sr'] = tag.get('value', None)
                elif tag['name'] == DEM_RX_VOLTAGE_ATTR_NAME:
                    if tag.get('checked', None) is not None and tag.get('value', None) is not None:
                        if tag['value'] == '1':
                            uhp_values['rx_voltage'] = 'dc13v'
                        else:
                            uhp_values['rx_voltage'] = 'dc18v'
                elif tag['name'] == DEM_RX1_ENABLE_ATTR_NAME:
                    rx1_enable = True
                elif tag['name'] == DEM_RX2_ENABLE_ATTR_NAME:
                    rx2_enable = True
            tags = soup.find_all('select')
            for tag in tags:
                if tag['name'] == DEM_RX1_INPUT_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            rx1_input = option.contents[0].lower().replace('-', '')
                elif tag['name'] == DEM_RX2_INPUT_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            rx2_input = option.contents[0].lower().replace('-', '')
            # Combining results of enable and input
            if not rx1_enable:
                uhp_values['rx1_input'] = 'off'
            else:
                uhp_values['rx1_input'] = rx1_input

            if not rx2_enable:
                uhp_values['rx2_input'] = 'off'
            else:
                uhp_values['rx2_input'] = rx2_input
        return uhp_values

    def get_tdm_tx_form(self, profile_number=1):
        """
        Get the data from the UHP TDM/SCPC TX page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
            tx_frq, tx_sr, tx_modcod, tx_pilots, and tx_rolloff

        :param int profile_number: UHP profile number. By default NMS uses profile number 1
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/ct3?da={profile_number}')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name, value = tag.get('name'), tag.get('value')
                if name is None or value is None:
                    continue
                elif name == TDM_TX_FREQ_ATTR_NAME:
                    uhp_values['tx_frq'] = value
                elif name == TDM_TX_SR_ATTR_NAME:
                    uhp_values['tx_sr'] = value
                elif name == TDM_TX_PILOTS_ATTR_NAME:
                    uhp_values['tx_pilots'] = '0' if tag.get('checked') is None else '1'
            tags = soup.find_all('select')
            for tag in tags:
                name = tag.get('name')
                if name is None:
                    continue
                elif name == TDM_TX_MODCOD_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            uhp_values['tx_modcod'] = option.contents[0].lstrip().rstrip().lower()
                elif name == TDM_TX_ROLLOFF_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            uhp_values['tx_rolloff'] = option.get('value')
        return uhp_values

    def get_crosspol_rf(self, profile_number=1):
        """
        Get the data from the UHP CrossPol RF page as a dictionary.
        The dictionary keys are the following: `tx_frq`, `duration`.

        The dictionary values are taken from the page unmodified.

        :param int profile_number: UHP profile number. By default NMS uses profile number 1
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cx3?da={profile_number}')
        if not req:
            return uhp_values
        soup = BeautifulSoup(req.content, 'html.parser')
        tags = soup.find_all('input')
        for tag in tags:
            name = tag.get('name', None)
            if name is None:
                continue
            elif name == CROSSPOL_TX_FRQ_ATTR_NAME:
                uhp_values['tx_frq'] = tag.get('value', None)
            elif name == CROSSPOL_DURATION_ATTR_NAME:
                uhp_values['duration'] = tag.get('value', None)
        return uhp_values

    def get_modulator_form(self, profile_number=1):
        """
        Get the data from the UHP Profile Modulator page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'tx_on', and 'tx_level'.
        The dictionary values are taken from the page unmodified, except for 'tx_level'
        because it is represented as two separated fields each.

        :param int profile_number: UHP profile number. By default NMS uses profile number 1
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        tx_level_int, tx_level_float = None, None
        req = self.get_request(f'http://{self._router_address}/cm3?da={profile_number}')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                if tag['name'] == MOD_TX_ON_ATTR_NAME:
                    if tag.get('checked') is not None:
                        uhp_values['tx_on'] = '1'
                    else:
                        uhp_values['tx_on'] = '0'
                elif tag['name'] == MOD_TX_LEVEL_INT_ATTR_NAME:
                    tx_level_int = tag.get('value', '')
                elif tag['name'] == MOD_TX_LEVEL_FLOAT_ATTR_NAME:
                    tx_level_float = tag.get('value', '')
            if tx_level_int and tx_level_float:
                uhp_values['tx_level'] = f'{tx_level_int}.{tx_level_float}'
        return uhp_values

    def get_timing_values(self, profile_number=1):
        """
        Get the timing data from the UHP profile timing page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'sat_lon_deg', 'sat_lon_min', 'hub_tts_mode', 'tts_value'.
        The dictionary values are taken from the corresponding fields.
        The satellite longitude degrees are converted to the -180 +180 format

        :param int profile_number: UHP profile number. By default NMS uses profile number 1
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        sat_lon_deg, sat_lon_min, sat_pos, hub_tts_mode = None, None, None, None
        # Getting the sat data from the profile page.
        req = self.get_request(f'http://{self._router_address}/ci3?da={profile_number}')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name = tag.get('name')
                if name is None:
                    continue
                elif name == SAT_LON_DEG_ATTR_NAME:
                    sat_lon_deg = tag.get('value')
                elif name == SAT_LON_MIN_ATTR_NAME:
                    sat_lon_min = tag.get('value')
                elif name == TIMING_VALUE_ATTR_NAME:
                    uhp_values['tts_value'] = tag.get('value')
            tags = soup.find_all('select')
            for tag in tags:
                name = tag.get('name')
                if name is None:
                    continue
                elif name == SAT_EAST_WEST_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            sat_pos = option.contents[0]
                            break
                # Trying to get `hub_tts_mode` element
                elif name == TIMING_MODE_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            uhp_values['hub_tts_mode'] = option.contents[0]
                            break
            # Reformatting satellite longitude degrees (NMS uses -180 +180 format)
            if sat_pos is not None and sat_lon_deg is not None and sat_pos.lower() == 'w':
                sat_lon_deg = f'-{sat_lon_deg}'
            if sat_lon_deg and sat_lon_min:
                uhp_values['sat_lon_deg'] = sat_lon_deg
                uhp_values['sat_lon_min'] = sat_lon_min
        return uhp_values

    def get_tlc_form(self, profile_number=1):
        """
        Get the data from the UHP Profile TLC page as a dictionary
        The dictionary keys correspond to the NMS naming convention:
        'tlc_enable', 'tlc_max_lvl', 'tlc_net_own', 'tlc_avg_min', 'tlc_cn_stn', and 'tlc_cn_hub'.
        The dictionary values are taken from the page unmodified, except for 'tlc_cn_hub' and 'tlc_cn_stn'
        because they are represented as two separated fields each

        :param int profile_number: UHP profile number. By default NMS uses profile number 1
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        cn_hub_int, cn_hub_float = None, None
        cn_stn_int, cn_stn_float = None, None
        req = self.get_request(f'http://{self._router_address}/cl3?da={profile_number}')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name = tag.get('name', None)
                value = tag.get('value', None)
                if name is None or value is None:
                    continue
                elif name == TLC_ENABLE_ATTR_NAME:
                    if tag.get('checked') is not None:
                        uhp_values['tlc_enable'] = '1'
                    else:
                        uhp_values['tlc_enable'] = '0'
                elif name == TLC_MAX_LVL_ATTR_NAME:
                    uhp_values['tlc_max_lvl'] = value
                elif name == TLC_NET_OWN_ATTR_NAME:
                    uhp_values['tlc_net_own'] = value
                elif name == TLC_AVG_MIN_ATTR_NAME:
                    uhp_values['tlc_avg_min'] = value
                elif name == TLC_CN_HUB_INT_ATTR_NAME:
                    cn_hub_int = value
                elif name == TLC_CN_HUB_FLOAT_ATTR_NAME:
                    cn_hub_float = value
                elif name == TLC_CN_STN_INT_ATTR_NAME:
                    cn_stn_int = value
                elif name == TLC_CN_STN_FLOAT_ATTR_NAME:
                    cn_stn_float = value
            # Combining cn_hub_int, cn_hub_float. Combining cn_stn_int, cn_stn_float.
            if cn_hub_int and cn_hub_float:
                uhp_values['tlc_cn_hub'] = f'{cn_hub_int}.{cn_hub_float}'
            if cn_stn_int and cn_stn_float:
                uhp_values['tlc_cn_stn'] = f'{cn_stn_int}.{cn_stn_float}'
        return uhp_values

    def get_tdma_rf_form(self, profile_number=1):

        # TODO: the method is too long. Split it.
        """
        Get the data from the UHP TDMA RF page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
            tdma_input, tdma_sr, tdma_roll, tdma_mc, enh_tables
            mf1_en, mf1_tx, mf1_rx, mf2_en, mf2_tx, mf2_rx, mf3_en, mf3_tx, mf3_rx, mf4_en, mf4_tx, mf4_rx,
            mf5_en, mf5_tx, mf5_rx, mf6_en, mf6_tx, mf6_rx, mf7_en, mf7_tx, mf7_rx, mf8_en, mf9_tx, mf10_rx,
            mf11_en, mf11_tx, mf11_rx, mf12_en, mf12_tx, mf12_rx, mf13_en, mf13_tx, mf13_rx, mf14_en, mf14_tx, mf14_rx,
            mf15_en, mf15_tx, mf15_rx, mf16_en, mf16_tx, mf16_rx
        The dictionary values are taken from the page unmodified.

        :param int profile_number: UHP profile number. By default NMS uses profile number 1
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cd3?da={profile_number}')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name, value = tag.get('name'), tag.get('value')
                if name is None or value is None:
                    continue
                elif name == TDMA_RF_SR_ATTR_NAME:
                    uhp_values['tdma_sr'] = value
                elif name == TDMA_RF_ROLL_ATTR_NAME:
                    if tag.get('checked') is not None:
                        uhp_values['tdma_roll'] = RollofModesStr.R5.lower()
                    else:
                        uhp_values['tdma_roll'] = RollofModesStr.R20.lower()
                elif name == TDMA_RF_ENH_TABLE_ATTR_NAME:
                    uhp_values['enh_tables'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE2_ATTR_NAME:
                    uhp_values['mf2_en'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE3_ATTR_NAME:
                    uhp_values['mf3_en'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE4_ATTR_NAME:
                    uhp_values['mf4_en'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE5_ATTR_NAME:
                    uhp_values['mf5_en'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE6_ATTR_NAME:
                    uhp_values['mf6_en'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE7_ATTR_NAME:
                    uhp_values['mf7_en'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE8_ATTR_NAME:
                    uhp_values['mf8_en'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE9_ATTR_NAME:
                    uhp_values['mf9_en'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE10_ATTR_NAME:
                    uhp_values['mf10_en'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE11_ATTR_NAME:
                    uhp_values['mf11_en'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE12_ATTR_NAME:
                    uhp_values['mf12_en'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE13_ATTR_NAME:
                    uhp_values['mf13_en'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE14_ATTR_NAME:
                    uhp_values['mf14_en'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE15_ATTR_NAME:
                    uhp_values['mf15_en'] = '0' if tag.get('checked') is None else '1'
                elif name == TDMA_RF_ENABLE16_ATTR_NAME:
                    uhp_values['mf16_en'] = '0' if tag.get('checked') is None else '1'

                elif name == TDMA_RF_RX1_ATTR_NAME:
                    uhp_values['mf1_rx'] = tag.get('value')
                elif name == TDMA_RF_RX2_ATTR_NAME:
                    uhp_values['mf2_rx'] = tag.get('value')
                elif name == TDMA_RF_RX3_ATTR_NAME:
                    uhp_values['mf3_rx'] = tag.get('value')
                elif name == TDMA_RF_RX4_ATTR_NAME:
                    uhp_values['mf4_rx'] = tag.get('value')
                elif name == TDMA_RF_RX5_ATTR_NAME:
                    uhp_values['mf5_rx'] = tag.get('value')
                elif name == TDMA_RF_RX6_ATTR_NAME:
                    uhp_values['mf6_rx'] = tag.get('value')
                elif name == TDMA_RF_RX7_ATTR_NAME:
                    uhp_values['mf7_rx'] = tag.get('value')
                elif name == TDMA_RF_RX8_ATTR_NAME:
                    uhp_values['mf8_rx'] = tag.get('value')
                elif name == TDMA_RF_RX9_ATTR_NAME:
                    uhp_values['mf9_rx'] = tag.get('value')
                elif name == TDMA_RF_RX10_ATTR_NAME:
                    uhp_values['mf10_rx'] = tag.get('value')
                elif name == TDMA_RF_RX11_ATTR_NAME:
                    uhp_values['mf11_rx'] = tag.get('value')
                elif name == TDMA_RF_RX12_ATTR_NAME:
                    uhp_values['mf12_rx'] = tag.get('value')
                elif name == TDMA_RF_RX13_ATTR_NAME:
                    uhp_values['mf13_rx'] = tag.get('value')
                elif name == TDMA_RF_RX14_ATTR_NAME:
                    uhp_values['mf14_rx'] = tag.get('value')
                elif name == TDMA_RF_RX15_ATTR_NAME:
                    uhp_values['mf15_rx'] = tag.get('value')
                elif name == TDMA_RF_RX16_ATTR_NAME:
                    uhp_values['mf16_rx'] = tag.get('value')

                elif name == TDMA_RF_TX1_ATTR_NAME:
                    uhp_values['mf1_tx'] = tag.get('value')
                elif name == TDMA_RF_TX2_ATTR_NAME:
                    uhp_values['mf2_tx'] = tag.get('value')
                elif name == TDMA_RF_TX3_ATTR_NAME:
                    uhp_values['mf3_tx'] = tag.get('value')
                elif name == TDMA_RF_TX4_ATTR_NAME:
                    uhp_values['mf4_tx'] = tag.get('value')
                elif name == TDMA_RF_TX5_ATTR_NAME:
                    uhp_values['mf5_tx'] = tag.get('value')
                elif name == TDMA_RF_TX6_ATTR_NAME:
                    uhp_values['mf6_tx'] = tag.get('value')
                elif name == TDMA_RF_TX7_ATTR_NAME:
                    uhp_values['mf7_tx'] = tag.get('value')
                elif name == TDMA_RF_TX8_ATTR_NAME:
                    uhp_values['mf8_tx'] = tag.get('value')
                elif name == TDMA_RF_TX9_ATTR_NAME:
                    uhp_values['mf9_tx'] = tag.get('value')
                elif name == TDMA_RF_TX10_ATTR_NAME:
                    uhp_values['mf10_tx'] = tag.get('value')
                elif name == TDMA_RF_TX11_ATTR_NAME:
                    uhp_values['mf11_tx'] = tag.get('value')
                elif name == TDMA_RF_TX12_ATTR_NAME:
                    uhp_values['mf12_tx'] = tag.get('value')
                elif name == TDMA_RF_TX13_ATTR_NAME:
                    uhp_values['mf13_tx'] = tag.get('value')
                elif name == TDMA_RF_TX14_ATTR_NAME:
                    uhp_values['mf14_tx'] = tag.get('value')
                elif name == TDMA_RF_TX15_ATTR_NAME:
                    uhp_values['mf15_tx'] = tag.get('value')
                elif name == TDMA_RF_TX16_ATTR_NAME:
                    uhp_values['mf16_tx'] = tag.get('value')

            tags = soup.find_all('select')
            for tag in tags:
                if tag['name'] == TDMA_RF_INPUT_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            uhp_values['tdma_input'] = option.contents[0].lower().replace('-', '')
                            break
                elif tag['name'] == TDMA_RF_MODCOD_ATTR_NAME:
                    options = tag.find_all('option')
                    for option in options:
                        if option.get('selected') is not None:
                            uhp_values['tdma_mc'] = option.contents[0].replace('-', ' ').lstrip().rstrip().lower()
                            break
        return uhp_values

    def get_tdma_protocol_form(self, profile_number=1):
        """
        Get the data from the UHP TDMA prot page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'stn_number', 'frame_length', 'slot_length' and 'no_stn_check'.
        The dictionary values are taken from the page unmodified.

        :param int profile_number: UHP profile number. By default NMS uses profile number 1
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cp3?da={profile_number}')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                if tag['name'] == TDMA_PROT_FRAME_LENGTH_ATTR_NAME:
                    uhp_values['frame_length'] = tag.get('value', None)
                elif tag['name'] == TDMA_PROT_STN_NUMBER_ATTR_NAME:
                    uhp_values['stn_number'] = tag.get('value', None)
                elif tag['name'] == TDMA_PROT_SLOT_LENGTH_ATTR_NAME:
                    uhp_values['slot_length'] = tag.get('value', None)
                elif tag['name'] == TDMA_PROT_NO_STN_CHECK_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['no_stn_check'] = '1'
                    else:
                        uhp_values['no_stn_check'] = '0'
        return uhp_values

    def get_tdma_bw_form(self, profile_number=1):
        # TODO: the method is too long. Split it.
        """
        Get the data from the UHP TDMA BW page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
        'act_on_traf', 'mir_limit', 'opt_latency', 'rt_to_cir', 'bw_rq_scale',
        'td_rq_act1', 'td_rq_act2', 'td_rq_act3', 'td_rq_act4', 'td_rq_idl1',
        'td_rq_idl2', 'td_rq_idl3', 'td_rq_idl4', 'td_rq_dwn1', 'td_rq_dwn2',
        'td_rq_dwn3', 'td_rq_dwn4', 'td_rq_tout1', 'td_rq_tout2', 'td_rq_tout3',
        'td_rq_tout4'.
        The dictionary values are taken from the page unmodified.

        :param int profile_number: UHP profile number. By default NMS uses profile number 1
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/cj3?da={profile_number}')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name = tag.get('name', None)
                if name is None:
                    continue
                if name == TDMA_BW_RQ_ACT1_ATTR_NAME:
                    uhp_values['td_rq_act1'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_ACT2_ATTR_NAME:
                    uhp_values['td_rq_act2'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_ACT3_ATTR_NAME:
                    uhp_values['td_rq_act3'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_ACT4_ATTR_NAME:
                    uhp_values['td_rq_act4'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_IDL1_ATTR_NAME:
                    uhp_values['td_rq_idl1'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_IDL2_ATTR_NAME:
                    uhp_values['td_rq_idl2'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_IDL3_ATTR_NAME:
                    uhp_values['td_rq_idl3'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_IDL4_ATTR_NAME:
                    uhp_values['td_rq_idl4'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_DWN1_ATTR_NAME:
                    uhp_values['td_rq_dwn1'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_DWN2_ATTR_NAME:
                    uhp_values['td_rq_dwn2'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_DWN3_ATTR_NAME:
                    uhp_values['td_rq_dwn3'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_DWN4_ATTR_NAME:
                    uhp_values['td_rq_dwn4'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_TOUT1_ATTR_NAME:
                    uhp_values['td_rq_tout1'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_TOUT2_ATTR_NAME:
                    uhp_values['td_rq_tout2'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_TOUT3_ATTR_NAME:
                    uhp_values['td_rq_tout3'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_TOUT4_ATTR_NAME:
                    uhp_values['td_rq_tout4'] = tag.get('value', None)
                elif name == TDMA_BW_RQ_SCALE_ATTR_NAME:
                    uhp_values['bw_rq_scale'] = tag.get('value', None)
                elif name == TDMA_BW_MIR_LIMIT_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['mir_limit'] = '1'
                    else:
                        uhp_values['mir_limit'] = '1'
                elif name == TDMA_BW_ACT_ON_TRAF_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['act_on_traf'] = '1'
                    else:
                        uhp_values['act_on_traf'] = '1'
                elif name == TDMA_BW_OPT_LATENCY_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['opt_latency'] = '1'
                    else:
                        uhp_values['opt_latency'] = '1'
                elif name == TDMA_BW_RT_TO_CIR_ATTR_NAME:
                    if tag.get('checked', None) is not None:
                        uhp_values['rt_to_cir'] = '1'
                    else:
                        uhp_values['rt_to_cir'] = '1'
        return uhp_values

    def get_rip_router(self, hub_vlan=None, stn_vlan=None, rip_next_hop=None):
        """
        Get RIP router parameters.
        If no params are passed the very first existing RIP router entry params are returned

        :param Optional int hub_vlan: hub_vlan RIP router value
        :param Optional int stn_vlan: stn_vlan RIP router value
        :param Optional str rip_next_hop: Next hop to advertise RIP router value
        :returns: None if no such RIP router found, otherwise dict of RIP router parameters
        """
        uhp_values = {}
        last_page = False
        # Failsafe to make sure that the cycle is not run forever
        for i in range(50000):
            if i == 0:
                req = self.get_request(f'http://{self._router_address}/cc4')
                if not req:
                    return uhp_values
            else:
                req = self.get_request(f'http://{self._router_address}/cc4?dq=1')
                if not req:
                    return uhp_values
                soup = BeautifulSoup(req.content, 'html.parser')
                for anchor_tag in soup.find_all('a'):
                    if anchor_tag.get('href') == 'cc4?dq=1':
                        break
                else:
                    last_page = True
            soup = BeautifulSoup(req.content, 'html.parser')
            for anchor_tag in soup.find_all('a'):
                if anchor_tag.get('href').startswith('cp4') and anchor_tag.get('href') != 'cp4?da=0':
                    req_rip = self.get_request(f'http://{self._router_address}/{anchor_tag.get("href")}')
                    if not req_rip:
                        return uhp_values
                    temp = {}
                    soup_rip = BeautifulSoup(req_rip.content, 'html.parser')
                    for inp in soup_rip.find_all('input'):
                        name = inp.get('name')
                        if name is None:
                            continue
                        elif name == RIP_HUB_VLAN_ATTR_NAME:
                            temp['hub_vlan'] = inp.get('value')
                        elif name == RIP_STN_VLAN_ATTR_NAME:
                            temp['stn_vlan'] = inp.get('value')
                        elif name == RIP_NEXT_HOP_ATTR_NAME:
                            temp['rip_next_hop'] = inp.get('value')
                        elif name == RIP_LAN_RX_ATTR_NAME:
                            if inp.get('checked') is not None:
                                temp['lan_rx'] = True
                            else:
                                temp['lan_rx'] = False
                        elif name == RIP_LAN_DEFAULT_ATTR_NAME:
                            if inp.get('checked') is not None:
                                temp['lan_default'] = True
                            else:
                                temp['lan_default'] = False
                        elif name == RIP_SAT_RX_ATTR_NAME:
                            if inp.get('checked') is not None:
                                temp['sat_rx'] = True
                            else:
                                temp['sat_rx'] = False
                        elif name == RIP_SAT_DEFAULT_ATTR_NAME:
                            if inp.get('checked') is not None:
                                temp['sat_default'] = True
                            else:
                                temp['sat_default'] = False
                        elif name == RIP_ANNOUNCE_ATTR_NAME:
                            if inp.get('checked') is not None:
                                temp['announce'] = True
                            else:
                                temp['announce'] = False
                    # Checking passed parameters
                    if hub_vlan is not None and temp['hub_vlan'] != str(hub_vlan):
                        continue
                    if stn_vlan is not None and temp['stn_vlan'] != str(stn_vlan):
                        continue
                    if rip_next_hop is not None and temp['rip_next_hop'] != rip_next_hop:
                        continue
                    for selector in soup_rip.find_all('select'):
                        name = selector.get('name')
                        if name is None:
                            continue
                        elif name == RIP_PRIORITY_ATTR_NAME:
                            options = selector.find_all('option')
                            for option in options:
                                if option.get('selected') is not None:
                                    temp['priority'] = option.contents[0]
                                    break
                        elif name == RIP_POLICY_ATTR_NAME:
                            options = selector.find_all('option')
                            for option in options:
                                if option.get('selected') is not None:
                                    temp['policy'] = option.contents[0]
                                    break
                        elif name == RIP_SHAPER_ATTR_NAME:
                            options = selector.find_all('option')
                            for option in options:
                                if option.get('selected') is not None:
                                    temp['shaper'] = option.contents[0]
                                    break
                    return temp
            if last_page:
                return uhp_values

    def get_dama_return_channel_form(self, profile_number=1, return_channel=1):
        """
        Get data from UHP Return Channel page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
            'stn_number', 'serial', 'red_serial', 'tcpa',
            'dama_tx_frq', 'dama_tx_sr', 'dama_sr', 'dama_modcod', 'dama_pilots', 'dama_rolloff',
            'dama_level', 'dama_tx', 'dama_cn_hub'
        Note: 'dama_tx_sr' and 'dama_sr' are the same - for previous compatibility

        :param int profile_number: UHP profile number. By default NMS uses profile number 1
        :param int return_channel: return channel number to get data from (1 or 2)
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        if return_channel == 2:
            ch = 1
        else:
            ch = 0
        uhp_values = {}
        tx_lvl_int, tx_lvl_float, cn_hub_int, cn_hub_float = 0, 0, 0, 0
        req = self.get_request(f'http://{self._router_address}/cq3?da={profile_number}&dA={ch}')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name = tag.get('name')
                value = tag.get('value')
                if name is None or value is None:
                    continue
                elif name == RET_CH_STN_NUM_ATTR_NAME:
                    uhp_values['stn_number'] = value
                elif name == RET_CH_SER_ATTR_NAME:
                    uhp_values['serial'] = value
                elif name == RET_CH_RED_SER_ATTR_NAME:
                    uhp_values['red_serial'] = value
                elif name == RET_CH_TCPA_ATTR_NAME:
                    if tag.get('checked') is not None:
                        uhp_values['tcpa'] = '1'
                    else:
                        uhp_values['tcpa'] = '0'
                elif name == RET_CH_FRQ_ATTR_NAME:
                    uhp_values['dama_tx_frq'] = value
                elif name == RET_CH_SR_ATTR_NAME:
                    uhp_values['dama_tx_sr'] = value
                    uhp_values['dama_sr'] = value
                elif name == RET_CH_PILOTS_ATTR_NAME:
                    if tag.get('checked') is not None:
                        uhp_values['dama_pilots'] = '1'
                    else:
                        uhp_values['dama_pilots'] = '0'
                elif name == RET_CH_TX_LVL_INT_ATTR_NAME:
                    tx_lvl_int = value
                elif name == RET_CH_TX_LVL_FLOAT_ATTR_NAME:
                    tx_lvl_float = value
                elif name == RET_CH_CN_HUB_INT_ATTR_NAME:
                    cn_hub_int = value
                elif name == RET_CH_CN_HUB_FLOAT_ATTR_NAME:
                    cn_hub_float = value
            uhp_values['dama_level'] = f'{tx_lvl_int}.{tx_lvl_float}'
            uhp_values['dama_cn_hub'] = f'{cn_hub_int}.{cn_hub_float}'
            # Getting selectors values
            tags = soup.find_all('select')
            for tag in tags:
                name = tag.get('name')
                if name is None:
                    continue
                elif name == RET_CH_MODCOD_ATTR_NAME:
                    selected = tag.find('option', selected=True)
                    uhp_values['dama_modcod'] = selected.get('value')
                elif name == RET_CH_ROLLOFF_ATTR_NAME:
                    selected = tag.find('option', selected=True)
                    uhp_values['dama_rolloff'] = selected.get('value')
                elif name == RET_CH_TX_MODE_ATTR_NAME:
                    selected = tag.find('option', selected=True)
                    uhp_values['dama_tx'] = selected.get('value')
        return uhp_values

    def get_uhp_options(self):
        """
        Get UHP modem SW options either as simple Options or (NMS)Options
        Sample output:
            'OUTR INR HMESH FMESH MASTER DVBS2 16AP 2DEM CCP 32AP5% MCD AES OP1 MCD8'

        :returns str: a string representing UHP SW options, or None if unexpectedly options are not found
        """
        req = self.get_request(f'http://{self._router_address}/ss30')
        if not req:
            return None
        res_lines = req.text.split('\r\n')
        for i in range(len(res_lines) - 1):
            if res_lines[i].startswith('Key 0') \
                    and (res_lines[i + 1].startswith('Options:') or res_lines[i + 1].startswith('(NMS)Options:')):
                return res_lines[i + 1]
            # if res_lines[i].startswith('Key 0') and res_lines[i+1].startswith('Options:'):
            #     return res_lines[i+1].split('Options:')[-1].rstrip().lstrip()
            # elif res_lines[i].startswith('Key 0') and res_lines[i+1].startswith('(NMS)Options:'):
            #     return res_lines[i+1].split('(NMS)Options:')[-1].rstrip().lstrip()
        return None

    def get_tdma_acm_form(self, profile_number=1):
        """
        Get the data from the UHP TDMA ACM page as a dictionary.
        The dictionary keys are the following:
            tdma_acm, mode, mesh_mc, hub_rx_mesh,
            bpsk1_2, bpsk2_3, bpsk3_4, bpsk5_6,
            qpsk1_2, qpsk2_3, qpsk3_4, qpsk5_6,
            8psk1_2, 8psk2_3, 8psk3_4, 8psk5_6,
            16apsk1_2, 16apsk2_3, 16apsk3_4, 16apsk5_6,
            bpsk1_2_thr, bpsk2_3_thr, bpsk3_4_thr, bpsk5_6_thr,
            qpsk1_2_thr, qpsk2_3_thr, qpsk3_4_thr, qpsk5_6_thr,
            8psk1_2_thr, 8psk2_3_thr, 8psk3_4_thr, 8psk5_6_thr,
            16apsk1_2_thr, 16apsk2_3_thr, 16apsk3_4_thr, 16apsk5_6_thr,
        The dictionary values are taken from the page unmodified.
        Note: mesh_mc values from 0 ('-') to 16 ('16APSK-5/6'). NMS values from 0 ('BPSK-1/2') to 15 ('16APSK-5/6')

        :param int profile_number: UHP profile number. By default NMS uses profile number 1
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {
            'tdma_acm': '0', 'mode': '0', 'mesh_mc': '0', 'hub_rx_mesh': '0',
            'bpsk1_2': '0', 'bpsk2_3': '0', 'bpsk3_4': '0', 'bpsk5_6': '0',
            'qpsk1_2': '0', 'qpsk2_3': '0', 'qpsk3_4': '0', 'qpsk5_6': '0',
            '8psk1_2': '0', '8psk2_3': '0', '8psk3_4': '0', '8psk5_6': '0',
            '16apsk1_2': '0', '16apsk2_3': '0', '16apsk3_4': '0', '16apsk5_6': '0'
        }
        req = self.get_request(f'http://{self._router_address}/cg3?da={profile_number}')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name, value, checked = tag.get('name'), tag.get('value'), tag.get('checked')
                if name is None or value is None:
                    continue
                elif name == TDMA_ACM_ENABLE_ATTR_NAME and checked is not None:
                    uhp_values['tdma_acm'] = '1'
                elif name == TDMA_ACM_ACTIVE_BPSK_1_2_ATTR_NAME and checked is not None:
                    uhp_values['bpsk1_2'] = '1'
                elif name == TDMA_ACM_ACTIVE_BPSK_2_3_ATTR_NAME and checked is not None:
                    uhp_values['bpsk2_3'] = '1'
                elif name == TDMA_ACM_ACTIVE_BPSK_3_4_ATTR_NAME and checked is not None:
                    uhp_values['bpsk3_4'] = '1'
                elif name == TDMA_ACM_ACTIVE_BPSK_5_6_ATTR_NAME and checked is not None:
                    uhp_values['bpsk5_6'] = '1'
                elif name == TDMA_ACM_ACTIVE_QPSK_1_2_ATTR_NAME and checked is not None:
                    uhp_values['qpsk1_2'] = '1'
                elif name == TDMA_ACM_ACTIVE_QPSK_2_3_ATTR_NAME and checked is not None:
                    uhp_values['qpsk2_3'] = '1'
                elif name == TDMA_ACM_ACTIVE_QPSK_3_4_ATTR_NAME and checked is not None:
                    uhp_values['qpsk3_4'] = '1'
                elif name == TDMA_ACM_ACTIVE_QPSK_5_6_ATTR_NAME and checked is not None:
                    uhp_values['qpsk5_6'] = '1'
                elif name == TDMA_ACM_ACTIVE_8PSK_1_2_ATTR_NAME and checked is not None:
                    uhp_values['8psk1_2'] = '1'
                elif name == TDMA_ACM_ACTIVE_8PSK_2_3_ATTR_NAME and checked is not None:
                    uhp_values['8psk2_3'] = '1'
                elif name == TDMA_ACM_ACTIVE_8PSK_3_4_ATTR_NAME and checked is not None:
                    uhp_values['8psk3_4'] = '1'
                elif name == TDMA_ACM_ACTIVE_8PSK_5_6_ATTR_NAME and checked is not None:
                    uhp_values['8psk5_6'] = '1'
                elif name == TDMA_ACM_ACTIVE_16APSK_1_2_ATTR_NAME and checked is not None:
                    uhp_values['16apsk1_2'] = '1'
                elif name == TDMA_ACM_ACTIVE_16APSK_2_3_ATTR_NAME and checked is not None:
                    uhp_values['16apsk2_3'] = '1'
                elif name == TDMA_ACM_ACTIVE_16APSK_3_4_ATTR_NAME and checked is not None:
                    uhp_values['16apsk3_4'] = '1'
                elif name == TDMA_ACM_ACTIVE_16APSK_5_6_ATTR_NAME and checked is not None:
                    uhp_values['16apsk5_6'] = '1'
                elif name == TDMA_ACM_THRESH_BPSK_1_2_ATTR_NAME:
                    uhp_values['bpsk1_2_thr'] = value
                elif name == TDMA_ACM_THRESH_BPSK_2_3_ATTR_NAME:
                    uhp_values['bpsk2_3_thr'] = value
                elif name == TDMA_ACM_THRESH_BPSK_3_4_ATTR_NAME:
                    uhp_values['bpsk3_4_thr'] = value
                elif name == TDMA_ACM_THRESH_BPSK_5_6_ATTR_NAME:
                    uhp_values['bpsk5_6_thr'] = value
                elif name == TDMA_ACM_THRESH_QPSK_1_2_ATTR_NAME:
                    uhp_values['qpsk1_2_thr'] = value
                elif name == TDMA_ACM_THRESH_QPSK_2_3_ATTR_NAME:
                    uhp_values['qpsk2_3_thr'] = value
                elif name == TDMA_ACM_THRESH_QPSK_3_4_ATTR_NAME:
                    uhp_values['qpsk3_4_thr'] = value
                elif name == TDMA_ACM_THRESH_QPSK_5_6_ATTR_NAME:
                    uhp_values['qpsk5_6_thr'] = value
                elif name == TDMA_ACM_THRESH_8PSK_1_2_ATTR_NAME:
                    uhp_values['8psk1_2_thr'] = value
                elif name == TDMA_ACM_THRESH_8PSK_2_3_ATTR_NAME:
                    uhp_values['8psk2_3_thr'] = value
                elif name == TDMA_ACM_THRESH_8PSK_3_4_ATTR_NAME:
                    uhp_values['8psk3_4_thr'] = value
                elif name == TDMA_ACM_THRESH_8PSK_5_6_ATTR_NAME:
                    uhp_values['8psk5_6_thr'] = value
                elif name == TDMA_ACM_THRESH_16APSK_1_2_ATTR_NAME:
                    uhp_values['16apsk1_2_thr'] = value
                elif name == TDMA_ACM_THRESH_16APSK_2_3_ATTR_NAME:
                    uhp_values['16apsk2_3_thr'] = value
                elif name == TDMA_ACM_THRESH_16APSK_3_4_ATTR_NAME:
                    uhp_values['16apsk3_4_thr'] = value
                elif name == TDMA_ACM_THRESH_16APSK_5_6_ATTR_NAME:
                    uhp_values['16apsk5_6_thr'] = value
                elif name == TDMA_RECEIVE_MESH_ATTR_NAME and checked is not None:
                    uhp_values['hub_rx_mesh'] = '1'

            tags = soup.find_all('select')
            for tag in tags:
                if tag.get('name') == TDMA_ACM_MODE_ATTR_NAME:
                    selected = tag.find('option', selected=True)
                    uhp_values['mode'] = selected.get('value')
                elif tag.get('name') == TDMA_MESH_MODCOD_ATTR_NAME:
                    selected = tag.find('option', selected=True)
                    if selected is not None:
                        uhp_values['mesh_mc'] = selected.get('value')
        return uhp_values

    def get_ip_routing_static(self):
        """
        Get UHP Static Routing table

        The dictionary keys correspond to the NMS naming convention:
        'ip_address', 'ipv6_address', 'network_tx', 'ipv6_net_tx', 'rip_router', 'static_route', 'ipv6_route',
        'l2_bridge', 'network_rx'.

        :returns Dict[str, List] uhp_values: a dictionary containing route types
        """
        uhp_values = {'ip_address': [], 'ipv6_address': [], 'network_tx': [], 'ipv6_net_tx': [], 'rip_router': [],
                      'static_route': [], 'ipv6_route': [], 'l2_bridge': [], 'network_rx': [], }
        first = True
        for _ in range(1000):
            if first:
                res = self.get_request(f'http://{self._router_address}/cc4')
                first = False
            else:
                res = self.get_request(f'http://{self._router_address}/cc4?dq=1')
            if not res:
                return uhp_values
            # Getting port mappings
            soup = BeautifulSoup(res.content, 'lxml')
            tables = soup.find_all('table')
            rows = tables[-1].find_all('tr')
            for i in range(len(rows)):
                row_data = rows[i].find_all('td')
                data = [td.text for td in row_data]
                if len(data) == 9 and data[0] == 'M':
                    _record = {'vlan': data[1], 'destination': data[3], 'rip': data[4], 'svlan': data[5],
                               'prio/pol': data[6], 'shaper': data[7], 'title': data[8].rstrip()}
                    if data[2] == 'Bridge':
                        uhp_values['l2_bridge'].append(_record)
                    elif is_ipv4(data[2]):
                        _record['ip'] = data[2].split()[0]
                        _record['mask'] = data[2].split()[1]
                        uhp_values['network_tx'].append(_record)
                    elif is_ipv6(data[2]):
                        _record['v6_ip'] = data[2].split()[0]
                        _record['v6_mask'] = data[2].split()[1]
                        uhp_values['ipv6_net_tx'].append(_record)
                elif len(data) == 7 and data[0] == 'A':
                    _record = {'vlan': data[1], 'destination': data[3], 'rip': data[4], 'title': data[6].rstrip()}
                    if is_ipv4(data[2]):
                        _record['ip'] = data[2].split()[0]
                        _record['mask'] = data[2].split()[1]
                        uhp_values['ip_address'].append(_record)
                    elif is_ipv6(data[2]):
                        _record['v6_ip'] = data[2].split()[0]
                        _record['v6_mask'] = data[2].split()[1]
                        uhp_values['ipv6_address'].append(_record)
                elif len(data) == 5 and data[0] == 'R':
                    _vlans = data[4].split()
                    _hub_vlan = _vlans[2].split('=')[1]
                    _stn_vlan = _vlans[5].split('=')[1]
                    _record = {'rip_next_hop': data[3], 'hub_vlan': _hub_vlan, 'stn_vlan': _stn_vlan}
                    uhp_values['rip_router'].append(_record)
                elif len(data) == 7 and data[0] == 'S':
                    _record = {'vlan': data[1], 'title': data[6].rstrip()}
                    if is_ipv4(data[2]):
                        _record['ip'] = data[2].split()[0]
                        _record['mask'] = data[2].split()[1]
                        _record['gateway'] = data[3]
                        uhp_values['static_route'].append(_record)
                    elif is_ipv6(data[2]):
                        _record['v6_ip'] = data[2].split()[0]
                        _record['v6_mask'] = data[2].split()[1]
                        _record['v6_gateway'] = data[3]
                        uhp_values['ipv6_route'].append(_record)
                elif len(data) == 5 and data[0] == 'V':
                    _record = {'vlan': data[1], 'svlan': data[2].split('-')[1], 'title': data[4].rstrip()}
                    uhp_values['network_rx'].append(_record)

            soup = BeautifulSoup(res.content, 'html.parser')
            links = soup.find_all('a')
            for link in links:
                if link.get('href') == 'cc4?dq=1':
                    break
            else:
                break
        return uhp_values

    def get_roaming_form(self, profile_number=1):
        """
        Get the data from the UHP Roaming page as a dictionary.
        The dictionary keys correspond to the NMS naming convention:
            roaming_enable, roaming_slots
        The dictionary values are taken from the page unmodified.

        :param int profile_number: UHP profile number. By default NMS uses profile number 1
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/co3?da={profile_number}')
        if req:
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name, value = tag.get('name'), tag.get('value')
                if name is None or value is None:
                    continue
                elif name == ROAMING_ENABLE_ATTR_NAME:
                    if tag.get('checked') is not None:
                        uhp_values['roaming_enable'] = '1'
                    else:
                        uhp_values['roaming_enable'] = '0'
                elif name == ROAMING_TIMEOUT_ATTR_NAME:
                    uhp_values['roaming_slots'] = value
        return uhp_values

    def get_tdm_acm_form(self, profile_number=1):
        """
        Get data from TDM ACM page as a dictionary. The dictionary keys correspond to the NMS naming convention:
            'acm_enable', 'acm_mc2, 'acm_mc3', 'acm_mc4', 'acm_mc5', 'acm_mc6', 'acm_mc7', 'acm_mc8', 'acm_thr',
            'max_modcod'
        Note: 'max_modcod' and 'acm_mc2' have equal values - for compatibility between various profiles

        :param int profile_number: profile number to get data from
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        if profile_number not in range(1, 9):
            raise InvalidOptionsException(f'Invalid profile number: you passed {profile_number} {type(profile_number)}')
        uhp_values = {}
        req = self.get_request(f'http://{self._router_address}/ca3?da={profile_number}')
        if not req:
            return uhp_values
        soup = BeautifulSoup(req.content, 'html.parser')
        tags = soup.find_all('input')
        cn_int = 0
        cn_float = 0
        for tag in tags:
            name, value, checked = tag.get('name'), tag.get('value'), tag.get('checked')
            if name is None or value is None:
                continue
            elif name == TDM_ACM_ENABLE_ATTR_NAME:
                if checked is not None:
                    uhp_values['acm_enable'] = '1'
                else:
                    uhp_values['acm_enable'] = '0'
            elif name == TDM_ACM_CN_THRESHOLD_INT_ATTR_NAME:
                cn_int = value
            elif name == TDM_ACM_CN_THRESHOLD_FLOAT_ATTR_NAME:
                cn_float = value
        uhp_values['acm_thr'] = f'{cn_int}.{cn_float}'
        tags = soup.find_all('select')
        for tag in tags:
            name = tag.get('name')
            if name is None:
                continue
            elif name == TDM_ACM_MODCOD2_ATTR_NAME:
                uhp_values['max_modcod'] = tag.find('option', selected=True).get('value')
                uhp_values['acm_mc2'] = tag.find('option', selected=True).get('value')
            elif name == TDM_ACM_MODCOD3_ATTR_NAME:
                uhp_values['acm_mc3'] = tag.find('option', selected=True).get('value')
            elif name == TDM_ACM_MODCOD4_ATTR_NAME:
                uhp_values['acm_mc4'] = tag.find('option', selected=True).get('value')
            elif name == TDM_ACM_MODCOD5_ATTR_NAME:
                uhp_values['acm_mc5'] = tag.find('option', selected=True).get('value')
            elif name == TDM_ACM_MODCOD6_ATTR_NAME:
                uhp_values['acm_mc6'] = tag.find('option', selected=True).get('value')
            elif name == TDM_ACM_MODCOD7_ATTR_NAME:
                uhp_values['acm_mc7'] = tag.find('option', selected=True).get('value')
            elif name == TDM_ACM_MODCOD8_ATTR_NAME:
                uhp_values['acm_mc8'] = tag.find('option', selected=True).get('value')
        return uhp_values

    def _get_tdma_acm_form36(self, profile_number=1):
        """
        Get the data from the UHP SW 3.6 TDMA ACM page as a dictionary.
        The dictionary keys are the following:
            tdma_acm, qpsk1_2, qpsk2_3, qpsk3_4, qpsk5_6, 8psk1_2, 8psk2_3, 8psk3_4, 8psk5_6,
            16apsk1_2, 16apsk2_3, 16apsk3_4, 16apsk5_6, tdma_thr_acm

        The dictionary values are taken from the page unmodified.

        :param int profile_number: UHP profile number. By default NMS uses profile number 1
        :returns Dict[str, str] uhp_values: a dictionary containing the field names and their corresponding values
        """
        uhp_values = {
            'tdma_acm': '0', 'mode': '0',
            'qpsk1_2': '0', 'qpsk2_3': '0', 'qpsk3_4': '0', 'qpsk5_6': '0',
            '8psk1_2': '0', '8psk2_3': '0', '8psk3_4': '0', '8psk5_6': '0',
            '16apsk1_2': '0', '16apsk2_3': '0', '16apsk3_4': '0', '16apsk5_6': '0',
        }
        req = self.get_request(f'http://{self._router_address}/cg3?da={profile_number}')
        if req:
            tdma_acm_thr_int, tdma_acm_thr_float = None, None
            soup = BeautifulSoup(req.content, 'html.parser')
            tags = soup.find_all('input')
            for tag in tags:
                name, value, checked = tag.get('name'), tag.get('value'), tag.get('checked')
                if name is None or value is None:
                    continue
                # Using same attribute name as for ver.3.7, therefore the result is shifted
                elif name == TDMA_ACM_ENABLE_ATTR_NAME and checked is not None:
                    uhp_values['tdma_acm'] = '1'
                elif name == TDMA_ACM_ACTIVE_BPSK_3_4_ATTR_NAME and checked is not None:
                    uhp_values['qpsk1_2'] = '1'
                elif name == TDMA_ACM_ACTIVE_BPSK_5_6_ATTR_NAME and checked is not None:
                    uhp_values['qpsk2_3'] = '1'
                elif name == TDMA_ACM_ACTIVE_QPSK_1_2_ATTR_NAME and checked is not None:
                    uhp_values['qpsk3_4'] = '1'
                elif name == TDMA_ACM_ACTIVE_QPSK_2_3_ATTR_NAME and checked is not None:
                    uhp_values['qpsk5_6'] = '1'
                elif name == TDMA_ACM_ACTIVE_QPSK_3_4_ATTR_NAME and checked is not None:
                    uhp_values['8psk1_2'] = '1'
                elif name == TDMA_ACM_ACTIVE_QPSK_5_6_ATTR_NAME and checked is not None:
                    uhp_values['8psk2_3'] = '1'
                elif name == TDMA_ACM_ACTIVE_8PSK_1_2_ATTR_NAME and checked is not None:
                    uhp_values['8psk3_4'] = '1'
                elif name == TDMA_ACM_ACTIVE_8PSK_2_3_ATTR_NAME and checked is not None:
                    uhp_values['8psk5_6'] = '1'
                elif name == TDMA_ACM_ACTIVE_8PSK_3_4_ATTR_NAME and checked is not None:
                    uhp_values['16apsk1_2'] = '1'
                elif name == TDMA_ACM_ACTIVE_8PSK_5_6_ATTR_NAME and checked is not None:
                    uhp_values['16apsk2_3'] = '1'
                elif name == TDMA_ACM_ACTIVE_16APSK_1_2_ATTR_NAME and checked is not None:
                    uhp_values['16apsk3_4'] = '1'
                elif name == TDMA_ACM_ACTIVE_16APSK_2_3_ATTR_NAME and checked is not None:
                    uhp_values['16apsk5_6'] = '1'
                elif name == TDMA_ACM_ACTIVE_16APSK_3_4_ATTR_NAME:
                    tdma_acm_thr_int = value
                elif name == TDMA_ACM_ACTIVE_16APSK_5_6_ATTR_NAME:
                    tdma_acm_thr_float = value
            if tdma_acm_thr_int is not None and tdma_acm_thr_float is not None:
                uhp_values['tdma_acm_thr'] = f'{tdma_acm_thr_int}.{tdma_acm_thr_float}'
            tags = soup.find_all('select')
            for tag in tags:
                if tag.get('name') == TDMA_ACM_MODE_ATTR_NAME:
                    selected = tag.find('option', selected=True)
                    uhp_values['mode'] = selected.get('value')
        return uhp_values

    def get_shapers(self):
        """
        Get all UHP shapers and their parameters

        The inner dictionary keys correspond to the NMS naming convention:
        'name', 'template', 'cir', 'up_queue', 'max_enable', 'max_cir', 'max_slope', 'min_enable', 'min_cir',
        'down_slope', 'up_slope', 'wfq_enable', 'wfq1', 'wfq2', 'wfq3', 'wfq4', 'wfq5', 'wfq6',
        'night_enable', 'night_cir', 'night_start', 'night_end'
        The following keys are not presented in NMS:
        'upper_enable', 'upper_channel_number', 'upper_channel_name'

        :returns Dict[str, Dict]: shaper channels as outer keys and a dictionary of parameters as the value
        """
        uhp_values = {}
        _next = False
        res = self.get_request(f'http://{self._router_address}/cc6')
        if not res:
            return uhp_values
        for _ in range(150):  # 2040 shapers are possible, 15 on each page. Breaking the cycle if there is no next link
            soup = BeautifulSoup(res.content, 'html.parser')
            anchors = soup.find_all('a')
            for anchor in anchors:
                _href = anchor.get('href')
                _cur_ch = anchor.contents[0]
                if _href.find('ce6?da=') != -1 and _cur_ch not in uhp_values.keys():
                    uhp_values[_cur_ch] = {}
                    # Getting next shaper channel page
                    shp_form_res = self.get_request(f'http://{self._router_address}/{_href}')
                    if not shp_form_res:
                        return uhp_values
                    shp_soup = BeautifulSoup(shp_form_res.content, 'html.parser')
                    tags = shp_soup.find_all('input')
                    for tag in tags:
                        name, value, checked, t = tag.get('name'), tag.get('value'), tag.get('checked'), tag.get('type')
                        if name is None or value is None:
                            continue
                        elif name in shaper_mapping.keys():
                            if t == 'checkbox':
                                if checked is not None:
                                    uhp_values[_cur_ch][shaper_mapping[name]] = 'ON'
                                else:
                                    uhp_values[_cur_ch][shaper_mapping[name]] = 'OFF'
                            elif t == 'text':
                                uhp_values[_cur_ch][shaper_mapping[name]] = value
                    tags = shp_soup.find_all('select')
                    for tag in tags:
                        name = tag.get('name')
                        if name is None:
                            continue
                        selected = tag.find('option', selected=True)
                        if name == SHAPER_UP_QUEUE_ATTR_NAME:
                            uhp_values[_cur_ch][shaper_mapping[name]] = shaper_queue_mapping[selected.contents[0]]
                        elif name == SHAPER_UPPER_CHANNEL_ATTR_NAME:
                            upper_channel_number = selected.contents[0].split()[0]
                            upper_channel_name = ''.join(selected.contents[0].split()[1:])
                            uhp_values[_cur_ch]['upper_channel_number'] = upper_channel_number
                            uhp_values[_cur_ch]['upper_channel_name'] = upper_channel_name
                if anchor.contents[0] == 'Next':
                    _next = _href
                    break
                else:
                    _next = False
            # Looking for next anchor tag
            if _next:
                res = self.get_request(f'http://{self._router_address}/{_next}')
                if not res:
                    return uhp_values
            else:
                break
        return uhp_values

    def get_modulator_stats(self) -> Union[Dict[str, str], None]:
        """
        Get modulator statistics page data. Keys' naming depends on the current mode:
            for TDM with no ACM queues' keys starts with priority queue number, i.e. 'p1_packets';
            for TDM ACM queues' keys starts with channel number, i.e. 'ch3_p4_bytes';
            for TDMA queues' keys starts with direction, i.e. 'to_hub_p1_drops

        :returns Dict: a dictionary containing statistics data as key/value pairs
        """
        uhp_values = {}
        res = self.get_request(f'http://{self._router_address}/ss32')
        if not res:
            return None
        content = res.text.lower()
        uhp_values['state'] = self._find_value_by_regex('modulator interface is ', '[a-z]+', content)
        uhp_values['type'] = self._find_value_by_regex('type: ', '[a-z]+', content)
        uhp_values['freq'] = self._find_value_by_regex('freq: ', '[0-9]+', content)
        uhp_values['freq_adj'] = self._find_value_by_regex('freqadj: ', '[0-9]+', content)
        uhp_values['sr'] = self._find_value_by_regex('sr: ', '[0-9]+', content)
        uhp_values['set_lvl'] = self._find_value_by_regex('setlvl: ', '[-]*[0-9]+.[0-9]*', content)
        uhp_values['max'] = self._find_value_by_regex('max: ', '[-]*[0-9]+', content)
        uhp_values['10m'] = self._find_value_by_regex('10m: ', '[a-z]+', content)
        uhp_values['lo'] = self._find_value_by_regex('lo: ', '[0-9]+', content)
        uhp_values['fix_corr'] = self._find_value_by_regex('fixcorr: ', '[0-9]+', content)
        uhp_values['br'] = self._find_value_by_regex('br: ', '[0-9]+', content)
        out_lvl = self._find_value_by_regex('outlvl: ', '[-]*[0-9]+.[0-9]*', content)
        # out level is OFF when modulator is disabled
        if out_lvl is not None:
            uhp_values['out_lvl'] = out_lvl
        else:
            uhp_values['out_lvl'] = self._find_value_by_regex('outlvl: ', '[a-z]+', content)
        uhp_values['tx'] = self._find_value_by_regex('tx: ', '[a-z]+', content)
        uhp_values['24v'] = self._find_value_by_regex('24v: ', '[a-z]+', content)
        uhp_values['mode'] = self._find_value_by_regex('mode: ', '[a-z]+[-]*[a-z]*[0-9]*', content)
        modcod = self._find_value_by_regex('modcod: ', '[a-z]+\s[0-9]*[a-z]+\s[0-9]+/[0-9]+', content)
        if modcod is not None:
            uhp_values['modcod'] = modcod
        else:  # modulator in TDMA mode has different modcod represenation
            m = self._find_value_by_regex('mod: ', '[0-9]*[a-z]+', content)
            f = self._find_value_by_regex('fec: ', '[0-9]+/[0-9]+', content)
            if m is not None and f is not None:
                uhp_values['modcod'] = f'{m} {f}'
        uhp_values['rolloff'] = self._find_value_by_regex('rolloff: ', '[0-9]+', content)
        uhp_values['pilots'] = self._find_value_by_regex('pilots: ', '[a-z]+', content)
        uhp_values['rate_bps'] = self._find_value_by_regex('rate/bps: ', '[0-9]+', content)
        uhp_values['load'] = self._find_value_by_regex('load\(%\): ', '[0-9]+', content, num_esc_char=2)
        uhp_values['shaper_drops'] = self._find_value_by_regex('shaper_drops: ', '[0-9]+', content)

        # Modulator queues stats depends on UHP profile and TDM ACM
        _key = ''  # for TDM with no ACM queues' stats starts with 'p', with ACM with 'ch' number,
        # for TDMA with 'to_hub' or 'to_stn'
        for line in content.split('\n'):
            if line.startswith('to hub:'):  # TDMA mode
                _key = 'to_hub_'
                uhp_values['to_hub_modcod'] = self._find_value_by_regex('to hub: ', '[a-z]+ [0-9]+/[0-9]+', line)

            elif line.startswith('to stations:'):  # TDMA mode
                _key = 'to_stn_'
                uhp_values['to_stations_modcod'] = self._find_value_by_regex('to stations: ', '[a-z]+ [0-9]+/[0-9]+', line)

            elif self._find_value_by_regex('ch[0-9]+', '', line) is not None:  # TDM ACM mode
                _key = f'{line[:3]}_'
                uhp_values[f'{_key}modcod'] = self._find_value_by_regex(line[:4], '[a-z]+ [0-9]*[a-z]+ [0-9]+/[0-9]+', line)
                uhp_values[f'{_key}br'] = self._find_value_by_regex('br: ', '[0-9]+', line)
                # Getting number of frames for a given channel
                p = re.compile('[0-9]+ frames')
                m = p.search(line)
                if m is not None:
                    uhp_values[f'{_key}frames'] = m.group().split()[0]
            elif line.startswith('p') or line.startswith('ctrl'):
                uhp_values[f'{_key}{line[:4].strip()}_packets'] = self._find_value_by_regex('packets: ', '[0-9]+', line)
                uhp_values[f'{_key}{line[:4].strip()}_bytes'] = self._find_value_by_regex('bytes: ', '[0-9]+', line)
                qlen = self._find_value_by_regex('q_len/', '[0-9]+[\s]+: [0-9]+', line)  # i.e. '3000 : 0'
                if qlen is not None:
                    uhp_values[f'{_key}{line[:4].strip()}_qlen'] = qlen.split(':')[-1].strip()
                uhp_values[f'{_key}{line[:4].strip()}_drops'] = self._find_value_by_regex('drops: ', '[0-9]+', line)

        return uhp_values

    def get_overview(self) -> Union[Dict, None]:
        # TODO: grab the rest data, such as TDM channels, IP protocols
        """
        Get data from Overview page

        :returns dict: a dictionary containing data from the page
        """
        uhp_values = {}
        res = self.get_request(f'http://{self._router_address}/ss40')
        if not res:
            return None
        soup = BeautifulSoup(res.content, 'lxml')
        tables = soup.find_all('table')
        for table in tables:
            trs = table.find_all('tr')
            for tr in trs:
                tds = [td.text for td in tr]
                if len(tds) == 4 and tds[0] == 'Refresh':
                    uhp_values['sn'] = self._find_value_by_regex('SN: ', '[0-9]+', tds[1])
                    uhp_values['sw'] = self._find_value_by_regex('SW: ', '.+', tds[2])
                    uhp_values['ver'] = self._find_value_by_regex('Ver: ', '.+', tds[3])
                elif len(tds) == 4 and tds[0].startswith('CPU'):
                    uhp_values['cpu_load'] = self._find_value_by_regex('CPU load: ', '[0-9]+', tds[0])
                    uhp_values['buffers'] = self._find_value_by_regex('Buffers: ', '[0-9]+', tds[1])
                    uhp_values['temp'] = self._find_value_by_regex('Temp: ', '[0-9]+', tds[2])
                    _profile = self._find_value_by_regex('Profile: ', '.+', tds[3])
                    if _profile is not None:
                        uhp_values['profile'] = ' '.join(_profile.split())
                # Interfaces table
                elif len(tds) == 6 and tds[0] in ('Ethernet', 'Demodulator-2', 'Demodulator-1', 'Modulator', 'Network'):
                    uhp_values[tds[0].lower()] = {}
                    uhp_values[tds[0].lower()]['state'] = tds[1]
                    uhp_values[tds[0].lower()]['info'] = tds[2]
                    uhp_values[tds[0].lower()]['tx_rate'] = tds[3]
                    uhp_values[tds[0].lower()]['rx_rate'] = tds[4]
                    uhp_values[tds[0].lower()]['rx_errors'] = self._find_value_by_regex('', '[\d-]+', tds[5])
                elif len(tds) == 6 and tds[0] in ('Enabled', 'Online', 'Active', 'Hub CN Low/High', 'Rem CN Low/High'):
                    if uhp_values.get('stations') is None:
                        uhp_values['stations'] = {}
                    uhp_values['stations']['_'.join(tds[0].lower().split(' '))] = tds[1]
                    uhp_values['stations']['_'.join(tds[2].lower().split(' '))] = tds[3]
                    uhp_values['stations']['_'.join(tds[4].lower().split(' '))] = \
                        self._find_value_by_regex('', '[-]*[\s]*[\d]+[\.]*[\d]*[\s]*[dBm|us]*', tds[5])
                elif len(tds) == 10 and tds[0] == 'Number':  # UHP in station mode
                    uhp_values['number'] = tds[1]
                    uhp_values['fp_lost'] = tds[3]
                    uhp_values['dtts_cor'] = tds[5]
                    uhp_values['frq_cor'] = tds[7]
                    uhp_values['lvl_cor'] = self._find_value_by_regex('', '[0-9]+[\.]*[0-9]* dBm', tds[9])
                elif len(tds) == 10 and tds[0] == 'Cur BW':  # UHP in station mode
                    uhp_values['cur_bw'] = tds[1]
                    uhp_values['sum_rq'] = tds[3]
                    uhp_values['rt_rq'] = tds[5]
                    uhp_values['codecs'] = tds[7]
                    uhp_values['timeout'] = tds[9]
                elif len(tds) == 4 and tds[0] == 'NMS mode':
                    uhp_values['nms'] = {}
                    uhp_values['nms']['nms_ip'] = self._find_value_by_regex('NMSIP: ', '\d+\.\d+.\d+\.\d+', tds[1])
                    uhp_values['nms']['packets_in'] = self._find_value_by_regex('Packets in: ', '\d+', tds[2])
                    uhp_values['nms']['password_errors'] = self._find_value_by_regex('Passwd errors: ', '\d+', tds[3])
        return uhp_values

    @staticmethod
    def _find_value_by_regex(first_part: str, value: str, string: str, num_esc_char=0) -> Union[str, None]:
        """
        Find a value in the passed string based on the regex: first_part + value
        Example:
            _find_value_by_regex('foo is ', '[a-z]', 'foo is bar') will return 'bar'

        :param str first_part: first part of the substring to match
        :param str value: second part of the substring to match
        :param str string: the string to find the pattern in
        :param int num_esc_char: the number of escape characters passed in the first_part
        :returns Union[str, None]: value if match found, otherwise None
        """
        p = re.compile(first_part + value)
        m = p.search(string)
        if m is not None:
            return m.group()[len(first_part) - num_esc_char:]
        else:
            return None

    def get_stlc_nms_red_form(self) -> Union[Dict, None]:
        """
        Get data from SCPC TLC, NMS, Redundancy page. The following parameters are obtained:
            'vlan', 'password', 'scpc_tlc_enable', 'scpc_tlc_peer_ip', 'monitoring', 'control', 'allow_local_config',
            'red_enable', 'red_remote_ip', 'red_local_ip', 'red_fault_timeout', 'red_link_timeout',
            'red_ser_monitor'

        :returns: Union[Dict, None]
        """
        uhp_values = {}
        res = self.get_request(f'http://{self._router_address}/cc14')
        if not res:
            return None
        soup = BeautifulSoup(res.content, 'html.parser')
        text_inputs = soup.find_all('input', {'type': 'text'})
        for tag in text_inputs:
            name, value = tag.get('name'), tag.get('value')
            if name is None or value is None:
                continue
            elif scpc_tlc_red_mapping.get(name) is not None:
                uhp_values[scpc_tlc_red_mapping.get(name)] = value
        checkbox_inputs = soup.find_all('input', {'type': 'checkbox'})
        for tag in checkbox_inputs:
            name, value, checked = tag.get('name'), tag.get('value'), tag.get('checked')
            if name is None or value is None:
                continue
            elif scpc_tlc_red_mapping.get(name) is not None:
                if checked is not None:
                    uhp_values[scpc_tlc_red_mapping.get(name)] = 1
                else:
                    uhp_values[scpc_tlc_red_mapping.get(name)] = 0
        return uhp_values
