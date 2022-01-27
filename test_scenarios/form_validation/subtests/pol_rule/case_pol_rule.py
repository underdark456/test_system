from unittest import skip

from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import RuleTypes, CheckTypes, ActionTypes
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.shaper import Shaper
from src.options_providers.options_provider import OptionsProvider
from test_scenarios.form_validation.abstract_case import _AbstractCase

__author__ = 'dkudryashov'
__version__ = '0.1'
options_path = 'test_scenarios.form_validation.subtests.pol_rule'
backup_name = 'default_config.txt'


@skip('There is data types validation test case. This one is not needed?')
class PolRuleValidationCase(_AbstractCase):
    """Not needed? Policy rule form validation"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        cls._init_params(cls.options)
        cls.net = Network.create(cls.driver, 0, {'name': 'test_net'})
        cls.pol = Policy.create(cls.driver, cls.net.get_id(), {'name': 'test_pol'})
        cls.pol2 = Policy.create(cls.driver, cls.net.get_id(), {'name': 'test_pol2'})
        cls.shp = Shaper.create(cls.driver, cls.net.get_id(), {'name': 'test_shp'})
        cls._object = PolicyRule.create(cls.driver, cls.pol.get_id(), {'sequence': 1})

    def test_check_802_1q_priority(self):
        """Policy rule check 802_1Q_priority validation test"""
        self._object.send_params({'type': RuleTypes.CHECK, 'check_type': CheckTypes.PRIORITY_802_1Q})
        self.assertEqual('Check', self._object.get_param('type'))
        self.assertEqual('priority_802_1q', self._object.get_param('check_type'))
        self.test_values = self.test_values.get('802_1q_priority')
        self.valid_values = self.valid_values.get('802_1q_priority')
        super()._test_validate_fields()

    def test_check_vlan(self):
        """Policy rule check VLAN validation test"""
        self._object.send_params({'type': RuleTypes.CHECK, 'check_type': CheckTypes.VLAN})
        self.assertEqual('Check', self._object.get_param('type'))
        self.assertEqual('VLAN', self._object.get_param('check_type'))
        self.test_values = self.test_values.get('vlan')
        self.valid_values = self.valid_values.get('vlan')
        super()._test_validate_fields()

        # Testing VLAN range (first value must be lower or equal to the second value
        self.first_values = self.first_values.get('vlan')
        self.second_values = self.second_values.get('vlan')
        super()._test_depending_values()

    def test_check_tos(self):
        """Policy rule check TOS validation test"""
        self._object.send_params({'type': RuleTypes.CHECK, 'check_type': CheckTypes.TOS})
        self.assertEqual('Check', self._object.get_param('type'))
        self.assertEqual('TOS', self._object.get_param('check_type'))
        self.test_values = self.test_values.get('tos')
        self.valid_values = self.valid_values.get('tos')
        super()._test_validate_fields()

        # Testing VLAN range (first value must be lower or equal to the second value
        self.first_values = self.first_values.get('tos')
        self.second_values = self.second_values.get('tos')
        super()._test_depending_values()

    def test_check_dscp(self):
        """Policy rule check DSCP validation test"""
        self._object.send_params({'type': RuleTypes.CHECK, 'check_type': CheckTypes.DSCP})
        self.assertEqual('Check', self._object.get_param('type'))
        self.assertEqual('DSCP', self._object.get_param('check_type'))
        self.test_values = self.test_values.get('dscp')
        self.valid_values = self.valid_values.get('dscp')
        super()._test_validate_fields()

        # Testing VLAN range (first value must be lower or equal to the second value
        self.first_values = self.first_values.get('dscp')
        self.second_values = self.second_values.get('dscp')
        super()._test_depending_values()

    def test_check_protocol(self):
        """Policy rule check Protocol validation test"""
        self._object.send_params({'type': RuleTypes.CHECK, 'check_type': CheckTypes.PROTOCOL})
        self.assertEqual('Check', self._object.get_param('type'))
        self.assertEqual('Protocol', self._object.get_param('check_type'))
        self.test_values = self.test_values.get('protocol')
        self.valid_values = self.valid_values.get('protocol')
        super()._test_validate_fields()

    def test_src_net(self):
        """Policy rule check SRC_NET validation test"""
        self._object.send_params({'type': RuleTypes.CHECK, 'check_type': CheckTypes.SRC_NET})
        self.assertEqual('Check', self._object.get_param('type'))
        self.assertEqual('SRC_Net', self._object.get_param('check_type'))
        self.test_values = self.test_values.get('src_net')
        self.valid_values = self.valid_values.get('src_net')
        super()._test_validate_fields()

    def test_dst_net(self):
        """Policy rule check DST_NET validation test"""
        self._object.send_params({'type': RuleTypes.CHECK, 'check_type': CheckTypes.DST_NET})
        self.assertEqual('Check', self._object.get_param('type'))
        self.assertEqual('DST_Net', self._object.get_param('check_type'))
        self.test_values = self.test_values.get('dst_net')
        self.valid_values = self.valid_values.get('dst_net')
        super()._test_validate_fields()

    def test_check_src_tcp_port(self):
        """Policy rule check SRC_TCP_port validation test"""
        self._object.send_params({'type': RuleTypes.CHECK, 'check_type': CheckTypes.SRC_TCP_PORT})
        self.assertEqual('Check', self._object.get_param('type'))
        self.assertEqual('SRC_TCP_port', self._object.get_param('check_type'))
        self.test_values = self.test_values.get('src_tcp_port')
        self.valid_values = self.valid_values.get('src_tcp_port')
        super()._test_validate_fields()

        # Testing VLAN range (first value must be lower or equal to the second value
        self.first_values = self.first_values.get('src_tcp_port')
        self.second_values = self.second_values.get('src_tcp_port')
        super()._test_depending_values()

    def test_check_dst_tcp_port(self):
        """Policy rule check DST_TCP_port validation test"""
        self._object.send_params({'type': RuleTypes.CHECK, 'check_type': CheckTypes.DST_TCP_PORT})
        self.assertEqual('Check', self._object.get_param('type'))
        self.assertEqual('DST_TCP_port', self._object.get_param('check_type'))
        self.test_values = self.test_values.get('dst_tcp_port')
        self.valid_values = self.valid_values.get('dst_tcp_port')
        super()._test_validate_fields()

        # Testing VLAN range (first value must be lower or equal to the second value
        self.first_values = self.first_values.get('dst_tcp_port')
        self.second_values = self.second_values.get('dst_tcp_port')
        super()._test_depending_values()

    def test_check_src_udp_port(self):
        """Policy rule check SRC_UDP_port validation test"""
        self._object.send_params({'type': RuleTypes.CHECK, 'check_type': CheckTypes.SRC_UDP_PORT})
        self.assertEqual('Check', self._object.get_param('type'))
        self.assertEqual('SRC_UDP_port', self._object.get_param('check_type'))
        self.test_values = self.test_values.get('src_udp_port')
        self.valid_values = self.valid_values.get('src_udp_port')
        super()._test_validate_fields()

        # Testing VLAN range (first value must be lower or equal to the second value
        self.first_values = self.first_values.get('src_udp_port')
        self.second_values = self.second_values.get('src_udp_port')
        super()._test_depending_values()

    def test_check_dst_udp_port(self):
        """Policy rule check DST_UDP_port validation test"""
        self._object.send_params({'type': RuleTypes.CHECK, 'check_type': CheckTypes.DST_UDP_PORT})
        self.assertEqual('Check', self._object.get_param('type'))
        self.assertEqual('DST_UDP_port', self._object.get_param('check_type'))
        self.test_values = self.test_values.get('dst_udp_port')
        self.valid_values = self.valid_values.get('dst_udp_port')
        super()._test_validate_fields()

        # Testing VLAN range (first value must be lower or equal to the second value
        self.first_values = self.first_values.get('dst_udp_port')
        self.second_values = self.second_values.get('dst_udp_port')
        super()._test_depending_values()

    def test_check_icmp_type(self):
        """Policy rule check ICMP_type validation test"""
        self._object.send_params({'type': RuleTypes.CHECK, 'check_type': CheckTypes.ICMP_TYPE})
        self.assertEqual('Check', self._object.get_param('type'))
        self.assertEqual('ICMP_type', self._object.get_param('check_type'))
        self.test_values = self.test_values.get('icmp_type')
        self.valid_values = self.valid_values.get('icmp_type')
        super()._test_validate_fields()

    def test_action_set_queue(self):
        """Policy rule action Set_queue validation test"""
        self._object.send_params({'type': RuleTypes.ACTION, 'action_type': ActionTypes.SET_QUEUE})
        self.assertEqual('Action', self._object.get_param('type'))
        self.assertEqual('Set_queue', self._object.get_param('action_type'))
        self.test_values = self.test_values.get('set_queue')
        self.valid_values = self.valid_values.get('set_queue')
        super()._test_validate_fields()

    def test_action_set_ts_ch(self):
        """Policy rule action Set_TS_ch validation test"""
        self._object.send_params({'type': RuleTypes.ACTION, 'action_type': ActionTypes.SET_TS_CH})
        self.assertEqual('Action', self._object.get_param('type'))
        self.assertEqual('Set_TS_ch', self._object.get_param('action_type'))
        self.test_values = self.test_values.get('set_ts_ch')
        self.valid_values = self.valid_values.get('set_ts_ch')
        super()._test_validate_fields()

    def test_action_no_tcpa(self):
        """Policy rule action No_TCPA validation test"""
        self._object.send_params({'type': RuleTypes.ACTION, 'action_type': ActionTypes.NO_TCPA})
        self.assertEqual('Action', self._object.get_param('type'))
        self.assertEqual('No_TCPA', self._object.get_param('action_type'))
        self.test_values = self.test_values.get('no_tcpa')
        self.valid_values = self.valid_values.get('no_tcpa')
        super()._test_validate_fields()

    def test_action_compress_rtp(self):
        """Policy rule action Compress_RTP validation test"""
        self._object.send_params({'type': RuleTypes.ACTION, 'action_type': ActionTypes.COMPRESS_RTP})
        self.assertEqual('Action', self._object.get_param('type'))
        self.assertEqual('Compress_RTP', self._object.get_param('action_type'))
        self.test_values = self.test_values.get('compress_rtp')
        self.valid_values = self.valid_values.get('compress_rtp')
        super()._test_validate_fields()

    def test_no_screening(self):
        """Policy rule action No_screening validation test"""
        self._object.send_params({'type': RuleTypes.ACTION, 'action_type': ActionTypes.NO_SCREENING})
        self.assertEqual('Action', self._object.get_param('type'))
        self.assertEqual('No_screening', self._object.get_param('action_type'))
        self.test_values = self.test_values.get('no_screening')
        self.valid_values = self.valid_values.get('no_screening')
        super()._test_validate_fields()

    def test_set_acm_channel(self):
        """Policy rule action Set_ACM_channel validation test"""
        self._object.send_params({'type': RuleTypes.ACTION, 'action_type': ActionTypes.SET_ACM_CHANNEL})
        self.assertEqual('Action', self._object.get_param('type'))
        self.assertEqual('Set_ACM_channel', self._object.get_param('action_type'))
        self.test_values = self.test_values.get('set_acm_channel')
        self.valid_values = self.valid_values.get('set_acm_channel')
        super()._test_validate_fields()

    def test_drop_if_station_down(self):
        """Policy rule action Drop_if_station_down validation test"""
        self._object.send_params({'type': RuleTypes.ACTION, 'action_type': ActionTypes.DROP_IF_STATION_DOWN})
        self.assertEqual('Action', self._object.get_param('type'))
        self.assertEqual('Drop_if_station_down', self._object.get_param('action_type'))
        self.test_values = self.test_values.get('drop_if_station_down')
        self.valid_values = self.valid_values.get('drop_if_station_down')
        super()._test_validate_fields()

    def test_encrypt(self):
        """Policy rule action Encrypt validation test"""
        self._object.send_params({'type': RuleTypes.ACTION, 'action_type': ActionTypes.ENCRYPT})
        self.assertEqual('Action', self._object.get_param('type'))
        self.assertEqual('Encrypt', self._object.get_param('action_type'))
        self.test_values = self.test_values.get('encrypt')
        self.valid_values = self.valid_values.get('encrypt')
        super()._test_validate_fields()

    def test_set_tos(self):
        """Policy rule action Set_TOS validation test"""
        self._object.send_params({'type': RuleTypes.ACTION, 'action_type': ActionTypes.SET_TOS})
        self.assertEqual('Action', self._object.get_param('type'))
        self.assertEqual('Set_TOS', self._object.get_param('action_type'))
        self.test_values = self.test_values.get('set_tos')
        self.valid_values = self.valid_values.get('set_tos')
        super()._test_validate_fields()

    def test_set_dscp(self):
        """Policy rule action Set_DSCP validation test"""
        self._object.send_params({'type': RuleTypes.ACTION, 'action_type': ActionTypes.SET_DSCP})
        self.assertEqual('Action', self._object.get_param('type'))
        self.assertEqual('Set_DSCP', self._object.get_param('action_type'))
        self.test_values = self.test_values.get('set_dscp')
        self.valid_values = self.valid_values.get('set_dscp')
        super()._test_validate_fields()

    def test_goto_policy(self):
        """Policy rule action GOTO_policy validation test"""
        # Policies are returned as `policy:<policy_id> <policy_name>
        self._object.send_params({
            'type': RuleTypes.ACTION,
            'action_type': ActionTypes.GOTO_POLICY,
            'policy': f'policy:{self.pol2.get_id()}'}
        )
        self.assertEqual('Action', self._object.get_param('type'))
        self.assertEqual('GOTO_policy', self._object.get_param('action_type'))
        self.test_values = self.test_values.get('goto_policy')
        self.valid_values = self.valid_values.get('goto_policy')
        super()._test_validate_fields()

    def test_call_policy(self):
        """Policy rule action CALL_policy validation test"""
        # Policies are returned as `policy:<policy_id> <policy_name>
        self._object.send_params({
            'type': RuleTypes.ACTION,
            'action_type': ActionTypes.CALL_POLICY,
            'policy': f'policy:{self.pol2.get_id()}',
        })
        self.assertEqual('Action', self._object.get_param('type'))
        self.assertEqual('CALL_policy', self._object.get_param('action_type'))
        self.test_values = self.test_values.get('call_policy')
        self.valid_values = self.valid_values.get('call_policy')
        super()._test_validate_fields()

    def test_compress_gtp(self):
        """Policy rule action Compress_GTP validation test"""
        self._object.send_params({'type': RuleTypes.ACTION, 'action_type': ActionTypes.COMPRESS_GTP})
        self.assertEqual('Action', self._object.get_param('type'))
        self.assertEqual('Compress_GTP', self._object.get_param('action_type'))
        self.test_values = self.test_values.get('compress_gtp')
        self.valid_values = self.valid_values.get('compress_gtp')
        super()._test_validate_fields()
