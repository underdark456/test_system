import time

from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import StationModes, RouteTypes, CheckboxStr, RouteIds

options_path = 'test_scenarios.balancer'
backup_name = 'default_config.txt'


class Balancer2BalCtrCase(CustomTestCase):
    """The test to check stations switching with 2 Balancer controllers 2.13"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.27'
    __review__ = ''
    __execution_time__ = 280  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        controllers, stations = test_api.get_uhp_controllers_stations(4, ['UHP200'], 3,
                                                                      ['ANY',])
        test_options = test_api.get_options(options_path)

        device1_uhp = controllers[0].get('web_driver')
        device2_uhp = controllers[1].get('web_driver')
        device3_uhp = controllers[2].get('web_driver')
        device4_uhp = controllers[3].get('web_driver')
        cls.station1_uhp = stations[0].get('web_driver')
        cls.station2_uhp = stations[1].get('web_driver')
        cls.station3_uhp = stations[2].get('web_driver')

        device1_uhp.set_nms_permission(vlan=controllers[0].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        device2_uhp.set_nms_permission(vlan=controllers[1].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        device3_uhp.set_nms_permission(vlan=controllers[2].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        device4_uhp.set_nms_permission(vlan=controllers[3].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))

        cls.station1_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': test_options.get('stations_tx_lvl')
        })
        cls.station2_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': test_options.get('stations_tx_lvl')
        })
        cls.station3_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': test_options.get('stations_tx_lvl')
        })
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        network = nms_api.create('nms:0', 'network', test_options.get('network'))
        nms_api.create(network, 'teleport', test_options.get('teleport1'))
        cls.balancer1 = nms_api.create('network:0', 'bal_controller',
                                      {'name': 'balancer1', 'enable': CheckboxStr.OFF, 'free_down': CheckboxStr.ON,
                                       'bal_interval': '60', 'load_higher': '50'})
        cls.balancer2 = nms_api.create('network:0', 'bal_controller',
                                      {'name': 'balancer2', 'enable': CheckboxStr.OFF, 'free_down': CheckboxStr.ON,
                                       'bal_interval': '60', 'load_higher': '50'})
        vno = nms_api.create(network, 'vno', {'name': 'vno_test'})
        cls.mf_hub = nms_api.create(network, 'controller', test_options.get('mf_hub'))
        cls.inroute1 = nms_api.create(network, 'controller', test_options.get('inroute1'))
        cls.inroute2 = nms_api.create(network, 'controller', test_options.get('inroute2'))
        cls.inroute3 = nms_api.create(network, 'controller', test_options.get('inroute3'))

        nms_api.update(cls.mf_hub, {
            'binding': '0',
            'device_ip': controllers[0].get('device_ip'),
            'device_gateway': controllers[0].get('device_gateway'),
            'device_vlan': controllers[0].get('device_vlan'),
        }
                       )
        nms_api.update(cls.inroute1, {
            'binding': '0',
            'device_ip': controllers[1].get('device_ip'),
            'device_gateway': controllers[1].get('device_gateway'),
            'device_vlan': controllers[1].get('device_vlan'),
        }
                       )
        nms_api.update(cls.inroute2, {
            'binding': '0',
            'device_ip': controllers[2].get('device_ip'),
            'device_gateway': controllers[2].get('device_gateway'),
            'device_vlan': controllers[2].get('device_vlan'),
        }
                       )
        nms_api.update(cls.inroute3, {
            'binding': '0',
            'device_ip': controllers[3].get('device_ip'),
            'device_gateway': controllers[3].get('device_gateway'),
            'device_vlan': controllers[3].get('device_vlan'),
        }
                       )

        station1 = nms_api.create(vno, 'station', {
            'name': f'Station1',
            'serial': stations[0].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub
        }
                                  )
        station2 = nms_api.create(vno, 'station', {
            'name': f'Station2',
            'serial': stations[1].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.inroute1
        })
        station3 = nms_api.create(vno, 'station', {
            'name': f'Station3',
            'serial': stations[2].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.inroute3
        })
        station4 = nms_api.create(vno, 'station', {
            'name': 'Fake',
            'serial': '666',
            'mode': StationModes.STAR,
            'rx_controller': cls.inroute2
        })

        service_local = nms_api.create(network, 'service', {
            'name': 'Local',
            'stn_vlan': controllers[0].get('device_vlan')
        })

        nms_api.create(station1, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_local,
            'ip': stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE
        })

        nms_api.create(station1, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_local,
            'ip': '0.0.0.0',
            'gateway': stations[0].get('device_gateway'),
            'mask': '/0',
            'id': RouteIds.PRIVATE
        })
        nms_api.create(station2, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_local,
            'ip': stations[1].get('device_ip'),
            'id': RouteIds.PRIVATE
        })

        nms_api.create(station2, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_local,
            'ip': '0.0.0.0',
            'gateway': stations[1].get('device_gateway'),
            'mask': '/0',
            'id': RouteIds.PRIVATE
        })
        nms_api.create(station3, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_local,
            'ip': stations[2].get('device_ip'),
            'id': RouteIds.PRIVATE
        })

        nms_api.create(station3, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_local,
            'ip': '0.0.0.0',
            'gateway': stations[2].get('device_gateway'),
            'mask': '/0',
            'id': RouteIds.PRIVATE
        })
        # nms_api.update(cls.balancer, {'enable': CheckboxStr.ON})
        # create routing to check stations availability
        service_ping = nms_api.create(network, 'service', test_options.get('service_ping'))

        nms_api.create(cls.mf_hub, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.1.1'
        })
        nms_api.create(station1, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.2.1'
        })
        nms_api.create(station2, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.3.1'
        })
        nms_api.create(station3, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.4.1'
        })
        nms_api.create(cls.mf_hub, 'route', {
            'type': RouteTypes.NETWORK_RX,
            'service': service_ping
        })
        nms_api.create(cls.inroute1, 'route', {
            'type': RouteTypes.NETWORK_RX,
            'service': service_ping
        })
        nms_api.create(cls.inroute1, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.1.2'
        })
        nms_api.create(cls.inroute1, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_ping,
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': '192.168.1.1'
        })
        nms_api.create(cls.inroute2, 'route', {
            'type': RouteTypes.NETWORK_RX,
            'service': service_ping
        })
        nms_api.create(cls.inroute2, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.1.3'
        })
        nms_api.create(cls.inroute2, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_ping,
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': '192.168.1.1'
        })
        nms_api.create(cls.inroute3, 'route', {
            'type': RouteTypes.NETWORK_RX,
            'service': service_ping
        })
        nms_api.create(cls.inroute3, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.1.4'
        })
        nms_api.create(cls.inroute3, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_ping,
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': '192.168.1.1'
        })

        nms_api.update(station1, {'enable': '1'})
        nms_api.update(station2, {'enable': '1'})
        nms_api.update(station3, {'enable': '1'})
        nms_api.update(station4, {'enable': '1'})

        if not nms_api.wait_up(cls.mf_hub, timeout=240):
            test_api.error('Controller is not in UP state')

        if not (nms_api.wait_up(station1) and nms_api.wait_up(station2) and nms_api.wait_up(station3)):
            test_api.error('One of the station is not Up')

        nms_api.update(cls.mf_hub, {
            'bal_enable': CheckboxStr.ON,
            'bal_controller': 'bal_controller:0',
            'lowest_cn': '3',
            'relative_cn': '0',
            'channel_bw': '650',
            'max_load': '500'
        }
                       )
        nms_api.update(cls.inroute1, {
            'bal_enable': CheckboxStr.ON,
            'bal_controller': 'bal_controller:0',
            'lowest_cn': '10',
            'relative_cn': '3',
            'channel_bw': '1900',
            'max_load': '1500'
        }
                       )
        nms_api.update(cls.inroute2, {
            'bal_enable': CheckboxStr.ON,
            'bal_controller': 'bal_controller:1',
            'lowest_cn': '10',
            'relative_cn': '3',
            'channel_bw': '5000',
            'max_load': '3500'
        }
                       )
        nms_api.update(cls.inroute3, {
            'bal_enable': CheckboxStr.ON,
            'bal_controller': 'bal_controller:1',
            'lowest_cn': '4',
            'relative_cn': '0',
            'channel_bw': '2000',
            'max_load': '1500'
        }
                       )
        nms_api.update(cls.balancer1, {'enable': CheckboxStr.ON})
        nms_api.update(cls.balancer2, {'enable': CheckboxStr.ON})
        nms_api.wait_ticks(3)

    def test_balancer_2_bal_ctr(self):

        self.station1_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 300, 'pps_to': 300,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station2_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 200, 'pps_to': 200,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station3_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 1000, 'pps_to': 1000,
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
        self.assertTrue(nms_api.wait_up('station:0'))

        # Check actual ctrl on station dashboard
        st1_ctrl_act = nms_api.get_param('station:0', 'rx_ctr_act')
        st1_ctrl_set = nms_api.get_param('station:0', 'rx_controller')
        self.assertNotEqual(st1_ctrl_act, st1_ctrl_set)

        st3_ctrl_act = nms_api.get_param('station:2', 'rx_ctr_act')
        st3_ctrl_set = nms_api.get_param('station:2', 'rx_controller')
        self.assertNotEqual(st3_ctrl_act, st3_ctrl_set)

        # Check parameter Load Balancing on Balancer ctrl dashboard (should be 1)
        self.assertEqual(nms_api.get_param('bal_controller:0', 'load_sw'), 1)
        self.assertEqual(nms_api.get_param('bal_controller:1', 'load_sw'), 1)

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
