import time

from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import StationModes, RouteTypes, CheckboxStr, RouteIds

options_path = 'test_scenarios.balancer'
backup_name = 'default_config.txt'


class BalancerStWithoutBalCase(CustomTestCase):
    """The test to check station with 'no balancing' enable isn't switched 2.14"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.27'
    __review__ = ''
    __execution_time__ = 360  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        controllers, stations = test_api.get_uhp_controllers_stations(2, ['UHP200'], 5,
                                                                      ['ANY',])
        test_options = test_api.get_options(options_path)

        device1_uhp = controllers[0].get('web_driver')
        device2_uhp = controllers[1].get('web_driver')
        cls.station1_uhp = stations[0].get('web_driver')
        cls.station2_uhp = stations[1].get('web_driver')
        cls.station3_uhp = stations[2].get('web_driver')
        cls.station4_uhp = stations[3].get('web_driver')
        cls.station5_uhp = stations[4].get('web_driver')

        device1_uhp.set_nms_permission(vlan=controllers[0].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        device2_uhp.set_nms_permission(vlan=controllers[1].get('device_vlan'),
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
        cls.station4_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': test_options.get('stations_tx_lvl')
        })
        cls.station5_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': test_options.get('stations_tx_lvl')
        })
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        network = nms_api.create('nms:0', 'network', test_options.get('network'))
        nms_api.create(network, 'teleport', test_options.get('teleport1'))
        cls.balancer = nms_api.create('network:0', 'bal_controller',
                                      {'name': 'balancer1', 'enable': CheckboxStr.OFF,
                                       'bal_interval': '60', 'load_higher': '35'})
        vno = nms_api.create(network, 'vno', {'name': 'vno_test'})
        cls.mf_hub = nms_api.create(network, 'controller', test_options.get('mf_hub'))
        cls.inroute1 = nms_api.create(network, 'controller', test_options.get('inroute1'))

        nms_api.update(cls.mf_hub, {
            'binding': '0',
            'device_ip': controllers[0].get('device_ip'),
            'device_gateway': controllers[0].get('device_gateway'),
            'device_vlan': controllers[0].get('device_vlan'),
            'tdma_sr': 1000
        }
                       )
        nms_api.update(cls.inroute1, {
            'binding': '0',
            'device_ip': controllers[1].get('device_ip'),
            'device_gateway': controllers[1].get('device_gateway'),
            'device_vlan': controllers[1].get('device_vlan'),
        }
                       )

        station1 = nms_api.create(vno, 'station', {
            'name': f'Station1',
            'serial': stations[0].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub,
            'no_balancing': '1'
        }
                                  )
        station2 = nms_api.create(vno, 'station', {
            'name': f'Station2',
            'serial': stations[1].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub
        })
        station3 = nms_api.create(vno, 'station', {
            'name': f'Station3',
            'serial': stations[2].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub
        })
        station4 = nms_api.create(vno, 'station', {
            'name': f'Station4',
            'serial': stations[3].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.inroute1
        })
        station5 = nms_api.create(vno, 'station', {
            'name': f'Station5',
            'serial': stations[4].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.inroute1
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
        nms_api.create(station4, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_local,
            'ip': stations[3].get('device_ip'),
            'id': RouteIds.PRIVATE
        })

        nms_api.create(station4, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_local,
            'ip': '0.0.0.0',
            'gateway': stations[3].get('device_gateway'),
            'mask': '/0',
            'id': RouteIds.PRIVATE
        })
        nms_api.create(station5, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_local,
            'ip': stations[4].get('device_ip'),
            'id': RouteIds.PRIVATE
        })

        nms_api.create(station5, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_local,
            'ip': '0.0.0.0',
            'gateway': stations[4].get('device_gateway'),
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
        nms_api.create(station4, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.5.1'
        })
        nms_api.create(station5, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_ping,
            'ip': '192.168.6.1'
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

        nms_api.update(station1, {'enable': '1'})
        nms_api.update(station2, {'enable': '1'})
        nms_api.update(station3, {'enable': '1'})
        nms_api.update(station4, {'enable': '1'})
        nms_api.update(station5, {'enable': '1'})

        if not nms_api.wait_up(cls.mf_hub, timeout=240):
            test_api.error('Controller is not in UP state')

        if not (nms_api.wait_up(station1) and nms_api.wait_up(station2) and nms_api.wait_up(station3)
                and nms_api.wait_up(station4) and nms_api.wait_up(station5)):
            test_api.error('One of the station is not Up')

        nms_api.update(cls.mf_hub, {
            'bal_enable': CheckboxStr.ON,
            'bal_controller': 'bal_controller:0',
            'lowest_cn': '3',
            'relative_cn': '0',
            'channel_bw': '1300',
            'max_load': '1000'
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

        nms_api.update(cls.balancer, {'enable': CheckboxStr.ON})
        nms_api.wait_ticks(3)

    def test_balancer_st_without_bal(self):

        self.station1_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 270, 'pps_to': 270,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station2_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 200, 'pps_to': 200,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station3_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 150, 'pps_to': 150,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})
        self.station4_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 100, 'pps_to': 100,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station5_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 50, 'pps_to': 50,
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

        # Check actual ctrl on station dashboard
        st1_ctrl_act = nms_api.get_param('station:0', 'rx_ctr_act')
        st1_ctrl_set = nms_api.get_param('station:0', 'rx_controller')
        self.assertEqual(st1_ctrl_act, st1_ctrl_set)

        # Check parameter Load Balancing on Balancer ctrl dashboard (should be 0)
        self.assertEqual(nms_api.get_param('bal_controller:0', 'load_sw'), 0)

        self.station1_uhp.traffic_generator({'enabled': 0})
        self.station2_uhp.traffic_generator({'enabled': 0})
        self.station3_uhp.traffic_generator({'enabled': 0})
        self.station4_uhp.traffic_generator({'enabled': 0})
        self.station5_uhp.traffic_generator({'enabled': 0})

        # Ping stations on Hub
        ip_address_hub = nms_api.get_param('controller:0', 'device_ip')
        self.ctrl_telnet = UhpTelnetDriver(ip_address_hub)

        if not self.ctrl_telnet.ping(ip_address='192.168.2.1', vlan=206):
            self.fail(f'Station1 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.3.1', vlan=206):
            self.fail(f'Station2 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.4.1', vlan=206):
            self.fail(f'Station3 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.5.1', vlan=206):
            self.fail(f'Station3 does not respond to ICMP echo requests!')
        if not self.ctrl_telnet.ping(ip_address='192.168.6.1', vlan=206):
            self.fail(f'Station3 does not respond to ICMP echo requests!')

    def tear_down(self):
        if self.ctrl_telnet is not None:
            self.ctrl_telnet.close()

