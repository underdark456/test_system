from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import StationModes, ControllerModes, RouteTypes, DeviceModes, RuleTypes, ActionTypes, \
    PriorityTypes
from src.file_manager.file_manager import FileManager
from src.nms_entities.basic_entities.access import Access
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.bal_controller import BalController
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_rip import ControllerRip
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.device import Device
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.profile import Profile
from src.nms_entities.basic_entities.qos import Qos
from src.nms_entities.basic_entities.scheduler import Scheduler
from src.nms_entities.basic_entities.scheduler_service import SchService
from src.nms_entities.basic_entities.scheduler_task import SchTask
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.sr_controller import SrController
from src.nms_entities.basic_entities.sr_teleport import SrTeleport
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.sw_upload import SwUpload
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

__author__ = 'dkudryashov'

options_path = 'utilities.create_config_for_test_cases'
backup_name = 'default_config.txt'


def get_drivers():
    connection_options = OptionsProvider.get_connection('global_options', API_CONNECT)
    api = DriversProvider.get_driver_instance(connection_options)
    return api


def get_options():
    options = OptionsProvider.get_options(options_path)
    return options


def create_config(driver=None):
    """Config for web_dynamic_dropdowns_case - maximum number of entities appearing in dynamic dropdowns"""
    backup = BackupManager()
    backup.apply_backup(backup_name)
    options = get_options()
    if driver is None:
        api = get_drivers()
    else:
        api = driver
    # Uploading a dummy UHP software file to be able to create sw_upload
    fm = FileManager()
    fm.upload_uhp_software('dummy_soft.240')

    net = Network.create(api, 0, {'name': 'test_net'})
    for i in range(1, options.get('number_of_teleport') + 1):
        Teleport.create(api, 0, {'name': f'teleport-{i}', 'sat_name': f'sat{i}'})
    for i in range(1, options.get('number_of_controller') - 3):
        Controller.create(api, net.get_id(), {
            'name': f'controller-{i}',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:0'
        })
    # 1. Inroute controller
    Controller.create(api, net.get_id(), {
        'name': f'inroute-1',
        'mode': ControllerModes.INROUTE,
        'teleport': f'teleport:0',
        'tx_controller': f'controller:0',
        'inroute': 2
    })
    # 2. controller
    Controller.create(api, net.get_id(), {
        'name': f'hubless_master-1',
        'mode': ControllerModes.HUBLESS_MASTER,
        'teleport': f'teleport:0',
        # 'tx_controller': f'controller:0',
        # 'inroute': 2
    })
    # 3. controller
    Controller.create(api, net.get_id(), {
        'name': f'test-3',
        'mode': ControllerModes.MF_HUB,
        'teleport': f'teleport:0',
        # 'tx_controller': f'controller:0',
        # 'inroute': 2
    })
    # 4. controller
    Controller.create(api, net.get_id(), {
        'name': f'test-4',
        'mode': ControllerModes.MF_HUB,
        'teleport': f'teleport:0',
        # 'tx_controller': f'controller:0',
        # 'inroute': 2
    })
    for i in range(1, options.get('number_of_group')):
        UserGroup.create(api, 0, {'name': f'usergroup-{i}'})
    Access.create(api, 0, {'group': 'group:1'})

    for i in range(1, options.get('number_of_alert') + 1):
        Alert.create(api, 0, {'name': f'alert-{i}', 'popup': True})
    for i in range(1, options.get('number_of_sr_controller') + 1):
        SrController.create(api, net.get_id(), {'name': f'sr_controller-{i}'})
    sr_tp = SrTeleport.create(api, 0, {'name': 'test_sr_teleport', 'teleport': 'teleport:0'})
    Device.create(api, sr_tp.get_id(), {'name': 'test_device', 'ip': '127.0.0.1', 'mode': DeviceModes.USED})
    for i in range(1, options.get('number_of_shaper') + 1):
        Shaper.create(api, net.get_id(), {'name': f'shaper-{i}'})
    for i in range(1, options.get('number_of_bal_controller') + 1):
        BalController.create(api, net.get_id(), {'name': f'bal_controller-{i}'})
    for i in range(1, options.get('number_of_policy') + 1):
        Policy.create(api, net.get_id(), {'name': f'policy-{i}'})
    PolicyRule.create(
        api,
        0,
        {'sequence': 1, 'type': RuleTypes.ACTION, 'action_type': ActionTypes.SET_TS_CH})
    PolicyRule.create(
        api,
        0,
        {'sequence': 2, 'type': RuleTypes.ACTION, 'action_type': ActionTypes.GOTO_POLICY, 'policy': 'policy:1'})
    for i in range(1, options.get('number_of_service') + 1):
        Service.create(api, net.get_id(), {'name': f'service-{i}'})
    for i in range(1, options.get('number_of_qos') + 1):
        Qos.create(api, net.get_id(), {'name': f'qos-{i}'})
    qos = Qos(api, net.get_id(), 0)
    qos.send_params({
        'priority': PriorityTypes.POLICY,
        'policy': 'policy:0',
    })
    for i in range(1, options.get('number_of_profile_set') + 1):
        Profile.create(api, net.get_id(), {'name': f'profile_set-{i}'})
    ControllerRip.create(api, 0, {'service': 'service:0'})
    ControllerRoute.create(api, 0, {'type': RouteTypes.IP_ADDRESS, 'service': 'service:0', 'ip': '127.0.0.2'})
    vno = Vno.create(api, net.get_id(), {'name': 'test_vno'})
    Station.create(api, vno.get_id(), {'name': 'test_stn', 'serial': 12345})
    Station.create(api, vno.get_id(), {'name': 'rx_only_stn', 'serial': 12346, 'mode': StationModes.RX_ONLY})
    SwUpload.create(api, net.get_id(), {'name': 'test_sw_upload', 'sw_file': 'dummy_soft.240'})
    for i in range(1, options.get('number_of_scheduler') + 1):
        Scheduler.create(api, net.get_id(), {'name': f'sched-{i}'})
    for i in range(1, options.get('number_of_sch_service') + 1):
        SchService.create(api, 0, {'name': f'sch_ser-{i}'})
    SchTask.create(api, 0, {'name': 'test_sch_task'})
    # TODO: add rest scheduler related objects
    backup.create_backup('case_dropdowns.txt')


if __name__ == '__main__':
    create_config()
