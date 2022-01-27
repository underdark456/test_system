from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.drivers.abstract_http_driver import API
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import *
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.options_providers.options_provider import OptionsProvider
from src.values_presenters import CHECK_BOX_TEST_VALUES, get_mixed_values_list, CHECK_BOX_VALID_VALUES, StrIntRange
from test_scenarios.form_validation.abstract_case import _AbstractCase
from test_scenarios.form_validation.utils.ip_protocol_values import test_values, valid_values

__version__ = '4.0.0.10'


@skip('There is a data types test. This one is not needed?')
class ControllerCase(_AbstractCase):
    """Not needed? Controller (MF hub) form validation case"""

    @classmethod
    def set_up_class(cls):
        options = OptionsProvider.get_options("test_scenarios.form_validation")
        options = OptionsProvider.get_options("test_scenarios.form_validation.subtests.controller", options=options)
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup('default_net_tel_ctrl.txt')
        cls.options = options
        cls._init_params(options)
        cls.ip_protocol = {
            'test_values': test_values,
            'valid_values': valid_values
        }
        cls._object = Controller(cls._driver, 0, 0)
        cls._object.set_param('mode', ControllerModes.MF_HUB)

    def test_alert_section(self):
        """Controller alert section validation"""
        self._validate_section('alert_settings')
        # TODO добавить проверку режима Specify

    def test_binding_section(self):
        """Controller binding section validation"""
        self._validate_section('device_binding')

    def test_device_a_section(self):
        """Controller device section validation"""
        self._validate_section('device_a')

    def test_teleport_and_rf_section(self):
        """Controller teleport and rf section validation"""
        self._validate_section('teleport_and_rf')

    def test_modulator_section(self):
        """Controller modulator section validation"""
        self._validate_section('modulator')

    def test_tlc_section(self):
        """Controller tlc section validation"""
        self._validate_section('tlc')

    def test_net_rf_id_section(self):
        """Controller RF feed section validation"""
        self._validate_section('net_rf_id')

    def test_tdma_section(self):
        """Controller TDMA section validation"""
        # TODO добавить проверку Roaming_slots
        self._validate_section('tdma')

    def test_tdma_channels_section(self):
        """Controller TDMA channels section validation"""
        for channel in range(1, 17):
            with self.subTest():
                self.test_values = {
                    F"mf{channel}_en": [*CHECK_BOX_TEST_VALUES, 1],
                    F"mf{channel}_tx": get_mixed_values_list(950000, 33000000),
                    F"mf{channel}_rx": get_mixed_values_list(950000, 33000000),
                }
                self.valid_values = {
                    F"mf{channel}_en": CHECK_BOX_VALID_VALUES,
                    F"mf{channel}_tx": StrIntRange(range(950000, 33000001)),
                    F"mf{channel}_rx": StrIntRange(range(950000, 33000001)),
                }
                super()._test_validate_fields()

    def test_ip_screening_section(self):
        """Controller ip screening section validation"""
        self.test_values = self.ip_protocol['test_values']['ip_screening']
        self.valid_values = self.ip_protocol['valid_values']['ip_screening']
        super()._test_validate_fields()

    def test_snmp_section(self):
        """Controller SNMP section validation"""
        self.test_values = self.ip_protocol['test_values']['snmp']
        self.valid_values = self.ip_protocol['valid_values']['snmp']
        super()._test_validate_fields()

    def test_dhcp_section(self):
        """Controller DHCP section validation"""
        self.test_values = {'dhcp_mode': DhcpModes()}
        self.valid_values = {'dhcp_mode': DhcpModes()}
        super()._test_validate_fields()

        self._object.send_param('dhcp_mode', DhcpModes.ON)
        self.test_values = self.ip_protocol['test_values']['dhcp']['on']
        self.valid_values = self.ip_protocol['valid_values']['dhcp']['on']
        super()._test_validate_fields()

        self._object.send_param('dhcp_mode', DhcpModes.RELAY)
        self.test_values = self.ip_protocol['test_values']['dhcp']['relay']
        self.valid_values = self.ip_protocol['valid_values']['dhcp']['relay']
        super()._test_validate_fields()

        self.test_values = {'dhcp_mode': [-8, 5, '6', 'ddsfs']}
        self.valid_values = {'dhcp_mode': []}
        super()._test_validate_fields()

    def test_dns_section(self):
        """Controller DNS section validation"""
        with self.subTest():
            if API != self._driver.get_type():
                self.skipTest('dns_caching only for API tests')
            self.test_values = self.ip_protocol['test_values']['dns_with_api']
            self.valid_values = self.ip_protocol['valid_values']['dns_with_api']
            super()._test_validate_fields()

        self._object.send_param('dns_caching', 1)
        self.test_values = self.ip_protocol['test_values']['dns']
        self.valid_values = self.ip_protocol['valid_values']['dns']
        super()._test_validate_fields()

    def test_arp_section(self):
        """Controller ARP section validation"""
        with self.subTest():
            if API != self._driver.get_type():
                self.skipTest('proxy_arp only for API tests')
            self.test_values = self.ip_protocol['test_values']['arp_with_api']
            self.valid_values = self.ip_protocol['valid_values']['arp_with_api']
            super()._test_validate_fields()

        self.test_values = self.ip_protocol['test_values']['arp']
        self.valid_values = self.ip_protocol['valid_values']['arp']
        super()._test_validate_fields()

    def test_tftp_section(self):
        """Controller TFTP section validation"""
        self.test_values = self.ip_protocol['test_values']['tftp']
        self.valid_values = self.ip_protocol['valid_values']['tftp']
        super()._test_validate_fields()

    def test_nat_section(self):
        """Controller NAT section validation"""
        self._object.send_param('nat_enable', 1)
        self.test_values = self.ip_protocol['test_values']['nat']
        self.valid_values = self.ip_protocol['valid_values']['nat']
        super()._test_validate_fields()

        with self.subTest():
            if API != self._driver.get_type():
                self.skipTest('nat_enable only for API tests')
            self.test_values = self.ip_protocol['test_values']['nat_with_api']
            self.valid_values = self.ip_protocol['valid_values']['nat_with_api']
            super()._test_validate_fields()

    def test_rip_section(self):
        """Controller RIP section validation"""
        self._object.send_param('rip_enable', 1)
        self.test_values = self.ip_protocol['test_values']['rip']
        self.valid_values = self.ip_protocol['valid_values']['rip']
        super()._test_validate_fields()

        with self.subTest():
            if API != self._driver.get_type():
                self.skipTest('rip checkboxes only for API tests')
            self.test_values = self.ip_protocol['test_values']['rip_with_api']
            self.valid_values = self.ip_protocol['valid_values']['rip_with_api']
            super()._test_validate_fields()

    def test_sntp_section(self):
        """Controller SNMP section validation"""
        self.test_values = self.ip_protocol['test_values']['sntp']
        self.valid_values = self.ip_protocol['valid_values']['sntp']
        super()._test_validate_fields()

    def test_mcast_section(self):
        """Controller multicast section validation"""
        self.test_values = self.ip_protocol['test_values']['mcast']
        self.valid_values = self.ip_protocol['valid_values']['mcast']
        super()._test_validate_fields()

    def test_acceleration_section(self):
        """Controller TCP acceleration section validation"""
        self._object.send_param('tcpa_enable', 1)
        self.test_values = self.ip_protocol['test_values']['acceleration']
        self.valid_values = self.ip_protocol['valid_values']['acceleration']
        super()._test_validate_fields()

        with self.subTest():
            if API != self._driver.get_type():
                self.skipTest('tcpa_enable only for API tests')
            self.test_values = self.ip_protocol['test_values']['tcpa_with_api']
            self.valid_values = self.ip_protocol['valid_values']['tcpa_with_api']
            super()._test_validate_fields()

    def test_mtu_section(self):
        """Controller MTU section validation"""
        self.test_values = self.ip_protocol['test_values']['mtu']
        self.valid_values = self.ip_protocol['valid_values']['mtu']
        super()._test_validate_fields()

    def test_buffering_section(self):
        """Controller buffering section validation"""
        self.test_values = self.ip_protocol['test_values']['buffering']
        self.valid_values = self.ip_protocol['valid_values']['buffering']
        super()._test_validate_fields()

    def test_retrying_section(self):
        """Controller retrying section validation"""
        self.test_values = self.ip_protocol['test_values']['retrying']
        self.valid_values = self.ip_protocol['valid_values']['retrying']
        super()._test_validate_fields()

    def test_monitoring_section(self):
        """Controller monitoring section validation"""
        self._object.send_param('sm_enable', 1)
        self._object.send_param('poll_enable1', 1)
        self._object.send_param('poll_enable2', 1)
        self._object.send_param('bkp_enable', 1)
        self._object.send_param('auto_reboot', 1)
        self.test_values = self.ip_protocol['test_values']['monitoring']
        self.valid_values = self.ip_protocol['valid_values']['monitoring']
        super()._test_validate_fields()
        with self.subTest():
            if API != self._driver.get_type():
                self.skipTest('monitoring checkboxes only for API tests')
            self.test_values = self.ip_protocol['test_values']['monitoring_with_api']
            self.valid_values = self.ip_protocol['valid_values']['monitoring_with_api']
            super()._test_validate_fields()

    def test_mod_queue_section(self):
        """Controller modulator queue section validation"""
        self.test_values = self.ip_protocol['test_values']['mod_queue']
        self.valid_values = self.ip_protocol['valid_values']['mod_queue']
        super()._test_validate_fields()

    def _validate_section(self, section):
        self.test_values = self.ip_protocol['test_values'][section]
        self.valid_values = self.ip_protocol['valid_values'][section]
        super()._test_validate_fields()
