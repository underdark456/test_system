import random
from src.enum_types_constants import StationModes
from src.exceptions import NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.station import Station
from src.options_providers.options_provider import OptionsProvider
from test_scenarios.form_confirmation.abstract_case import _AbstractCase

options_path = 'test_scenarios.form_confirmation.dama_controller'
backup_name = 'default_config.txt'


class DamaHubConfirmationCase(_AbstractCase):
    """DAMA hub controller UHP gets all the settings"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 60  # approximate case execution time in seconds
    __express__ = True
    uhp_option = None
    driver = None
    network = None
    vno = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()
        cls.options = OptionsProvider.get_options(options_path, options=cls.options)

        cls.dama_hub_options = cls.options.get('controller', {})
        # Formatting controller options to pass them to the controller instance.
        dama_hub_options = {}
        for key, value in cls.dama_hub_options.items():
            if dict == type(value):
                dama_hub_options.update(value)
        dama_hub_options['device_ip'] = cls.uhp_option.get('device_ip')
        dama_hub_options['device_vlan'] = cls.uhp_option.get('device_vlan')
        dama_hub_options['device_gateway'] = cls.uhp_option.get('device_gateway')
        dama_hub_options['uhp_model'] = 'UHP200'
        # for key, value in dama_hub_options.items():
        #     print(key, value)
        cls.dama_hub = Controller.create(cls.driver, cls.network.get_id(), params=dama_hub_options)
        for i in range(2):
            Station.create(cls.driver, cls.vno.get_id(), {
                'name': f'damastn{i+1}',
                'mode': StationModes.DAMA,
                'serial': random.randint(1, 10000),
                'rx_controller': f'controller:{cls.dama_hub.get_id()}',
                'enable': '1',
                'dama_ab': i,
            })

        cls.nms = Nms(cls.driver, 0, 0)
        if not cls.dama_hub.wait_not_states(['Unknown', 'Unreachable']):
            raise NmsControlledModeException(f'DAMA hub is in {cls.dama_hub.read_param("state")} state')
        cls.nms.wait_ticks(3)

    def test_check_rx(self):
        """Test check RX value"""
        self.nms_values = self.dama_hub_options.get('settings').get('check_rx')
        super()._test_check_rx()

    def test_dama_return_1(self):
        """Test Return Channel 1 values"""
        self.nms_values = self.dama_hub_options.get('dama_return_a')
        super()._test_return_channel(channel=1)

    def test_dama_return_2(self):
        """Test Return Channel 2 values"""
        self.nms_values = self.dama_hub_options.get('dama_return_b')
        super()._test_return_channel(channel=2)

    def test_teleport(self):
        """Test teleport values"""
        self.nms_values = self.dama_hub_options.get('teleport')
        self.nms_values.pop('teleport')
        super()._test_teleport()

    def test_modulator(self):
        """Test modulator section values"""
        self.nms_values = self.dama_hub_options.get('modulator')
        super()._test_modulator()

    def test_tdm_acm(self):
        """Test TDM ACM values"""
        self.nms_values = self.dama_hub_options.get('tdm_acm')
        super()._test_tdm_acm_settings()

    def test_tlc(self):
        """Test tlc section values"""
        self.nms_values = self.dama_hub_options.get('tlc')
        super()._test_tlc()

    def test_ip_screening(self):
        """Test IP screening values"""
        self.nms_values = self.dama_hub_options.get('ip_screening')
        super()._test_ip_screening()

    def test_snmp(self):
        """Test SNMP settings values"""
        self.nms_values = self.dama_hub_options.get('snmp')
        super()._test_snmp()

    def test_dhcp(self):
        """TestDHCP settings values"""
        self.nms_values = self.dama_hub_options.get('dhcp')
        super()._test_dhcp()

    def test_dns(self):
        """Test DNS settings values"""
        self.nms_values = self.dama_hub_options.get('dns')
        super()._test_dns()

    def test_arp(self):
        """Test ARP settings values"""
        self.nms_values = self.dama_hub_options.get('arp')
        super()._test_arp()

    def test_tftp(self):
        """Test TFTP settings values"""
        self.nms_values = self.dama_hub_options.get('tftp')
        super()._test_tftp()

    def test_nat(self):
        """Test NAT settings values"""
        self.nms_values = self.dama_hub_options.get('nat')
        super()._test_nat()

    def test_rip(self):
        """Test RIP settings values"""
        self.nms_values = self.dama_hub_options.get('rip')
        super()._test_rip()

    def test_sntp(self):
        """Test SNTP settings values"""
        self.nms_values = self.dama_hub_options.get('sntp')
        super()._test_sntp()

    def test_multicast(self):
        """Test Multicast settings values"""
        self.nms_values = self.dama_hub_options.get('mcast')
        super()._test_multicast()

    def test_traffic_protection(self):
        """Test Traffic protection settings values"""
        self.nms_values = self.dama_hub_options.get('ctl')
        super()._test_traffic_protection()

    def test_tcpa(self):
        """Test TCPA settings values"""
        self.nms_values = self.dama_hub_options.get('tcpa')
        super()._test_tcpa()

    def test_service_monitoring(self):
        """Test Service monitoring settings values"""
        self.nms_values = self.dama_hub_options.get('service_monitoring')
        super()._test_service_monitoring()

    def test_modulator_queues(self):
        """Test Modulator queues settings values"""
        self.nms_values = self.dama_hub_options.get('queue')
        super()._test_modulator_queues()

    def test_tdm_tx_section(self):
        """Test roaming section settings values"""
        self.nms_values = self.dama_hub_options.get('tdm_tx')
        super()._test_tdm_tx()
