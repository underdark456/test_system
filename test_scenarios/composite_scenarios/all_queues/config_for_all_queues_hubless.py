from unittest import skip

from src.enum_types_constants import RuleTypes, ActionTypes, QueueTypes, RouteTypes, PriorityTypes, RouteIds
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider
from test_scenarios.composite_scenarios.abstract_case import _AbstractCase

__author__ = 'dkudryashov'
__version__ = '0.2'
options_path = 'test_scenarios.composite_scenarios.all_queues'
backup_name = 'default_config.txt'


# TODO: need to be fixed in order to comply with NMS 4.0.0.20
class ConfigForAllQueuesHublessCase(_AbstractCase):
    """Config creation for all queues traffic case in a hubless network"""
    # Simple case that creates a config that features a hubless network with a master and a station.
    # Seven Network TX are created in the hub and the station using services in the manner that traffic from
    # a given vlan gets into a corresponding modulator queue.

    backup = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        cls.controller_ip = cls.options.get('controller').get('device_ip')
        cls.station_ip = cls.options.get('station_ip').get('device_ip')

    def test_create_network(self):
        net = Network.create(self.driver, 0, params=self.options.get('network'))
        tp = Teleport.create(self.driver, net.get_id(), params=self.options.get('teleport'))
        hubless_controller = Controller.create(self.driver, net.get_id(),params=self.options.get('controller'))
        vno = Vno.create(self.driver, net.get_id(), params=self.options.get('vno'))
        stn = Station.create(self.driver, vno.get_id(), params=self.options.get('station'))

        # Create 7 policies with ACTION SET QUEUE. Queues are incremented in each step
        queues = [*QueueTypes()]
        for i in range(len(queues)):
            pol = Policy.create(self.driver, net.get_id(), params={'name': f'pol-{i+1}'})
            pol_rule = PolicyRule.create(self.driver, pol.get_id(), params={
                 'sequence': 1,
                 'type': RuleTypes.ACTION,
                 'action_type': ActionTypes.SET_QUEUE,
                 'queue': queues[i]
                }
                                  )
        def_service = Service.create(self.driver, net.get_id(), params={
            'name': 'def_service',
            'ctr_normal': 0,
            'ctr_gateway': 0,
            'ctr_mesh': 0,
            'stn_normal': 0,
            'stn_gateway': 0,
            'stn_mesh': 0,
        })
        # Return station IP address
        StationRoute.create(self.driver, stn.get_id(), params={
            'type': RouteTypes.IP_ADDRESS,
            'service': 'service:0',
            'ip': self.options.get('station_ip').get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        StationRoute.create(self.driver, stn.get_id(), params={
            'type': RouteTypes.STATIC_ROUTE,
            'service': 'service:0',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': self.options.get('station_ip').get('device_ip'),
            'id': RouteIds.PRIVATE,
        })

        hub_vlan = 206
        stn_vlan = 306
        for i in range(7):
            ser = Service.create(self.driver, net.get_id(), params={
                'name': f'ser-{i+1}',
                'hub_priority': PriorityTypes.POLICY,
                'hub_policy': f'policy:{i}',
                'hub_vlan': hub_vlan,
                'stn_priority': PriorityTypes.POLICY,
                'stn_policy': f'policy:{i}',
                'stn_vlan': stn_vlan,
                'ctr_normal': 0,
                'ctr_gateway': 0,
                'ctr_mesh': 0,
                'stn_normal': 0,
                'stn_gateway': 0,
                'stn_mesh': 0,
            })
            net_tx_hub = ControllerRoute.create(self.driver, hubless_controller.get_id(), params={
                'type': RouteTypes.NETWORK_TX,
                'service': f'service:{i+1}',
                'ip': self.options.get('test_ip')
            })
            net_tx_stn = StationRoute.create(self.driver, stn.get_id(), params={
                'type': RouteTypes.NETWORK_TX,
                'service': f'service:{i+1}',
                'ip': self.options.get('test_ip'),
            })
            hub_vlan += 1
            stn_vlan += 1
        self.backup.create_backup('all_queues_policies_hubless.txt')
