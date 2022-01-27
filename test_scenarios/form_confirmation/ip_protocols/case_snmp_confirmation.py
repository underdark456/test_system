import ipaddress
import time

from src import nms_api
from src.enum_types_constants import SnmpModesStr, SnmpAuthStr
from utilities.network_up.mf_hub_1stn_up import MfHub1StnUp


class SnmpConfirmationCase(MfHub1StnUp):
    """MF hub and 1 station SNMP confirmation"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.25'
    __execution_time__ = 660  # approximate test case execution time in seconds
    __express__ = False

    @classmethod
    def set_up_class(cls):
        super().set_up_class()

    def test_snmp_v1_v2c(self):
        """SNMP V1_V2C confirmation MF hub and station"""
        for i in range(6):
            snmp_params = {
                'snmp_mode': SnmpModesStr.V1_V2C,
                'access1_ip': str(ipaddress.ip_address('196.101.53.255') + 200_000_000 * i),
                'access2_ip': str(ipaddress.ip_address('17.148.215.255') + 800_000_000 * i),
                'snmp_read': '1234567890'[:i * 2],
                'snmp_write': 'abcdefghij'[:i * 2],
            }
            self.check_expected_params(snmp_params)

        self.check_snmp_off()

    def test_snmp_v3_no_auth(self):
        """SNMP V3 No Auth confirmation MF hub and station"""
        for i in range(6):
            snmp_params = {
                'snmp_mode': SnmpModesStr.V3,
                'access1_ip': str(ipaddress.ip_address('196.101.53.255') + 200_000_000 * i),
                'access2_ip': str(ipaddress.ip_address('17.148.215.255') + 800_000_000 * i),
                'snmp_auth': SnmpAuthStr.NO_AUTH,
                'snmp_user': 'aAbBcCdDeEf'[:i * 2],
            }
            self.check_expected_params(snmp_params)
        self.check_snmp_off()

    def test_snmp_v3_auth_no_priv(self):
        """SNMP V3 Auth No Priv confirmation MF hub and station"""
        for i in range(6):
            snmp_params = {
                'snmp_mode': SnmpModesStr.V3,
                'access1_ip': str(ipaddress.ip_address('196.101.53.255') + 200_000_000 * i),
                'access2_ip': str(ipaddress.ip_address('17.148.215.255') + 800_000_000 * i),
                'snmp_auth': SnmpAuthStr.AUTH_NO_PRIV,
                'snmp_user': 'aAbBcCdDeEf'[:i * 2],
                'snmp_read': '1234567890'[:i * 2],
            }
            self.check_expected_params(snmp_params)
        self.check_snmp_off()

    def test_snmp_v3_auth_priv(self):
        """SNMP V3 Auth Priv confirmation MF hub and station"""
        for i in range(6):
            snmp_params = {
                'snmp_mode': SnmpModesStr.V3,
                'access1_ip': str(ipaddress.ip_address('196.101.53.255') + 200_000_000 * i),
                'access2_ip': str(ipaddress.ip_address('17.148.215.255') + 800_000_000 * i),
                'snmp_auth': SnmpAuthStr.AUTH_PRIV,
                'snmp_user': 'aAbBcCdDeEf'[:i * 2],
                'snmp_read': '1234567890'[:i * 2],
                'snmp_write': '1234567890'[:i * 2],
            }
            self.check_expected_params(snmp_params)
        self.check_snmp_off()

    def check_expected_params(self, snmp_params):
        nms_api.update(self.mf_hub, snmp_params)
        nms_api.update(self.stn1, snmp_params)
        time.sleep(20)
        hub_snmp = self.mf_hub_uhp.get_snmp_form()
        stn_snmp = self.stn1_uhp.get_snmp_form()
        for key, value in snmp_params.items():
            if key == 'snmp_read' and snmp_params.get('snmp_auth') in (SnmpAuthStr.AUTH_PRIV, SnmpAuthStr.AUTH_NO_PRIV):
                self.assertEqual(
                    str(value).lower(),
                    hub_snmp.get('snmp_auth_pass'),
                    msg=f'NMS {key}={value}, UHP Hub snmp_auth_pass={hub_snmp.get("snmp_auth_pass")}'
                )
                self.assertEqual(
                    str(value).lower(),
                    stn_snmp.get('snmp_auth_pass'),
                    msg=f'NMS {key}={value}, UHP Stn snmp_auth_pass={stn_snmp.get("snmp_auth_pass")}'
                )
            elif key == 'snmp_write' and snmp_params.get('snmp_auth') in (SnmpAuthStr.AUTH_PRIV, SnmpAuthStr.AUTH_NO_PRIV):
                self.assertEqual(
                    str(value).lower(),
                    hub_snmp.get('snmp_priv_pass'),
                    msg=f'NMS {key}={value}, UHP Hub snmp_priv_pass={hub_snmp.get("snmp_priv_pass")}'
                )
                self.assertEqual(
                    str(value).lower(),
                    stn_snmp.get('snmp_priv_pass'),
                    msg=f'NMS {key}={value}, UHP Stn snmp_priv_pass={stn_snmp.get("snmp_priv_pass")}'
                )
            else:
                self.assertEqual(
                    str(value).lower(),
                    hub_snmp.get(key),
                    msg=f'NMS {key}={value}, UHP Hub {key}={hub_snmp.get(key)}'
                )
                self.assertEqual(
                    str(value).lower(),
                    stn_snmp.get(key),
                    msg=f'NMS {key}={value}, UHP Stn {key}={stn_snmp.get(key)}'
                )

    def check_snmp_off(self):
        """Check if SNMP is off after setting in NMS"""
        nms_api.update(self.mf_hub, {'snmp_mode': SnmpModesStr.OFF})
        nms_api.update(self.stn1, {'snmp_mode': SnmpModesStr.OFF})
        nms_api.wait_ticks(4)
        hub_snmp = self.mf_hub_uhp.get_snmp_form()
        stn_snmp = self.stn1_uhp.get_snmp_form()
        self.assertEqual(SnmpModesStr.V1_V2C.lower(), hub_snmp.get('snmp_mode'), msg=f'UHP MF hub SNMP is not OFF')
        self.assertEqual(SnmpModesStr.V1_V2C.lower(), stn_snmp.get('snmp_mode'), msg=f'UHP stn SNMP is not OFF')
        self.assertEqual('0.0.0.0', hub_snmp.get('access1_ip'), msg=f'UHP MF hub SNMP access1_ip is not 0.0.0.0')
        self.assertEqual('0.0.0.0', stn_snmp.get('access1_ip'), msg=f'UHP stn SNMP access1_ip is not 0.0.0.0')
        self.assertEqual('0.0.0.0', hub_snmp.get('access2_ip'), msg=f'UHP MF hub SNMP access2_ip is not 0.0.0.0')
        self.assertEqual('0.0.0.0', stn_snmp.get('access2_ip'), msg=f'UHP stn SNMP access2_ip is not 0.0.0.0')
        self.assertEqual('public', hub_snmp.get('snmp_read'), msg=f'UHP MF hub SNMP snmp_read is not public')
        self.assertEqual('public', stn_snmp.get('snmp_read'), msg=f'UHP stn SNMP snmp_read is not public')
        self.assertEqual('private', hub_snmp.get('snmp_write'), msg=f'UHP MF hub SNMP snmp_write is not private')
        self.assertEqual('private', stn_snmp.get('snmp_write'), msg=f'UHP stn SNMP snmp_read is not private')
