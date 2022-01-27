from src.custom_test_case import CustomTestCase
from src import nms_api, test_api

__author__ = 'ish'  # place your name in here
__version__ = '0.1'

from src.enum_types_constants import ControllerModes, StationModes, RouteTypes

options_path = ''
backup_name = 'default_config.txt'  # edit if needed


# edit name of the test case class, should end with `Case`, i.e. `class StarNetworkUpCase(CustomTestCase)`:
class SampleCase(CustomTestCase):
    """One line string describing the test case"""


    @classmethod
    def set_up_class(cls):
        # initial setup for the test case
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)
        net = nms_api.create('nms:0', 'network', {'name': 'test'})
        tp = nms_api.create(net, 'teleport', {'name': 'test_tp', 'sat_name':'test_sat', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0,})
        vno = nms_api.create(net,'vno',{'name':'testvno'})

        controllers, stations = test_api.get_uhp_controllers_stations(1,['UHP200','UHP200X'],1,['ANY'])
        cls.mf_hub_uhp = controllers[0].get('web_driver')
        cls.station_uhp = stations[0].get('web_driver')
        cls.mf_hub_nms = nms_api.create(net,'controller',{
            'name':'test1',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
            'device_ip': controllers[0].get('device_ip'),
            'device_vlan': controllers[0].get('device_vlan'),
            'device_gateway': controllers[0].get('device_gateway'),
            'tx_on': 1,
        })
        station_nms = nms_api.create(vno, 'station', {
            'name': 'station1',
            'enable': True,
            'serial': stations[0].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub_uhp
        })
        ser = nms_api.create(net, 'service', {'name': 'testservice','stn_vlan': stations[0].get('device_vlan')})
        nms_api.create(station_nms, 'route',{
            'type': RouteTypes.IP_ADDRESS,
            'service': ser,
            'ip': stations[0].get('device_ip')
        })
        nms_api.create(station_nms,'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': ser,
            'mask': '/0',
            'gateway':stations[0].get('device_gateway')
        })

        cls.mf_hub_uhp.set_nms_permission(vlan=controllers[0].get('device_vlan'), password='')

        cls.station_uhp.star_station(params={
            'rx1_frq': nms_api.get_param(cls.mf_hub_nms, 'rx1_frq'),
            'rx1_sr': nms_api.get_param(cls.mf_hub_nms, 'rx1_sr')
        })
        if not nms_api.wait_up(cls.mf_hub_nms, timeout=60):
            test_api.error('hub_not_up')
        if not nms_api.wait_up(station_nms, timeout=60):
            test_api.error('st_not_up')

    def test_sample(self):
        """One line string describing the test method"""
        test_tx = str(nms_api.get_param(self.mf_hub_nms,'station_tx'))
        uhp_tx = self.mf_hub_uhp.get_stations_state().get('2').get('sttx')
        self.assertEqual(test_tx,uhp_tx)

