from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import StationModes, ControllerModes, RouteTypes, RuleTypes, ActionTypes, \
    PriorityTypes, Checkbox, CheckTypes, QueueTypes
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_route import ControllerRoute
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.qos import Qos
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
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
    """Config for case_policy_config_confirm"""
    backup = BackupManager()
    backup.apply_backup(backup_name)
    if driver is None:
        api = get_drivers()
    else:
        api = driver

    net = Network.create(api, 0, {'name': 'test_net'})
    tp = Teleport.create(api, net.get_id(), {
        'name': 'test_tp',
        'sat_name': 'test_sat',
        'tx_lo': 0,
        'rx1_lo': 0,
        'rx2_lo': 0,
    })
    ctrl = Controller.create(api, net.get_id(), {
        'name': 'test_ctrl',
        'mode': ControllerModes.HUBLESS_MASTER,
        'teleport': f'teleport:{tp.get_id()}',
        'tx_on': Checkbox.ON,
        'tx_level': 20,
    }
    )
    vno = Vno.create(api, net.get_id(), {'name': 'test_vno'})
    stn = Station.create(api, vno.get_id(), {
        'name': 'test_stn',
        'serial': 12345,
        'enable': Checkbox.ON,
        'mode': StationModes.HUBLESS,
        'rx_controller': f'controller:{ctrl.get_id()}'
    })

    pol1 = Policy.create(api, net.get_id(), {'name': 'policy1'})
    pol2 = Policy.create(api, net.get_id(), {'name': 'policy2'})
    shaper = Shaper.create(api, net.get_id(), {'name': 'test_shaper'})

    # Based on a client's config
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 1,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.DST_NET,
        'net_ip': '10.0.0.0',
        'net_mask': '/8'
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 2,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.PROTOCOL,
        'protocol': 17,
        'goto_actions': Checkbox.ON
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 3,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.PROTOCOL,
        'protocol': 1,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 4,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.SET_QUEUE,
        'queue': QueueTypes.HIGH,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 5,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.SET_DSCP,
        'set_dscp': 46,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 6,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.DST_NET,
        'not': Checkbox.ON,
        'net_ip': '10.0.0.0',
        'net_mask': '/8',
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 7,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.PROTOCOL,
        'not': Checkbox.ON,
        'protocol': 1,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 8,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.DST_UDP_PORT,
        'not': Checkbox.ON,
        'port_min': 53,
        'port_max': 53,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 9,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.DST_TCP_PORT,
        'not': Checkbox.ON,
        'port_min': 25,
        'port_max': 25,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 10,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.DST_TCP_PORT,
        'not': Checkbox.ON,
        'port_min': 110,
        'port_max': 110,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 11,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.DST_NET,
        'not': Checkbox.ON,
        'net_ip': '31.47.189.230',
        'net_mask': '/32',
    })

    # Next config is to add all types
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 12,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.PRIORITY_802_1Q,
        'not': Checkbox.ON,
        'prio_802': 0,
        'goto_actions': Checkbox.ON,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 13,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.DROP,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 14,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.VLAN,
        'vlan_min': 100,
        'vlan_max': 200
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 15,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.SET_TS_CH,
        'shaper': f'shaper:{shaper.get_id()}',
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 16,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.NO_TCPA,
        'terminate': Checkbox.ON,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 17,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.TOS,
        'tos_min': 1,
        'tos_max': 5,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 18,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.COMPRESS_RTP,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 19,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.NO_SCREENING,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 20,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.SRC_NET,
        'net_ip': '172.16.7.0',
        'net_mask': '/24',
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 21,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.SET_ACM_CHANNEL,
        'acm_channel': 3,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 22,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.DROP_IF_STATION_DOWN,
        'terminate': Checkbox.ON,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 23,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.DSCP,
        'not': Checkbox.ON,
        'dscp_min': 2,
        'dscp_max': 3,
        'goto_actions': Checkbox.ON,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 24,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.ENCRYPT,
        'key': 28,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 25,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.SET_TOS,
        'set_tos': 255,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 26,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.GOTO_POLICY,
        'policy': f'policy:{pol2.get_id()}',
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 27,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.SRC_TCP_PORT,
        'port_min': 20000,
        'port_max': 25001,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 28,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.CALL_POLICY,
        'policy': f'policy:{pol2.get_id()}',
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 29,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.SRC_UDP_PORT,
        'not': Checkbox.ON,
        'port_min': 30001,
        'port_max': 35002,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 30,
        'type': RuleTypes.CHECK,
        'check_type': CheckTypes.ICMP_TYPE,
        'not': Checkbox.ON,
        'icmp_type': 8,
    })
    PolicyRule.create(api, pol1.get_id(), {
        'sequence': 31,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.COMPRESS_GTP,
        'terminate': Checkbox.ON,
    })
    service = Service.create(api, net.get_id(), {
        'name': 'test_service',
    })
    qos = Qos.create(api, net.get_id(), {
        'name': 'test_qos',
        'priority': PriorityTypes.POLICY,
        'policy': f'policy:{pol1.get_id()}',
    })
    ControllerRoute.create(api, ctrl.get_id(), {
        'type': RouteTypes.NETWORK_TX,
        'service': f'service:{service.get_id()}',
        'forward_qos': f'qos:{qos.get_id()}',
        'ip': '172.16.0.0',
        'mask': '/16',
    })
    StationRoute.create(api, stn.get_id(), {
        'type': RouteTypes.NETWORK_TX,
        'service': f'service:{service.get_id()}',
        'return_qos': f'qos:{qos.get_id()}',
        'ip': '192.168.13.0',
        'mask': '/24',
    })

    PolicyRule.create(api, pol2.get_id(), {
        'sequence': 1,
        'type': RuleTypes.ACTION,
        'action_type': ActionTypes.DROP,
    })

    backup.create_backup('case_policy_config_confirm.txt')


if __name__ == '__main__':
    create_config()
