import ipaddress

from src.backup_manager.backup_manager import BackupManager
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, StationModes, Checkbox, RouteTypes, RouteIds
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
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
    """Config for WebUsersUseCase: 3 networks with 3 vnos in each and 3 sub vnos etc."""
    backup = BackupManager()
    backup.apply_backup(backup_name)
    if driver is None:
        api = get_drivers()
    else:
        api = driver

    # Used in station routes
    ip_address = ipaddress.IPv4Address('127.0.0.1')
    next_stn_sn = 10000

    for n in range(1, 4):
        net = Network.create(api, 0, {'name': f'net{n}'})
        tp = Teleport.create(api, net.get_id(), {'name': f'tp_net{n}', 'sat_name': f'sat_net{n}'})
        # All controllers types creation block
        mf_hub = Controller.create(
            api,
            net.get_id(),
            {'name': f'mf_hub_net{n}', 'mode': ControllerModes.MF_HUB, 'teleport': f'teleport:{tp.get_id()}'})
        outroute = Controller.create(
            api,
            net.get_id(),
            {'name': f'outroute_net{n}', 'mode': ControllerModes.OUTROUTE, 'teleport': f'teleport:{tp.get_id()}'}
        )
        dama_hub = Controller.create(
            api,
            net.get_id(),
            {'name': f'dama_hub_net{n}', 'mode': ControllerModes.DAMA_HUB, 'teleport': f'teleport:{tp.get_id()}'}
        )
        hubless = Controller.create(
            api,
            net.get_id(),
            {'name': f'hubless_net{n}', 'mode': ControllerModes.HUBLESS_MASTER, 'teleport': f'teleport:{tp.get_id()}'}
        )
        inroute = Controller.create(
            api,
            net.get_id(),
            {
                'name': f'inroute_net{n}',
                'mode': ControllerModes.INROUTE,
                'teleport': f'teleport:{tp.get_id()}',
                'tx_controller': f'controller:{mf_hub.get_id()}',
                'inroute': n + 1,
            }
        )
        dama_inroute = Controller.create(
            api,
            net.get_id(),
            {
                'name': f'dama_inroute_net{n}',
                'mode': ControllerModes.DAMA_INROUTE,
                'teleport': f'teleport:{tp.get_id()}',
                'tx_controller': f'controller:{dama_hub.get_id()}',
            }
        )
        mf_inroute = Controller.create(
            api,
            net.get_id(),
            {'name': f'mf_inroute_net{n}', 'mode': ControllerModes.MF_INROUTE, 'teleport': f'teleport:{tp.get_id()}'})
        gateway = Controller.create(
            api,
            net.get_id(),
            {
                'name': f'gateway_net{n}',
                'mode': ControllerModes.GATEWAY,
                'teleport': f'teleport:{tp.get_id()}',
                'tx_controller': f'controller:{mf_hub.get_id()}',
            }
        )
        # End of all controllers types creation block

        # Services
        for ser in range(1, 6):
            ser = Service.create(api, net.get_id(), {'name': f'service{ser}_net{n}'})
        # Shapers
        for shp in range(1, 6):
            Shaper.create(api, net.get_id(), {'name': f'shaper{shp}_net{n}'})

        # User groups and users in Network
        for gr in range(1, 4):
            group = UserGroup.create(
                api,
                net.get_id(),
                {'name': f'gr{gr}_net{n}', 'active': Checkbox.ON},
                parent_type='network'
            )
            for us in range(1, 4):
                user = User.create(api, group.get_id(), {'name': f'us{us}_gr{gr}_net{n}', 'password': 'qwerty'})

        for v in range(1, 4):
            vno = Vno.create(api, net.get_id(), {'name': f'vno{v}_net{n}'})

            # User groups and users in VNO
            for gr in range(1, 4):
                group = UserGroup.create(
                    api,
                    vno.get_id(),
                    {'name': f'gr{gr}_vno{v}_net{n}', 'active': Checkbox.ON},
                    parent_type='vno'
                )
                for us in range(1, 4):
                    user = User.create(api, group.get_id(),
                                       {'name': f'us{us}_gr{gr}_vno{v}_net{n}', 'password': 'qwerty'})

            for st1 in range(1, 4):
                stn = Station.create(
                    api,
                    vno.get_id(),
                    {
                        'name': f'stn{st1}_vno{v}_net{n}',
                        'serial': next_stn_sn,
                        'mode': StationModes.STAR,
                        'rx_controller': f'controller:{mf_hub.get_id()}'
                    }
                )
                next_stn_sn += 1
                route = StationRoute.create(api, stn.get_id(), {
                    'type': RouteTypes.IP_ADDRESS,
                    'service': f'service:{ser.get_id()}',
                    'ip': str(ip_address + 1),
                    'id': RouteIds.PRIVATE
                })
                ip_address += 1

            for s in range(1, 4):
                sub_vno = Vno.create(api, vno.get_id(), {'name': f'sub{s}_vno{v}_net{n}'}, parent_type='vno')
                # User groups and users in Sub-VNO
                for gr in range(1, 4):
                    group = UserGroup.create(
                        api,
                        sub_vno.get_id(),
                        {'name': f'gr{gr}_sub{s}_vno{v}_net{n}', 'active': Checkbox.ON},
                        parent_type='vno'
                    )
                    for us in range(1, 4):
                        user = User.create(
                            api,
                            group.get_id(),
                            {'name': f'us{us}_gr{gr}_sub{s}_vno{v}_net{n}', 'password': 'qwerty'}
                        )
                for st2 in range(1, 4):
                    stn = Station.create(
                        api,
                        sub_vno.get_id(),
                        {
                            'name': f'stn{st2}_sub{s}_vno{v}_net{n}',
                            'serial': next_stn_sn,
                            'mode': StationModes.STAR,
                            'rx_controller': f'controller:{mf_hub.get_id()}'
                        }
                    )
                    next_stn_sn += 1
                    route = StationRoute.create(api, stn.get_id(), {
                        'type': RouteTypes.IP_ADDRESS,
                        'service': f'service:{ser.get_id()}',
                        'ip': str(ip_address + 1),
                        'id': RouteIds.PRIVATE
                    })
                    ip_address += 1
    backup.create_backup('case_users_use_access.txt')


if __name__ == '__main__':
    create_config()
