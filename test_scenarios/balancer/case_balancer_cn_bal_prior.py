import time

from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.drivers.uhp.uhp_telnet_driver import UhpTelnetDriver
from src.enum_types_constants import StationModes, RouteTypes, CheckboxStr, RouteIds, TdmaModcod

options_path = 'test_scenarios.balancer'
backup_name = 'default_config.txt'


class BalancerCnBalPriorCase(CustomTestCase):
    """The test to check priority of switching - low c/n then load balancing 2.15"""

    __author__ = 'vpetuhova'
    __version__ = '4.0.0.27'
    __review__ = ''
    __execution_time__ = 360  # approximate test case execution time in seconds
    ctrl_telnet = None

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        controllers, stations = test_api.get_uhp_controllers_stations(3, ['UHP200'], 4,
                                                                      ['ANY',])
        test_options = test_api.get_options(options_path)

        device1_uhp = controllers[0].get('web_driver')
        device2_uhp = controllers[1].get('web_driver')
        cls.device3_uhp = controllers[2].get('web_driver')
        cls.station1_uhp = stations[0].get('web_driver')
        cls.station2_uhp = stations[1].get('web_driver')
        cls.station3_uhp = stations[2].get('web_driver')
        cls.station4_uhp = stations[3].get('web_driver')

        device1_uhp.set_nms_permission(vlan=controllers[0].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        device2_uhp.set_nms_permission(vlan=controllers[1].get('device_vlan'),
                                       password=test_options.get('network').get('dev_password'))
        cls.device3_uhp.scpc_modem(params={
            'rx1_frq': '1000300', 'rx1_sr': '5000',
            'tx_frq': '1000300', 'tx_sr': '5000',
            'tx_on': '1', 'tx_level': '46.0'
        })

        tx_lvl = test_options.get('stations_tx_lvl')
        cls.station1_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': tx_lvl + 2  # + 4
        })
        cls.station2_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': tx_lvl
        })
        cls.station3_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': tx_lvl - 2
        })
        cls.station4_uhp.star_station(params={
            'rx1_sr': test_options.get('mf_hub').get('tx_sr'),
            'rx1_frq': test_options.get('mf_hub').get('tx_frq'),
            'tx_level': tx_lvl
        })
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        network = nms_api.create('nms:0', 'network', test_options.get('network'))
        nms_api.create(network, 'teleport', test_options.get('teleport1'))
        cls.balancer = nms_api.create('network:0', 'bal_controller',
                                      {'name': 'balancer', 'enable': CheckboxStr.OFF,
                                       'bal_interval': '100', 'load_higher': '35', 'low_cn_time': '100'})
        vno = nms_api.create(network, 'vno', {'name': 'vno_test'})
        cls.mf_hub = nms_api.create(network, 'controller', test_options.get('mf_hub'))
        cls.inroute1 = nms_api.create(network, 'controller', test_options.get('inroute1'))

        nms_api.update(cls.mf_hub, {
            'binding': '0',
            'device_ip': controllers[0].get('device_ip'),
            'device_gateway': controllers[0].get('device_gateway'),
            'device_vlan': controllers[0].get('device_vlan'),
            'tdma_sr': 1000,
            'tdma_mc': TdmaModcod._8PSK_2_3
        }
                       )
        nms_api.update(cls.inroute1, {
            'binding': '0',
            'device_ip': controllers[1].get('device_ip'),
            'device_gateway': controllers[1].get('device_gateway'),
            'device_vlan': controllers[1].get('device_vlan'),
            'tdma_sr': 1000,
            'tdma_mc': TdmaModcod._QPSK_2_3
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

        if not nms_api.wait_up(cls.mf_hub, timeout=240):
            test_api.error('Controller is not in UP state')

        if not (nms_api.wait_up(station1) and nms_api.wait_up(station2) and nms_api.wait_up(station3)
                and nms_api.wait_up(station4)):
            test_api.error('One of the station is not Up')

        nms_api.update(cls.mf_hub, {
            'bal_enable': CheckboxStr.ON,
            'bal_controller': 'bal_controller:0',
            'lowest_cn': '10',
            'relative_cn': '3',
            'channel_bw': '1900',
            'max_load': '1500'
        }
                       )
        nms_api.update(cls.inroute1, {
            'bal_enable': CheckboxStr.ON,
            'bal_controller': 'bal_controller:0',
            'lowest_cn': '4',
            'relative_cn': '0',
            'channel_bw': '1300',
            'max_load': '1000'
        }
                       )

        nms_api.update(cls.balancer, {'enable': CheckboxStr.ON})
        nms_api.wait_ticks(3)

    def test_balancer_cn_bal_prior(self):

        # Increase noise level to switch station due to low_cn fault
        st1_hub_cn = nms_api.get_param('station:0', 'cn_on_hub')
        tx_lvl = 46
        while st1_hub_cn > 9.8:
            if tx_lvl <= 1:
                self.fail(f'Cannot adjust SCPC modem TX level (noise level) to get desired station 1 CN at Hub')
            self.device3_uhp.scpc_modem(params={
                'rx1_frq': '1000300', 'rx1_sr': '5000',
                'tx_frq': '1000300', 'tx_sr': '5000',
                'tx_on': '1', 'tx_level': tx_lvl
            })
            nms_api.wait_ticks(2)
            tx_lvl = round(tx_lvl - 0.3, 1)
            st1_hub_cn = nms_api.get_param('station:0', 'cn_on_hub')
            print(st1_hub_cn, tx_lvl)

        self.station1_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 300, 'pps_to': 300,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station2_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 150, 'pps_to': 150,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        self.station3_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 400, 'pps_to': 400,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})
        self.station4_uhp.traffic_generator({'enabled': 1, 'vlan': 306,
                                             'ipv4': '192.168.1.1',
                                             'pps_from': 100, 'pps_to': 100,
                                             'pkt_len_from': 250, 'pkt_len_to': 250})

        for _ in range(5):
            nms_api.wait_ticks(3)
            st1_rate = nms_api.get_param('station:0', 'return_rate1')
            if st1_rate > 500:
                break
        else:
            self.fail(f'Station1 return_rate1 is unexpectedly lower than 500')
        time.sleep(100)
        nms_api.wait_ticks(3)

        # Check parameter Load Balancing on Balancer ctrl dashboard (should be 0)
        # self.assertEqual(nms_api.get_param('bal_controller:0', 'load_sw'), 0)
        # Check parameter Low CN on Balancer ctrl dashboard (should be 1)
        self.assertEqual(nms_api.get_param('bal_controller:0', 'level_sw'), 1)

        self.station1_uhp.traffic_generator({'enabled': 0})
        self.station2_uhp.traffic_generator({'enabled': 0})
        self.station3_uhp.traffic_generator({'enabled': 0})
        self.station4_uhp.traffic_generator({'enabled': 0})

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

    def tear_down(self):
        if self.ctrl_telnet is not None:
            self.ctrl_telnet.close()

