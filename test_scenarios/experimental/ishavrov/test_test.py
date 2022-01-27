from src.custom_test_case import CustomTestCase
from src import nms_api, test_api

__author__ = 'ish'  # place your name in here
__version__ = '0.1'

from src.enum_types_constants import ControllerModes, StationModes, RouteTypes

options_path = ''
backup_name = 'default_config.txt'  # edit if needed

nms_options = test_api.get_nms()
nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
nms_api.load_config(backup_name)
net = nms_api.create('nms:0', 'network', {'name': 'test'})
tp = nms_api.create(net, 'teleport', {'name': 'test_tp', 'sat_name':'test_sat', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0,})
vno = nms_api.create(net,'vno',{'name':'testvno'})

controllers, stations = test_api.get_uhp_controllers_stations(1,['UHP200','UHP200X'],1,['ANY'])
mf_hub_uhp = controllers[0].get('web_driver')
mf_hub_nms = nms_api.create(net,'controller',{
            'name':'test1',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
            'device_ip': controllers[0].get('device_ip'),
            'device_vlan': controllers[0].get('device_vlan'),
            'device_gateway': controllers[0].get('device_gateway'),
            'tx_on': 1,
        })
ser = nms_api.create(net, 'service', {'name': 'testservice','stn_vlan': stations[0].get('device_vlan')})

for a in range(1,256):
    for b in range(1, 256):
        for c in range(1, 256):
            for d in range(1, 256):
                nms_api.create(mf_hub_nms, 'route', {
                    'type': RouteTypes.IP_ADDRESS,
                    'service': ser,
                    'ip': f'{a}.{b}.{c}.{d}'
                })

