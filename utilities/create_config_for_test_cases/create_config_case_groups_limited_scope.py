from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes
from src.nms_entities.basic_entities.access import Access
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user import User
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
    """
    Config creation for case_users limited scopes:
        - 2 Networks with a controller, a VNO and a Sub-VNO are created;
        - In each net and vno a user group and a user are created;
        - In each net and vno an access with the corresponding group is created;
        - In each controller an access with a dedicated group is created.
    """
    backup = BackupManager()
    backup.apply_backup(backup_name)
    if driver is None:
        api = get_drivers()
    else:
        api = driver

    net1 = Network.create(api, 0, params={'name': 'net-1'})
    group_net_1 = UserGroup.create(
        api,
        net1.get_id(),
        params={'name': 'group_net_1'},
        parent_type='network'
    )
    User.create(api, group_net_1.get_id(), params={'name': 'user_net_1', 'password': 'qwerty'})
    Access.create(
        api,
        net1.get_id(),
        params={
            'group': f'group:{group_net_1.get_id()}',
            'edit': 'ON',
            'use': 'ON'
        },
        parent_type='network'
    )
    vno1 = Vno.create(api, net1.get_id(), params={'name': 'vno-1'})
    group_vno_1 = UserGroup.create(api, vno1.get_id(), params={'name': 'group_vno_1'}, parent_type='vno')
    User.create(api, group_vno_1.get_id(), params={'name': 'user_vno_1', 'password': 'qwerty'})
    Access.create(
        api,
        vno1.get_id(),
        params={
            'group': f'group:{group_vno_1.get_id()}',
            'edit': 'ON',
            'use': 'ON'
        },
        parent_type='vno'
    )
    sub_vno1 = Vno.create(api, vno1.get_id(), params={'name': 'subvno-1'}, parent_type='vno')
    group_sub_vno_1 = UserGroup.create(
        api,
        sub_vno1.get_id(),
        params={'name': 'group_sub_vno_1'},
        parent_type='vno'
    )
    User.create(api, group_sub_vno_1.get_id(), params={
        'name': 'user_sub_vno_1',
        'password': 'qwerty'
    })
    Access.create(
        api,
        sub_vno1.get_id(),
        params={
            'group': f'group:{group_sub_vno_1.get_id()}',
            'edit': 'ON',
            'use': 'ON'
        },
        parent_type='vno'
    )
    tp1 = Teleport.create(api, net1.get_id(), params={'name': 'tp-1', 'sat_name': 'sat-1'})
    ctrl1 = Controller.create(api, net1.get_id(), params={
        'name': 'ctrl-1',
        'mode': ControllerModes.HUBLESS_MASTER,
        'teleport': f'teleport:{tp1.get_id()}'
    })
    group_ctrl_1 = UserGroup.create(api, 0, params={'name': 'group_ctrl_1'})
    User.create(api, group_ctrl_1.get_id(), params={'name': 'user_ctrl_1'})
    Access.create(
        api,
        ctrl1.get_id(),
        params={
            'group': f'group:{group_ctrl_1.get_id()}',
            'edit': 'ON',
            'use': 'ON'
        },
        parent_type='controller'
    )

    net2 = Network.create(api, 0, params={'name': 'net-2'})
    group_net_2 = UserGroup.create(
        api,
        net2.get_id(),
        params={'name': 'group_net_2'},
        parent_type='network'
    )
    User.create(api, group_net_2.get_id(), params={'name': 'user_net_2', 'password': 'qwerty'})
    Access.create(
        api,
        net2.get_id(),
        params={
            'group': f'group:{group_net_2.get_id()}',
            'edit': 'ON',
            'use': 'ON'
        },
        parent_type='network'
    )
    vno2 = Vno.create(api, net2.get_id(), params={'name': 'vno-2'})
    group_vno_2 = UserGroup.create(api, vno2.get_id(), params={'name': 'group_vno_2'}, parent_type='vno')
    User.create(api, group_vno_2.get_id(), params={'name': 'user_vno_2', 'password': 'qwerty'})
    Access.create(
        api,
        vno2.get_id(),
        params={
            'group': f'group:{group_vno_2.get_id()}',
            'edit': 'ON',
            'use': 'ON'
        },
        parent_type='vno'
    )
    sub_vno2 = Vno.create(api, vno2.get_id(), params={'name': 'subvno-2'}, parent_type='vno')
    group_sub_vno_2 = UserGroup.create(
        api,
        sub_vno2.get_id(),
        params={'name': 'group_sub_vno_2'},
        parent_type='vno'
    )
    User.create(api, group_sub_vno_2.get_id(), params={
        'name': 'user_sub_vno_2',
        'password': 'qwerty'
    })
    Access.create(
        api,
        sub_vno2.get_id(),
        params={
            'group': f'group:{group_sub_vno_2.get_id()}',
            'edit': 'ON',
            'use': 'ON'
        },
        parent_type='vno'
    )
    tp2 = Teleport.create(api, net2.get_id(), params={'name': 'tp-2', 'sat_name': 'sat2'})
    ctrl2 = Controller.create(api, net2.get_id(), params={
        'name': 'ctrl-2',
        'mode': ControllerModes.HUBLESS_MASTER,
        'teleport': f'teleport:{tp2.get_id()}'
    })
    group_ctrl_2 = UserGroup.create(api, 0, params={'name': 'group_ctrl_2'})
    User.create(api, group_ctrl_2.get_id(), params={'name': 'user_ctrl_2'})
    Access.create(
        api,
        ctrl2.get_id(),
        params={
            'group': f'group:{group_ctrl_2.get_id()}',
            'edit': 'ON',
            'use': 'ON'
        },
        parent_type='controller'
    )
    backup.create_backup('groups_limited_scopes.txt')


if __name__ == '__main__':
    create_config()
