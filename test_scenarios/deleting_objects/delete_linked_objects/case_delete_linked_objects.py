from src.backup_manager.backup_manager import BackupManager
from src.constants import CANNOT_DELETE
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModesStr, AlertPriorityStr, CheckboxStr, AlertModesStr, RouteTypesStr, \
    PriorityTypesStr, BindingModesStr, DeviceModes, RuleTypes, ActionTypes, ControllerModes, Checkbox, StationModes
from src.exceptions import ObjectNotDeletedException
from src.file_manager.file_manager import FileManager
from src.nms_entities.basic_entities.access import Access
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.bal_controller import BalController
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_rip import ControllerRip
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.device import Device
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.profile import Profile
from src.nms_entities.basic_entities.qos import Qos
from src.nms_entities.basic_entities.scheduler import Scheduler
from src.nms_entities.basic_entities.scheduler_range import SchRange
from src.nms_entities.basic_entities.scheduler_service import SchService
from src.nms_entities.basic_entities.scheduler_task import SchTask
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.sr_controller import SrController
from src.nms_entities.basic_entities.sr_teleport import SrTeleport
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_rip import StationRip
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.deleting_objects.delete_linked_objects'
backup_name = 'default_config.txt'


class DeleteLinkedObjectsCase(CustomTestCase):
    """Linked objects deletion case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __execution_time__ = 80  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path)
        )
        cls.backup = BackupManager()
        fm = FileManager()
        fm.upload_uhp_software('dummy_soft.240')

    def set_up(self) -> None:
        self.backup.apply_backup(backup_name)

    def test_alert(self):
        """Alert linked to NMS objects"""
        alert = Alert.create(self.driver, 0, {
            'name': 'test_alert',
            'priority': AlertPriorityStr.HIGH,
            'popup': CheckboxStr.ON
        })
        nms = Nms(self.driver, 0, 0)
        nms.send_params({'alert_mode': AlertModesStr.SPECIFY, 'set_alert': f'alert:{alert.get_id()}'})
        with self.subTest('Alert linked to the NMS'):
            self.assertRaises(ObjectNotDeletedException, alert.delete)
        if alert.get_id() is None:
            alert = Alert.create(self.driver, 0, {
                'name': 'test_alert',
                'priority': AlertPriorityStr.HIGH,
                'popup': CheckboxStr.ON
            })
        nms.send_param('alert_mode', AlertModesStr.OFF)

        net = Network.create(self.driver, 0, {
            'name': 'test_net',
            'alert_mode': AlertModesStr.SPECIFY,
            'set_alert': f'alert:{alert.get_id()}'
        })
        with self.subTest('Alert linked to a network'):
            self.assertRaises(ObjectNotDeletedException, alert.delete)
        if alert.get_id() is None:
            alert = Alert.create(self.driver, 0, {
                'name': 'test_alert',
                'priority': AlertPriorityStr.HIGH,
                'popup': CheckboxStr.ON
            })
        net.send_param('alert_mode', AlertModesStr.OFF)

        tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})
        ctrl = Controller.create(self.driver, net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModesStr.MF_HUB,
            'teleport': f'teleport:{tp.get_id()}',
            'alert_mode': AlertModesStr.SPECIFY,
            'set_alert': f'alert:{alert.get_id()}'
        })
        with self.subTest('Alert linked to a controller'):
            self.assertRaises(ObjectNotDeletedException, alert.delete)
        if alert.get_id() is None:
            alert = Alert.create(self.driver, 0, {
                'name': 'test_alert',
                'priority': AlertPriorityStr.HIGH,
                'popup': CheckboxStr.ON
            })
        ctrl.send_param('alert_mode', AlertModesStr.OFF)

        vno = Vno.create(self.driver, net.get_id(), {'name': 'test_vno'})
        Station.create(self.driver, vno.get_id(), {
            'name': 'test_stn',
            'enable': CheckboxStr.ON,
            'serial': 12345,
            'rx_controller': f'controller:{ctrl.get_id()}',
            'alert_mode': AlertModesStr.SPECIFY,
            'set_alert': f'alert:{alert.get_id()}'
        })
        with self.subTest('Alert linked to a vno'):
            self.assertRaises(ObjectNotDeletedException, alert.delete)
        vno.send_param('alert_mode', AlertModesStr.OFF)

        sr_ctrl = SrController.create(self.driver, net.get_id(), {
            'name': 'test_sr_ctrl',
            'alert_mode': AlertModesStr.SPECIFY,
            'set_alert': f'alert:{alert.get_id()}',
        })
        with self.subTest('Alert linked to an sr controller'):
            self.assertRaises(ObjectNotDeletedException, alert.delete)
        sr_ctrl.send_param('alert_mode', AlertModesStr.OFF)

        sr_tp = SrTeleport.create(self.driver, sr_ctrl.get_id(), {
            'name': 'sr_tp',
            'teleport': f'teleport:{tp.get_id()}',
            'alert_mode': AlertModesStr.SPECIFY,
            'set_alert': f'alert:{alert.get_id()}',
        })
        with self.subTest('Alert linked to an sr teleport'):
            self.assertRaises(ObjectNotDeletedException, alert.delete)
        sr_tp.send_param('alert_mode', AlertModesStr.OFF)

        dev = Device.create(self.driver, sr_tp.get_id(), {
            'name': 'test_dev',
            'mode': DeviceModes.USED,
            'alert_mode': AlertModesStr.SPECIFY,
            'set_alert': f'alert:{alert.get_id()}',
        })
        with self.subTest('Alert linked to a device'):
            self.assertRaises(ObjectNotDeletedException, alert.delete)
        dev.send_param('alert_mode', AlertModesStr.OFF)

    def test_controller(self):
        """Controller linked to either a station or a sw upload or a gateway"""
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})
        ctrl = Controller.create(self.driver, net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModesStr.MF_HUB,
            'teleport': f'teleport:{tp.get_id()}'
        })
        vno = Vno.create(self.driver, net.get_id(), {'name': 'test_vno'})
        stn = Station.create(self.driver, vno.get_id(), {
            'name': 'test_stn',
            'enable': CheckboxStr.ON,
            'serial': 12345,
            'rx_controller': f'controller:{ctrl.get_id()}',
        })
        with self.subTest('Controller linked to a station'):
            self.assertRaises(ObjectNotDeletedException, ctrl.delete)
        stn.send_param('rx_controller', '')
        if ctrl.get_id() is None:
            ctrl = Controller.create(self.driver, net.get_id(), {
                'name': 'test_ctrl',
                'mode': ControllerModesStr.MF_HUB,
                'teleport': f'teleport:{tp.get_id()}'
            })
        SwUpload.create(self.driver, net.get_id(), {
            'name': 'test_sw_up',
            'tx_controller': f'controller:{ctrl.get_id()}',
            'sw_file': 'dummy_soft.240',
        })
        with self.subTest('Controller linked to a SW upload'):
            self.assertRaises(ObjectNotDeletedException, ctrl.delete)
        if ctrl.get_id() is None:
            ctrl = Controller.create(self.driver, net.get_id(), {
                'name': 'test_ctrl',
                'mode': ControllerModesStr.MF_HUB,
                'teleport': f'teleport:{tp.get_id()}'
            })
        Controller.create(self.driver, net.get_id(), {
            'name': 'test_gateway',
            'mode': ControllerModesStr.GATEWAY,
            'tx_controller': f'controller:{ctrl.get_id()}',
            'teleport': f'teleport:{tp.get_id()}',
        })
        with self.subTest('Controller linked to a gateway'):
            self.assertRaises(ObjectNotDeletedException, ctrl.delete)

    def test_policy(self):
        """Policy linked to a qos"""
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        policy = Policy.create(self.driver, net.get_id(), {'name': 'test_pol'})
        PolicyRule.create(self.driver, policy.get_id(), {'sequence': 1})
        Qos.create(self.driver, net.get_id(), {
            'name': 'test_qos',
            'priority': PriorityTypesStr.POLICY,
            'policy': f'policy:{policy.get_id()}'
        })
        with self.subTest('Policy linked to a qos'):
            self.assertRaises(ObjectNotDeletedException, policy.delete)

    def test_profile_set(self):
        """Profile set linked to a station"""
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})
        ctrl = Controller.create(self.driver, net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModesStr.MF_HUB,
            'teleport': f'teleport:{tp.get_id()}'
        })
        vno = Vno.create(self.driver, net.get_id(), {
            'name': 'test_vno',
        })

        profile = Profile.create(self.driver, net.get_id(), {'name': 'test_pro'})

        Station.create(self.driver, vno.get_id(), {
            'name': 'test_stn',
            'enable': CheckboxStr.ON,
            'serial': 12345,
            'rx_controller': f'controller:{ctrl.get_id()}',
            'profile_set': f'profile_set:{profile.get_id()}',
        })
        with self.subTest('Profile set linked to a station'):
            self.assertRaises(ObjectNotDeletedException, profile.delete)

    def test_qos(self):
        """Qos linked to either to a controller route or a controller rip or station route or a station rip"""
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})
        ctrl = Controller.create(self.driver, net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModesStr.MF_HUB,
            'teleport': f'teleport:{tp.get_id()}'
        })
        vno = Vno.create(self.driver, net.get_id(), {
            'name': 'test_vno',
        })
        stn = Station.create(self.driver, vno.get_id(), {
            'name': 'test_stn',
            'enable': CheckboxStr.ON,
            'serial': 12345,
            'rx_controller': f'controller:{ctrl.get_id()}',
        })
        ser = Service.create(self.driver, net.get_id(), {'name': 'test_service'})
        qos = Qos.create(self.driver, net.get_id(), {'name': 'test_qos'})

        # Controller block
        ctrl_route = ControllerRoute.create(self.driver, ctrl.get_id(), {
            'type': RouteTypesStr.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'forward_qos': f'qos:{qos.get_id()}',
            'ip': '127.0.0.1',
        })
        with self.subTest('Qos linked to a controller route as forward_qos'):
            self.assertRaises(ObjectNotDeletedException, qos.delete)
        ctrl_route.delete()
        if qos.get_id() is None:
            qos = Qos.create(self.driver, net.get_id(), {'name': 'test_qos'})

        ctrl_route = ControllerRoute.create(self.driver, ctrl.get_id(), {
            'type': RouteTypesStr.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'return_qos': f'qos:{qos.get_id()}',
            'ip': '127.0.0.1',
        })
        with self.subTest('Qos linked to a controller route as return_qos'):
            self.assertRaises(ObjectNotDeletedException, qos.delete)
        ctrl_route.delete()
        if qos.get_id() is None:
            qos = Qos.create(self.driver, net.get_id(), {'name': 'test_qos'})

        ctrl_rip = ControllerRip.create(self.driver, ctrl.get_id(), {
            'service': f'service:{ser.get_id()}',
            'forward_qos': f'qos:{qos.get_id()}',
            'rip_next_hop': '127.0.0.1',
        })
        with self.subTest('Qos linked to a controller rip as forward_qos'):
            self.assertRaises(ObjectNotDeletedException, qos.delete)
        ctrl_rip.delete()
        if qos.get_id() is None:
            qos = Qos.create(self.driver, net.get_id(), {'name': 'test_qos'})

        ctrl_rip = ControllerRip.create(self.driver, ctrl.get_id(), {
            'service': f'service:{ser.get_id()}',
            'return_qos': f'qos:{qos.get_id()}',
            'rip_next_hop': '127.0.0.1',
        })
        with self.subTest('Qos linked to a controller rip as return_qos'):
            self.assertRaises(ObjectNotDeletedException, qos.delete)
        ctrl_rip.delete()
        if qos.get_id() is None:
            qos = Qos.create(self.driver, net.get_id(), {'name': 'test_qos'})

        # Station block
        stn_route = StationRoute.create(self.driver, stn.get_id(), {
            'type': RouteTypesStr.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'forward_qos': f'qos:{qos.get_id()}',
            'ip': '127.0.0.1',
        })
        with self.subTest('Qos linked to a station route as forward_qos'):
            self.assertRaises(ObjectNotDeletedException, qos.delete)
        stn_route.delete()
        if qos.get_id() is None:
            qos = Qos.create(self.driver, net.get_id(), {'name': 'test_qos'})

        stn_route = StationRoute.create(self.driver, stn.get_id(), {
            'type': RouteTypesStr.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'return_qos': f'qos:{qos.get_id()}',
            'ip': '127.0.0.1',
        })
        with self.subTest('Qos linked to a station route as return_qos'):
            self.assertRaises(ObjectNotDeletedException, qos.delete)
        stn_route.delete()
        if qos.get_id() is None:
            qos = Qos.create(self.driver, net.get_id(), {'name': 'test_qos'})

        stn_rip = StationRip.create(self.driver, stn.get_id(), {
            'service': f'service:{ser.get_id()}',
            'forward_qos': f'qos:{qos.get_id()}',
            'rip_next_hop': '127.0.0.1',
        })
        with self.subTest('Qos linked to a station rip as forward_qos'):
            self.assertRaises(ObjectNotDeletedException, qos.delete)
        stn_rip.delete()
        if qos.get_id() is None:
            qos = Qos.create(self.driver, net.get_id(), {'name': 'test_qos'})

        StationRip.create(self.driver, stn.get_id(), {
            'service': f'service:{ser.get_id()}',
            'return_qos': f'qos:{qos.get_id()}',
            'rip_next_hop': '127.0.0.1',
        })
        with self.subTest('Qos linked to a station rip as return_qos'):
            self.assertRaises(ObjectNotDeletedException, qos.delete)

    def test_service(self):
        """Service linked to either to a controller route or a controller rip or station route or a station rip"""
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})
        ctrl = Controller.create(self.driver, net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModesStr.MF_HUB,
            'teleport': f'teleport:{tp.get_id()}'
        })
        ser = Service.create(self.driver, net.get_id(), {
            'name': 'test_service',
        })
        ctrl_route = ControllerRoute.create(self.driver, ctrl.get_id(), {
            'type': RouteTypesStr.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': '127.0.0.1',
        })
        with self.subTest('Service linked to a controller route'):
            self.assertRaises(ObjectNotDeletedException, ser.delete)
        ctrl_route.delete()
        if ser.get_id() is None:
            ser = Service.create(self.driver, net.get_id(), {
                'name': 'test_service',
            })
        ctrl_rip = ControllerRip.create(self.driver, ctrl.get_id(), {
            'service': f'service:{ser.get_id()}',
            'rip_next_hop': '127.0.0.1',
        })
        with self.subTest('Service linked to a controller RIP'):
            self.assertRaises(ObjectNotDeletedException, ser.delete)
        ctrl_rip.delete()
        if ser.get_id() is None:
            ser = Service.create(self.driver, net.get_id(), {
                'name': 'test_service',
            })

        vno = Vno.create(self.driver, net.get_id(), {
            'name': 'test_vno',
        })
        stn = Station.create(self.driver, vno.get_id(), {
            'name': 'test_stn',
            'enable': CheckboxStr.ON,
            'serial': 12345,
            'rx_controller': f'controller:{ctrl.get_id()}',
        })
        stn_route = StationRoute.create(self.driver, stn.get_id(), {
            'type': RouteTypesStr.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': '127.0.0.1',
        })
        with self.subTest('Service linked to a station route'):
            self.assertRaises(ObjectNotDeletedException, ser.delete)
        stn_route.delete()
        if ser.get_id() is None:
            ser = Service.create(self.driver, net.get_id(), {
                'name': 'test_service',
            })
        StationRip.create(self.driver, stn.get_id(), {
            'service': f'service:{ser.get_id()}',
            'rip_next_hop': '127.0.0.1',
        })
        with self.subTest('Service linked to a station RIP'):
            self.assertRaises(ObjectNotDeletedException, ser.delete)

    def test_shaper(self):
        """Shaper linked to any of the allowed objects"""
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})

        hub_shp = Shaper.create(self.driver, net.get_id(), {'name': 'hub_shp'})
        stn_shp = Shaper.create(self.driver, net.get_id(), {'name': 'stn_shp'})

        ctrl_hl = Controller.create(self.driver, net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModesStr.HUBLESS_MASTER,
            'hub_shaper': f'shaper:{hub_shp.get_id()}',
            'teleport': f'teleport:{tp.get_id()}'
        })
        with self.subTest('Hub shaper linked to a controller'):
            self.assertRaises(ObjectNotDeletedException, hub_shp.delete)
        ctrl_hl.send_param('hub_shaper', '')

        # Controller for station
        ctrl = Controller.create(self.driver, net.get_id(), {
            'name': 'test_ctrl2',
            'mode': ControllerModesStr.MF_HUB,
            'hub_shaper': f'shaper:{hub_shp.get_id()}',
            'teleport': f'teleport:{tp.get_id()}'
        })

        Qos.create(self.driver, net.get_id(), {
            'name': 'test_service',
            'shaper': f'shaper:{hub_shp.get_id()}',
        })
        with self.subTest('Shaper linked to a qos'):
            self.assertRaises(ObjectNotDeletedException, hub_shp.delete)

        if hub_shp.get_id() is None:
            hub_shp = Shaper.create(self.driver, net.get_id(), {'name': 'hub_shp'})
        if stn_shp.get_id() is None:
            stn_shp = Shaper.create(self.driver, net.get_id(), {'name': 'stn_shp'})

        vno = Vno.create(self.driver, net.get_id(), {
            'name': 'test_vno',
            'hub_shaper': f'shaper:{hub_shp.get_id()}',
            'stn_shaper': f'shaper:{stn_shp.get_id()}',
        })
        with self.subTest('Hub shaper linked to a vno'):
            self.assertRaises(ObjectNotDeletedException, hub_shp.delete)
        with self.subTest('Stn shaper linked to a vno'):
            self.assertRaises(ObjectNotDeletedException, stn_shp.delete)
        vno.send_params({'hub_shaper': '', 'stn_shaper': ''})
        if hub_shp.get_id() is None:
            hub_shp = Shaper.create(self.driver, net.get_id(), {'name': 'hub_shp'})
        if stn_shp.get_id() is None:
            stn_shp = Shaper.create(self.driver, net.get_id(), {'name': 'stn_shp'})

        stn = Station.create(self.driver, vno.get_id(), {
            'name': 'test_stn',
            'enable': CheckboxStr.ON,
            'serial': 12345,
            'rx_controller': f'controller:{ctrl.get_id()}',
            'hub_shaper': f'shaper:{hub_shp.get_id()}',
            'stn_shaper': f'shaper:{stn_shp.get_id()}',
        })
        with self.subTest('Hub shaper linked to a station'):
            self.assertRaises(ObjectNotDeletedException, hub_shp.delete)
        with self.subTest('Stn shaper linked to a station'):
            self.assertRaises(ObjectNotDeletedException, stn_shp.delete)
        if hub_shp.get_id() is None:
            hub_shp = Shaper.create(self.driver, net.get_id(), {'name': 'hub_shp'})
        if stn_shp.get_id() is None:
            Shaper.create(self.driver, net.get_id(), {'name': 'stn_shp'})
        stn.send_params({'hub_shaper': '', 'stn_shaper': ''})

        policy = Policy.create(self.driver, net.get_id(), {'name': 'test_policy'})
        PolicyRule.create(self.driver, policy.get_id(), {
            'sequence': 1,
            'type': RuleTypes.ACTION,
            'action_type': ActionTypes.SET_TS_CH,
            'shaper': f'shaper:{hub_shp.get_id()}'
        })
        with self.subTest('Hub shaper linked to a policy rule'):
            self.assertRaises(ObjectNotDeletedException, hub_shp.delete)

        # Commented out as it is not a linked object
        # sub_hub_shp = Shaper.create(self.driver, hub_shp, {'name': 'test_sub_shp'}, parent_type='shaper')
        # with self.subTest('Sub shaper that is used along with a shaper'):
        #     self.assertRaises(ObjectNotDeletedException, sub_hub_shp.delete)

    def test_sr_controller(self):
        """Sr controller linked to a controller"""
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})
        sr_ctrl = SrController.create(self.driver, net.get_id(), {'name': 'test_sr_ctrl', 'enable': CheckboxStr.ON})
        SrTeleport.create(self.driver, sr_ctrl.get_id(), {
            'name': 'test_sr_tp',
            'teleport': f'teleport:{tp.get_id()}'
        })
        Controller.create(self.driver, net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModesStr.MF_HUB,
            'binding': BindingModesStr.SMART,
            'sr_controller': f'sr_controller:{sr_ctrl.get_id()}'
        })
        with self.subTest('Sr controller linked to a controller'):
            self.assertRaises(ObjectNotDeletedException, sr_ctrl.delete)

    def test_bal_controller(self):
        """Bal_controller linked to a controller"""
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})
        bal_ctrl = BalController.create(self.driver, net.get_id(), {'name': 'test_bal_ctrl', 'enable': CheckboxStr.ON})
        Controller.create(self.driver, net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModesStr.MF_HUB,
            'teleport':  f'teleport:{tp.get_id()}',
            'bal_enable': Checkbox.ON,
            'bal_controller': f'bal_controller:{bal_ctrl.get_id()}',
        })
        with self.subTest('Bal controller linked to a controller'):
            self.assertRaises(ObjectNotDeletedException, bal_ctrl.delete)

    def test_teleport(self):
        """Teleport linked to either a controller or an sr_teleport"""
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})
        ctrl = Controller.create(self.driver, net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModesStr.MF_HUB,
            'teleport': f'teleport:{tp.get_id()}'
        })
        with self.subTest('Teleport linked to a controller'):
            self.assertRaises(ObjectNotDeletedException, tp.delete)
        ctrl.delete()
        if tp.get_id() is None:
            tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})

        sr_ctrl = SrController.create(self.driver, net.get_id(), {'name': 'test_sr_ctrl'})
        SrTeleport.create(self.driver, sr_ctrl.get_id(), {
            'name': 'test_sr_tp',
            'teleport': f'teleport:{tp.get_id()}',
        })
        with self.subTest('Teleport linked to a SR teleport'):
            self.assertRaises(ObjectNotDeletedException, tp.delete)

    def test_user_group(self):
        """User group linked to an access"""
        gr = UserGroup.create(self.driver, 0, {'name': 'nms_group'})
        Access.create(self.driver, 0, {'group': f'group:{gr.get_id()}'})
        with self.subTest('User group linked to an NMS access'):
            self.assertRaises(ObjectNotDeletedException, gr.delete)
        if gr.get_id() is None:
            gr = UserGroup.create(self.driver, 0, {'name': 'nms_group'})

        net = Network.create(self.driver, 0, {'name': 'test_net'})
        Access.create(self.driver, net.get_id(), {'group': f'group:{gr.get_id()}'}, parent_type='network')
        with self.subTest('User group linked to a network access'):
            self.assertRaises(ObjectNotDeletedException, gr.delete)
        if gr.get_id() is None:
            gr = UserGroup.create(self.driver, 0, {'name': 'nms_group'})

        ser = Service.create(self.driver, 0, {'name': 'test_service'})
        Access.create(self.driver, ser.get_id(), {'group': f'group:{gr.get_id()}'}, parent_type='service')
        with self.subTest('User group linked to a service access'):
            self.assertRaises(ObjectNotDeletedException, gr.delete)
        if gr.get_id() is None:
            gr = UserGroup.create(self.driver, 0, {'name': 'nms_group'})

        shp = Shaper.create(self.driver, 0, {'name': 'test_shaper'})
        Access.create(self.driver, shp.get_id(), {'group': f'group:{gr.get_id()}'}, parent_type='shaper')
        with self.subTest('User group linked to a shaper access'):
            self.assertRaises(ObjectNotDeletedException, gr.delete)
        if gr.get_id() is None:
            gr = UserGroup.create(self.driver, 0, {'name': 'nms_group'})

        tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})
        ctrl = Controller.create(self.driver, net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModesStr.MF_HUB,
            'teleport': f'teleport:{tp.get_id()}'
        })
        Access.create(self.driver, ctrl.get_id(), {
            'group': f'group:{gr.get_id()}'}, parent_type='controller')
        with self.subTest('User group linked to a controller access'):
            self.assertRaises(ObjectNotDeletedException, gr.delete)
        if gr.get_id() is None:
            gr = UserGroup.create(self.driver, 0, {'name': 'nms_group'})

        vno = Vno.create(self.driver, net.get_id(), {'name': 'test_vno'})
        Access.create(self.driver, vno.get_id(), {'group': f'group:{gr.get_id()}'}, parent_type='vno')
        with self.subTest('User group linked to a vno access'):
            self.assertRaises(ObjectNotDeletedException, gr.delete)

    def test_scheduler(self):
        """Scheduler linked to a station"""
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})
        ctrl = Controller.create(self.driver, net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModesStr.MF_HUB,
            'teleport': f'teleport:{tp.get_id()}'
        })
        vno = Vno.create(self.driver, net.get_id(), {'name': 'test_vno'})
        sched = Scheduler.create(self.driver, net.get_id(), {'name': 'test_sched'})
        SchRange.create(self.driver, sched.get_id(), {'name': 'test_sch_range'})
        SchService.create(self.driver, sched.get_id(), {'name': 'test_sch_service'})
        Station.create(self.driver, vno.get_id(), {
            'name': 'test_stn',
            'enable': CheckboxStr.ON,
            'serial': 12345,
            'rx_controller': f'controller:{ctrl.get_id()}',
            'scheduler': f'scheduler:{sched.get_id()}',
        })
        with self.subTest('Scheduler linked to a station'):
            self.assertRaises(ObjectNotDeletedException, sched.delete)

    def test_sch_service(self):
        """Sch_service linked to a station's sch_task"""
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})
        ctrl = Controller.create(self.driver, net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModesStr.MF_HUB,
            'teleport': f'teleport:{tp.get_id()}'
        })
        vno = Vno.create(self.driver, net.get_id(), {'name': 'test_vno'})
        sched = Scheduler.create(self.driver, net.get_id(), {'name': 'test_sched'})
        SchRange.create(self.driver, sched.get_id(), {'name': 'test_sch_range'})
        sch_s = SchService.create(self.driver, sched.get_id(), {'name': 'test_sch_service'})
        stn = Station.create(self.driver, vno.get_id(), {
            'name': 'test_stn',
            'enable': CheckboxStr.ON,
            'serial': 12345,
            'rx_controller': f'controller:{ctrl.get_id()}',
            'scheduler': f'scheduler:{sched.get_id()}',
        })
        SchTask.create(self.driver, stn.get_id(), {
            'name': 'test_sch_task',
            'sch_service': f'sch_service:{sch_s.get_id()}'
        })
        with self.subTest('Sch_service linked to a station\'s sch_task'):
            self.assertRaises(ObjectNotDeletedException, sch_s.delete)

    def test_external_gateway(self):
        """Gateway linked to a station as the external gateway"""
        Network.create(self.driver, 0, params={'name': 'net1'})
        Vno.create(self.driver, 0, params={'name': 'vno1'})
        Teleport.create(self.driver, 0, params={'name': 'tp1'})
        dama_hub = Controller.create(self.driver, 0, {
            'name': 'dama_hub',
            'mode': ControllerModes.DAMA_HUB,
            'teleport': 'teleport:0',
        })
        gateway = Controller.create(self.driver, 0, {
            'name': 'gateway',
            'mode': ControllerModes.GATEWAY,
            'tx_controller': f'controller:{dama_hub.get_id()}',
            'teleport': 'teleport:0',
        })
        Station.create(self.driver, 0, {
            'name': 'test_stn',
            'serial': 12122,
            'enable': Checkbox.ON,
            'mode': StationModes.DAMA,
            'rx_controller': f'controller:{dama_hub.get_id()}',
            'ext_gateway': f'controller:{gateway.get_id()}',
        })
        with self.subTest('Gateway linked to a station as the external gateway'):
            self.assertRaises(ObjectNotDeletedException, gateway.delete)

    def test_multiple_links(self):
        """Teleport linked to multiple controller objects"""
        Network.create(self.driver, 0, params={'name': 'net1'})
        Vno.create(self.driver, 0, params={'name': 'vno1'})
        Teleport.create(self.driver, 0, params={'name': 'tp1'})
        for i in range(512):
            Controller.create(
                self.driver,
                0,
                params={'name': f'ctrl{i}', 'mode': ControllerModes.HUBLESS_MASTER, 'teleport': f'teleport:0'}
            )
        reply, error, error_code = self.driver.custom_get('api/object/delete/teleport=0')
        self.assertEqual(CANNOT_DELETE, error_code)
