import time
from src import nms_api
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from test_scenarios.balancer.base_config_3ctrls_1bal import _Base3Ctrl1BalCase

options_path = 'test_scenarios.balancer'
backup_name = 'default_config.txt'


class Balancer2OverloadCase(_Base3Ctrl1BalCase):
    """The test to check 2 stations from overloaded cts are switched to free ctrl 2.6"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.26'
    __review__ = ''
    __execution_time__ = 360  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()

    def test_balancer_2_overload(self):
        nms_api.update('bal_controller:0', {'load_higher': '50'})

        self.station1_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 270, 'pps_to': 270,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station2_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 770, 'pps_to': 770,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        for _ in range(5):
            nms_api.wait_ticks(5)
            st1_rate = nms_api.get_param('station:0', 'return_rate1')
            if st1_rate > 500:
                break
        else:
            self.fail(f'Station1 return_rate1 is unexpectedly lower than 500')

        time.sleep(60)
        nms_api.wait_ticks(5)

        # wait station Up
        self.assertTrue(nms_api.wait_up('station:0'), msg=f'Station1 state is not Up after switching')

        # Check actual ctrl on station dashboard
        st1_ctrl_act = nms_api.get_param('station:0', 'rx_ctr_act')
        st1_ctrl_set = nms_api.get_param('station:0', 'rx_controller')
        self.assertNotEqual(st1_ctrl_act, st1_ctrl_set, msg=f'Station1 was not switched by balancer')

        st2_ctrl_act = nms_api.get_param('station:1', 'rx_ctr_act')
        st2_ctrl_set = nms_api.get_param('station:1', 'rx_controller')
        self.assertNotEqual(st2_ctrl_act, st2_ctrl_set, msg=f'Station2 was not switched by balancer')

        # Check parameter Load Balancing on Balancer ctrl dashboard (should be 2)
        self.assertEqual(nms_api.get_param('bal_controller:0', 'load_sw'), 2,
                         msg='Load balancing parameter on dashboard is not correct')

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
