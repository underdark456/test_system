import random
import time

from src import nms_api
from src.enum_types_constants import PriorityTypes, RouteTypes, CheckboxStr, RuleTypesStr, CheckTypesStr, \
    QueueTypesStr, ActionTypesStr
from utilities.network_up.mf_hub_1stn_up import MfHub1StnUp

options_path = 'test_scenarios.form_confirmation.policy'
backup_name = 'default_config.txt'


class PoliciesRangeConfirmationCase(MfHub1StnUp):
    """Every policy rule range confirmation case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.27'
    __execution_time__ = None
    __express__ = False

    @classmethod
    def set_up_class(cls):
        super().set_up_class()
        cls.pol = nms_api.create('network:0', 'policy', {'name': 'pol'})
        cls.rule = nms_api.create(cls.pol, 'polrule', {'sequence': 1})
        cls.ser = nms_api.create('network:0', 'service', {'name': 'ser', 'hub_vlan': 206, 'stn_vlan': 306})
        cls.qos = nms_api.create(
            'network:0', 'qos', {'name': 'qos', 'priority': PriorityTypes.POLICY, 'policy': cls.pol}
        )
        nms_api.create('controller:0', 'route', {
            'type': RouteTypes.NETWORK_TX,
            'service': cls.ser,
            'forward_qos': cls.qos,
            'ip': '192.168.100.0',
            'mask': '/24',
        })
        nms_api.create('station:0', 'route', {
            'type': RouteTypes.NETWORK_TX,
            'service': cls.ser,
            'return_qos': cls.qos,
            'ip': '192.168.200.0',
            'mask': '/24',
        })

    def test_check_802_1q_priority(self):
        for prio_802 in (0, 3, 7):
            _not = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            goto_actions = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            params = {
                'type': RuleTypesStr.CHECK,
                'check_type': CheckTypesStr.PRIORITY_802_1Q,
                'prio_802': prio_802,
                'not': _not,
                'goto_actions': goto_actions,
            }
            self.check_next_rule(params)

    def test_vlan(self):
        for vlan_min in (0, 2345, 4095):
            _not = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            goto_actions = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            params = {
                'type': RuleTypesStr.CHECK,
                'check_type': CheckTypesStr.VLAN,
                'vlan_min': vlan_min,
                'vlan_max': vlan_min,
                'not': _not,
                'goto_actions': goto_actions,
            }
            self.check_next_rule(params)

    def test_tos(self):
        for tos_min in (0, 123, 255):
            _not = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            goto_actions = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            params = {
                'type': RuleTypesStr.CHECK,
                'check_type': CheckTypesStr.TOS,
                'tos_min': tos_min,
                'tos_max': tos_min,
                'not': _not,
                'goto_actions': goto_actions,
            }
            self.check_next_rule(params)

    def test_dscp(self):
        for dscp_min in (0, 31, 63):
            _not = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            goto_actions = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            params = {
                'type': RuleTypesStr.CHECK,
                'check_type': CheckTypesStr.DSCP,
                'dscp_min': dscp_min,
                'dscp_max': dscp_min,
                'not': _not,
                'goto_actions': goto_actions,
            }
            self.check_next_rule(params)

    def test_protocol(self):
        for protocol in (0, 123, 255):
            _not = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            goto_actions = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            params = {
                'type': RuleTypesStr.CHECK,
                'check_type': CheckTypesStr.PROTOCOL,
                'protocol': protocol,
                'not': _not,
                'goto_actions': goto_actions,
            }
            self.check_next_rule(params)

    def test_src_net(self):
        for net_ip, net_mask in (['192.168.124.0', '/24'], ['172.16.0.0', '/16'], ['10.0.0.0', '/8']):
            _not = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            goto_actions = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            params = {
                'type': RuleTypesStr.CHECK,
                'check_type': CheckTypesStr.SRC_NET,
                'net_ip': net_ip,
                'net_mask': net_mask,
                'goto_actions': goto_actions,
            }
            self.check_next_rule(params)

    def test_dst_net(self):
        for net_ip, net_mask in (['192.168.124.0', '/24'], ['172.16.0.0', '/16'], ['10.0.0.0', '/8']):
            _not = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            goto_actions = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            params = {
                'type': RuleTypesStr.CHECK,
                'check_type': CheckTypesStr.DST_NET,
                'net_ip': net_ip,
                'net_mask': net_mask,
                'goto_actions': goto_actions,
            }
            self.check_next_rule(params)

    def test_port(self):
        for check_type in (
            CheckTypesStr.SRC_TCP_PORT,
            CheckTypesStr.SRC_UDP_PORT,
            CheckTypesStr.DST_TCP_PORT,
            CheckTypesStr.DST_UDP_PORT
        ):
            for port_min in (0, 1, 65535):
                _not = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
                goto_actions = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
                params = {
                    'type': RuleTypesStr.CHECK,
                    'check_type': check_type,
                    'port_min': port_min,
                    'port_max': port_min,
                    'goto_actions': goto_actions,
                }
                self.check_next_rule(params)

    def test_icmp_type(self):
        for icmp_type in (0, 123, 255):
            _not = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            goto_actions = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            params = {
                'type': RuleTypesStr.CHECK,
                'check_type': CheckTypesStr.ICMP_TYPE,
                'icmp_type': icmp_type,
                'goto_actions': goto_actions,
            }
            self.check_next_rule(params)

    def test_set_queue(self):
        for queue in ([*QueueTypesStr()]):
            terminate = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            params = {
                'type': RuleTypesStr.ACTION,
                'action_type': ActionTypesStr.SET_QUEUE,
                'queue': queue,
                'terminate': terminate,
            }
            self.check_next_rule(params)

    def test_set_acm_channel(self):
        # UHP200 supports only 6 ACM channels
        for acm_channel in (1, 3, 6):
            terminate = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            params = {
                'type': RuleTypesStr.ACTION,
                'action_type': ActionTypesStr.SET_ACM_CHANNEL,
                'acm_channel': acm_channel,
                'terminate': terminate,
            }
            self.check_next_rule(params)

    def test_encrypt(self):
        for key in (1, 127, 256):
            terminate = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            params = {
                'type': RuleTypesStr.ACTION,
                'action_type': ActionTypesStr.ENCRYPT,
                'key': key,
                'terminate': terminate,
            }
            self.check_next_rule(params)

    def test_set_tos(self):
        for set_tos in (0, 127, 255):
            terminate = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            params = {
                'type': RuleTypesStr.ACTION,
                'action_type': ActionTypesStr.SET_TOS,
                'set_tos': set_tos,
                'terminate': terminate,
            }
            self.check_next_rule(params)

    def test_set_dscp(self):
        for set_dscp in (0, 21, 63):
            terminate = random.choice([CheckboxStr.ON, CheckboxStr.OFF])
            params = {
                'type': RuleTypesStr.ACTION,
                'action_type': ActionTypesStr.SET_DSCP,
                'set_dscp': set_dscp,
                'terminate': terminate,
            }
            self.check_next_rule(params)

    def check_next_rule(self, params):
        nms_api.update(self.rule, params)
        time.sleep(20)
        hub_values = self.mf_hub_uhp.get_policy_rule()
        stn_values = self.stn1_uhp.get_policy_rule()
        for key, value in params.items():
            self.assertEqual(
                str(value),
                hub_values.get(key),
                msg=f'MF Hub {key}={value}, UHP got {key}={hub_values.get(key)}'
            )
            self.assertEqual(
                str(value),
                stn_values.get(key),
                msg=f'Station {key}={value}, UHP got {key}={stn_values.get(key)}'
            )
