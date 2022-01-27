import time
from src import nms_api
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import CheckboxStr
from test_scenarios.balancer.base_config_3ctrls_1bal import _Base3Ctrl1BalCase

options_path = 'test_scenarios.balancer'
backup_name = 'default_config.txt'


class BalancerFreeFaultCase(_Base3Ctrl1BalCase):
    """The test to check stations switching from fault ctrl 2.2"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.26'
    __review__ = ''
    __execution_time__ = 360  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()

    def test_balancer_free_fault(self):
        nms_api.update('bal_controller:0', {'free_down': CheckboxStr.ON,
                                            'free_fault': CheckboxStr.ON, 'down_time': '60'})

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
        # Change settings for controller Inroute-1 to go fault
        # Add SM monitoring fault
        nms_api.update('controller:1', {
            'sm_enable': CheckboxStr.ON,
            'lan_rx_check': '2',
            'rx_check_rate': '5000'
        })
        nms_api.wait_ticks(5)
        self.assertTrue(nms_api.wait_fault('controller:1'), msg=f'Inroute-1 is not in expected fault state')
        time.sleep(60)

        # wait station Up
        self.assertTrue(nms_api.wait_up('station:1'))

        # Check actual ctrl on station dashboard
        st2_ctrl_act = nms_api.get_param('station:1', 'rx_ctr_act')
        st2_ctrl_set = nms_api.get_param('station:1', 'rx_controller')
        self.assertNotEqual(st2_ctrl_act, st2_ctrl_set)

        # Repeat for Inroute-2
        nms_api.update('bal_controller:0', {'down_time': '30'})
        # Add SM monitoring fault
        nms_api.update('controller:2', {
            'sm_enable': CheckboxStr.ON,
            'lan_rx_check': '2',
            'rx_check_rate': '5000'
        })
        nms_api.wait_ticks(5)
        self.assertTrue(nms_api.wait_fault('controller:2'), msg=f'Inroute-2 is not in expected fault state')
        time.sleep(60)

        # wait station Up
        self.assertTrue(nms_api.wait_up('station:2'))

        # Check actual ctrl on station dashboard
        st2_ctrl_act = nms_api.get_param('station:2', 'rx_ctr_act')
        st2_ctrl_set = nms_api.get_param('station:2', 'rx_controller')
        self.assertNotEqual(st2_ctrl_act, st2_ctrl_set)
        # Check parameter Controller down on Balancer ctrl dashboard (should be 2)
        self.assertEqual(nms_api.get_param('bal_controller:0', 'down_sw'), 2)

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
