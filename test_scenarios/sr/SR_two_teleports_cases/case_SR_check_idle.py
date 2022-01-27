import time

from src import nms_api, test_api
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import CheckboxStr
from test_scenarios.sr.SR_two_teleports_cases.base_config_2dev_1stn import _Base2Dev1StnCase

options_path = 'test_scenarios.sr.SR_two_teleports_cases'
backup_name = 'default_config.txt'


class SrCheckIdleCase(_Base2Dev1StnCase):
    """Check teleport switching due to check idle fault"""

    __author__ = 'vpetuhova'
    __version__ = '0.1'
    __review__ = 'dkudryashov'
    __execution_time__ = 400  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()

    def test_sr_check_idle(self):
        state1 = nms_api.get_param(self.device1, 'state')
        state2 = nms_api.get_param(self.device2, 'state')
        nms_api.update(self.sr_controller, {'check_idle': CheckboxStr.ON, 'min_idle': '2'})

        time.sleep(80)
        if not nms_api.get_param(self.sr_controller, 'tp_fail_code') == 'Minimum_idle':
            test_api.fail(self, 'There are no fail code on teleport')
        time.sleep(20)

        if not nms_api.wait_log_message('sr_controller:0', 'Teleport reconfigured'):
            test_api.fail(self, 'There are no expected log messages')

        time.sleep(60)
        state11 = nms_api.get_param(self.device1, 'state')
        state22 = nms_api.get_param(self.device2, 'state')
        # Device states should change due to a fault (the controller was switched to a redundant device)
        if state1 != state22 or state2 != state11:
            test_api.fail(self, 'There was no teleport switching')

        nms_api.update(self.sr_controller, {'check_idle': CheckboxStr.OFF})
        # Find device with controller MF-Hub
        state_up_device, state_red_device, ip_address_A, ip_address_B = \
            self.find_active_device(self.device1, self.device2)

        self.ctrl_telnet = UhpTelnetDriver(ip_address_A)
        time.sleep(20)
        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station does not respond to ICMP echo requests!')

    def tear_down(self):
        if self.ctrl_telnet is not None:
            self.ctrl_telnet.close()

    def find_active_device(self, sr_device1, sr_device2):
        # find active device
        if nms_api.get_param(sr_device1, 'state') == 'Up':
            ip_address_A = nms_api.get_param(sr_device1, 'ip')
            ip_address_B = nms_api.get_param(sr_device2, 'ip')
            state_up_device = sr_device1
            state_red_device = sr_device2
        elif nms_api.get_param(sr_device2, 'state') == 'Up':
            ip_address_A = nms_api.get_param(sr_device2, 'ip')
            ip_address_B = nms_api.get_param(sr_device1, 'ip')
            state_up_device = sr_device2
            state_red_device = sr_device1
        else:
            self.fail('Devices statuses are unexpected')

        return state_up_device, state_red_device, ip_address_A, ip_address_B
