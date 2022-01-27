from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import CheckboxStr, ControllerModesStr, PriorityTypesStr, RouteTypesStr, \
    StationModesStr
from src.exceptions import InvalidOptionsException
from src.nms_entities.basic_entities.access import Access
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.bal_controller import BalController
from src.nms_entities.basic_entities.camera import Camera
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_port_map import ControllerPortMap
from src.nms_entities.basic_entities.controller_rip import ControllerRip
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.dashboard import Dashboard
from src.nms_entities.basic_entities.device import Device
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.profile import Profile
from src.nms_entities.basic_entities.qos import Qos
from src.nms_entities.basic_entities.scheduler import Scheduler
from src.nms_entities.basic_entities.scheduler_range import SchRange
from src.nms_entities.basic_entities.scheduler_service import SchService
from src.nms_entities.basic_entities.scheduler_task import SchTask
from src.nms_entities.basic_entities.server import Server
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.sr_controller import SrController
from src.nms_entities.basic_entities.sr_license import SrLicense
from src.nms_entities.basic_entities.sr_teleport import SrTeleport
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_port_map import StationPortMap
from src.nms_entities.basic_entities.station_rip import StationRip
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.database_operations.create_delete_loop'
backup_name = 'default_config.txt'


class CreateDeleteCase(CustomTestCase):
    """Create and delete objects multiple times. No backups are called between the iterations"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 230  # approximate test case execution time (100 cycles) in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        cls.number_of_cycles = cls.options.get('number_of_test_cycle')
        if cls.number_of_cycles is None:
            raise InvalidOptionsException('`number_of_cycles` is not provided in the options')

    def test_create_delete_loop(self):
        """Create and delete every single NMS object in a loop"""
        for i in range(self.number_of_cycles):
            # CREATE BLOCK
            network = Network.create(self.driver, 0, {'name': 'test_net'})
            server = Server.create(self.driver, 0, {'name': 'test_server', 'ip': '127.0.0.1', 'enable': CheckboxStr.ON})
            nms_user_group = UserGroup.create(self.driver, 0, {'name': 'nms_group', 'active': CheckboxStr.ON})
            nms_user = User.create(self.driver, nms_user_group.get_id(), {'name': 'nms_user', 'enable': CheckboxStr.ON})
            alert = Alert.create(self.driver, 0, {'name': 'test_alert', 'popup': True})
            nms_access = Access.create(self.driver, 0, {
                'group': f'group:{nms_user_group.get_id()}',
                'edit': CheckboxStr.ON
            })
            nms_dashboard = Dashboard.create(self.driver, 0, {'name': 'nms_dashboard'}, parent_type='nms')
            teleport = Teleport.create(self.driver, network.get_id(), {'name': 'test_teleport'})

            shaper = Shaper.create(self.driver, network.get_id(), {'name': 'test_shaper'})
            policy = Policy.create(self.driver, network.get_id(), {'name': 'test_policy'})
            rule = PolicyRule.create(self.driver, policy.get_id(), {'sequence': 1})
            service = Service.create(self.driver, network.get_id(), {
                'name': 'test_service',
            })
            qos = Qos.create(self.driver, network.get_id(), {
                'name': 'test_qos',
                'priority': PriorityTypesStr.POLICY,
                'policy': f'policy:{policy.get_id()}',
                'shaper': f'shaper:{shaper.get_id()}',
            })
            network_group = UserGroup.create(self.driver, network.get_id(), {
                'name': 'network_group',
                'active': CheckboxStr.ON
            })
            network_user = User.create(self.driver, network_group.get_id(), {
                'name': 'net_user',
                'enable': CheckboxStr.ON
            })
            network_access = Access.create(self.driver, network.get_id(), {
                'group': f'group:{network_group.get_id()}',
                'edit': CheckboxStr.ON,
            })

            controller = Controller.create(self.driver, network.get_id(), {
                'name': 'test_controller',
                'mode': ControllerModesStr.MF_HUB,
                'teleport': f'teleport:{teleport.get_id()}'
            })
            controller_route = ControllerRoute.create(self.driver, controller.get_id(), {
                'type': RouteTypesStr.IP_ADDRESS,
                'service': f'service:{service.get_id()}',
                'ip': '127.0.1.1',
                'mask': '/24',
            })
            controller_rip = ControllerRip.create(self.driver, controller.get_id(), {
                'service': f'service:{service.get_id()}',
                'rip_next_hop': '127.0.1.100',
            })
            controller_access = Access.create(
                self.driver,
                controller.get_id(),
                {'group': f'group:{network_group.get_id()}', 'edit': CheckboxStr.ON, },
                parent_type='controller'
            )
            controller_nat = ControllerPortMap.create(self.driver, controller.get_id(), {
                'external_port': 1111,
                'internal_ip': '127.0.1.4',
                'internal_port': 2222,
            })

            sr_controller = SrController.create(self.driver, network.get_id(), {
                'name': 'test_sr_controller',
                'enable': CheckboxStr.ON,
            })
            sr_teleport = SrTeleport.create(self.driver, sr_controller.get_id(), {
                'name': 'test_sr_teleport',
                'teleport': f'teleport:{teleport.get_id()}',
            })
            device = Device.create(self.driver, sr_teleport.get_id(), {'name': 'test_device', 'ip': '127.0.0.5'})

            sr_license = SrLicense.create(self.driver, network.get_id(), {
                'name': 'test_license',
                'license_key': 'qwerty'
            })

            bal_controller = BalController.create(self.driver, network.get_id(), {
                'name': 'test_bal_controller',
                'enable': CheckboxStr.ON,
            })

            profile = Profile.create(self.driver, network.get_id(), {'name': 'test_profile'})

            camera = Camera.create(self.driver, network.get_id(), {'name': 'test_camera', 'url': 'localhost:1234'})

            network_dashboard = Dashboard.create(
                self.driver,
                network.get_id(),
                {'name': 'network_dashboard'},
                parent_type='network'
            )

            vno = Vno.create(self.driver, network.get_id(), {'name': 'test_vno'})
            vno_user_group = UserGroup.create(self.driver, vno.get_id(), {'name': 'vno_user_group'}, parent_type='vno')
            vno_user = User.create(self.driver, vno_user_group.get_id(), {'name': 'vno_user', 'enable': CheckboxStr.ON})
            vno_access = Access.create(
                self.driver,
                vno.get_id(),
                {'group': f'group:{vno_user_group.get_id()}', 'edit': CheckboxStr.ON, },
                parent_type='vno',
            )
            vno_dashboard = Dashboard.create(
                self.driver,
                vno.get_id(),
                {'name': 'vno_dashboard'},
                parent_type='vno',
            )

            station_vno = Station.create(self.driver, vno.get_id(), {
                'name': 'test_vno_station',
                'enable': CheckboxStr.ON,
                'serial': 12345,
                'mode': StationModesStr.STAR,
                'rx_controller': f'controller:{controller.get_id()}',
                'profile_set': f'profile_set:{profile.get_id()}',
            })
            station_vno_route = StationRoute.create(self.driver, station_vno.get_id(), {
                'type': RouteTypesStr.IP_ADDRESS,
                'service': f'service:{service.get_id()}',
                'ip': '127.0.2.1',
                'mask': '/24',
            })
            station_vno_rip = StationRip.create(self.driver, station_vno.get_id(), {
                'service': f'service:{service.get_id()}',
                'rip_next_hop': '127.0.2.100',
            })
            station_vno_nat = StationPortMap.create(self.driver, station_vno.get_id(), {
                'external_port': 3333,
                'internal_ip': '127.0.2.2',
                'internal_port': 4444,
            })

            sub_vno = Vno.create(self.driver, vno.get_id(), {'name': 'test_sub_vno'}, parent_type='vno')
            sub_vno_user_group = UserGroup.create(
                self.driver,
                sub_vno.get_id(),
                {'name': 'sub_vno_user_group'},
                parent_type='vno'
            )
            sub_vno_user = User.create(self.driver, sub_vno_user_group.get_id(), {
                'name': 'sub_vno_user', 'enable': CheckboxStr.ON
            })
            sub_vno_access = Access.create(
                self.driver,
                sub_vno.get_id(),
                {'group': f'group:{sub_vno_user_group.get_id()}', 'edit': CheckboxStr.ON, },
                parent_type='vno',
            )
            sub_vno_dashboard = Dashboard.create(
                self.driver,
                sub_vno.get_id(),
                {'name': 'sub_vno_dashboard'},
                parent_type='vno',
            )
            station_sub_vno = Station.create(self.driver, sub_vno.get_id(), {
                'name': 'test_sub_vno_station',
                'enable': CheckboxStr.ON,
                'serial': 67898,
                'mode': StationModesStr.STAR,
                'rx_controller': f'controller:{controller.get_id()}',
                'profile_set': f'profile_set:{profile.get_id()}',
            })
            station_sub_vno_route = StationRoute.create(self.driver, station_sub_vno.get_id(), {
                'type': RouteTypesStr.IP_ADDRESS,
                'service': f'service:{service.get_id()}',
                'ip': '127.0.3.1',
                'mask': '/24',
            })
            station_sub_vno_rip = StationRip.create(self.driver, station_sub_vno.get_id(), {
                'service': f'service:{service.get_id()}',
                'rip_next_hop': '127.0.3.100',
            })
            station_sub_vno_nat = StationPortMap.create(self.driver, station_sub_vno.get_id(), {
                'external_port': 3333,
                'internal_ip': '127.0.3.2',
                'internal_port': 4444,
            })

            scheduler = Scheduler.create(self.driver, network.get_id(), {'name': 'test_scheduler'})
            sch_service = SchService.create(self.driver, scheduler.get_id(), {'name': 'test_sch_service'})
            sch_range = SchRange.create(self.driver, scheduler.get_id(), {'name': 'test_sch_range'})
            sch_task = SchTask.create(self.driver, station_vno.get_id(), {
                'name': 'test_sch_task',
                'sch_service': 'sch_service:0'
            })

            # DELETE CHECK BLOCK
            sch_task.delete()
            self.assertEqual(set(), SchTask.scheduler_task_list(self.driver, station_vno.get_id()))
            sch_service.delete()
            self.assertEqual(set(), SchService.scheduler_service_list(self.driver, scheduler.get_id()))
            sch_range.delete()
            self.assertEqual(set(), SchRange.scheduler_range_list(self.driver, scheduler.get_id()))
            scheduler.delete()
            self.assertEqual(set(), Scheduler.scheduler_list(self.driver, network.get_id()))

            station_sub_vno_nat.delete()
            self.assertEqual(set(), StationPortMap.port_map_list(self.driver, station_sub_vno.get_id()))
            station_sub_vno_rip.delete()
            self.assertEqual(set(), StationRip.station_rip_list(self.driver, station_sub_vno.get_id()))
            station_sub_vno_route.delete()
            self.assertEqual(set(), StationRoute.station_route_list(self.driver, station_sub_vno.get_id()))
            station_sub_vno_id = station_sub_vno.get_id()
            station_sub_vno.delete()
            self.assertNotIn(station_sub_vno_id, Station.station_list(self.driver, sub_vno.get_id()))

            sub_vno_dashboard_id = sub_vno_dashboard.get_id()
            sub_vno_dashboard.delete()
            self.assertNotIn(
                sub_vno_dashboard_id,
                Dashboard.dashboard_list(self.driver, sub_vno.get_id(), parent_type='vno')
            )

            sub_vno_access_id = sub_vno_access.get_id()
            sub_vno_access.delete()
            self.assertNotIn(
                sub_vno_access_id,
                Access.access_list(self.driver, sub_vno.get_id(), parent_type='vno')
            )
            sub_vno_user_id = sub_vno_user.get_id()
            sub_vno_user.delete()
            self.assertNotIn(
                sub_vno_user_id,
                User.user_list(self.driver, sub_vno_user_group.get_id())
            )
            sub_vno_user_group_id = sub_vno_user_group.get_id()
            sub_vno_user_group.delete()
            self.assertNotIn(
                sub_vno_user_group_id,
                UserGroup.user_group_list(self.driver, sub_vno.get_id(), parent_type='vno')
            )
            sub_vno_id = sub_vno.get_id()
            sub_vno.delete()
            self.assertNotIn(
                sub_vno_id,
                Vno.vno_list(self.driver, vno.get_id(), parent_type='vno')
            )

            station_vno_nat_id = station_vno_nat.get_id()
            station_vno_nat.delete()
            self.assertNotIn(station_vno_nat_id, StationPortMap.port_map_list(self.driver, station_vno.get_id()))
            station_vno_rip_id = station_vno_rip.get_id()
            station_vno_rip.delete()
            self.assertNotIn(station_vno_rip_id, StationRip.station_rip_list(self.driver, station_vno.get_id()))
            station_vno_route_id = station_vno_route.get_id()
            station_vno_route.delete()
            self.assertNotIn(station_vno_route_id, StationRoute.station_route_list(self.driver, station_vno.get_id()))
            station_vno.delete()

            vno_dashboard_id = vno_dashboard.get_id()
            vno_dashboard.delete()
            self.assertNotIn(vno_dashboard_id, Dashboard.dashboard_list(self.driver, vno.get_id(), parent_type='vno'))
            vno_access_id = vno_access.get_id()
            vno_access.delete()
            self.assertNotIn(vno_access_id, Access.access_list(self.driver, vno.get_id(), parent_type='vno'))
            vno_user_id = vno_user.get_id()
            vno_user.delete()
            self.assertNotIn(vno_user_id, User.user_list(self.driver, vno_user_group.get_id()))
            vno_user_group.delete()
            vno_id = vno.get_id()
            vno.delete()
            self.assertNotIn(vno_id, Vno.vno_list(self.driver, network.get_id()))

            camera_id = camera.get_id()
            camera.delete()
            self.assertNotIn(camera_id, Camera.camera_list(self.driver, network.get_id()))
            profile_id = profile.get_id()
            profile.delete()
            self.assertNotIn(profile_id, Profile.profile_list(self.driver, network.get_id()))
            bal_controller_id = bal_controller.get_id()
            bal_controller.delete()
            self.assertNotIn(bal_controller_id, BalController.bal_controller_list(self.driver, network.get_id()))
            sr_license.delete()

            device_id = device.get_id()
            device.delete()
            self.assertNotIn(device_id, Device.device_list(self.driver, sr_teleport.get_id()))
            sr_teleport_id = sr_teleport.get_id()
            sr_teleport.delete()
            self.assertNotIn(sr_teleport_id, SrTeleport.sr_teleport_list(self.driver, sr_controller.get_id()))
            sr_controller_id = sr_controller.get_id()
            sr_controller.delete()
            self.assertNotIn(sr_controller_id, SrController.sr_controller_list(self.driver, network.get_id()))

            controller_nat_id = controller_nat.get_id()
            controller_nat.delete()
            self.assertNotIn(controller_nat_id, ControllerPortMap.port_map_list(self.driver, controller.get_id()))
            controller_rip_id = controller_rip.get_id()
            controller_rip.delete()
            self.assertNotIn(controller_rip_id, ControllerRip.controller_rip_list(self.driver, controller.get_id()))
            controller_route_id = controller_route.get_id()
            controller_route.delete()
            self.assertNotIn(
                controller_route_id,
                ControllerRoute.controller_route_list(self.driver, controller.get_id())
            )
            controller_access_id = controller_access.get_id()
            controller_access.delete()
            self.assertNotIn(
                controller_access_id,
                Access.access_list(self.driver, controller.get_id(), parent_type='controller')
            )
            controller_id = controller.get_id()
            controller.delete()
            self.assertNotIn(controller_id, Controller.controller_list(self.driver, network.get_id()))

            network_access_id = network_access.get_id()
            network_access.delete()
            self.assertNotIn(
                network_access_id,
                Access.access_list(self.driver, network.get_id(), parent_type='network')
            )

            network_user_id = network_user.get_id()
            network_user.delete()
            self.assertNotIn(network_user_id, User.user_list(self.driver, network_group.get_id()))
            network_group_id = network_group.get_id()
            network_group.delete()
            self.assertNotIn(
                network_group_id,
                UserGroup.user_group_list(self.driver, network.get_id(), parent_type='network')
            )
            network_dashboard_id = network_dashboard.get_id()
            network_dashboard.delete()
            self.assertNotIn(
                network_dashboard_id,
                Dashboard.dashboard_list(self.driver, network.get_id(), parent_type='network')
            )

            service_id = service.get_id()
            service.delete()
            self.assertNotIn(service_id, Service.service_list(self.driver, network.get_id()))
            qos_id = qos.get_id()
            qos.delete()
            self.assertNotIn(qos_id, Qos.qos_list(self.driver, network.get_id()))

            rule_id = rule.get_id()
            rule.delete()
            self.assertNotIn(rule_id, PolicyRule.policy_rules_list(self.driver, policy.get_id()))
            policy_id = policy.get_id()
            policy.delete()
            self.assertNotIn(policy_id, Policy.policy_list(self.driver, network.get_id()))
            shaper_id = shaper.get_id()
            shaper.delete()
            self.assertNotIn(shaper_id, Shaper.shaper_list(self.driver, network.get_id()))
            teleport_id = teleport.get_id()
            teleport.delete()
            self.assertNotIn(teleport_id, Teleport.teleport_list(self.driver, network.get_id()))
            nms_dashboard_id = nms_dashboard.get_id()
            nms_dashboard.delete()
            self.assertNotIn(nms_dashboard_id, Dashboard.dashboard_list(self.driver, 0))
            nms_access_id = nms_access.get_id()
            nms_access.delete()
            self.assertNotIn(nms_access_id, Access.access_list(self.driver, 0))
            nms_user_id = nms_user.get_id()
            nms_user.delete()
            self.assertNotIn(nms_user_id, User.user_list(self.driver, nms_user_group.get_id()))
            nms_user_group_id = nms_user_group.get_id()
            nms_user_group.delete()
            self.assertNotIn(nms_user_group_id, UserGroup.user_group_list(self.driver, 0))
            alert_id = alert.get_id()
            alert.delete()
            self.assertNotIn(alert_id, Alert.alert_list(self.driver, 0))
            server_id = server.get_id()
            server.delete()
            self.assertNotIn(server_id, Server.server_list(self.driver, 0))

            network_id = network.get_id()
            network.delete()
            self.assertNotIn(network_id, Network.network_list(self.driver, 0))
