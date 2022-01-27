import re

from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, StationModes, RouteTypes, RouteIds, PriorityTypes

options_path = 'test_scenarios.statistics.traffic'
backup_name = 'default_config.txt'


class TrafficEachQueueCase(CustomTestCase):
    """Traffic statistics for MF hub and station, setting a particular queue at a time"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.22'
    __execution_time__ = 300  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        controllers, stations = test_api.get_uhp_controllers_stations(1, ['UHP200', 'UHP200X'], 1, ['ANY'])
        cls.mf_hub_uhp = controllers[0].get('web_driver')
        cls.stn1_uhp = stations[0].get('web_driver')
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)
        options = test_api.get_options(options_path)
        net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        tp = nms_api.create(net, 'teleport', {'name': 'test_tp', 'rx1_lo': 0, 'rx2_lo': 0, 'tx_lo': 0})
        cls.mf_hub = nms_api.create(net, 'controller', {
            'name': f'test_ctrl',
            'mode': ControllerModes.MF_HUB,
            'uhp_model': controllers[0].get('model'),
            'teleport': tp,
            'device_ip': controllers[0].get('device_ip'),
            'device_vlan': controllers[0].get('device_vlan'),
            'device_gateway': controllers[0].get('device_gateway'),
            'tx_sr': 2000,
            'rx1_sr': 2000,
            'tx_on': True,
            'tx_level': (46 if options.get('tx_level') + 10 > 46 else options.get('tx_level') + 10),
            'own_cn_high': 50,
        })
        vno = nms_api.create(net, 'vno', {'name': 'test_vno'})
        local_ser = nms_api.create(net, 'service', {'name': 'local', 'stn_vlan': stations[0].get('device_vlan')})
        cls.stn1 = nms_api.create(vno, 'station', {
            'name': f'stn1',
            'serial': stations[0].get('serial'),
            'enable': True,
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub,
        })
        nms_api.create(cls.stn1, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': local_ser,
            'ip': stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        nms_api.create(cls.stn1, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': local_ser,
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': stations[0].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })
        cls.mf_hub_uhp.set_nms_permission(
            vlan=controllers[0].get('device_vlan'),
            password=nms_api.get_param(net, 'dev_password')
        )
        cls.stn1_uhp.star_station(params={
            'rx1_frq': nms_api.get_param(cls.mf_hub, 'tx_frq'),
            'rx1_sr': nms_api.get_param(cls.mf_hub, 'tx_sr'),
            'tx_level': options.get('tx_level'),
        })
        cls.traffic_ser = nms_api.create(
            net,
            'service',
            {'name': 'ser_tr', 'hub_vlan': 2006, 'stn_vlan': 3006, 'stn_normal': True},
        )
        cls.qos = nms_api.create(net, 'qos', {'name': 'qos_tr'})
        cls.hub_tr_route = nms_api.create(cls.mf_hub, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': cls.traffic_ser,
            'return_qos': cls.qos,
            'ip': '192.168.0.1',
            'id': RouteIds.NORMAL,
        })
        cls.stn_tr_route = nms_api.create(cls.stn1, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': cls.traffic_ser,
            'forward_qos': cls.qos,
            'ip': '192.168.1.1',
            'id': RouteIds.NORMAL,
        })

        if not nms_api.wait_up(cls.mf_hub, timeout=60):
            test_api.error('MF hub is not UP')
        if not nms_api.wait_up(f'station:0'):
            test_api.error(f'Station 1 is not UP')

    def test_traffic_qos_queue(self):
        """Controller statistics for traffic in each queue at a time"""
        test_pps = 2000
        bps = test_pps * 44 * 8
        kbps = round(bps / 1000, 1)
        for queue in range(0, 7):
            nms_api.update(self.qos, {'priority': queue})
            self.mf_hub_uhp.traffic_generator({  # UHP Sat. bandwidth 704000 bps (~687.5 kbps)
                'enabled': '1',
                'ipv4': '192.168.1.1',
                'vlan': 2006,
                'pps_from': test_pps,
                'pps_to': test_pps,
            })
            nms_api.wait_ticks(6)  # in order to let station get new config and update traffic statistics
            ctrl_values = nms_api.get_params(self.mf_hub)
            ctl_queue_kbps = ctrl_values.get('forward_rate8')
            stn_values = nms_api.get_params(self.stn1)

            # Checking load
            self.assertAlmostEqual(
                int(self.mf_hub_uhp.get_support_info_value(regex=re.compile(r'\sload\(%\):\s[0-9]+'))),
                ctrl_values.get('mod_load'),
                delta=3,
                msg=f'Ctrl load fwd={ctrl_values.get("mod_load")} is not as expected'
            )
            self.assertAlmostEqual(
                int(self.mf_hub_uhp.get_support_info_value(regex=re.compile(r'\sload:\s[0-9]+'))),
                ctrl_values.get('rq_total'),
                delta=3,
                msg=f'Ctrl load rtn={ctrl_values.get("rq_total")} is not as expected'
            )
            # checking overall rate
            self.assertAlmostEqual(kbps + ctl_queue_kbps, ctrl_values.get('forward_rate_all'), delta=20)
            for i in range(1, 8):  # Checking all queues but control
                if i - 1 == queue:
                    self.assertAlmostEqual(kbps, ctrl_values.get(f'forward_rate{i}'), delta=20)
                    self.assertAlmostEqual(kbps, ctrl_values.get(f'return_rate{i}'), delta=20)
                else:
                    self.assertEqual(0, ctrl_values.get(f'forward_rate{i}'))
                    self.assertEqual(0, ctrl_values.get(f'return_rate{i}'))
