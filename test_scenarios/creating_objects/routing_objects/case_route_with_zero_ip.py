from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, RouteTypes
from src.exceptions import ObjectNotCreatedException

options_path = 'test_scenarios.creating_objects.routing_objects'
backup_name = 'default_config.txt'


class RouteWithZeroIpCase(CustomTestCase):
    """Create routes with zero IP address"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = 5  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)
        net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        tp = nms_api.create(net, 'teleport', {'name': 'test_tp'})
        cls.mf_hub = nms_api.create(
            net,
            'controller',
            {'name': 'mf_hub', 'mode': ControllerModes.MF_HUB, 'teleport': tp}
        )
        cls.ser = nms_api.create(net, 'service', {'name': 'test_ser'})

    def test_ip_address(self):
        """Create IP_address with ip=0.0.0.0"""
        with self.assertRaises(ObjectNotCreatedException):
            nms_api.create(self.mf_hub, 'route', {
                'type': RouteTypes.IP_ADDRESS,
                'service': self.ser,
                'ip': '0.0.0.0',
            })

    def test_static_route(self):
        """Create Static_route with gateway=0.0.0.0"""
        with self.assertRaises(ObjectNotCreatedException):
            nms_api.create(self.mf_hub, 'route', {
                'type': RouteTypes.STATIC_ROUTE,
                'service': self.ser,
                'gateway': '0.0.0.0',
            })

    def test_ipv6_address(self):
        """Create IPv6_address with v6_ip=::"""
        with self.assertRaises(ObjectNotCreatedException):
            nms_api.create(self.mf_hub, 'route', {
                'type': RouteTypes.IPV6_ADDRESS,
                'service': self.ser,
                'v6_ip': '::',
            })

    def test_ipv6_route(self):
        """Create IPv6_address with v6_gateway=::"""
        with self.assertRaises(ObjectNotCreatedException):
            nms_api.create(self.mf_hub, 'route', {
                'type': RouteTypes.IPV6_ROUTE,
                'service': self.ser,
                'v6_gateway': '::',
            })
