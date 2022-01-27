import os
import re
import subprocess
import time
from importlib import import_module
from time import sleep

from src.custom_test_case import CustomTestCase
from src.drivers.snmp.snmp_executor import SnmpExecutor
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.exceptions import InvalidOptionsException, UhpResponseException, ObjectNotFoundException, \
    NotImplementedException
from src.options_providers.options_provider import OptionsProvider
from utilities import mib_convertor

options_path = 'test_scenarios.clients.subtests.rikei'


# TODO: instead of configuring UHP for each test, upload a dedicated config
# TODO: For some tests it is necessary to have a valid hubless network: a master and a station
class RikeiSnmpSyntaxCase(CustomTestCase):
    """Rikei SNMP requests syntax confirmation case"""

    uhp_telnet_driver = None
    uhp_telnet_driver2 = None

    @classmethod
    def set_up_class(cls):
        cls.addClassCleanup(cls.clean)
        cls.options = OptionsProvider.get_options(options_path)
        cls.uhp_ip_address = cls.options.get('ip_address', None)
        cls.uhp_ip_address2 = cls.options.get('ip_address2', None)
        if cls.uhp_ip_address is None or cls.uhp_ip_address2 is None:
            raise InvalidOptionsException('UHP IP-addresses are not provided in the options')
        cls.uhp_telnet_driver = UhpTelnetDriver(cls.uhp_ip_address)
        cls.uhp_telnet_driver2 = UhpTelnetDriver(cls.uhp_ip_address2)
        cls.uhp_telnet_driver.get_raw_result('rf lo 0 0 0')
        cls.uhp_telnet_driver2.get_raw_result('rf lo 0 0 0')
        cls.uhp_driver = UhpRequestsDriver(cls.uhp_ip_address)
        cls.uhp_driver2 = UhpRequestsDriver(cls.uhp_ip_address2)
        cls.uhp_software_version = cls.uhp_driver.get_software_version()
        cls.uhp_software_version2 = cls.uhp_driver2.get_software_version()
        cls.uhp_serial_number = cls.uhp_driver.get_serial_number()
        cls.uhp_serial_number2 = cls.uhp_driver2.get_serial_number()
        cls.uhp_driver.add_station(number=1, sn=cls.uhp_serial_number)
        cls.uhp_driver.add_station(number=2, sn=cls.uhp_serial_number2)
        if cls.class_logger is not None:
            cls.class_logger.info(f'UHP1 {cls.uhp_ip_address} SW: {cls.uhp_software_version};'
                            f' UHP2 {cls.uhp_ip_address2} SW: {cls.uhp_software_version2}')
        # Make sure that UHPs are not under NMS control
        if not cls.uhp_driver.set_nms_permission(control=False, monitoring=False):
            raise UhpResponseException('Cannot set UHP1 NMS permissions')
        if not cls.uhp_driver.set_snmp(cls.options.get('snmp', None)):
            raise UhpResponseException('Cannot set UHP1 SNMP settings')
        if not cls.uhp_driver2.set_nms_permission(control=False, monitoring=False):
            raise UhpResponseException('Cannot set UHP2 NMS permissions')
        if not cls.uhp_driver2.set_snmp(cls.options.get('snmp', None)):
            raise UhpResponseException('Cannot set UHP2 SNMP settings')
        cls.snmp_read = cls.options.get('snmp', {}).get('snmp_read', 'public')
        cls.snmp_write = cls.options.get('snmp', {}).get('snmp_write', 'private')
        cls.oid_executor = SnmpExecutor()

    def test_get_set_profile(self):
        """1. OID: .1.3.6.1.4.1.8000.22.1.5.0 can be used to GET current profile number and SET profile"""
        # Check active profile in Master, Station, and SCPC modes

        for mode in ('master', 'slave', 'scpc'):
            # Setting UHP2 profile 8 to one of the tested modes
            self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual {mode}')
            self.uhp_telnet_driver.get_raw_result(f'profile 8 timeout 250')
            self.uhp_telnet_driver.get_raw_result(f'profile 8 run')
            if not self.uhp_driver.wait_active_profile():
                raise UhpResponseException(f'Active profile is not set to 8')
            current_profile = self.oid_executor.get(
                self.uhp_ip_address,
                161,
                self.snmp_read,
                '.1.3.6.1.4.1.8000.22.1.5.0',
            )
            with self.subTest(f'GET profile in {mode}'):
                self.assertIn(self.uhp_driver.get_current_profile_number(), (current_profile, str(current_profile)))
            # Setting profile 7 via SNMP
            self.uhp_telnet_driver.get_raw_result(f'profile 7 type manual {mode}')
            self.uhp_telnet_driver.get_raw_result(f'profile 7 timeout 250')
            self.uhp_telnet_driver.get_raw_result(f'profile 7 autorun on')
            self.oid_executor.set(
                self.uhp_ip_address,
                161,
                self.snmp_write,
                '.1.3.6.1.4.1.8000.22.1.5.0',
                7,
            )
            with self.subTest(f'SET profile in {mode}'):
                self.assertIn(self.uhp_driver.get_current_profile_number(), (7, '7'))

    def test_get_alarm_codes(self):
        """2. OID: .1.3.6.1.4.1.8000.22.5.3.3 alarms"""
        # Converting MIB to py file
        self.load_mib()
        output_name = f'uhp_mib_{self.uhp_software_version[:3].replace(".", "_")}.py'
        mib = import_module(output_name.replace('.py', ''))
        alarms = mib.MIB.get('nodes').get('serverFaults')
        # Checking that the expected OID is in the file
        self.assertEqual(alarms.get('oid'), '1.3.6.1.4.1.8000.22.5.3.3')
        expected_alarm_codes = self.options.get('expected_alarm_codes')
        description = alarms.get('description')
        mib_alarm_codes = {}
        for line in description.split('\n'):
            if line.startswith('0x'):
                mib_alarm_codes[line[:6].strip()] = line[8:].strip(';')
        for alarm_key, alarm_desc in expected_alarm_codes.items():
            with self.subTest(alarm_key):
                self.assertIn(alarm_key, mib_alarm_codes.keys())
                self.assertEqual(alarm_desc, mib_alarm_codes.get(alarm_key))
        # Testing CRC BD errors
        self.uhp_telnet_driver.get_raw_result(f'ge 4299 1/0')
        for mode in ('master', 'scpc'):
            self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual {mode}')
            self.uhp_telnet_driver.get_raw_result(f'profile 8 timeout 250')
            self.uhp_telnet_driver.get_raw_result(f'profile 8 mod on 200')
            self.uhp_telnet_driver.get_raw_result(f'profile 8 run')
            time.sleep(3)
            alarm = self.oid_executor.get(
                self.uhp_ip_address,
                161,
                self.snmp_read,
                '.1.3.6.1.4.1.8000.22.5.3.3',
            )
            with self.subTest(f'{mode} CRC BD alarm'):
                self.assertEqual('4096', alarm)
        # Removing test CRC BD errors
        self.uhp_telnet_driver.get_raw_result(f'ge 4299')

    def test_get_netState_codes(self):
        """3. OID: .1.3.6.1.4.1.8000.22.5.2.1 MASTER status (Judgment of receive lock state)"""
        # `netState`. Checks that MIB file for the corresponding UHP version contains
        # expected `netState` codes.

        self.load_mib()
        output_name = f'uhp_mib_{self.uhp_software_version[:3].replace(".", "_")}.py'
        mib = import_module(output_name.replace('.py', ''))
        net_state = mib.MIB.get('nodes').get('netState')
        # Checking that the expected OID is in the file
        with self.subTest('OID number'):
            self.assertEqual(net_state.get('oid'), '1.3.6.1.4.1.8000.22.5.2.1')
        expected_state_codes = self.options.get('expected_state_codes')
        for key, value in expected_state_codes.items():
            if value in net_state.get('syntax').get('type').keys():
                with self.subTest(value):
                    self.assertEqual(key, net_state.get('syntax').get('type').get(value).get('number'))
            else:
                with self.subTest(value):
                    raise ObjectNotFoundException(f'Cannot find {value} in MIB')

    def test_get_cn_value(self):
        """4. 5. 6. OID: .1.3.6.1.4.1.8000.22.9.4.0 and .1.3.6.1.4.1.8000.22.9.6.0 Receive (C/N value) Carrier ON/OFF"""
        for mode in ('scpc', 'master', 'slave', ):
            print(mode)
            if mode == 'slave':
                self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual master')
                self.uhp_telnet_driver.get_raw_result(f'profile 8 modulator on 200')
                self.uhp_telnet_driver.get_raw_result(f'profile 8 timeout 250')
                self.uhp_telnet_driver.get_raw_result(f'profile 8 autorun on')
                self.uhp_telnet_driver.get_raw_result(f'profile 8 run')

                self.uhp_telnet_driver2.get_raw_result(f'profile 8 type manual {mode}')
                self.uhp_telnet_driver2.get_raw_result(f'profile 8 modulator on 200')
                self.uhp_telnet_driver2.get_raw_result(f'profile 8 timeout 250')
                self.uhp_telnet_driver2.get_raw_result(f'profile 8 autorun on')
                self.uhp_telnet_driver2.get_raw_result(f'profile 8 run')
                self.uhp_driver.set_cotm_amip({'tx_control': 1})
                if not self.uhp_driver2.wait_active_profile():
                    raise UhpResponseException(f'Active profile is not set to 8')
            else:
                self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual {mode}')
                self.uhp_telnet_driver.get_raw_result(f'profile 8 modulator on 200')
                self.uhp_telnet_driver.get_raw_result(f'profile 8 timeout 250')
                self.uhp_telnet_driver.get_raw_result(f'profile 8 autorun on')
                self.uhp_telnet_driver.get_raw_result(f'profile 8 run')
                self.uhp_driver.set_cotm_amip({'tx_control': 1})

            if not self.uhp_driver.wait_active_profile():
                raise UhpResponseException(f'Active profile is not set to 8')

            if mode == 'slave':
                ip_address = self.uhp_ip_address2
            else:
                ip_address = self.uhp_ip_address

            set_tx_control_off = self.oid_executor.set(
                ip_address,
                161,
                self.snmp_write,
                '.1.3.6.1.4.1.8000.22.9.6.0',
                0,
                value_type='gauge32',
            )
            if set_tx_control_off is None:
                raise UhpResponseException(f'Cannot set UHP txControl off')
            time.sleep(3)
            print('txControl off')

            snmp_cn = self.oid_executor.get(
                ip_address,
                161,
                self.snmp_read,
                '.1.3.6.1.4.1.8000.22.9.4.0',
            )
            time.sleep(3)

            with self.subTest(f'mode={mode} txControl off'):
                self.assertIn(snmp_cn, (2, '2'))

            set_tx_control_on = self.oid_executor.set(
                ip_address,
                161,
                self.snmp_write,
                '.1.3.6.1.4.1.8000.22.9.6.0',
                1,
                value_type='gauge32',
            )
            if set_tx_control_on is None:
                raise UhpResponseException(f'Cannot set UHP txControl on')
            time.sleep(3)
            print('txControl on')

            if not self.uhp_driver.wait_operation_state(timeout=120):
                raise UhpResponseException(f'UHP in {mode} mode is not in operation state')

            time.sleep(3)
            if mode == 'master':
                uhp_cn = self.uhp_driver.get_stations_state().get('1').get('strx')
            elif mode == 'slave':
                if not self.uhp_driver2.wait_operation_state():
                    raise UhpResponseException(f'UHP in {mode} mode is not in operation state')
                uhp_cn = self.uhp_driver.get_stations_state().get('2').get('strx')
            else:
                uhp_cn = self.uhp_driver.get_demodulator_statistics().get('cn')

            snmp_cn = self.oid_executor.get(
                ip_address,
                161,
                self.snmp_read,
                '.1.3.6.1.4.1.8000.22.9.4.0',
            )

            with self.subTest(f'mode={mode} txControl on'):
                self.assertAlmostEqual(int(snmp_cn) / 10, float(uhp_cn), delta=0.9)
            self.uhp_driver.set_cotm_amip()
            self.uhp_driver2.set_cotm_amip()

    def test_set_carrier_on_off(self):
        """5. OID: .1.3.6.1.4.1.8000.22.9.6.0 can be used to SET carrier ON/OFF mode in Master, Station, SCPC modes"""
        self.uhp_driver.set_cotm_amip({'tx_control': 1})
        for mode in ('master', 'scpc'):
            # Setting UHP profile 8 to one of the tested modes
            self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual {mode}')
            self.uhp_telnet_driver.get_raw_result(f'profile 8 timeout 250')
            self.uhp_telnet_driver.get_raw_result(f'profile 8 run')
            if not self.uhp_driver.wait_active_profile():
                raise UhpResponseException(f'Active profile is not set to 8')
            current_tx_mode = self.uhp_driver.get_modulator_form(profile_number=8)
            if current_tx_mode.get('tx_on') == '1':
                self.uhp_driver.set_profile_modulator(profile_number=8, params={'tx_on': '0'})
                self.assertEqual('0', self.uhp_driver.get_modulator_form(profile_number=8).get('tx_on'))
            self.oid_executor.set(
                self.uhp_ip_address,
                161,
                self.snmp_write,
                '.1.3.6.1.4.1.8000.22.9.6.0',
                1,
                value_type='gauge32'
            )
            with self.subTest(f'{mode} Setting TX ON'):
                self.assertEqual('1', self.uhp_driver.get_modulator_form(profile_number=8).get('tx_on'))
            self.oid_executor.set(
                self.uhp_ip_address,
                161,
                self.snmp_write,
                '.1.3.6.1.4.1.8000.22.9.6.0',
                0,
                value_type='gauge32'
            )
            with self.subTest(f'{mode} Setting TX OFF'):
                self.assertEqual('0', self.uhp_driver.get_modulator_form(profile_number=8).get('tx_on'))
        self.uhp_driver.set_cotm_amip()

    def test_get_carrier_on(self):
        """6. OID:.1.3.6.1.4.1.8000.22.9.6.0 Carrier ON - can be used to GET carrier ON mode in Master, Station, SCPC"""
        # Note: in hubless station mode to get the correct results when carrier is on it is necessary to get
        # reception from the hub.
        self.uhp_driver.set_cotm_amip({'tx_control': 1})
        for mode in ('master', 'scpc'):
            # Setting UHP2 profile 8 to one of the tested modes
            self.uhp_telnet_driver2.get_raw_result(f'profile 8 type manual {mode}')
            self.uhp_telnet_driver2.get_raw_result(f'profile 8 run')
            if not self.uhp_driver2.wait_active_profile(profile_number=8):
                raise UhpResponseException('Active profile is not set to 8')
            if mode == 'master' and self.uhp_driver2.get_active_profile_name().lower() != 'hubless master':
                raise UhpResponseException(f'Current active profile is not set to Hubless master')
            elif mode == 'scpc' and self.uhp_driver2.get_active_profile_name().lower() != 'scpc modem':
                raise UhpResponseException(f'Current active profile is not set to SCPC modem')
            current_tx_mode = self.uhp_driver2.get_modulator_form(profile_number=8)
            if current_tx_mode.get('tx_on') == '0':
                self.uhp_driver2.set_profile_modulator(profile_number=8, params={'tx_on': '1'})
                # Confirms that TX ON is applied to modulator
                self.assertEqual('1', self.uhp_driver2.get_modulator_form(profile_number=8).get('tx_on'))
            time.sleep(1)
            snmp_tx_mode = self.oid_executor.get(
                self.uhp_ip_address2,
                161,
                self.snmp_read,
                '.1.3.6.1.4.1.8000.22.9.6.0',
            )
            with self.subTest(mode):
                self.assertEqual('1', snmp_tx_mode)
        # Preparing hubless config. Hubless station must be in operation mode to get correct TX ON status
        # Setting profile 8 to one of the tested modes
        # TODO: replace telnet with web driver for performance
        self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual master')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 hubless tdma 100 10 2')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 hubless rf 1000000 1000000 1000 1')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 modulator on 200')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 timeout 250')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 run')
        self.uhp_telnet_driver2.get_raw_result(f'profile 8 type manual slave')
        self.uhp_telnet_driver2.get_raw_result(f'profile 8 hubless tdma 100 10 2')
        self.uhp_telnet_driver2.get_raw_result(f'profile 8 hubless rf 1000000 1000000 1000 1')
        self.uhp_telnet_driver2.get_raw_result(f'profile 8 modulator on 200')
        self.uhp_telnet_driver2.get_raw_result(f'profile 8 timeout 250')
        self.uhp_telnet_driver2.get_raw_result(f'profile 8 run')
        if not self.uhp_driver.wait_active_profile(profile_number=8):
            raise UhpResponseException(f'UHP1 active profile is not set to 8')
        if not self.uhp_driver2.wait_active_profile(profile_number=8):
            raise UhpResponseException(f'UHP2 active profile is not set to 8')
        if mode == 'master' and self.uhp_driver.get_active_profile_name().lower() != 'hubless master':
            raise UhpResponseException(f'UHP1 current active profile is not set to Hubless master')
        elif mode == 'slave' and self.uhp_driver2.get_active_profile_name().lower() != 'hubless station':
            raise UhpResponseException(f'UHP2 current active profile is not set to hubless station')
        if not self.uhp_driver2.wait_operation_state():
            raise UhpResponseException(f'UHP hubless station not in operation mode')
        snmp_tx_mode = self.oid_executor.get(
            self.uhp_ip_address2,
            161,
            self.snmp_read,
            '.1.3.6.1.4.1.8000.22.9.6.0',
        )
        with self.subTest('station'):
            self.assertEqual('1', snmp_tx_mode)

    def test_get_carrier_off(self):
        """7. OID: .1.3.6.1.4.1.8000.22.9.4.0 Carrier OFF can be used to GET TX status in SCPC, Hubless, and station"""

        for mode in ('master', 'slave', 'scpc'):
            self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual {mode}')
            self.uhp_telnet_driver.get_raw_result(f'profile 8 timeout 250')
            self.uhp_telnet_driver.get_raw_result(f'profile 8 run')
            if not self.uhp_driver.wait_active_profile(profile_number=8):
                raise UhpResponseException(f'Active profile is not set to 8')
            self.uhp_driver.set_cotm_amip({'tx_control': 1})
            carrier = self.oid_executor.get(
                self.uhp_ip_address,
                161,
                self.snmp_read,
                '.1.3.6.1.4.1.8000.22.9.4.0',
            )
            with self.subTest(mode):
                self.assertEqual('2', carrier)
        # Turning off COTM/AMIP tx_control off
        self.uhp_driver.set_cotm_amip()

    def test_set_command_stn_location(self):
        """8. OID: .1.3.6.1.4.1.8000.22.1.3.0 Location information of station - can be used to set station location"""
        # Type: OctetString can be used to
        # set `station location [La-deg] [La-min] [La-dir] [Lo-deg] [Lo-min] [Lo-dir]` in station mode

        lat_deg = '13'
        lat_min = '59'
        lat_dir = 'south'
        lon_deg = '17'
        lon_min = '58'
        lon_dir = 'west'
        # Setting profile 8 to Hubless station mode valid and running it
        self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual slave')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 timeout 250')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 run')
        if not self.uhp_driver.wait_active_profile(profile_number=8):
            raise UhpResponseException(f'Active profile is not set to 8')
        if self.uhp_driver.get_active_profile_name().lower() != 'hubless station':
            raise UhpResponseException(f'Current active profile is not set to hubless station')
        self.oid_executor.set(
            self.uhp_ip_address,
            161,
            self.snmp_write,
            '.1.3.6.1.4.1.8000.22.1.3.0',
            f'station location {lat_deg} {lat_min} {lat_dir} {lon_deg} {lon_min} {lon_dir}'
        )
        uhp_values = self.uhp_driver.get_teleport_values()
        self.assertEqual(lat_deg, uhp_values.get('lat_deg', None))
        self.assertEqual(lat_min, uhp_values.get('lat_min', None))
        self.assertEqual(lat_dir.capitalize(), uhp_values.get('lat_south', None))
        self.assertEqual(lon_deg, uhp_values.get('lon_deg', None))
        self.assertEqual(lon_min, uhp_values.get('lon_min', None))
        self.assertEqual(lon_dir.capitalize(), uhp_values.get('lon_west', None))
        # Make sure that the profile is stayed the same
        time.sleep(10)
        # TODO: probably remove as issuing station location command leads to another autorun profile to run
        self.assertEqual('8', self.uhp_driver.get_current_profile_number())

    def test_set_command_autorun(self):
        """9. OID: .1.3.6.1.4.1.8000.22.1.3.0 Autorun - can be used to set Autorun OFF|ON"""
        # Type: OctetString can be used to
        # set `profile [1-8] autorun [on|off]` in MASTER, STATION, and SCPC modes.

        for mode in ('master', 'slave', 'scpc'):
            # Setting profile 8 to one of the tested modes
            self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual {mode}')
            self.uhp_telnet_driver.get_raw_result(f'profile 8 autorun on')
            self.uhp_telnet_driver.get_raw_result(f'profile 8 timeout 250')
            self.uhp_telnet_driver.get_raw_result(f'profile 8 run')
            if not self.uhp_driver.wait_active_profile(profile_number=8):
                raise UhpResponseException(f'Active profile is not set to 8')
            current_autorun_mode = self.uhp_driver.get_basic_form(profile_number=8).get('autorun', None)
            if current_autorun_mode not in ('0', '1'):
                raise UhpResponseException('Cannot get UHP profile 8 autorun status')
            if current_autorun_mode == '0':
                self.oid_executor.set(
                    self.uhp_ip_address,
                    161,
                    self.snmp_write,
                    '.1.3.6.1.4.1.8000.22.1.3.0',
                    f'profile 8 autorun on'
                )
                sleep(1)
                set_autorun_mode = self.uhp_driver.get_basic_form(profile_number=8).get('autorun', None)
                if current_autorun_mode not in ('0', '1'):
                    raise UhpResponseException('Cannot get UHP profile 8 autorun status')
                self.assertEqual('1', set_autorun_mode)
            # probably not needed as after setting `profile 8 type manual [mode]` autorun is off
            else:
                self.oid_executor.set(
                    self.uhp_ip_address,
                    161,
                    self.snmp_write,
                    '.1.3.6.1.4.1.8000.22.1.3.0',
                    f'profile 8 autorun off'
                )
                sleep(1)
                set_autorun_mode = self.uhp_driver.get_basic_form(profile_number=8).get('autorun', None)
                if current_autorun_mode is None:
                    raise UhpResponseException('Cannot get UHP profile 8 autorun status')
                self.assertEqual('0', set_autorun_mode)
            # Make sure that the profile is stayed the same
            self.assertEqual('8', self.uhp_driver.get_current_profile_number())

    def test_set_command_rx_settings(self):
        """10. OID: .1.3.6.1.4.1.8000.22.1.3.0 Rx Setting - can be used to set RX FREQ SYMRATE in SCPC mode"""
        # Type: OctetString can be used to
        # set `profile [1-8] rx [950000-32000000] [300-65000]` -
        # Rx FREQ SYMRATE(64000(200X)/64995(200)) in SCPC mode

        freq = '1020304'
        symrate = '3166'
        # Setting profile 8 to SCPC mode valid and running it
        self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual scpc')
        # Have to set autorun as long as `profile 8 rx ...` causes next autorun profile to run
        self.uhp_telnet_driver.get_raw_result(f'profile 8 autorun on')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 timeout 250')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 run')
        if not self.uhp_driver.wait_active_profile(profile_number=8):
            raise UhpResponseException(f'Active profile is not set to 8')
        self.oid_executor.set(
            self.uhp_ip_address,
            161,
            self.snmp_write,
            '.1.3.6.1.4.1.8000.22.1.3.0',
            f'profile 8 rx {freq} {symrate}'
        )
        uhp_values = self.uhp_driver.get_demodulator_form(profile_number=8)
        self.assertEqual(freq, uhp_values.get('rx1_frq', None))
        self.assertEqual(symrate, uhp_values.get('rx1_sr', None))
        # Make sure that the profile is stayed the same
        self.assertEqual('8', self.uhp_driver.get_current_profile_number())

    def test_set_command_tx_settings(self):
        """11. OID: .1.3.6.1.4.1.8000.22.1.3.0 Tx Setting - can be used to set TX FREQ SYMRATE MODCOD"""
        # Type: OctetString
        # set `profile [1-8] tx [950000-32000000] [300-65000] [1-128]` -
        # Tx FREQ SYMRATE(64000(200X)/64995(200)) MODCOD(1-127(200X)/2-28(200)) in SCPC mode

        freq = '1111111'
        symrate = '6332'
        modcod = '7'
        # Setting profile 8 to SCPC mode valid and running it
        self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual scpc')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 timeout 250')
        # Have to set autorun as long as `profile 8 tx ...` causes next autorun profile to run
        self.uhp_telnet_driver.get_raw_result(f'profile 8 autorun on')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 run')
        if not self.uhp_driver.wait_active_profile(profile_number=8):
            raise UhpResponseException(f'Active profile is not set to 8')
        self.oid_executor.set(
            self.uhp_ip_address,
            161,
            self.snmp_write,
            '.1.3.6.1.4.1.8000.22.1.3.0',
            f'profile 8 tx {freq} {symrate} {modcod}'
        )
        uhp_values = self.uhp_driver.get_tdm_tx_form(profile_number=8)
        self.assertEqual(freq, uhp_values.get('tx_freq', None))
        self.assertEqual(symrate, uhp_values.get('tx_sr', None))
        self.assertEqual('sf qpsk 3/4', uhp_values.get('tx_modcod', None))
        # Make sure that the profile is stayed the same
        self.assertEqual('8', self.uhp_driver.get_current_profile_number())

    def test_set_command_mod_on_off(self):
        """12. OID: .1.3.6.1.4.1.8000.22.1.3.0 Carrier ON/OFF - can be used to set `modulator tx [off|on]` in SCPC"""
        # Setting profile 8 to SCPC mode valid and running it
        self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual scpc')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 timeout 250')
        # Have to set autorun as long as `modulator tx off/on` causes next autorun profile to run
        self.uhp_telnet_driver.get_raw_result(f'profile 8 autorun on')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 run')
        if not self.uhp_driver.wait_active_profile(profile_number=8):
            raise UhpResponseException(f'Active profile is not set to 8')
        mod_tx_status = self.uhp_driver.get_support_info_value(regex=re.compile(r'tx:\s[a-z]+'))
        if mod_tx_status is None or mod_tx_status not in ('on', 'off'):
            raise UhpResponseException('Cannot get UHP modulator status')
        elif mod_tx_status == 'on':
            self.oid_executor.set(
                self.uhp_ip_address,
                161,
                self.snmp_write,
                '.1.3.6.1.4.1.8000.22.1.3.0',
                'modulator tx off'
            )
            sleep(1)
            new_tx_status = self.uhp_driver.get_support_info_value(regex=re.compile(r'tx:\s[a-z]+'))
            self.assertEqual(new_tx_status, 'off')
        else:
            self.oid_executor.set(
                self.uhp_ip_address,
                161,
                self.snmp_write,
                '.1.3.6.1.4.1.8000.22.1.3.0',
                'modulator tx on'
            )
            sleep(1)
            new_tx_status = self.uhp_driver.get_support_info_value(regex=re.compile(r'tx:\s[a-z]+'))
            self.assertEqual(new_tx_status, 'on')

    def load_mib(self):
        if self.uhp_software_version.startswith('3.5'):
            if not os.path.isfile(f'{os.path.dirname(mib_convertor.__file__)}{os.sep}uhp3.5-RE.mib'):
                input_name = 'uhp3.5.mib'
                self.info(f'Cannot find special uhp3.5-RE.mib file. Trying to locate the ordinary one...')
            else:
                input_name = 'uhp3.5-RE.mib'
        elif self.uhp_software_version.startswith('3.6'):
            if not os.path.isfile(f'{os.path.dirname(mib_convertor.__file__)}{os.sep}uhp3.6-RE.mib'):
                input_name = 'uhp3.6.mib'
                self.info(f'Cannot find special uhp3.6-RE.mib file. Trying to locate the ordinary one...')
            else:
                input_name = 'uhp3.6-RE.mib'
        elif self.uhp_software_version.startswith('3.7'):
            if not os.path.isfile(f'{os.path.dirname(mib_convertor.__file__)}{os.sep}uhp3.7-RE.mib'):
                input_name = 'uhp3.7.mib'
                self.info(f'Cannot find special uhp3.7-RE.mib file. Trying to locate the ordinary one...')
            else:
                input_name = 'uhp3.7-RE.mib'
        else:
            raise ObjectNotFoundException(f'There is no MIB files for the current UHP version'
                                       f'{self.uhp_software_version}')

        if not os.path.isfile(f'{os.path.dirname(mib_convertor.__file__)}{os.sep}{input_name}'):
            raise ObjectNotFoundException(f'Cannot locate MIB file for UHP version {self.uhp_software_version}')

        output_name = f'uhp_mib_{self.uhp_software_version[:3].replace(".", "_")}.py'
        # Dumping MIB file to a python file, trying find special JAP MIB build in the first place
        cmd = f'smidump -f python {os.path.dirname(mib_convertor.__file__)}{os.sep}{input_name}' \
              f' > {output_name}'
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)

    def tearDown(self) -> None:
        self.uhp_driver.set_cotm_amip()
        self.uhp_driver2.set_cotm_amip()

    @classmethod
    def clean(cls):
        if cls.uhp_telnet_driver is not None:
            cls.uhp_telnet_driver.get_raw_result('station location 0 0 north 0 0 east')
            cls.uhp_telnet_driver.close()
        if cls.uhp_telnet_driver2 is not None:
            cls.uhp_telnet_driver2.get_raw_result('station location 0 0 north 0 0 east')
            cls.uhp_telnet_driver2.close()



