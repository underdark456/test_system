import time
from src import nms_api
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from test_scenarios.balancer.base_config_3ctrls_1bal import _Base3Ctrl1BalCase

options_path = 'test_scenarios.balancer'
backup_name = 'default_config.txt'


class BalancerAmong3St2Case(_Base3Ctrl1BalCase):
    """The test to check 2 stations are switched due to load_higher1 limit 2.5.2"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.26'
    __review__ = ''
    __execution_time__ = 325  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()

    def test_balancer_among3_2st(self):
        nms_api.update('bal_controller:0', {'load_higher': '40', 'load_lower': '10'})

        nms_api.update('station:1', {
            'rx_controller': self.mf_hub,
            'no_balancing': '1'
        })
        time.sleep(60)

        nms_api.update('station:1', {
            'no_balancing': '0'
        })
        self.assertTrue(nms_api.wait_up('station:1'), msg='Station 2 is not in Up state after ctrl changing ')

        self.station1_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 200, 'pps_to': 200,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station2_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 100, 'pps_to': 100,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station3_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 60, 'pps_to': 60,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        for _ in range(5):
            nms_api.wait_ticks(5)
            st1_rate = nms_api.get_param('station:0', 'return_rate1')
            if st1_rate > 350:
                break
        else:
            self.fail(f'Station1 return_rate1 is unexpectedly lower than 350')
        time.sleep(60)
        nms_api.wait_ticks(5)

        # wait station Up
        self.assertTrue(nms_api.wait_up('station:0'))

        # Check actual ctrl on station dashboard
        st1_ctrl_act = nms_api.get_param('station:0', 'rx_ctr_act')
        st1_ctrl_set = nms_api.get_param('station:0', 'rx_controller')
        self.assertNotEqual(st1_ctrl_act, st1_ctrl_set)

        st2_ctrl_act = nms_api.get_param('station:1', 'rx_ctr_act')
        st2_ctrl_set = nms_api.get_param('station:1', 'rx_controller')
        self.assertEqual(st2_ctrl_act, st2_ctrl_set)

        # Check parameter Load Balancing on Balancer ctrl dashboard (should be 1)
        self.assertEqual(nms_api.get_param('bal_controller:0', 'load_sw'), 1)

        self.station1_uhp.traffic_generator({'enabled': 0})
        self.station2_uhp.traffic_generator({'enabled': 0})
        self.station3_uhp.traffic_generator({'enabled': 0})

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
