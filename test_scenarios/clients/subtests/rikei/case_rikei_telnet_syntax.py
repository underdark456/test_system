from src.custom_test_case import CustomTestCase
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.exceptions import InvalidOptionsException, UhpResponseException
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.clients.subtests.rikei'


class RikeiTelnetSyntaxCase(CustomTestCase):
    """Rikei Telnet syntax confirmation case"""
    # The tests check the syntax of the output of several commands which the client wants to remain untouched.
    # WARNING: UHP Profile 8 will be overwritten during the tests.
    # No NMS is used for the test.

    uhp_telnet_driver = None

    @classmethod
    def set_up_class(cls):
        cls.options = OptionsProvider.get_options(options_path)
        cls.uhp_ip_address = cls.options.get('ip_address', None)
        if cls.uhp_ip_address is None:
            raise InvalidOptionsException('UHP IP-address is not provided in the options')
        cls.uhp_driver = UhpRequestsDriver(cls.uhp_ip_address)
        if not cls.uhp_driver.set_nms_permission(control=False, monitoring=False):
            raise UhpResponseException('Cannot set UHP NMS permissions')
        cls.uhp_telnet_driver = UhpTelnetDriver(cls.uhp_ip_address)
        cls.uhp_software_version = cls.uhp_telnet_driver.get_sw_version()
        if cls.class_logger is not None:
            cls.class_logger.info(f'UHP {cls.uhp_ip_address} SW: {cls.uhp_software_version}')

    def test_telnet_show_profiles(self):
        """1. `Autorun's current settings` - `show profiles` telnet command in MASTER/STATION/SCPC modes"""
        # Main task - make sure autorun OFF/ON starts at index 32 (33rd character to the left).
        #    - checks that `Valid` and `Autorun` are displayed in their respective positions;
        #    - checks that there is either OFF or ON in each profile line at index 26 (`Valid` mode);
        #    - checks that there is either OFF or ON in each profile line starting with index 32 ('Autorun` mode);
        #    - checks that there are exactly 8 profile lines.

        modes = ('master', 'scpc', 'slave')
        for mode in modes:
            # Changing Profile 8 mode to one of the tested
            self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual {mode}')
            self.uhp_telnet_driver.get_raw_result(f'profile 8 run')
            result_bytes = self.uhp_telnet_driver.get_raw_result('show profiles')
            result_list = result_bytes.decode().split('\n')
            profiles_checked = 0
            for line in result_list:
                if line.startswith('Num'):
                    # make sure that `Valid` and `Autorun` headings are in their places
                    self.assertEqual(24, line.find('Valid'))
                    self.assertEqual(30, line.find('Autorun'))
                elif not line[0].isdigit():
                    continue
                else:
                    # make sure that valid status is found in its place
                    self.assertEqual('O', line[25])
                    self.assertIn(line[26], ('N', 'F'))
                    self.assertIn(line[27], (' ', 'F'))
                    # make sure that `autorun` status is found in its place
                    self.assertEqual('O', line[32])
                    self.assertIn(line[33], ('N', 'F'))
                    self.assertIn(line[34], (' ', 'F'))
                    profiles_checked += 1
            # make sure that all the profiles are checked
            self.assertEqual(8, profiles_checked)

    def test_telnet_show_interface_demod(self):
        """2. `Rx Frequency, Symbol Rate current settings` - `show interface demod` telnet command in SCPC mode"""
        # Main task - make sure the RX frequency `Frq:` value starts at index 23 (24th character to the left), and
        # the RX symbol rate `SR:` value starts at index 37 (38th character to the left).

        # Setting profile 8 to SCPC mode valid and running it
        self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual scpc')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 run')
        result_bytes = self.uhp_telnet_driver.get_raw_result('show interface demod')
        result_list = result_bytes.decode().split('\n')
        for line in result_list:
            if line.find('Frq:') != -1 and line.find('SR:') != -1:
                with self.subTest('Frq: position'):
                    self.assertEqual(18, line.find('Frq:'))
                    self.assertEqual(' ', line[22])  # whitespace between `Frq:` and the value
                    self.assertTrue(line[23].isdigit())  # index of the first digit of the value
                with self.subTest('SR: position'):
                    self.assertEqual(33, line.find('SR:'))
                    self.assertEqual(' ', line[36])  # whitespace between `SR:` and the value
                    self.assertTrue(line[37].isdigit())  # index of the first digit of the value
                break
        else:
            self.assertTrue(False, 'Frq and SR found in the output')

    def test_telnet_show_interface_modulator(self):
        """3.`Tx Frequency, MOOD, Symbol rate※1 current setting` - `show int modulator` telnet command in SCPC mode."""
        # Main task - make sure the TX frequency `Freq:` value starts at index 6 exit(7th character to the left),
        # the TX symbol rate `SR:` value starts at index 33 (34th character to the left),
        # the TX bitrate `BR:` value starts at index 33 (34th character to the left),
        # and the MODCOD frame length value starts at index 22 (23rd character to the left).

        # Setting profile 8 to SCPC mode valid and running it
        self.uhp_telnet_driver.get_raw_result(f'profile 8 type manual scpc')
        self.uhp_telnet_driver.get_raw_result(f'profile 8 run')
        result_bytes = self.uhp_telnet_driver.get_raw_result('show interface modulator')
        result_list = result_bytes.decode().split('\n')
        checked_values = 0
        for line in result_list:
            if line.find('Freq:') != -1 and line.find('SR:') != -1:
                with self.subTest('Freq: position'):
                    self.assertEqual(0, line.find('Freq:'))
                    self.assertEqual(' ', line[5])  # whitespace between `Freq:` and the value
                    self.assertTrue(line[6].isdigit())  # index of the first digit of the value
                    checked_values += 1
                with self.subTest('SR: position'):
                    self.assertEqual(29, line.find('SR:'))
                    self.assertEqual(' ', line[32])  # whitespace between `Freq:` and the value
                    self.assertTrue(line[33].isdigit())  # index of the first digit of the value
                    checked_values += 1
            elif line.find('BR:') != -1:
                with self.subTest('BR: position'):
                    self.assertEqual(29, line.find('BR:'))
                    self.assertEqual(' ', line[32])  # whitespace between `BR:` and the value
                    self.assertTrue(line[33].isdigit())  # index of the first digit of the value
                    checked_values += 1
            elif line.find('MODCOD:') != -1:
                with self.subTest('MODCOD: position'):
                    self.assertEqual(14, line.find('MODCOD:'))
                    self.assertEqual(' ', line[21])  # whitespace between `MODCOD:` and the mode
                    self.assertIn(line[22], ('S', 'L'))  # first character of the mode
                    self.assertEqual(line[23], 'F')  # second character of the mode
                    checked_values += 1
        self.assertEqual(4, checked_values, 'All the values are checked')

    @classmethod
    def tear_down_class(cls) -> None:
        if cls.uhp_telnet_driver is not None:
            cls.uhp_telnet_driver.close()
