from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.enum_types_constants import StationModes, RouteTypes, RouteIds, ControllerModes, TtsModes

backup_name = 'default_config.txt'


class MfHub1StnUp(CustomTestCase):
    """MF hub and 1 station network UP preconfiguration"""

    @classmethod
    def set_up_class(cls):
        cls.controllers, cls.stations = test_api.get_uhp_controllers_stations(1, ['UHP200', 'UHP200X'], 1, ['ANY', ], )

        cls.mf_hub_uhp = cls.controllers[0].get('web_driver')
        cls.stn1_uhp = cls.stations[0].get('web_driver')
        cls.mf_hub_uhp.set_nms_permission(
            vlan=cls.controllers[0].get('device_vlan'),
            password='',
        )
        test_options = test_api.get_options(None)

        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        network = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        tp = nms_api.create(network, 'teleport', {'name': 'test_tp', 'rx1_lo': 0, 'rx2_lo': 0, 'tx_lo': 0})
        vno = nms_api.create(network, 'vno', {'name': 'vno_test'})
        cls.mf_hub = nms_api.create(network, 'controller', {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
            'uhp_model': cls.controllers[0].get('model'),
            'device_ip': cls.controllers[0].get('device_ip'),
            'device_vlan': cls.controllers[0].get('device_vlan'),
            'device_gateway': cls.controllers[0].get('device_gateway'),
            'hub_tts_mode': TtsModes.VALUE,
            'tts_value': 0,
            'tx_on': False,
            'tx_level': test_options.get('tx_level')
        })

        cls.stn1_uhp.star_station(params={
            'rx1_sr': nms_api.get_param(cls.mf_hub, 'tx_sr'),
            'rx1_frq': nms_api.get_param(cls.mf_hub, 'tx_frq'),
            'tx_level': test_options.get('tx_level')
        })

        cls.stn1 = nms_api.create(vno, 'station', {
            'name': 'stn1',
            'serial': cls.stations[0].get('serial'),
            'enable': True,
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub
        })

        service_local = nms_api.create(network, 'service', {
            'name': 'local',
            'stn_vlan': cls.stations[0].get('device_vlan')
        })

        nms_api.create(cls.stn1, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': service_local,
            'ip': cls.stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })

        nms_api.create(cls.stn1, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': service_local,
            'ip': '0.0.0.0',
            'gateway': cls.stations[0].get('device_gateway'),
            'mask': '/0',
            'id': RouteIds.PRIVATE,
        })

        nms_api.update(cls.mf_hub, {'tx_on': True})

        if not nms_api.wait_up(cls.mf_hub, timeout=60):
            test_api.error('MF hub is not UP')

        if not nms_api.wait_up(cls.stn1, timeout=60):
            test_api.error('Station 1 is not Up')

        nms_api.wait_ticks(3)
