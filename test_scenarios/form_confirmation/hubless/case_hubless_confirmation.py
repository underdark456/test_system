from src.enum_types_constants import StationModes
from src.exceptions import NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.station import Station
from src.options_providers.options_provider import OptionsProvider
from test_scenarios.form_confirmation.abstract_case import _AbstractCase

options_path = "test_scenarios.form_confirmation.hubless"


class HublessControllerConfirmationCase(_AbstractCase):
    """Confirm that UHP gets correct settings from a hubless controller"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 60  # approximate case execution time in seconds
    __express__ = True

    uhp_option = None
    uhp = None
    uhp_ip_address = None
    driver = None
    vno = None
    network = None
    teleport = None
    system_options = None
    station1 = None
    station2 = None
    station3 = None
    station4 = None
    station5 = None

    @classmethod
    def set_up_class(cls) -> None:
        # By calling the abstract class the default empty config is loaded, the following default objects are created:
        # a network, a teleport, a shaper, a VNO, and a station.
        super().set_up_class()
        cls.options = OptionsProvider.get_options('test_scenarios.form_confirmation')
        cls.options = OptionsProvider.get_options(options_path, options=cls.options)

        cls.network.send_params(cls.options.get('network', None))
        cls.teleport.send_params(cls.options.get('teleport', None))

        cls.controller_options = cls.options.get('controller', {})
        # Formatting controller options to pass them to the controller instance.
        controller_options = {}
        for key, value in cls.controller_options.items():
            if dict == type(value):
                controller_options.update(value)
        controller_options['device_ip'] = cls.uhp_option.get('device_ip')
        controller_options['device_vlan'] = cls.uhp_option.get('device_vlan')
        controller_options['device_gateway'] = cls.uhp_option.get('device_gateway')
        cls.controller = Controller.create(cls.driver, cls.network.get_id(), params=controller_options)
        cls.station1 = Station.create(cls.driver, cls.vno.get_id(), {
            'name': 'test_station1',
            'mode': StationModes.HUBLESS,
            'serial': '10001',
            'rx_controller': f'controller:{cls.controller.get_id()}',
            'enable': '1',
        })
        cls.station2 = Station.create(cls.driver, cls.vno.get_id(), {
            'name': 'test_station2',
            'mode': StationModes.HUBLESS,
            'serial': '10002',
            'rx_controller': f'controller:{cls.controller.get_id()}',
            'enable': '1'
        })
        cls.station3 = Station.create(cls.driver, cls.vno.get_id(), {
            'name': 'test_station3',
            'mode': StationModes.HUBLESS,
            'serial': '10003',
            'rx_controller': f'controller:{cls.controller.get_id()}',
            'enable': '1'
        })

        cls.station4 = Station.create(cls.driver, cls.vno.get_id(), {
            'name': 'test_station4',
            'mode': StationModes.HUBLESS,
            'serial': '10004',
            'rx_controller': f'controller:{cls.controller.get_id()}',
            'enable': '1'
        })
        cls.station5 = Station.create(cls.driver, cls.vno.get_id(), {
            'name': 'test_station5',
            'mode': StationModes.HUBLESS,
            'serial': '10005',
            'rx_controller': f'controller:{cls.controller.get_id()}',
            'enable': '1'
        })

        cls.uhp_model = cls.uhp.get_platform_version()

        cls.nms = Nms(cls.driver, 0, 0)

        if not cls.controller.wait_not_states(['Unknown', 'Unreachable']):
            raise NmsControlledModeException('Controller is not in either Unknown or Unreachable state')
        cls.nms.wait_ticks(3)

    def test_teleport(self):
        """Test teleport values"""
        self.nms_values = self.controller_options.get('teleport', None)
        self.nms_values.pop('teleport', None)
        super()._test_teleport()

    def test_modulator(self):
        """Test modulator section values"""
        self.nms_values = self.controller_options.get('modulator', None)
        super()._test_modulator()

    def test_tlc(self):
        """Test tlc section values"""
        self.nms_values = self.controller_options.get('tlc', None)
        super()._test_tlc()

    def test_demodulator1(self):
        """Test demodulator1 values"""
        self.nms_values = self.controller_options.get('demodulator1', None)
        # No such param for any UHP except for UHP-200X
        if self.uhp_model != 'uhp-200x':
            self.nms_values.pop('check_rx', None)
        super()._test_demodulator1()

    def test_demodulator2(self):
        """Test demodulator2 values"""
        self.nms_values = self.controller_options.get('demodulator2', None)
        # No such param rx2_input for any UHP except for UHP-200X
        if self.uhp_model != 'uhp-200x':
            pass
        else:
            super()._test_demodulator2()

    def test_tdma_protocol(self):
        """Test TDMA protocol values"""
        self.nms_values = self.controller_options.get('tdma_prot', None)
        # TODO: find the usage of 'no_stn_check'
        self.nms_values.pop('no_stn_check', None)
        super()._test_tdma_protocol()

    def test_tdma_rf_setup(self):
        """Test TDMA RF setup values"""
        self.nms_values = self.controller_options.get('tdma_rf', None)
        self.nms_values.pop('mf1_en', None)  # mf1_en enable does not make any sense
        # No such param for UHP-200X
        if self.uhp_model == 'uhp-200x':
            self.nms_values.pop('tdma_input', None)
        super()._test_tdma_rf_setup()

    def test_tdma_bw_allocation(self):
        """Test TDMA BW allocation values"""
        self.nms_values = self.controller_options.get('tdma_bw', None)
        super()._test_tdma_bw_allocation()

    def test_master_settings(self):
        """Test Master settings values"""
        self.nms_values = self.controller_options.get('master', None)
        super()._test_master_settings()

    def test_ip_screening(self):
        """Test IP screening values"""
        self.nms_values = self.controller_options.get('ip_screening', None)
        super()._test_ip_screening()

    def test_snmp(self):
        """Test SNMP settings values"""
        self.nms_values = self.controller_options.get('snmp', None)
        super()._test_snmp()

    def test_dhcp(self):
        """TestDHCP settings values"""
        self.nms_values = self.controller_options.get('dhcp', None)
        super()._test_dhcp()

    def test_dns(self):
        """Test DNS settings values"""
        self.nms_values = self.controller_options.get('dns', None)
        super()._test_dns()

    def test_arp(self):
        """Test ARP settings values"""
        self.nms_values = self.controller_options.get('arp', None)
        super()._test_arp()

    def test_tftp(self):
        """Test TFTP settings values"""
        self.nms_values = self.controller_options.get('tftp', None)
        super()._test_tftp()

    def test_nat(self):
        """Test NAT settings values"""
        self.nms_values = self.controller_options.get('nat', None)
        super()._test_nat()

    def test_rip(self):
        """Test RIP settings values"""
        self.nms_values = self.controller_options.get('rip', None)
        super()._test_rip()

    def test_sntp(self):
        """Test SNTP settings values"""
        self.nms_values = self.controller_options.get('sntp', None)
        super()._test_sntp()

    def test_multicast(self):
        """Test Multicast settings values"""
        self.nms_values = self.controller_options.get('mcast', None)
        super()._test_multicast()

    def test_traffic_protection(self):
        """Test Traffic protection settings values"""
        self.nms_values = self.controller_options.get('ctl', None)
        super()._test_traffic_protection()

    def test_tcpa(self):
        """Test TCPA settings values"""
        self.nms_values = self.controller_options.get('tcpa', None)
        super()._test_tcpa()

    def test_service_monitoring(self):
        """Test Service monitoring settings values"""
        self.nms_values = self.controller_options.get('service_monitoring', None)
        super()._test_service_monitoring()

    def test_modulator_queues(self):
        """Test Modulator queues settings values"""
        self.nms_values = self.controller_options.get('queue', None)
        super()._test_modulator_queues()
