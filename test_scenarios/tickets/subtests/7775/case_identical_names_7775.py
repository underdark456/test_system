import requests

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes
from src.exceptions import ObjectNotCreatedException
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.bal_controller import BalController
from src.nms_entities.basic_entities.camera import Camera
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.dashboard import Dashboard
from src.nms_entities.basic_entities.device import Device
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.profile import Profile
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

options_path = 'test_scenarios.tickets.subtests.7775'
backup_name = 'default_config.txt'


class IdenticalNamesCase(CustomTestCase):
    """Ticket 7775 - Crash upon creating objects with identical names"""

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.net1 = Network.create(cls.driver, 0, {'name': 'test_net'})
        cls.vno1 = Vno.create(cls.driver, cls.net1.get_id(), {'name': 'test_vno'})
        cls.server1 = Server.create(cls.driver, 0, {'name': 'test_server'})
        cls.group1 = UserGroup.create(cls.driver, 0, {'name': 'test_group'})
        cls.user1 = User.create(cls.driver, cls.group1.get_id(), {'name': 'test_user'})
        cls.alert1 = Alert.create(cls.driver, 0, {'name': 'test_alert', 'popup': True})
        cls.dash1 = Dashboard.create(cls.driver, 0, {'name': 'test_dash'})
        cls.tp1 = Teleport.create(cls.driver, cls.net1.get_id(), {'name': 'test_tp'})
        cls.ctrl1 = Controller.create(cls.driver, cls.net1.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModes.HUBLESS_MASTER,
            'teleport': f'teleport:{cls.tp1.get_id()}'
        })
        cls.service1 = Service.create(cls.driver, cls.net1.get_id(), {'name': 'test_service'})
        cls.shp1 = Shaper.create(cls.driver, cls.net1.get_id(), {'name': 'test_shp'})
        cls.pol1 = Policy.create(cls.driver, cls.net1.get_id(), {'name': 'test_pol'})
        cls.sr_ctrl = SrController.create(cls.driver, cls.net1.get_id(), {'name': 'test_sr_ctrl'})
        cls.sr_tp1 = SrTeleport.create(cls.driver, cls.sr_ctrl.get_id(), {'name': 'test_sr_tp'})
        cls.device = Device.create(cls.driver, cls.sr_tp1.get_id(), {'name': 'test_device'})
        cls.license = SrLicense.create(cls.driver, cls.net1.get_id(), {'name': 'test_lic'})
        cls.bal_ctrl = BalController.create(cls.driver, cls.net1.get_id(), {'name': 'test_bal_ctrl'})
        cls.pro_set = Profile.create(cls.driver, cls.net1.get_id(), {'name': 'test_pro'})
        cls.sw_up = SwUpload.create(cls.driver, cls.net1.get_id(), {'name': 'test_sw_up'})
        cls.cam = Camera.create(cls.driver, cls.net1.get_id(), {'name': 'test_cam'})
        cls.stn = Station.create(cls.driver, cls.vno1.get_id(), {
            'name': 'test_stn',
            'serial': 1,
            'mode': StationModes.MESH,
            'rx_controller': f'controller:{cls.ctrl1.get_id()}'
        })

    def test_network(self):
        """Test that creation of a Network with the name of the existing network does not lead to crash"""

        try:
            Network.create(self.driver, 0, {'name': 'test_net'})
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of a network with the name of the existing network leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('A network with the name of the existing network is not created without causing a crash')

    def test_vno(self):
        """Test that creation of a VNO with the name of the existing VNO does not lead to crash"""

        try:
            Vno.create(self.driver, self.net1.get_id(), {'name': 'test_vno'})
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of a VNO with the name of the existing VNO leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('A VNO with the name of the existing VNO is not created without causing a crash')

    def test_server(self):
        """Test that creation of a Server with the name of the existing Server does not lead to crash"""

        try:
            Server.create(self.driver, 0, {'name': 'test_server'})
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of a Server with the name of the existing Server leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('A Server with the name of the existing Server is not created without causing a crash')

    def test_group(self):
        """Test that creation of a Group with the name of the existing Group does not lead to crash"""

        try:
            Server.create(self.driver, 0, {'name': 'test_group'})
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of a Group with the name of the existing Group leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('A Group with the name of the existing Group is not created without causing a crash')

    def test_user(self):
        """Test that creation of a User in a group with the name
        of the existing User in the group does not lead to crash
        """
        try:
            User.create(self.driver, self.group1.get_id(), {'name': 'test_user'})
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of a User with the name of the existing User leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('A User with the name of the existing User is not created without causing a crash')

    def test_alert(self):
        """Test that creation of an Alert the name of the existing Alert does not lead to crash"""

        try:
            Alert.create(self.driver, 0, {'name': 'test_alert', 'popup': True})
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of an Alert with the name of the existing Alert leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('An Alert with the name of the existing Alert is not created without causing a crash')

    def test_dash(self):
        """Test that creation of a Dashboard the name of the existing Dashboard does not lead to crash"""

        try:
            Dashboard.create(self.driver, 0, {'name': 'test_dash'})
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of an Dashboard with the name of the existing Dashboard leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('An Dashboard with the name of the existing Dashboard is not created without causing a crash')

    def test_teleport(self):
        """Test that creation of a Teleport the name of the existing Teleport does not lead to crash"""

        try:
            Teleport.create(self.driver, 0, {'name': 'test_tp'})
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of an Teleport with the name of the existing Teleport leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('An Teleport with the name of the existing Teleport is not created without causing a crash')

    def test_controller(self):
        """Test that creation of a Controller the name of the existing Controller does not lead to crash"""

        try:
            Controller.create(self.driver, 0, {
                'name': 'test_ctrl',
                'mode': ControllerModes.HUBLESS_MASTER,
                'teleport': f'teleport:{self.tp1.get_id()}'
            })
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of an Controller with the name of the existing Controller leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('An Controller with the name of the existing Controller is not created without causing a crash')

    def test_service(self):
        """Test that creation of a Service the name of the existing Service does not lead to crash"""

        try:
            Service.create(self.driver, 0, {
                'name': 'test_service',
            })
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of an Service with the name of the existing Service leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('A Service with the name of the existing Service is not created without causing a crash')

    def test_shaper(self):
        """Test that creation of a Shaper the name of the existing Shaper does not lead to crash"""

        try:
            Shaper.create(self.driver, 0, {
                'name': 'test_shp',
            })
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of an Shaper with the name of the existing Shaper leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('An Shaper with the name of the existing Shaper is not created without causing a crash')

    def test_policy(self):
        """Test that creation of a Policy the name of the existing Policy does not lead to crash"""

        try:
            Policy.create(self.driver, 0, {
                'name': 'test_pol',
            })
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of an Policy with the name of the existing Policy leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('An Policy with the name of the existing Policy is not created without causing a crash')

    def test_sr_controller(self):
        """Test that creation of an SrController the name of the existing SrController does not lead to crash"""

        try:
            SrController.create(self.driver, 0, {
                'name': 'test_sr_ctrl',
            })
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of an SrController with the name of the existing SrController leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('An SrController with the name of the existing SrController '
                      'is not created without causing a crash')

    def test_sr_teleport(self):
        """Test that creation of an SrTeleport the name of the existing SrTeleport does not lead to crash"""

        try:
            SrTeleport.create(self.driver, 0, {
                'name': 'test_sr_tp',
            })
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of an SrTeleport with the name of the existing SrTeleport leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('An SrTeleport with the name of the existing SrTeleport '
                      'is not created without causing a crash')

    def test_device(self):
        """Test that creation of an Device the name of the existing Device does not lead to crash"""

        try:
            Device.create(self.driver, 0, {
                'name': 'test_device',
            })
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of an Device with the name of the existing Device leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('An Device with the name of the existing Device '
                      'is not created without causing a crash')

    def test_sr_license(self):
        """Test that creation of an SrLicense the name of the existing SrLicense does not lead to crash"""

        try:
            SrLicense.create(self.driver, 0, {
                'name': 'test_lic',
            })
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of an SrLicense with the name of the existing SrLicense leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('An SrLicense with the name of the existing SrLicense '
                      'is not created without causing a crash')

    def test_bal_controller(self):
        """Test that creation of an BalController the name of the existing BalController does not lead to crash"""

        try:
            BalController.create(self.driver, 0, {
                'name': 'test_bal_ctrl',
            })
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of an BalController with the name of the existing BalController leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('An BalController with the name of the existing BalController '
                      'is not created without causing a crash')

    def test_profile_set(self):
        """Test that creation of a Profile the name of the existing Profile does not lead to crash"""

        try:
            Profile.create(self.driver, 0, {
                'name': 'test_pro',
            })
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of a Profile with the name of the existing Profile leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('A Profile with the name of the existing Profile '
                      'is not created without causing a crash')

    def test_sw_upload(self):
        """Test that creation of a SwUpload the name of the existing SwUpload does not lead to crash"""

        try:
            SwUpload.create(self.driver, 0, {
                'name': 'test_sw_up',
            })
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of an SwUpload with the name of the existing SwUpload leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('A SwUpload with the name of the existing SwUpload '
                      'is not created without causing a crash')

    def test_camera(self):
        """Test that creation of a Camera the name of the existing Camera does not lead to crash"""

        try:
            Camera.create(self.driver, 0, {
                'name': 'test_cam',
            })
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of a Camera with the name of the existing Camera leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('A Camera with the name of the existing Camera '
                      'is not created without causing a crash')

    def test_station(self):
        """Test that creation of a Station the name of the existing Station does not lead to crash"""

        try:
            Station.create(self.driver, 0, {
                'name': 'test_stn',
                'serial': 2,
                'mode': StationModes.MESH,
                'rx_controller': f'controller:{self.ctrl1.get_id()}'
            })
        except requests.exceptions.ConnectionError as exc:
            self.critical('Creation of a Station with the name of the existing Station leads to a crash')
            raise exc
        except ObjectNotCreatedException:
            self.info('A Station with the name of the existing Station '
                      'is not created without causing a crash')
