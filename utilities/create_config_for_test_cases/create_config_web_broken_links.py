from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, RouteTypes, StationModes, CheckboxStr, RuleTypes
from src.file_manager.file_manager import FileManager
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
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

options_path = 'utilities.create_config_for_test_cases'
backup_name = 'default_config.txt'


def get_drivers():
    connection_options = OptionsProvider.get_connection('global_options', API_CONNECT)
    api = DriversProvider.get_driver_instance(connection_options)
    return api


def create_each_entity(driver=None):
    if driver is None:
        api = get_drivers()
    else:
        api = driver
    backup = BackupManager()
    backup.apply_backup(backup_name)

    # Uploading a dummy UHP software file to be able to create sw_upload
    fm = FileManager()
    fm.upload_uhp_software('dummy_soft.240')

    Dashboard.create(api, 0, {'name': 'nms_dash'}, parent_type='nms')
    alert = Alert.create(api, 0, {'name': 'test_alert', 'popup': True})
    network = Network.create(api, 0, {'name': 'test_network'})
    net_group = UserGroup.create(api, network.get_id(), {'name': 'test_group_net'}, parent_type='network')
    net_user = User.create(api, net_group.get_id(), {'name': 'test_user_net'})
    Access.create(api, network.get_id(), {'group': f'group:{net_group.get_id()}'})
    teleport = Teleport.create(api, network.get_id(), {'name': 'test_teleport', 'sat_name': 'test_sat'})
    controller = Controller.create(api, network.get_id(), {
        'name': 'test_ctrl',
        'mode': ControllerModes.MF_HUB,
        'teleport': f'teleport:{teleport.get_id()}',
        'device_ip': '127.0.0.1',
    })
    service = Service.create(api, network.get_id(), {'name': 'test_service'})
    qos = Qos.create(api, network.get_id(), {'name': 'test_qos'})
    Server.create(api, 0, {'name': 'test_server', 'ip': '127.0.0.10'})
    shp = Shaper.create(api, network.get_id(), {'name': 'test_shaper'})
    Shaper.create(api, shp.get_id(), {'name': 'test_sub_shaper'}, parent_type='shaper')
    policy = Policy.create(api, network.get_id(), {'name': 'test_policy'})
    PolicyRule.create(api, policy.get_id(), {'sequence': 1, 'type': RuleTypes.CHECK})
    PolicyRule.create(api, policy.get_id(), {'sequence': 2, 'type': RuleTypes.ACTION})
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

    # Added in NMS 4.0.0.13
    sch = Scheduler.create(api, network.get_id(), {'name': 'test_scheduler'})
    SchRange.create(api, sch.get_id(), {'name': 'test_sch_range'})
    sch_ser = SchService.create(api, sch.get_id(), {'name': 'test_sch_service'})

    vno = Vno.create(api, network.get_id(), {'name': 'test_vno'})
    Dashboard.create(api, vno.get_id(), {'name': 'vno_dash'}, parent_type='vno')
    stn_vno = Station.create(api, vno.get_id(), {
        'name': 'test_stn_vno',
        'serial': 111111,
        'enable': CheckboxStr.ON,
        'mode': StationModes.STAR,
        'rx_controller': f'controller:{controller.get_id()}',
    })
    stn_vno_route = StationRoute.create(
        api,
        stn_vno.get_id(),
        {'type': RouteTypes.IP_ADDRESS, 'ip': '127.0.0.10', 'service': f'service:{service.get_id()}'})
    stn_vno_rip = StationRip.create(api, stn_vno.get_id(), {'service': f'service:{service.get_id()}'})
    stn_vno_port_map = StationPortMap.create(api, stn_vno.get_id(), {})
    stn_vno_sch_task = SchTask.create(
        api,
        stn_vno.get_id(),
        {'name': 'sch_task1', 'sch_service': f'sch_service:{sch_ser.get_id()}'}
    )

    sub_vno = Vno.create(api, vno.get_id(), {'name': 'test_sub_vno'}, parent_type='vno')
    Dashboard.create(api, sub_vno.get_id(), {'name': 'sub_vno_dash'}, parent_type='vno')
    stn_sub_vno = Station.create(api, sub_vno.get_id(), {
        'name': 'test_stn_vno',
        'serial': 222222,
        'enable': CheckboxStr.ON,
        'mode': StationModes.STAR,
        'rx_controller': f'controller:{controller.get_id()}',
    })
    stn_sub_vno_route = StationRoute.create(
        api,
        stn_vno.get_id(),
        {'type': RouteTypes.IP_ADDRESS, 'ip': '127.0.0.11', 'service': f'service:{service.get_id()}'}
    )
    stn_sub_vno_rip = StationRip.create(api, stn_sub_vno.get_id(), {'service': f'service:{service.get_id()}'})
    stn_sub_vno_port_map = StationPortMap.create(api, stn_sub_vno.get_id(), {})
    stn_sub_vno_sch_task = SchTask.create(
        api,
        stn_sub_vno.get_id(),
        {'name': 'sch_task2', 'sch_service': f'sch_service:{sch_ser.get_id()}'}
    )

    backup.create_backup('case_web_broken_links.txt')


if __name__ == '__main__':
    create_each_entity()
