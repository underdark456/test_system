import time

from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, StationModes, RouteTypes, RouteIds

options_path = 'test_scenarios.statistics.traffic'
backup_name = 'default_config.txt'


# TODO: compare traffic values in net, vno, and stn as well
class TrafficAllQueueCase(CustomTestCase):
    """MF hub and 7 stations, traffic in all queues"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = 131  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.number_of_stn = 7  # should be less or equal to the number of queues (7)
        cls.controllers, cls.stations = test_api.get_uhp_controllers_stations(
            1, ['UHP200', 'UHP200X'], cls.number_of_stn, ['ANY', ]
        )
        cls.mf_hub_uhp = cls.controllers[0].get('web_driver')
        cls.stn1_uhp = cls.stations[0].get('web_driver')
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)
        options = test_api.get_options(options_path)
        net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        tp = nms_api.create(net, 'teleport', {'name': 'test_tp', 'rx1_lo': 0, 'rx2_lo': 0, 'tx_lo': 0, 'sat_name': 's'})
        cls.mf_hub = nms_api.create(net, 'controller', {
            'name': f'test_ctrl',
            'mode': ControllerModes.MF_HUB,
            'uhp_model': cls.controllers[0].get('model'),
            'teleport': tp,
            'device_ip': cls.controllers[0].get('device_ip'),
            'device_vlan': cls.controllers[0].get('device_vlan'),
            'device_gateway': cls.controllers[0].get('device_gateway'),
            'tx_sr': 3000,
            'rx1_sr': 3000,
            'tx_on': True,
            'tx_level': (46 if options.get('tx_level') + 10 > 46 else options.get('tx_level') + 10),
            'own_cn_high': 50,
            'tdma_sr': 3000
        })
        vno = nms_api.create(net, 'vno', {'name': 'test_vno'})
        local_ser = nms_api.create(net, 'service', {'name': 'local', 'stn_vlan': cls.stations[0].get('device_vlan')})
        rx1_frq, rx1_sr = nms_api.get_param(cls.mf_hub, 'tx_frq'), nms_api.get_param(cls.mf_hub, 'tx_sr')

        for i in range(cls.number_of_stn):
            next_traffic_ser = nms_api.create(
                net,
                'service',
                {'name': f'ser_tr{i+1}', 'hub_vlan': 2006 + i, 'stn_vlan': 3006 + i, 'stn_normal': True},
            )
            next_traffic_qos = nms_api.create(
                net,
                'qos',
                {'name': f'qos_tr{i+1}', 'priority': i}
            )
            next_hub_tr_route = nms_api.create(cls.mf_hub, 'route', {
                'type': RouteTypes.IP_ADDRESS,
                'service': next_traffic_ser,
                'return_qos': next_traffic_qos,
                'ip': f'192.168.{i}.1',
                'id': RouteIds.NORMAL,
            })
            next_stn = nms_api.create(vno, 'station', {
                'name': f'stn{i + 1}',
                'serial': cls.stations[i].get('serial'),
                'enable': True,
                'mode': StationModes.STAR,
                'rx_controller': cls.mf_hub,
            })
            nms_api.create(next_stn, 'route', {
                'type': RouteTypes.IP_ADDRESS,
                'service': local_ser,
                'ip': cls.stations[i].get('device_ip'),
                'id': RouteIds.PRIVATE,
            })
            nms_api.create(next_stn, 'route', {
                'type': RouteTypes.STATIC_ROUTE,
                'service': local_ser,
                'ip': '0.0.0.0',
                'mask': '/0',
                'gateway': cls.stations[i].get('device_gateway'),
                'id': RouteIds.PRIVATE,
            })

            nms_api.create(next_stn, 'route', {
                'type': RouteTypes.IP_ADDRESS,
                'service': next_traffic_ser,
                'forward_qos': next_traffic_qos,
                'ip': f'192.168.{10+i}.1',
                'id': RouteIds.NORMAL,
            })
            cls.stations[i].get('web_driver').star_station(params={
                'rx1_frq': rx1_frq,
                'rx1_sr': rx1_sr,
                'tx_level': options.get('tx_level'),
            })
        cls.mf_hub_uhp.set_nms_permission(
            vlan=cls.controllers[0].get('device_vlan'),
            password=nms_api.get_param(net, 'dev_password')
        )

        if not nms_api.wait_up(cls.mf_hub, timeout=60):
            test_api.error('MF hub is not UP')
        for i in range(cls.number_of_stn):
            if not nms_api.wait_up(f'station:{i}', timeout=60):
                test_api.error(f'Station {i + 1} is not UP')

    def test_controller_traffic(self):
        """Traffic stats for controller"""
        # Stations' traffic pattern: stn1 P1 400kbps, stn2 P2 350kbps, stn3 P3 300kbps
        for i in range(self.number_of_stn):
            self.stations[i].get('web_driver').traffic_generator({
                'enabled': '1',
                'ipv4': f'192.168.{i}.1',
                'vlan': 3006 + i,
                'pps_from': 142 * (8 - i),
                'pps_to': 142 * (8 - i),
            })
        time.sleep(60)
        ctrl_values = nms_api.get_params(self.mf_hub)
        ctl_queue_kbps = ctrl_values.get('forward_rate8')
        ctrl_forward_rate_all = ctrl_values.get('forward_rate_all')
        ctrl_return_rate_all = ctrl_values.get('forward_rate_all')

        for i in range(self.number_of_stn):
            next_forward_rate = ctrl_values.get(f'forward_rate{i + 1}')
            next_return_rate = ctrl_values.get(f'return_rate{i + 1}')
            max_diff = 20 - 2 * i  # allowed difference between expected and actual values in kbps
            self.assertAlmostEqual(
                50 * (8 - i),
                next_return_rate,
                delta=max_diff,
                msg=f'Expected return_rate{i+1}={50 * (8 - i)}, actual return_rate{i + 1}={next_return_rate}'
            )
            self.assertAlmostEqual(
                50 * (8 - i),
                next_forward_rate,
                delta=max_diff,
                msg=f'Expected forward_rate{i+1}={50 * (8 - i)}, actual forward_rate{i+1}={next_forward_rate}'
            )
