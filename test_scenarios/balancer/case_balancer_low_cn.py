import time
from src import nms_api
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from test_scenarios.balancer.base_config_3ctrls_1bal import _Base3Ctrl1BalCase

options_path = 'test_scenarios.balancer'
backup_name = 'default_config.txt'


class BalancerLowCNCase(_Base3Ctrl1BalCase):
    """The test to check stations switching due to low cn 2.3"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.25'
    __review__ = ''
    __execution_time__ = 360  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()

    def test_balancer_low_cn(self):
        nms_api.update('bal_controller:0', {'low_cn_time': '30'})

        self.station1_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 70, 'pps_to': 70,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station2_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 80, 'pps_to': 80,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station3_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 60, 'pps_to': 60,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        nms_api.wait_ticks(5)
        # Increase noise level to switch station due to low_cn fault
        inr2_hub_cn = nms_api.get_param('controller:2', 'hub_cn_avg')
        tx_lvl = 46
        while inr2_hub_cn > 13.9:
            if tx_lvl <= 1:
                self.fail(f'Cannot adjust SCPC modem TX level (noise level) to get desired Inroute 2 hub_cn_avg')
            self.device4_uhp.scpc_modem(params={
                'rx1_frq': '1003000', 'rx1_sr': '10000',
                'tx_frq': '1003000', 'tx_sr': '10000',
                'tx_on': '1', 'tx_level': tx_lvl
            })
            nms_api.wait_ticks(2)
            tx_lvl = round(tx_lvl - 0.2, 1)
            inr2_hub_cn = nms_api.get_param('controller:2', 'hub_cn_avg')
            print(tx_lvl, inr2_hub_cn)

        time.sleep(40)

        # wait station Up
        self.assertTrue(nms_api.wait_up('station:2'))

        # Check actual ctrl on station dashboard
        st2_ctrl_act = nms_api.get_param('station:2', 'rx_ctr_act')
        st2_ctrl_set = nms_api.get_param('station:2', 'rx_controller')
        self.assertNotEqual(st2_ctrl_act, st2_ctrl_set)

        # Check parameter Low CN on Balancer ctrl dashboard (should be 1)
        self.assertEqual(nms_api.get_param('bal_controller:0', 'level_sw'), 1)

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
