from src.enum_types_constants import RuleTypes, ActionTypes, QueueTypes, RouteTypes, PriorityTypes
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.teleport import Teleport
from src.options_providers.options_provider import OptionsProvider
from test_scenarios.composite_scenarios.abstract_case import _AbstractCase

__author__ = 'dkudryashov'
__version__ = '0.1'
options_path = 'test_scenarios.composite_scenarios.all_queues'
backup_name = 'default_config.txt'


# TODO: need to be fixed in order to comply with NMS 4.0.0.20
class ConfigForAllQueuesTwoHubsCase(_AbstractCase):
    """Config creation for all queues traffic case in a network featuring two hubs"""
    # Simple case that creates two hubs in a network to check traffic statistics.
    # Seven Network TX are created in each hub  using services in the manner that traffic from
    # a given vlan gets into a corresponding modulator queue.

    backup = None

    @classmethod
    def set_up_class(cls):
        super().set_up_class()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        cls.controller1_ip = cls.options.get('controller_star').get('device_ip')
        cls.controller2_ip = cls.options.get('station_ip').get('device_ip')

    def test_create_network(self):
        net = Network.create(self.driver, 0, params=self.options.get('network'))
        tp = Teleport.create(self.driver, net.get_id(), params=self.options.get('teleport'))
        controller1 = Controller.create(self.driver, net.get_id(), params=self.options.get('controller'))
        options2 = self.options.get('controller')
        options2['device_ip'] = self.controller2_ip
        options2['name'] = 'HL_MAS2'
        options2['mf1_rx'] = 960000
        options2['mf1_tx'] = 960000
        controller2 = Controller.create(self.driver, net.get_id(), params=options2)

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

        hub_vlan = 206
        for i in range(7):
            ser = Service.create(self.driver, net.get_id(), params={
                'name': f'ser-{i}',
                'hub_priority': PriorityTypes.POLICY,
                'hub_policy': f'policy:{i}',
                'hub_vlan': hub_vlan,
                #'stn_priority': PriorityTypes.POLICY,
                #'stn_policy': f'policy:{i}',
                #'stn_vlan': 206,
                'ctr_normal': 0,
                'ctr_gateway': 0,
                'ctr_mesh': 0,
                'stn_normal': 0,
                'stn_gateway': 0,
                'stn_mesh': 0,
            })
            hub_vlan += 1
            net_tx_hub1 = ControllerRoute.create(self.driver, controller1.get_id(), params={
                'type': RouteTypes.NETWORK_TX,
                'service': f'service:{i}',
                'ip': self.options.get('test_ip')
            })
        for i in range(7, 14):
            ser = Service.create(self.driver, net.get_id(), params={
                'name': f'ser-{i}',
                'hub_priority': PriorityTypes.POLICY,
                'hub_policy': f'policy:{i-7}',
                'hub_vlan': hub_vlan,
                #'stn_priority': PriorityTypes.POLICY,
                #'stn_policy': f'policy:{i}',
                #'stn_vlan': 206,
                'ctr_normal': 0,
                'ctr_gateway': 0,
                'ctr_mesh': 0,
                'stn_normal': 0,
                'stn_gateway': 0,
                'stn_mesh': 0,
            })
            hub_vlan += 1
            net_tx_hub2 = ControllerRoute.create(self.driver, controller2.get_id(), params={
                'type': RouteTypes.NETWORK_TX,
                'service': f'service:{i}',
                'ip': self.options.get('test_ip'),
            })
        self.backup.create_backup('all_queues_pol_two_hubs.txt')
