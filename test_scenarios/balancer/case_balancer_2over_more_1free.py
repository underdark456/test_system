import time
from src import nms_api
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import TdmaModcod
from test_scenarios.balancer.base_config_3ctrls_1bal import _Base3Ctrl1BalCase

options_path = 'test_scenarios.balancer'
backup_name = 'default_config.txt'


class Balancer2OverMore1FreeCase(_Base3Ctrl1BalCase):
    """The test to check that stations are not switched in overloaded net 2.8"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.26'
    __review__ = ''
    __execution_time__ = 360  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()

    def test_balancer_2_over_more_1_free(self):
        nms_api.update(self.mf_hub, {'tdma_sr': 1000, 'tdma_mc': TdmaModcod._8PSK_2_3,
                                     'channel_bw': '1900', 'max_load': '1500'})
        nms_api.update(self.inroute2, {'tdma_sr': 1200, 'tdma_mc': TdmaModcod._8PSK_2_3,
                                       'channel_bw': '2400', 'max_load': '2000'})

        self.assertTrue(nms_api.wait_up(self.inroute2), msg='Inroute-2 is not Up after settings changing')

        nms_api.update('bal_controller:0', {'load_higher': '50'})

        self.station1_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 800, 'pps_to': 800,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station2_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 1000, 'pps_to': 1000,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        for _ in range(5):
            nms_api.wait_ticks(5)
            st1_rate = nms_api.get_param('station:0', 'return_rate1')
            if st1_rate > 1500:
                break
        else:
            self.fail(f'Station1 return_rate1 is unexpectedly lower than 1500')
        time.sleep(60)
        nms_api.wait_ticks(5)

        # Check parameter Load Balancing on Balancer ctrl dashboard (should be 1)
        self.assertEqual(nms_api.get_param('bal_controller:0', 'load_sw'), 1,
                         msg='Load balancing parameter on dashboard is not correct')

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
