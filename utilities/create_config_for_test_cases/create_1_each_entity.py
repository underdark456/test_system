from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, RouteTypes
from src.file_manager.file_manager import FileManager
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
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

options_path = 'utilities.create_config_for_test_cases'
backup_name = 'default_config.txt'
__author__ = 'dkudryashov'


def get_drivers():
    connection_options = OptionsProvider.get_connection('global_options', API_CONNECT)
    api = DriversProvider.get_driver_instance(connection_options)
    return api


def create_config(driver=None):
    backup = BackupManager()
    backup.apply_backup(backup_name)
    if driver is None:
        api = get_drivers()
    else:
        api = driver

    # Uploading a dummy UHP software file to be able to create sw_upload
    fm = FileManager()
    fm.upload_uhp_software('dummy_soft.240')

    Alert.create(api, 0, {'name': 'test_alert', 'popup': True})
    network = Network.create(api, 0, {'name': 'test_network'})
    teleport = Teleport.create(api, network.get_id(), {'name': 'test_teleport', 'sat_name': 'test_sat'})
    controller = Controller.create(api, network.get_id(), {
        'name': 'test_ctrl',
        'mode': ControllerModes.MF_HUB,
        'teleport': f'teleport:{teleport.get_id()}',
        'device_ip': '127.0.0.1',
    })
    service = Service.create(api, network.get_id(), {'name': 'test_service'})
    Server.create(api, 0, {'name': 'test_server', 'ip': '127.0.0.10'})
    Shaper.create(api, network.get_id(), {'name': 'test_shaper'})
    policy = Policy.create(api, network.get_id(), {'name': 'test_policy'})
    PolicyRule.create(api, policy.get_id(), {'sequence': 1})
    sr_ctrl = SrController.create(api, network.get_id(), {'name': 'test_sr_ctrl'})
    sr_teleport = SrTeleport.create(api, sr_ctrl.get_id(), {
        'name': 'test_sr_tp',
        'teleport': f'teleport:{teleport.get_id()}'
    })
    Device.create(api, sr_teleport.get_id(), {'name': 'test_device', 'ip': '127.0.0.2'})
    SrLicense.create(api, network.get_id(), {'name': 'test_sr_lic', 'license_key': '123456'})
    BalController.create(api, network.get_id(), {'name': 'test_bal_ctrl'})
    Profile.create(api, network.get_id(), {'name': 'test_profile'})
    SwUpload.create(api, network.get_id(), {'name': 'test_sw_up', 'sw_file': 'dummy_soft.240'})
    Camera.create(api, network.get_id(), {'name': 'test_camera'})
    Dashboard.create(api, network.get_id(), {'name': 'net_dash'}, parent_type='network')
    ControllerRoute.create(api, controller.get_id(), {
        'type': RouteTypes.IP_ADDRESS,
        'service': f'service:{service.get_id()}',
        'ip': '127.0.0.3',
    })
    ControllerRip.create(api, controller.get_id(), {'service': f'service:{service.get_id()}'})
    ControllerPortMap.create(api, controller.get_id(), {'internal_ip': '127.0.0.4'})
    vno = Vno.create(api, network.get_id(), {'name': 'test_vno'})
    stn = Station.create(api, vno.get_id(), {
        'name': 'test_stn',
        'serial': 12345
    })

    # Added in NMS 4.0.0.13
    sch = Scheduler.create(api, network.get_id(), {'name': 'test_scheduler'})
    SchRange.create(api, sch.get_id(), {'name': 'test_sch_range'})
    SchService.create(api, sch.get_id(), {'name': 'test_sch_service'})
    # Where is sch_service in the dropdown?
    SchTask.create(api, stn.get_id(), {'name': 'test_sch_task'})
    # Added in NMS 4.0.0.20
    Qos.create(api, network.get_id(), {'name': 'test_qos'})

    backup.create_backup('each_entity.txt')


if __name__ == '__main__':
    create_config()
