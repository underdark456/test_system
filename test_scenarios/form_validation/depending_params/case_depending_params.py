import ipaddress
import random

from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, DhcpModes, RuleTypes, CheckTypes, StationModes
from src.exceptions import ObjectNotUpdatedException

options_path = 'test_scenarios.form_validation.depending_params'
backup_name = 'default_config.txt'


class DependingParamsCase(CustomTestCase):
    """Valid value of one of the parameters depends on value of another parameter(s)"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.22'
    __execution_time__ = 11
    __express__ = True

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)
        net = nms_api.create('nms:0', 'network', {'name': 'net'})
        tp = nms_api.create(net, 'teleport', {'name': 'tp'})
        vno = nms_api.create(net, 'vno', {'name': 'vno'})
        cls.mf_hub = nms_api.create(net, 'controller', {
            'name': 'mf_hub',
            'teleport': tp,
            'mode': ControllerModes.MF_HUB
        })
        cls.shp = nms_api.create(net, 'shaper', {'name': 'shp'})
        pol = nms_api.create(net, 'policy', {'name': 'pol'})
        cls.rule = nms_api.create(pol, 'polrule', {'sequence': 1})
        cls.bal = nms_api.create(net, 'bal_controller', {'name': 'bal'})
        cls.stn = nms_api.create(vno, 'station', {'name': 'stn', 'serial': 10000, 'mode': StationModes.STAR})

    def test_own_cn(self):
        """own_cn_low must be lower than own_cn_high"""
        for cn in range(0, 51):
            params = {'own_cn_low': cn, 'own_cn_high': 50 - cn}
            if cn <= 50 - cn:
                try:
                    nms_api.update(self.mf_hub, params)
                except ObjectNotUpdatedException:
                    self.fail(f'own_cn_low={cn}, own_cn_high={50-cn} is not applied in MF hub')
            else:
                with self.assertRaises(ObjectNotUpdatedException, msg=f'own_cn_low={cn}, own_cn_high={50-cn} applied'):
                    nms_api.update(self.mf_hub, params)

    def test_stn_low_high_cn(self):
        for cn in range(26):
            for o in ('hub_', 'station_'):
                params = {f'{o}low_cn': cn, f'{o}high_cn': 25 - cn}
                if cn <= 25 - cn:
                    try:
                        nms_api.update(self.stn, params)
                    except ObjectNotUpdatedException:
                        self.fail(f'{o}low_cn={cn}, {o}high_cn={25 - cn} is not applied in Star station')
                else:
                    with self.assertRaises(ObjectNotUpdatedException,
                                           msg=f'{o}low_cn={cn}, {o}high_cn={25 - cn} applied'):
                        nms_api.update(self.mf_hub, params)

    def test_dhcp_start_end(self):
        """DHCP dhcp_ip_start must be lower than dhcp_ip_end"""
        _ip = ipaddress.IPv4Address('192.168.1.1')
        for i in range(0, 400, 10):
            ip_start = _ip + i
            ip_end = _ip + 400 - i
            params = {
                'dhcp_mode': DhcpModes.ON,
                'dhcp_ip_start': str(ip_start),
                'dhcp_ip_end': str(ip_end),
                'dhcp_mask': '/16'
            }
            if ip_start <= ip_end:
                try:
                    nms_api.update(self.mf_hub, params)
                except ObjectNotUpdatedException:
                    self.fail(f'dhcp_ip_start={ip_start}, dhcp_ip_end={ip_end} is not applied')
            else:
                with self.assertRaises(
                        ObjectNotUpdatedException,
                        msg=f'dhcp_ip_start={ip_start}, dhcp_ip_end={ip_end} applied'
                ):
                    nms_api.update(self.mf_hub, params)

    def test_tcpa_svlan(self):
        """TCPA from_svlan must be lower than to_svlan"""
        for i in range(1, 64000, 1000):
            params = {'tcpa_enable': True, 'from_svlan': i, 'to_svlan': 64000 - i}
            if i <= 64000 - i:
                try:
                    nms_api.update(self.mf_hub, params)
                except ObjectNotUpdatedException:
                    self.fail(f'from_svlan={i}, to_svlan={64000 - i} is not applied in MF hub')
            else:
                with self.assertRaises(ObjectNotUpdatedException,
                                       msg=f'from_svlan={i}, to_svlan={64000 - i} is applied'):
                    nms_api.update(self.mf_hub, params)

    def test_wfq_sum(self):
        """Shaper WFQ sum must be 100"""
        for i in range(50):
            params = self.get_valid_wfq()
            try:
                nms_api.update(self.shp, params)
            except ObjectNotUpdatedException:
                self.fail(f'Shaper wfq={params} is not applied')
            params = self.get_invalid_wfq()
            with self.assertRaises(ObjectNotUpdatedException, msg=f'Shaper wfq={params} applied'):
                nms_api.update(self.shp, params)

    def test_policy_check_vlan(self):
        """Policy rule check vlan vlan_min, vlan_max"""
        for i in range(0, 4096, 10):
            params = {'type': RuleTypes.CHECK, 'check_type': CheckTypes.VLAN, 'vlan_min': i, 'vlan_max': 4095 - i}
            if i <= 4095 - i:
                try:
                    nms_api.update(self.rule, params)
                except ObjectNotUpdatedException:
                    self.fail(f'Polrule VLAN vlan_min={i} vlan_max={4095-i} is not applied')
            else:
                with self.assertRaises(ObjectNotUpdatedException, msg=f'vlan_min={i} vlan_max={4095-i} applied'):
                    nms_api.update(self.rule, params)

    def test_policy_check_tos(self):
        """Policy rule check tos tos_min, tos_max"""
        for i in range(0, 256, 5):
            params = {'type': RuleTypes.CHECK, 'check_type': CheckTypes.TOS, 'tos_min': i, 'tos_max': 255 - i}
            if i <= 255 - i:
                try:
                    nms_api.update(self.rule, params)
                except ObjectNotUpdatedException:
                    self.fail(f'Polrule TOS tos_min={i} tos_max={255-i} is not applied')
            else:
                with self.assertRaises(ObjectNotUpdatedException, msg=f'tos_min={i} tos_max={255-i} applied'):
                    nms_api.update(self.rule, params)

    def test_policy_check_dscp(self):
        """Policy rule check dscp dscp_min, dscp_max"""
        for i in range(0, 64, 3):
            params = {'type': RuleTypes.CHECK, 'check_type': CheckTypes.DSCP, 'dscp_min': i, 'dscp_max': 63 - i}
            if i <= 63 - i:
                try:
                    nms_api.update(self.rule, params)
                except ObjectNotUpdatedException:
                    self.fail(f'Polrule DSCP dscp_min={i} dscp_max={63-i} is not applied')
            else:
                with self.assertRaises(ObjectNotUpdatedException, msg=f'dscp_min={i} dscp_max={63-i} applied'):
                    nms_api.update(self.rule, params)

    def test_policy_check_port(self):
        """Policy rule check port DST/SRC, TCP/UDP"""
        for c in (CheckTypes.DST_TCP_PORT, CheckTypes.DST_UDP_PORT, CheckTypes.SRC_TCP_PORT, CheckTypes.SRC_UDP_PORT):
            for i in range(0, 65536, 1000):
                params = {'type': RuleTypes.CHECK, 'check_type': c, 'port_min': i, 'port_max': 65535 - i}
                if i <= 65535 - i:
                    try:
                        nms_api.update(self.rule, params)
                    except ObjectNotUpdatedException:
                        self.fail(f'Polrule check_type={c} port_min={i} port_max={65535-i} is not applied')
                else:
                    with self.assertRaises(ObjectNotUpdatedException, msg=f'port_min={i} port_max={65535-i} applied'):
                        nms_api.update(self.rule, params)

    def test_bal_controller_load(self):
        """load_lower must be lower than load_higher"""
        for i in range(101):
            for j in range(1, 3):
                params = {f'load_lower{j}': i, f'load_higher{j}': 100 - i}
                if i <= 100 - i:
                    try:
                        nms_api.update(self.bal, params)
                    except ObjectNotUpdatedException:
                        self.fail(f'load_lower{j}={i} load_higher{j}={100 - i} is not applied')
                else:
                    with self.assertRaises(
                            ObjectNotUpdatedException,
                            msg=f'load_lower{j}={i} load_higher{j}={100-i} applied'
                    ):
                        nms_api.update(self.rule, params)

    @staticmethod
    def get_valid_wfq():
        wfqs = ['wfq1', 'wfq2', 'wfq3', 'wfq4', 'wfq5', 'wfq6']
        random.shuffle(wfqs)
        params = {'wfq_enable': True}
        rest_values = 100
        for i in range(len(wfqs)):
            if i == len(wfqs) - 1:
                params[wfqs[i]] = rest_values
            else:
                value = random.randint(0, rest_values)
                rest_values = rest_values - value
                params[wfqs[i]] = value
        return params

    @staticmethod
    def get_invalid_wfq():
        wfqs = ['wfq1', 'wfq2', 'wfq3', 'wfq4', 'wfq5', 'wfq6']
        random.shuffle(wfqs)
        params = {'wfq_enable': True}
        while True:
            wfqs = [random.randint(0, 100) for _ in range(6)]
            if sum(wfqs) != 100:
                for i in range(6):
                    params[f'wfq{i+1}'] = wfqs[i]
                break
        return params
