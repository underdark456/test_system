from src.custom_test_case import CustomTestCase
from src import nms_api, test_api

__author__ = 'ish'  # place your name in here
__version__ = '0.1'

from src.enum_types_constants import ControllerModes, StationModes, RouteTypes, TdmaModcod

options_path = ''
backup_name = 'default_config.txt'  # edit if needed

# edit name of the test case class, should end with `Case`, i.e. `class StarNetworkUpCase(CustomTestCase)`:

nms_options = test_api.get_nms()
nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
nms_api.load_config(backup_name)

net = nms_api.create('nms:0', 'network', {'name': 'hubless'})
tp = nms_api.create(net, 'teleport', {'name': 'hubless_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0,})
vno = nms_api.create(net,'vno',{'name':'hubless_vno'})
controllers, stations = test_api.get_uhp_controllers_stations(1,['UHP200','UHP200X'],1,['ANY'])
service = nms_api.create(net, 'service', {'name': 'hubless_service','stn_vlan': stations[0].get('device_vlan')})

hubless_master_uhp = controllers[0].get('web_driver')
hubless_staton_uhp = stations[0].get('web_driver')
hubless_master_nms = nms_api.create(net,'controller',{
            'name':'hubless_master',
            'mode': ControllerModes.HUBLESS_MASTER,
            'teleport': tp,
            'device_ip': controllers[0].get('device_ip'),
            'device_vlan': controllers[0].get('device_vlan'),
            'device_gateway': controllers[0].get('device_gateway'),
            'tx_on': 1,
             })
hubless_station_nms = nms_api.create(vno, 'station', {
            'name': 'hubless_station',
            'enable': True,
            'serial': stations[0].get('serial'),
            'mode': StationModes.HUBLESS,
            'rx_controller': hubless_master_nms
        })
nms_api.create(hubless_station_nms, 'route',{
            'type': RouteTypes.IP_ADDRESS,
            'service': service,
            'ip': stations[0].get('device_ip')
        })
nms_api.create(hubless_station_nms, 'route', {
    'type': RouteTypes.STATIC_ROUTE,
    'service': service,
    'mask': '/0',
    'gateway': stations[0].get('device_gateway')
})

hubless_master_uhp.set_nms_permission(vlan=controllers[0].get('device_vlan'), password='')

hubless_staton_uhp.hubless_station(params={
    'rx1_frq': nms_api.get_param(hubless_master_nms,'rx1_frq'),
    'rx1_sr': nms_api.get_param(hubless_master_nms,'rx1_sr'),
    'rx1_enable': 1,
    'tx_on': nms_api.get_param(hubless_master_nms,'tx_on'),
    'tdma_mc': TdmaModcod._QPSK_1_2,
    'mf1_rx': nms_api.get_param(hubless_master_nms,'mf1_rx'),
    'mf1_tx': nms_api.get_param(hubless_master_nms,'mf1_rx'),
})

