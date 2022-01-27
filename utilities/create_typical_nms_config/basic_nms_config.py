# test_system/utilities/create_typical_nms_config/basic_nms_config.py
from src.constants import NEW_OBJECT_ID
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.basic_entities.alert import Alert
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.profile import Profile
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.user_group import UserGroup
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, API_CONNECT


def get_drivers():
    connection_options = OptionsProvider.get_connection('global_options', API_CONNECT)
    api = DriversProvider.get_driver_instance(connection_options)
    return api


def create_basic_nms_config():
    api = get_drivers()

    alert = Alert(api, 0, NEW_OBJECT_ID, {'name': 'test_alert'})
    alert.save()

    network = Network(api, 0, NEW_OBJECT_ID, {'name': 'default_network'})
    network.save()

    profile = Profile(api, network.get_id(), NEW_OBJECT_ID, {'name': 'test_profile'})
    profile.save()

    shaper = Shaper(api, network.get_id(), NEW_OBJECT_ID, {'name': 'test_shaper'})
    shaper.save()

    teleport = Teleport(api, network.get_id(), NEW_OBJECT_ID, {'name': 'test_teleport'})
    teleport.save()

    controller = Controller(api, network.get_id(), NEW_OBJECT_ID,
                            {
                                'name': 'test_mf_hub',
                                'mode': '1',
                                'teleport': F"teleport:{teleport.get_id()}"
                            }
                            )
    controller.save()

    vno = Vno(api, network.get_id(), NEW_OBJECT_ID, {'name': 'test_vno'})
    vno.save()

    station = Station(api, vno.get_id(), NEW_OBJECT_ID,
                      {
                          'name': 'test_station',
                          'serial': '12345'
                      }
                      )
    station.save()

    user_group = UserGroup(api, 0, NEW_OBJECT_ID, {'name': 'operators'})
    user_group.save()
