from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, RouteTypes
from src.nms_entities.basic_entities.access import Access
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.bal_controller import BalController
from src.nms_entities.basic_entities.camera import Camera
from src.nms_entities.basic_entities.controller import Controller
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
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.web.web_default_values'
backup_name = 'default_config.txt'


class WebDefaultValuesCase(CustomTestCase):
    """WEB create objects by passing only minimum required parameters to check if there are wrong defaults in meta"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.22'
    __execution_time__ = 50  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        # WEB driver
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT),
            driver_id='case_web_default_values',
            store_driver=False,
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

    def test_default_parameters(self):
        """One line string describing the test case"""
        net = Network.create(self.driver, 0, {'name': 'test_net'})
        Server.create(self.driver, 0, {'name': 'ser'})
        gr = UserGroup.create(self.driver, 0, {'name': 'gr'})
        User.create(self.driver, gr.get_id(), {'name': 'us'})
        Alert.create(self.driver, 0, {'name': 'al', 'popup': True})
        Access.create(self.driver, 0, {'group': f'group:{gr.get_id()}'})
        Dashboard.create(self.driver, 0, {'name': 'dash'})
        tp = Teleport.create(self.driver, net.get_id(), {'name': 'test_tp'})
        vno = Vno.create(self.driver, net.get_id(), {'name': 'vno'})
        ser = Service.create(self.driver, net.get_id(), {'name': 'ser'})
        Shaper.create(self.driver, net.get_id(), {'name': 'shp'})
        pol = Policy.create(self.driver, net.get_id(), {'name': 'pol'})
        PolicyRule.create(self.driver, pol.get_id(), {'sequence': 1})
        sr_ctrl = SrController.create(self.driver, net.get_id(), {'name': 'sr_ctl'})
        sr_tp = SrTeleport.create(
            self.driver,
            sr_ctrl.get_id(),
            {'name': 'sr_tp', 'teleport': f'teleport:{tp.get_id()}'}
        )
        Device.create(self.driver, sr_tp.get_id(), {'name': 'dev'})
        SrLicense.create(self.driver, 0, {'name': 'lic'})
        BalController.create(self.driver, 0, {'name': 'bal'})
        Profile.create(self.driver, 0, {'name': 'pro'})
        SwUpload.create(self.driver, 0, {'name': 'sw'})
        Camera.create(self.driver, 0, {'name': 'cam'})
        sch = Scheduler.create(self.driver, 0, {'name': 'sch'})
        SchRange.create(self.driver, sch.get_id(), {'name': 'sch_r'})
        SchService.create(self.driver, sch.get_id(), {'name': 'sch_s'})
        Qos.create(self.driver, 0, {'name': 'qos'})
        stn = Station.create(self.driver, vno.get_id(), {'name': 'stn', 'serial': 25363})
        StationRoute.create(self.driver, stn.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{ser.get_id()}',
            'ip': '127.0.0.1'
        })
        StationRip.create(self.driver, stn.get_id(), {'service': f'service:{ser.get_id()}'})
        StationPortMap.create(self.driver, stn.get_id(), {})
        SchTask.create(self.driver, stn.get_id(), {'name': 'sch_t'})
        Controller.create(self.driver, net.get_id(), {
            'name': 'mf-hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{tp.get_id()}'
        })
