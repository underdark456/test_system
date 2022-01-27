from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_HIERARCHY
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes, RuleTypes, ActionTypes, PriorityTypes, RouteTypes, \
    BindingModes, RouteIds
from src.file_manager.file_manager import FileManager
from src.nms_entities.basic_entities.bal_controller import BalController
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_rip import ControllerRip
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.profile import Profile
from src.nms_entities.basic_entities.qos import Qos
from src.nms_entities.basic_entities.scheduler import Scheduler
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.sr_controller import SrController
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_rip import StationRip
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api.validation'
backup_name = 'default_config.txt'


class ApiParentValidationCase(CustomTestCase):
    """Check if objects belonging to a network cannot be assigned to objects in another network"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.21'
    __execution_time__ = 6
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        fm = FileManager()
        fm.upload_uhp_software('dummy_soft.240')
        cls.net1 = Network.create(cls.driver, 0, params={'name': 'net-0'})
        cls.net2 = Network.create(cls.driver, 0, params={'name': 'net-1'})
        cls.tp1 = Teleport.create(cls.driver, cls.net1.get_id(), params={'name': 'tp-1'})
        cls.tp2 = Teleport.create(cls.driver, cls.net2.get_id(), params={'name': 'tp-2'})
        cls.ctrl1 = Controller.create(cls.driver, cls.net1.get_id(), params={
            'name': 'ctrl-1',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{cls.tp1.get_id()}'
        })
        cls.ctrl2 = Controller.create(cls.driver, cls.net2.get_id(), params={
            'name': 'ctrl-2',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{cls.tp2.get_id()}'
        })
        cls.vno1 = Vno.create(cls.driver, cls.net1.get_id(), params={'name': 'vno-1'})
        cls.vno2 = Vno.create(cls.driver, cls.net2.get_id(), params={'name': 'vno-2'})
        cls.sub_vno1 = Vno.create(cls.driver, cls.vno1.get_id(), params={'name': 'vno-1'}, parent_type='vno')
        cls.sub_vno2 = Vno.create(cls.driver, cls.vno2.get_id(), params={'name': 'vno-2'}, parent_type='vno')
        cls.shp1 = Shaper.create(cls.driver, cls.net1.get_id(), params={'name': 'shp-1'})
        cls.shp2 = Shaper.create(cls.driver, cls.net2.get_id(), params={'name': 'shp-2'})
        cls.stn1 = Station.create(cls.driver, cls.vno1.get_id(), params={
            'name': 'stn-1',
            'serial': 1,
            'mode': StationModes.MESH
        })
        cls.stn2 = Station.create(cls.driver, cls.vno2.get_id(), params={
            'name': 'stn-2',
            'serial': 2,
            'mode': StationModes.MESH
        })
        cls.profile_set1 = Profile.create(cls.driver, cls.net1.get_id(), params={'name': 'pro_set-1'})
        cls.profile_set2 = Profile.create(cls.driver, cls.net2.get_id(), params={'name': 'pro_set-2'})
        cls.ser1 = Service.create(cls.driver, cls.net1.get_id(), params={'name': 'ser-1'})
        cls.ser2 = Service.create(cls.driver, cls.net2.get_id(), params={'name': 'ser-2 '})
        cls.qos1 = Qos.create(cls.driver, cls.net1.get_id(), params={'name': 'qos-1'})
        cls.qos2 = Qos.create(cls.driver, cls.net2.get_id(), params={'name': 'qos-2 '})
        cls.pol1 = Policy.create(cls.driver, cls.net1.get_id(), params={'name': 'pol-1'})
        cls.pol2 = Policy.create(cls.driver, cls.net2.get_id(), params={'name': 'pol-2'})
        cls.rule1 = PolicyRule.create(cls.driver, cls.pol1.get_id(), params={
            'sequence': 1,
            'type': RuleTypes.ACTION,
            'action_type': ActionTypes.DROP
        })
        cls.rule2 = PolicyRule.create(cls.driver, cls.pol2.get_id(), params={
            'sequence': 1,
            'type': RuleTypes.ACTION,
            'action_type': ActionTypes.DROP
        })
        cls.sr_ctrl1 = SrController.create(cls.driver, cls.net1.get_id(), params={'name': 'sr_ctrl-1', 'enable': 'ON'})
        cls.sr_ctrl2 = SrController.create(cls.driver, cls.net2.get_id(), params={'name': 'sr_ctrl-2', 'enable': 'ON'})
        cls.sw_up1 = SwUpload.create(
            cls.driver,
            cls.net1.get_id(),
            params={'name': 'sw_up-1', 'sw_file': 'dummy_soft.240'}
        )
        cls.sw_up2 = SwUpload.create(
            cls.driver,
            cls.net2.get_id(),
            params={'name': 'sw_up-2', 'sw_file': 'dummy_soft.240'}
        )
        cls.gr_net_1 = UserGroup.create(cls.driver, cls.net1.get_id(), params={'name': 'gr_net-1'},
                                        parent_type='network')
        cls.gr_net_2 = UserGroup.create(cls.driver, cls.net2.get_id(), params={'name': 'gr_net-2'},
                                        parent_type='network')
        # Balance controller in Network 2
        cls.bal_ctrl2 = BalController.create(cls.driver, cls.net2.get_id(),
                                             params={'name': 'bal_ctrl-2', 'enable': 'ON'})
        # MF HUB in Network 1
        cls.mf_hub1 = Controller.create(cls.driver, cls.net1.get_id(), params={
            'name': 'mf_hub1',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{cls.tp1.get_id()}'
        })
        # Inroute in Network 1
        cls.inr1 = Controller.create(cls.driver, cls.net1.get_id(), params={
            'name': 'inr1',
            'mode': ControllerModes.INROUTE,
            'teleport': f'teleport:{cls.tp1.get_id()}',
            'tx_controller': f'controller:{cls.ctrl1.get_id()}',
            'inroute': 2
        })
        cls.ctrl_route1 = ControllerRoute.create(cls.driver, cls.ctrl1.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.ser1.get_id()}',
            'ip': '127.0.10.1',
            'id': RouteIds.PRIVATE,
        })
        cls.ctrl_route2 = ControllerRoute.create(cls.driver, cls.ctrl2.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.ser2.get_id()}',
            'ip': '127.0.11.1',
            'id': RouteIds.PRIVATE,
        })
        cls.ctrl_rip1 = ControllerRip.create(
            cls.driver,
            cls.ctrl1.get_id(),
            {'service': f'service:{cls.ser1.get_id()}'}
        )
        cls.ctrl_rip2 = ControllerRip.create(
            cls.driver,
            cls.ctrl2.get_id(),
            {'service': f'service:{cls.ser2.get_id()}'}
        )
        cls.stn_route1 = StationRoute.create(cls.driver, cls.stn1.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.ser1.get_id()}',
            'ip': '127.0.13.1',
            'id': RouteIds.PRIVATE,
        })
        cls.stn_route2 = StationRoute.create(cls.driver, cls.stn2.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.ser2.get_id()}',
            'ip': '127.0.14.1',
            'id': RouteIds.PRIVATE,
        })
        cls.stn_rip1 = StationRip.create(cls.driver, cls.stn1.get_id(), {'service': f'service:{cls.ser1.get_id()}'})
        cls.stn_rip2 = StationRip.create(cls.driver, cls.stn2.get_id(), {'service': f'service:{cls.ser2.get_id()}'})

        cls.scheduler2 = Scheduler.create(cls.driver, cls.net2.get_id(), {'name': 'sched2'})

    def test_teleport(self):
        """Teleport from one network cannot be assigned to a controller and SR controller in another network"""
        api_path = f'api/object/write/controller={self.ctrl1.get_id()}'
        payload = {'teleport': f'teleport:{self.tp2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/controller={self.ctrl2.get_id()}'
        payload = {'teleport': f'teleport:{self.tp1.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/sr_controller={self.sr_ctrl1.get_id()}/new_item=sr_teleport'
        payload = {'name': 'sr_tp-1', 'teleport': f'teleport:{self.tp2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/sr_controller={self.sr_ctrl2.get_id()}/new_item=sr_teleport'
        payload = {'name': 'sr_tp-2', 'teleport': f'teleport:{self.tp1.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

    def test_shaper(self):
        """Shaper from one network cannot be assigned to a controller, vno, sub-vno, service, and station in another"""
        api_path = f'api/object/write/controller={self.ctrl1.get_id()}'
        payload = {'hub_shaper': f'shaper:{self.shp2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/vno={self.vno1.get_id()}'
        payload = {'hub_shaper': f'shaper:{self.shp2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/vno={self.vno1.get_id()}'
        payload = {'stn_shaper': f'shaper:{self.shp2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/controller={self.ctrl2.get_id()}'
        payload = {'hub_shaper': f'shaper:{self.shp1.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        # VNO section
        api_path = f'api/object/write/vno={self.vno1.get_id()}'
        payload = {'hub_shaper': f'shaper:{self.shp2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/vno={self.vno2.get_id()}'
        payload = {'stn_shaper': f'shaper:{self.shp1.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        # Sub-VNO section
        api_path = f'api/object/write/vno={self.sub_vno1.get_id()}'
        payload = {'hub_shaper': f'shaper:{self.shp2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/vno={self.sub_vno2.get_id()}'
        payload = {'stn_shaper': f'shaper:{self.shp1.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        # Station section
        api_path = f'api/object/write/station={self.stn1.get_id()}'
        payload = {'hub_shaper': f'shaper:{self.shp2.get_id()}', 'stn_shaper': f'shaper:{self.shp2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/station={self.stn2.get_id()}'
        payload = {'hub_shaper': f'shaper:{self.shp1.get_id()}', 'stn_shaper': f'shaper:{self.shp1.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/qos={self.qos1.get_id()}'
        payload = {'shaper': f'shaper:{self.shp2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/qos={self.qos2.get_id()}'
        payload = {'shaper': f'shaper:{self.shp1.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

    def test_rx_controller(self):
        """Controller from one network cannot be assigned to a station in another network"""
        api_path = f'api/object/write/station={self.stn1.get_id()}'
        payload = {'rx_controller': f'controller:{self.ctrl2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/station={self.stn2.get_id()}'
        payload = {'rx_controller': f'controller:{self.ctrl1.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

    def test_tx_controller(self):
        """Controller from one network cannot be assigned to an Inroute, station and SW upload in another network"""
        # SW upload section
        api_path = f'api/object/write/sw_upload={self.sw_up1.get_id()}'
        payload = {'tx_controller': f'controller:{self.ctrl2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/sw_upload={self.sw_up2.get_id()}'
        payload = {'tx_controller': f'controller:{self.ctrl1.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        # Inroute section
        api_path = f'api/object/write/controller={self.inr1.get_id()}'
        payload = {'tx_controller': f'controller:{self.ctrl2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        # Also checking tx controller for station
        self.stn1.send_param('mode', StationModes.DAMA)
        api_path = f'api/object/write/station={self.stn1.get_id()}'
        payload = {'tx_controller': self.ctrl2.get_id()}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)
        self.stn1.send_param('mode', StationModes.MESH)

    def test_profile_set(self):
        """Profile set from one network cannot be assigned to a station in another network"""
        api_path = f'api/object/write/station={self.stn1.get_id()}'
        payload = {'profile_set': f'profile_set:{self.profile_set2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/station={self.stn2.get_id()}'
        payload = {'profile_set': f'profile_set:{self.profile_set1.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

    def test_policy(self):
        """Policy from one network cannot be assigned to a qos in another network"""
        api_path = f'api/object/write/qos={self.qos1.get_id()}'
        payload = {
            'priority': PriorityTypes.POLICY,
            'policy': f'policy:{self.pol2.get_id()}',
        }
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/qos={self.qos2.get_id()}'
        payload = {
            'priority': PriorityTypes.POLICY,
            'policy': f'policy:{self.pol1.get_id()}',
        }
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

    def test_service(self):
        """Service from one network cannot be assigned to a controller and station route in another network,
        controller RIP and station RIP in another network"""
        # Controller route section
        api_path = f'api/object/write/controller={self.ctrl1.get_id()}/new_item=route'
        payload = {'type': RouteTypes.IP_ADDRESS, 'service': f'service:{self.ser2.get_id()}', 'ip': '127.0.0.1'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/controller={self.ctrl2.get_id()}/new_item=route'
        payload = {'type': RouteTypes.IP_ADDRESS, 'service': f'service:{self.ser1.get_id()}', 'ip': '127.0.0.2'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        # Station route section
        api_path = f'api/object/write/station={self.stn1.get_id()}/new_item=route'
        payload = {'type': RouteTypes.IP_ADDRESS, 'service': f'service:{self.ser2.get_id()}', 'ip': '127.0.0.3'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/station={self.stn2.get_id()}/new_item=route'
        payload = {'type': RouteTypes.IP_ADDRESS, 'service': f'service:{self.ser1.get_id()}', 'ip': '127.0.0.4'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        # Controller RIP section
        api_path = f'api/object/write/rip_router={self.ctrl_rip1.get_id()}'
        payload = {'service': f'service:{self.ser2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/rip_router={self.ctrl_rip2.get_id()}'
        payload = {'service': f'service:{self.ser1.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        # Station RIP section
        api_path = f'api/object/write/rip_router={self.stn_rip1.get_id()}'
        payload = {'service': f'service:{self.ser2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/rip_router={self.stn_rip2.get_id()}'
        payload = {'service': f'service:{self.ser1.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

    def test_bal_controller(self):
        """Balance controller from network 2 cannot be assigned to a MF HUB in network1"""
        api_path = f'api/object/write/controller={self.mf_hub1.get_id()}'
        payload = {
            'bal_enable': 'ON',
            'bal_controller': f'bal_controller:{self.bal_ctrl2}'
        }
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

    def test_sr_controller(self):
        """Sr controller from network 2 cannot be assigned to MF hub in network 1"""
        api_path = f'api/object/write/controller={self.ctrl1.get_id()}'
        payload = {
            'binding': BindingModes.SMART,
            'sr_controller': f'sr_controller:{self.sr_ctrl2.get_id()}'
        }
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/controller={self.ctrl2.get_id()}'
        payload = {
            'binding': BindingModes.SMART,
            'sr_controller': f'sr_controller:{self.sr_ctrl1.get_id()}'
        }
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

    def test_scheduler(self):
        """Scheduler from network 2 cannot be assigned to station in network 1"""
        api_path = f'api/object/write/station={self.stn1.get_id()}'
        payload = {'scheduler': f'scheduler:{self.scheduler2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

    def test_qos(self):
        """Qos from one network cannot be assigned to objects in another network"""
        api_path = f'api/object/write/route={self.stn_route1.get_id()}'
        payload = {'forward_qos': f'qos:{self.qos2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/route={self.ctrl_route1.get_id()}'
        payload = {'forward_qos': f'qos:{self.qos2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/rip_router={self.stn_rip1.get_id()}'
        payload = {'forward_qos': f'qos:{self.qos2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)

        api_path = f'api/object/write/rip_router={self.ctrl_route1.get_id()}'
        payload = {'forward_qos': f'qos:{self.qos2.get_id()}'}
        reply, error, error_code = self.driver.custom_post(api_path, payload=payload)
        self.assertEqual(NO_HIERARCHY, error_code)
