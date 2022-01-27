from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, RouteTypes, StationModes
from src.exceptions import ObjectNotCreatedException

options_path = 'test_scenarios.form_validation.routing'
backup_name = 'default_config.txt'


class RoutingSameMaskCase(CustomTestCase):
    """Valid and invalid routing combinations for controller and station, Ticket 8097"""

    __author__ = 'dkudryashov'
    __version__ = '0.1'
    __execution_time__ = None  # approximate case execution time in seconds

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))

    def set_up(self):
        nms_api.load_config(backup_name)
        net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        tp = nms_api.create(net, 'teleport', {'name': 'test_tp'})
        # Service without route auto-generation
        self.ser = nms_api.create(net, 'service', {
            'name': 'no_auto_gen',
            'hub_vlan': 206,
            'stn_vlan': 306,
            'ctr_normal': False,
            'ctr_gateway': False,
            'ctr_mesh': False,
            'stn_normal': False,
            'stn_gateway': False,
            'stn_mesh': False,
        })
        # Service with route auto-generation
        self.ser2 = nms_api.create(net, 'service', {
            'name': 'auto_gen',
            'hub_vlan': 1006,
            'stn_vlan': 4006,
            'ctr_normal': True,
            'ctr_gateway': True,
            'ctr_mesh': True,
            'stn_normal': True,
            'stn_gateway': True,
            'stn_mesh': True,
        })

        self.mf_hub = nms_api.create(net, 'controller', {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp
        })
        vno = nms_api.create(net, 'vno', {'name': 'test_vno'})
        self.stn = nms_api.create(vno, 'station', {
            'name': 'stn1',
            'enable': True,
            'mode': StationModes.STAR,
            'serial': 12345,
            'rx_controller': self.mf_hub,
        })

        # Controller and station IP_addresses without route auto-generation
        nms_api.create(self.mf_hub, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': self.ser,
            'ip': '10.0.0.1',
            'mask': '/24',
        })
        # nms_api.create(self.stn, 'route', {
        #     'type': RouteTypes.IP_ADDRESS,
        #     'service': self.ser,
        #     'ip': '10.0.0.2',
        #     'mask': '/24',
        # })

        # Controller and station IP_addresses with route auto-generation
        nms_api.create(self.mf_hub, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': self.ser2,
            'ip': '10.0.0.1',
            'mask': '/24',
        })

        nms_api.create(self.stn, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': self.ser2,
            'ip': '10.0.0.2',
            'mask': '/24',
        })

    def test_valid_ctrl(self):
        """No routes auto generation: ctrl ip=10.0.0.1/24, ctrl tx=10.0.0.0/26, ctrl static ip=10.0.0.0/16"""
        nms_api.create(self.mf_hub, 'route', {
            'type': RouteTypes.NETWORK_TX,
            'service': self.ser,
            'ip': '10.0.0.0',
            'mask': '/26',
        })
        nms_api.create(self.mf_hub, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': self.ser,
            'ip': '10.0.0.0',
            'mask': '/16',
            'gateway': '127.0.0.1',
        })

    def test_valid_stn(self):
        """No routes auto generation: stn ip=10.0.0.2/24, stn tx=10.0.0.0/26, stn static ip=10.0.0.0/16"""
        nms_api.create(self.stn, 'route', {
            'type': RouteTypes.NETWORK_TX,
            'service': self.ser,
            'ip': '172.16.0.0',
            'mask': '/26',
        })
        nms_api.create(self.stn, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': self.ser,
            'ip': '172.16.0.0',
            'mask': '/16',
            'gateway': '127.0.1.1',
        })

    def test_valid_ctrl_auto(self):
        """Routes auto generation: ctrl ip=10.0.0.1/24, stn ip=10.0.0.2/24, ctrl static ip=10.0.0.0/16"""
        with self.assertRaises(
                ObjectNotCreatedException,
                msg=f'Static route to 10.0.0.0/24 is created in Controller using service with routes auto-generation'
        ):
            nms_api.create(self.mf_hub, 'route', {
                'type': RouteTypes.STATIC_ROUTE,
                'service': self.ser2,
                'ip': '10.0.0.0',
                'mask': '/24',
                'gateway': '172.16.78.1',
            })

    def test_valid_stn_auto(self):
        """Routes auto generation: ctrl ip=10.0.0.1/24, stn ip=10.0.0.2/24, stn static ip=10.0.0.0/16"""
        with self.assertRaises(
                ObjectNotCreatedException,
                msg=f'Static route to 10.0.0.0/24 is created in Station using service with routes auto-generation'
        ):
            nms_api.create(self.stn, 'route', {
                'type': RouteTypes.STATIC_ROUTE,
                'service': self.ser2,
                'ip': '10.0.0.0',
                'mask': '/16',
                'gateway': '172.16.54.2',
            })

    def test_invalid_ctrl(self):
        """No routes auto generation: ctrl ip=10.0.0.1/24, ctrl tx=10.0.0.0/24, ctrl static ip=10.0.0.0/24"""
        nms_api.create(self.mf_hub, 'route', {
            'type': RouteTypes.NETWORK_TX,
            'service': self.ser,
            'ip': '10.0.0.0',
            'mask': '/24',
        })
        with self.assertRaises(
                ObjectNotCreatedException,
                msg=f'Static route to 10.0.0.0/24 via 127.0.0.1 with existing Network_TX 10.0.0.0/24'
        ):
            nms_api.create(self.mf_hub, 'route', {
                'type': RouteTypes.STATIC_ROUTE,
                'service': self.ser,
                'ip': '10.0.0.0',
                'mask': '/24',
                'gateway': '127.0.0.1',
            })

    def test_invalid_stn(self):
        """No routes auto generation: stn ip=10.0.0.2/24, stn tx=10.0.0.0/24, stn static ip=10.0.0.0/24"""
        nms_api.create(self.stn, 'route', {
            'type': RouteTypes.NETWORK_TX,
            'service': self.ser,
            'ip': '10.0.0.0',
            'mask': '/24',
        })

        with self.assertRaises(
                ObjectNotCreatedException,
                msg=f'Static route to 10.0.0.0/24 via 127.0.1.1 with existing Network_TX 10.0.0.0/24'
        ):
            nms_api.create(self.stn, 'route', {
                'type': RouteTypes.STATIC_ROUTE,
                'service': self.ser,
                'ip': '10.0.0.0',
                'mask': '/24',
                'gateway': '127.0.1.1',
            })

    def test_invalid_ctrl_auto(self):
        """Routes auto generation: ctrl ip=10.0.0.1/24, stn ip=10.0.0.2/24, ctrl static ip=10.0.0.0/24"""
        with self.assertRaises(
                ObjectNotCreatedException,
                msg=f'Static route to 10.0.0.0/24 is created in Controller using service with routes auto-generation'
        ):
            nms_api.create(self.mf_hub, 'route', {
                'type': RouteTypes.STATIC_ROUTE,
                'service': self.ser2,
                'ip': '10.0.0.0',
                'mask': '/24',
                'gateway': '172.16.78.1',
            })

    def test_invalid_stn_auto(self):
        """Routes auto generation: ctrl ip=10.0.0.1/24, stn ip=10.0.0.2/24, stn static ip=10.0.0.0/24"""
        with self.assertRaises(
                ObjectNotCreatedException,
                msg=f'Static route to 10.0.0.0/24 is created in Station using service with routes auto-generation'
        ):
            nms_api.create(self.stn, 'route', {
                'type': RouteTypes.STATIC_ROUTE,
                'service': self.ser2,
                'ip': '10.0.0.0',
                'mask': '/24',
                'gateway': '172.16.54.2',
            })
