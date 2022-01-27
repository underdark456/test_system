from src.backup_manager.backup_manager import BackupManager
from src.constants import NEW_OBJECT_ID
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, RouteTypes, StationModes, AlertModes, BindingModes, PriorityTypes
from src.exceptions import ObjectNotCreatedException
from src.file_manager.file_manager import FileManager
from src.nms_entities.basic_entities.access import Access
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.bal_controller import BalController
from src.nms_entities.basic_entities.camera import Camera
from src.nms_entities.basic_entities.controller import Controller
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
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.api.required_params'
backup_name = 'default_config.txt'


class ApiRequiredParamsCase(CustomTestCase):
    """Test if objects can be created without passing any of the required (nonzero) parameters"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.23'
    __execution_time__ = 145  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()

    def set_up(self) -> None:
        self.backup.apply_backup(backup_name)

    def test_network(self):
        """Test if a network can be created without passing the required parameters: `name`"""
        net = Network(self.driver, 0, NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, net.save)

    def test_server(self):
        """Test if a server can be created without passing the required parameters: `name`"""
        server = Server(self.driver, 0, NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, server.save)

    def test_user_group(self):
        """Test if a UserGroup can be created without passing the required parameters: `name`"""
        ug = UserGroup(self.driver, 0, NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, ug.save)

    def test_user(self):
        """Test if a User can be created without passing the required parameters: `name`"""
        user = User(self.driver, 0, NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, user.save)

    def test_alert(self):
        """Test if an Alert can be created without passing the required parameters: `name`, one of the actions etc"""
        with self.assertRaises(ObjectNotCreatedException, msg='Alert without name'):
            Alert.create(self.driver, 0, {'popup': True})
        with self.assertRaises(ObjectNotCreatedException, msg='Alert without actions'):
            Alert.create(self.driver, 0, {'name': 'al'})
        with self.assertRaises(ObjectNotCreatedException, msg='Alert sound without file_name'):
            Alert.create(self.driver, 0, {'name': 'al1', 'sound': True})
        with self.assertRaises(ObjectNotCreatedException, msg='Alert script without script_file'):
            Alert.create(self.driver, 0, {'name': 'al2', 'script': True})

    def test_set_alert(self):
        """Set alert is obligatory when setting alert_mode to Specify"""
        with self.assertRaises(ObjectNotCreatedException, msg='Network with alert_mode specify without set_alert'):
            Network.create(self.driver, 0, {'name': 'test_net', 'alert_mode': AlertModes.SPECIFY})

    def test_access(self):
        """Test if an Access can be created without passing the required parameters: `group`"""
        access = Access(self.driver, 0, NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, access.save)

    def test_dashboard(self):
        """Test if a Dashboard can be created without passing the required parameters: `name`, `sat_name`"""
        Network.create(self.driver, 0, params={'name': 'net-0'})
        dash = Dashboard(self.driver, 0, NEW_OBJECT_ID, {}, parent_type='network')
        self.assertRaises(ObjectNotCreatedException, dash.save)

    def test_teleport(self):
        """Test if a Teleport can be created without passing the required parameters: `name`"""
        net = Network.create(self.driver, 0, params={'name': 'net-0'})
        with self.assertRaises(ObjectNotCreatedException, msg='Teleport without name'):
            Teleport.create(self.driver, net.get_id(), {'sat_name': 'sat'})

    def test_controller(self):
        """Test if a Controller can be created without passing the required params: `name`, `mode`, and `teleport`"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'tp-0', 'sat_name': 'sat'})
        with self.subTest('No name in required params'):
            ctrl = Controller(self.driver, net.get_id(), NEW_OBJECT_ID, {
                'mode': ControllerModes.HUBLESS_MASTER,
                'teleport': f'teleport:{tp.get_id()}'
            })
            self.assertRaises(ObjectNotCreatedException, ctrl.save)

        with self.subTest('No mode in required params'):
            ctrl = Controller(self.driver, net.get_id(), NEW_OBJECT_ID, {
                'name': 'ctrl-0',
                'teleport': f'teleport:{tp.get_id()}'
            })
            self.assertRaises(ObjectNotCreatedException, ctrl.save)
        with self.subTest('No teleport in required params'):
            ctrl = Controller(self.driver, net.get_id(), NEW_OBJECT_ID, {
                'name': 'ctrl-1',
                'mode': ControllerModes.HUBLESS_MASTER,
            })
            self.assertRaises(ObjectNotCreatedException, ctrl.save)

    def test_inroute(self):
        """Test if an Inroute can be created without passing the required parameters: `tx_controller` and `inroute`"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'tp-0', 'sat_name': 'sat'})
        ctrl = Controller.create(self.driver, 0, {
            'name': 'ctrl-0',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{tp.get_id}'
        })
        with self.subTest('No tx_controller in required params'):
            inr = Controller(self.driver, net.get_id(), NEW_OBJECT_ID, {
                'name': 'inroute-0',
                'mode': ControllerModes.INROUTE,
                'teleport': f'teleport:{tp.get_id()}',
                'inroute': 2,
            })

            self.assertRaises(ObjectNotCreatedException, inr.save)

        with self.subTest('No correct inroute number in required params'):
            inr = Controller(self.driver, net.get_id(), NEW_OBJECT_ID, {
                'name': 'inroute-0',
                'mode': ControllerModes.INROUTE,
                'teleport': f'teleport:{tp.get_id()}',
                'tx_controller': f'controller:{ctrl.get_id()}'
            })
            self.assertRaises(ObjectNotCreatedException, inr.save)

    def test_vno(self):
        """Test if a VNO can be created without passing the required parameters: `name`"""
        net = Network.create(self.driver, 0, params={'name': 'net-0'})
        vno = Vno(self.driver, net.get_id(), NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, vno.save)

    def test_service(self):
        """Test if a Service can be created without passing the required parameters: `name`"""
        net = Network.create(self.driver, 0, params={'name': 'net-0'})
        ser = Service(self.driver, net.get_id(), NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, ser.save)

    def test_qos(self):
        """Test if Qos can be created without passing the required parameters: `name`"""
        net = Network.create(self.driver, 0, params={'name': 'net-0'})
        qos = Qos(self.driver, net.get_id(), NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, qos.save)

    def test_qos_priority_policy(self):
        """Test if Qos can be created without passing the required parameter policy upon choosing priority Policy"""
        net = Network.create(self.driver, 0, params={'name': 'net-0'})
        Policy.create(self.driver, 0, {'name': 'pol'})
        with self.assertRaises(ObjectNotCreatedException, msg='Qos with Priority set to Policy without setting policy'):
            Qos.create(self.driver, net.get_id(), {'name': 'qos', 'priority': PriorityTypes.POLICY})

    def test_shapers(self):
        """Test if a Shaper can be created without passing the required parameters: `name`"""
        net = Network.create(self.driver, 0, params={'name': 'net-0'})
        shp = Shaper(self.driver, net.get_id(), NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, shp.save)

    def test_policy(self):
        """Test if a Policy can be created without passing the required parameters: `name`"""
        net = Network.create(self.driver, 0, params={'name': 'net-0'})
        pol = Policy(self.driver, net.get_id(), NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, pol.save)

    def test_policy_rule(self):
        """Test if a Policy rule can be created without passing the required parameters: `sequence`"""
        net = Network.create(self.driver, 0, params={'name': 'net-0'})
        pol = Policy.create(self.driver, net.get_id(), {'name': 'pol-0'})
        rule = PolicyRule(self.driver, pol.get_id(), NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, rule.save)

    def test_sr_controller(self):
        """Test if an SrController can be created without passing the required parameters: `name`"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        sr_ctrl = SrController(self.driver, net.get_id(), NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, sr_ctrl.save)

    def test_binding_smart(self):
        Network.create(self.driver, 0, {'name': 'net-0'})
        SrController.create(self.driver, 0, {'name': 'sr_ctr'})
        with self.assertRaises(ObjectNotCreatedException, msg=f'MF hub binding smart without sr_controller'):
            Controller.create(self.driver, 0, {
                'name': 'mf_hub',
                'mode': ControllerModes.MF_HUB,
                'binding': BindingModes.SMART
            })

    def test_sr_teleport(self):
        """Test if an SrTeleport can be created without passing the required parameters: `name`, `teleport`"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'tp-0', 'sat_name': 'sat'})
        sr_ctrl = SrController.create(self.driver, net.get_id(), {'name': 'sr_ctrl-0'})
        with self.subTest('SrTeleport without name'):
            sr_tp = SrTeleport(self.driver, sr_ctrl.get_id(), NEW_OBJECT_ID, {'teleport': f'teleport:{tp.get_id()}'})
            self.assertRaises(ObjectNotCreatedException, sr_tp.save)
        with self.subTest('SrTeleport without teleport'):
            sr_tp = SrTeleport(self.driver, sr_ctrl.get_id(), NEW_OBJECT_ID, {'name': 'sr_tp-0'})
            self.assertRaises(ObjectNotCreatedException, sr_tp.save)

    def test_device(self):
        """Test if a Device can be created without passing the required parameters: `name`"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        tp = Teleport.create(self.driver, 0, {'name': 'tp-0', 'sat_name': 'sat'})
        sr_ctrl = SrController.create(self.driver, net.get_id(), {'name': 'sr_ctrl-0'})
        sr_tp = SrTeleport.create(self.driver, sr_ctrl.get_id(),
                                  {'name': 'sr_tp-0', 'teleport': f'teleport:{tp.get_id()}'})
        dev = Device(self.driver, sr_tp.get_id(), NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, dev.save)

    def test_sr_license(self):
        """Test if an SrLicense can be created without passing the required parameters: `name`"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        sr_lic = SrLicense(self.driver, net.get_id(), NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, sr_lic.save)

    def test_bal_controller(self):
        """Test if a BalController can be created without passing the required parameters: `name`"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        bal_ctrl = BalController(self.driver, net.get_id(), NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, bal_ctrl.save)

    def test_profile_set(self):
        """Test if a Profile set can be created without passing the required parameters: `name`"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        pro = Profile(self.driver, net.get_id(), NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, pro.save)

    def test_sw_upload(self):
        """Test if a SwUpload set can be created without passing the required parameters"""
        fm = FileManager()
        fm.upload_uhp_software('dummy_soft.240')
        net = Network.create(self.driver, 0, {'name': 'net'})
        Teleport.create(self.driver, 0, {'name': 'tp', 'sat_name': 'sat'})
        Controller.create(self.driver, 0, {
            'name': 'mf',
            'mode': ControllerModes.MF_HUB,
            'teleport': 'teleport:0'
        })
        with self.assertRaises(ObjectNotCreatedException, msg='Sw upload without name'):
            SwUpload.create(self.driver, net.get_id(), {'tx_controller': 'controller:0', 'sw_file': 'dummy_soft.240'})
        with self.assertRaises(ObjectNotCreatedException, msg='Sw upload without sw_file'):
            SwUpload.create(self.driver, net.get_id(), {'name': 'sw', 'tx_controller': 'controller:0'})
        # with self.assertRaises(ObjectNotCreatedException, msg='Sw upload without tx_controller'):
        #     SwUpload.create(self.driver, net.get_id(), {'name': 'sw', 'sw_file': 'dummy_soft.240'})

    def test_camera(self):
        """Test if a Camera set can be created without passing the required parameters: `name`"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        cam = Camera(self.driver, net.get_id(), NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, cam.save)

    def test_station(self):
        """Test if a Station can be created without passing the required parameters: `name`, `serial`"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        vno = Vno.create(self.driver, net.get_id(), {'name': 'vno-0'})
        Teleport.create(self.driver, net.get_id(), {'name': 'tp-0', 'sat_name': 'sat'})
        with self.subTest('Station without name'):
            stn = Station(
                self.driver,
                vno.get_id(),
                NEW_OBJECT_ID,
                {'serial': 111111, 'mode': StationModes.STAR},
            )
            self.assertRaises(ObjectNotCreatedException, stn.save)
        with self.subTest('Station without serial'):
            stn = Station(self.driver, vno.get_id(), NEW_OBJECT_ID, {'name': 'no_serial', 'mode': StationModes.STAR})
            self.assertRaises(ObjectNotCreatedException, stn.save)
        # with self.subTest('Station without mode'):
        #     stn = Station(self.driver, vno.get_id(), NEW_OBJECT_ID, {'name': 'no_mode', 'serial': 12345})
        #     self.assertRaises(ObjectNotCreatedException, stn.save)

    def test_rip_router(self):
        """Test if a Rip router set can be created without passing the required parameters: `service`"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'tp-0', 'sat_name': 'sat'})
        ctrl = Controller.create(self.driver, net.get_id(), {
            'name': 'ctrl-0',
            'mode': ControllerModes.HUBLESS_MASTER,
            'teleport': f'teleport:{tp.get_id()}'
        })
        rip = ControllerRip(self.driver, ctrl.get_id(), NEW_OBJECT_ID, {})
        self.assertRaises(ObjectNotCreatedException, rip.save)

    def test_route(self):
        """Test if a route set can be created without passing the required parameters: `type`, `service`"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'tp-0', 'sat_name': 'sat'})
        ctrl = Controller.create(self.driver, net.get_id(), {
            'name': 'ctrl-0',
            'mode': ControllerModes.HUBLESS_MASTER,
            'teleport': f'teleport:{tp.get_id()}'
        })
        ser = Service.create(self.driver, net.get_id(), {'name': 'ser-0'})
        with self.subTest('Route without service'):
            route = ControllerRoute(self.driver, ctrl.get_id(), NEW_OBJECT_ID, {'type': RouteTypes.IP_ADDRESS})
            self.assertRaises(ObjectNotCreatedException, route.save)
        with self.subTest('Route without type'):
            route = ControllerRoute(self.driver, ctrl.get_id(), NEW_OBJECT_ID,
                                    {'service': f'service:{ser}', 'ip': '127.0.0.1'})
            self.assertRaises(ObjectNotCreatedException, route.save)

    def test_dama_inroute(self):
        """Test if a dama_inroute can be created without passing the required parameter: `tx_controller`"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'tp-0', 'sat_name': 'sat'})
        Controller.create(self.driver, net.get_id(), {
            'name': 'ctrl-0',
            'mode': ControllerModes.DAMA_HUB,
            'teleport': f'teleport:{tp.get_id()}'
        })
        with self.subTest('No tx_controller in required params'):
            dama_inr = Controller(self.driver, net.get_id(), NEW_OBJECT_ID, {
                'name': 'inroute-0',
                'mode': ControllerModes.DAMA_INROUTE,
                'teleport': f'teleport:{tp.get_id()}',
            })
            self.assertRaises(ObjectNotCreatedException, dama_inr.save)

    def test_gateway(self):
        """Test if a gateway can be created without passing the required parameter: `tx_controller`"""
        net = Network.create(self.driver, 0, {'name': 'net-0'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'tp-0', 'sat_name': 'sat'})
        Controller.create(self.driver, net.get_id(), {
            'name': 'ctrl-0',
            'mode': ControllerModes.DAMA_HUB,
            'teleport': f'teleport:{tp.get_id()}'
        })
        with self.subTest('No tx_controller in required params'):
            dama_inr = Controller(self.driver, net.get_id(), NEW_OBJECT_ID, {
                'name': 'gateway',
                'mode': ControllerModes.GATEWAY,
                'teleport': f'teleport:{tp.get_id()}',
            })
            self.assertRaises(ObjectNotCreatedException, dama_inr.save)

    def test_sch_range(self):
        """Test if a Sch Range can be created without passing the required parameters: `name`"""
        Network.create(self.driver, 0, {'name': 'net-0'})
        Scheduler.create(self.driver, 0, {'name': 'sch'})
        with self.assertRaises(ObjectNotCreatedException, msg='Sch range without name'):
            SchRange.create(self.driver, 0, {})

    def test_sch_service(self):
        """Test if a Sch Service can be created without passing the required parameters: `name`"""
        Network.create(self.driver, 0, {'name': 'net-0'})
        Scheduler.create(self.driver, 0, {'name': 'sch'})
        with self.assertRaises(ObjectNotCreatedException, msg='Sch service without name'):
            SchService.create(self.driver, 0, {})

    def test_sch_task(self):
        """Test if a Sch Service can be created without passing the required parameters: `name`"""
        Network.create(self.driver, 0, {'name': 'net-0'})
        Teleport.create(self.driver, 0, {'name': 'tp', 'sat_name': 'sat'})
        Vno.create(self.driver, 0, {'name': 'vno'})
        Controller.create(self.driver, 0, {'name': 'ctr', 'mode': ControllerModes.MF_HUB, 'teleport': 'teleport:0'})
        Station.create(self.driver, 0, {'name': 'stn', 'serial': 10000})
        with self.assertRaises(ObjectNotCreatedException, msg='Sch task without name'):
            SchTask.create(self.driver, 0, {})
