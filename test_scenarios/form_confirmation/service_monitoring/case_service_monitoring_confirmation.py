import time

from src import nms_api
from src.enum_types_constants import Checkbox, LanCheckModesStr
from utilities.network_up.mf_hub_1stn_up import MfHub1StnUp

options_path = 'test_scenarios.form_confirmation.policy'
backup_name = 'default_config.txt'


class SmConfirmationCase(MfHub1StnUp):
    """Service monitoring values range confirmation case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.27'
    __execution_time__ = 355
    __express__ = False

    @classmethod
    def set_up_class(cls):
        super().set_up_class()

    def test_sm_interval_lost(self):
        for sm_interval, sm_losts in ([1, 0], [30, 50], [60, 100]):
            params = {'sm_enable': Checkbox.ON, 'sm_interval': sm_interval, 'sm_losts': sm_losts}
            self.check_next(params)

    def test_poll_enable1(self):
        for poll_ip1, poll_vlan1, max_delay1 in (
                ['10.56.24.11', 0, 1], ['172.16.56.2', 2031, 16742], ['192.168.0.254', 4095, 32000]
        ):
            params = {
                'sm_enable': Checkbox.ON,
                'poll_enable1': Checkbox.ON,
                'poll_ip1': poll_ip1,
                'poll_vlan1': poll_vlan1,
                'chk_delay1': Checkbox.ON,
                'max_delay1': max_delay1
            }
            self.check_next(params)

    def test_poll_enable2(self):
        for poll_ip2, poll_vlan2, max_delay2 in (
                ['8.8.8.8', 0, 1], ['172.16.56.2', 2031, 16742], ['192.13.4.1', 4095, 32000]
        ):
            params = {
                'sm_enable': Checkbox.ON,
                'poll_enable2': Checkbox.ON,
                'poll_ip2': poll_ip2,
                'poll_vlan2': poll_vlan2,
                'chk_delay2': Checkbox.ON,
                'max_delay2': max_delay2
            }
            self.check_next(params)

    def test_lan_check(self):
        for p in (
            [LanCheckModesStr.LOWER, 0, LanCheckModesStr.HIGHER, 100000],
            [LanCheckModesStr.HIGHER, 100000, LanCheckModesStr.LOWER, 0],
            [LanCheckModesStr.LOWER, 1000, LanCheckModesStr.HIGHER, 90000],
            [LanCheckModesStr.HIGHER, 54321, LanCheckModesStr.HIGHER, 12345],
        ):
            params = {
                'sm_enable': Checkbox.ON,
                'lan_rx_check': p[0],
                'rx_check_rate': p[1],
                'lan_tx_check': p[2],
                'tx_check_rate': p[3],
            }
            self.check_next(params)

    def check_next(self, params):
        nms_api.update(self.mf_hub, params)
        nms_api.update(self.stn1, params)
        time.sleep(20)
        hub_values = self.mf_hub_uhp.get_service_monitoring_form()
        stn_values = self.stn1_uhp.get_service_monitoring_form()
        for key, value in params.items():
            self.assertEqual(
                str(value).lower(),
                hub_values.get(key),
                msg=f'MF Hub {key}={value}, UHP got {key}={hub_values.get(key)}'
            )
            self.assertEqual(
                str(value).lower(),
                stn_values.get(key),
                msg=f'Station {key}={value}, UHP got {key}={stn_values.get(key)}'
            )