from src import nms_api, test_api
from src.drivers.uhp.uhp_requests_driver import UhpRequestsDriver
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from test_scenarios.balancer.base_config_3ctrls_1bal import _Base3Ctrl1BalCase

options_path = 'test_scenarios.balancer'
backup_name = 'default_config.txt'


class BalancerSetUpCase(_Base3Ctrl1BalCase):
    """The test to set up network with Balancer 1"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.26'
    __review__ = ''
    #__execution_time__ = 400  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()

    def test_balancer_set_up(self):
        self.station1_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 70, 'pps_to': 70,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station2_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 170, 'pps_to': 170,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station3_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 180, 'pps_to': 180,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        nms_api.wait_ticks(10)
        # Check values on Balancer dashboard
        ch_bw_hub = nms_api.get_param('controller:0', 'channel_bw')
        ch_bw_inr1 = nms_api.get_param('controller:1', 'channel_bw')
        ch_bw_inr2 = nms_api.get_param('controller:2', 'channel_bw')
        ctr_ch_bw = [ch_bw_hub, ch_bw_inr1, ch_bw_inr2]
        bal_ch1_bw = nms_api.get_param('bal_controller:0', 'ch1_bw')
        bal_ch2_bw = nms_api.get_param('bal_controller:0', 'ch2_bw')
        bal_ch3_bw = nms_api.get_param('bal_controller:0', 'ch3_bw')
        bal_ch_bw = [bal_ch1_bw, bal_ch2_bw, bal_ch3_bw]

        self.assertEqual(ctr_ch_bw, bal_ch_bw, 'Channel bw on Bal_controller dashboard are not correct')

        ch_max_hub = nms_api.get_param('controller:0', 'max_load')
        ch_max_inr1 = nms_api.get_param('controller:1', 'max_load')
        ch_max_inr2 = nms_api.get_param('controller:2', 'max_load')
        ctr_max_bw = [ch_max_hub, ch_max_inr1, ch_max_inr2]
        bal_ch1_max = nms_api.get_param('bal_controller:0', 'ch1_max')
        bal_ch2_max = nms_api.get_param('bal_controller:0', 'ch2_max')
        bal_ch3_max = nms_api.get_param('bal_controller:0', 'ch3_max')
        bal_ch_max = [bal_ch1_max, bal_ch2_max, bal_ch3_max]

        self.assertEqual(ctr_max_bw, bal_ch_max, 'Max load values on Bal_controller dashboard are not correct')
        # Ping stations on Hub
        ip_address_hub = nms_api.get_param('controller:0', 'device_ip')
        self.ctrl_telnet = UhpTelnetDriver(ip_address_hub)

        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station1 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.3.1', vlan=206):
            self.fail(f'Station2 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.4.1', vlan=206):
            self.fail(f'Station3 does not respond to ICMP echo requests!')

        self.station1_uhp.traffic_generator({'enabled': 0})
        self.station2_uhp.traffic_generator({'enabled': 0})
        self.station3_uhp.traffic_generator({'enabled': 0})

    def tear_down(self):
        if self.ctrl_telnet is not None:
            self.ctrl_telnet.close()
