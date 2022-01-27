import time
from src import nms_api
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from test_scenarios.balancer.base_config_3ctrls_1bal import _Base3Ctrl1BalCase

options_path = 'test_scenarios.balancer'
backup_name = 'default_config.txt'


class BalancerSwIdleCase(_Base3Ctrl1BalCase):
    """The test to check idle stations are switched in pass1 2.9"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.27'
    __review__ = ''
    __execution_time__ = 360  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()

    def test_balancer_sw_idle(self):
        nms_api.update('bal_controller:0', {'load_higher': '70', 'switch_idle': '1'})

        nms_api.update('station:1', {
            'rx_controller': self.mf_hub,
            'no_balancing': '1'
        })
        nms_api.update('station:2', {
            'rx_controller': self.mf_hub,
            'no_balancing': '1'
        })
        time.sleep(60)

        nms_api.update('station:1', {
            'no_balancing': '0'
        })
        nms_api.update('station:2', {
            'no_balancing': '0'
        })
        self.assertTrue(nms_api.wait_up('station:1'), msg='Station 2 is not in Up state after ctrl changing ')

        self.station1_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 170, 'pps_to': 170,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})
        self.station2_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 190, 'pps_to': 190,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        for _ in range(5):
            nms_api.wait_ticks(5)
            st1_rate = nms_api.get_param('station:0', 'return_rate1')
            if st1_rate > 300:
                break
        else:
            self.fail(f'Station1 return_rate1 is unexpectedly lower than 500')
        time.sleep(60)
        nms_api.wait_ticks(5)

        # wait station Up
        self.assertTrue(nms_api.wait_up('station:0'))

        # Check actual ctrl on station dashboard
        st1_ctrl_act = nms_api.get_param('station:0', 'rx_ctr_act')
        st1_ctrl_set = nms_api.get_param('station:0', 'rx_controller')
        self.assertEqual(st1_ctrl_act, st1_ctrl_set)

        st3_ctrl_act = nms_api.get_param('station:2', 'rx_ctr_act')
        st3_ctrl_set = nms_api.get_param('station:2', 'rx_controller')
        self.assertNotEqual(st3_ctrl_act, st3_ctrl_set)

        # Check parameter Load Balancing on Balancer ctrl dashboard (should be 1)
        self.assertEqual(nms_api.get_param('bal_controller:0', 'load_sw'), 1)

        self.station1_uhp.traffic_generator({'enabled': 0})
        self.station2_uhp.traffic_generator({'enabled': 0})

        # Ping stations on Hub
        ip_address_hub = nms_api.get_param('controller:0', 'device_ip')
        self.ctrl_telnet = UhpTelnetDriver(ip_address_hub)

        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station1 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.3.1', vlan=206):
            self.fail(f'Station2 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.4.1', vlan=206):
            self.fail(f'Station3 does not respond to ICMP echo requests!')

    def tear_down(self):
        if self.ctrl_telnet is not None:
            self.ctrl_telnet.close()
