from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import TdmaModcodStr, TdmaModcod
from src.nms_entities.basic_entities.dashboard import Dashboard
from src.options_providers.options_provider import OptionsProvider

__author__ = 'dkudryashov'
__version__ = '0.1'
options_path = 'test_scenarios.tickets.subtests.7822'


# NMS is not used in the case
class TdmaBpskTelnetCase(CustomTestCase):
    """Ticket 7822. TDMA BPSK settings via telnet"""

    @classmethod
    def set_up_class(cls):
        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.uhp_ip_address = cls.system_options.get('uhp1_ip')
        cls.uhp_driver = UhpRequestsDriver(cls.uhp_ip_address)
        cls.uhp_software_version = cls.uhp_driver.get_software_version()
        cls.uhp_serial_number = cls.uhp_driver.get_serial_number()
        if cls.class_logger is not None:
            cls.class_logger.info(f'UHP under tests ip={cls.uhp_ip_address}  '
                                  f'SW={cls.uhp_software_version} serial={cls.uhp_serial_number}')
        cls.uhp_telnet = UhpTelnetDriver(cls.uhp_ip_address)
        cls.uhp_telnet.get_raw_result(f'profile 8 type manual master')

    def test_tdma_modcodes_telnet(self):
        """Check that all TDMA modcodes (including BPSK) can be set via telnet"""
        tdma_modcodes_str = [*TdmaModcodStr()]
        # Telnet tdma modcodes range 1-16, NMS and UHP modcodes range 0-15
        for i in range(1, 17):
            expected_modcod_str = tdma_modcodes_str[i - 1]
            self.uhp_telnet.get_raw_result(f'profile 8 hubless rf 1000000 1000000 1000 {i}')
            uhp_tdma_modcod = self.uhp_driver.get_tdma_rf_form(profile_number=8).get('tdma_mc')
            self.assertEqual(uhp_tdma_modcod.lower(), expected_modcod_str.lower())
