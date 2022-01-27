from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, StationModes, RouteTypes, RouteIds

options_path = 'test_scenarios.statistics.states'
backup_name = 'default_config.txt'


class StationsStatesCase(CustomTestCase):
    """Star network with 3 real stations and numerous dummy ones (enabled, disabled, no rx_controller) check states"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.22'
    __execution_time__ = 100
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.real_stations = 2
        controllers, stations = test_api.get_uhp_controllers_stations(
            1, ['UHP200', 'UHP200X'], cls.real_stations, ['ANY']
        )
        mf_hub_uhp = controllers[0].get('web_driver')

        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        options = test_api.get_options(options_path)

        cls.dummy_off_stations = 15
        cls.dummy_on_stations = 10
        cls.dummy_unr_stations = 12
        cls.dummy_stations_above_limit = 15

        net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        tp = nms_api.create(net, 'teleport', {'name': 'test_tp', 'rx1_lo': 0, 'rx2_lo': 0, 'tx_lo': 0, 'sat_name': 's'})
        mf_hub = nms_api.create(net, 'controller', {
            'name': f'test_ctrl',
            'mode': ControllerModes.MF_HUB,
            'uhp_model': controllers[0].get('model'),
            'teleport': tp,
            'device_ip': controllers[0].get('device_ip'),
            'device_vlan': controllers[0].get('device_vlan'),
            'device_gateway': controllers[0].get('device_gateway'),
            'tx_on': True,
            'tx_level': options.get('tx_level'),
            'no_stn_check': True,
            'stn_number': cls.real_stations + cls.dummy_off_stations + cls.dummy_on_stations + 1
        })
        # Real stations
        vno = nms_api.create(net, 'vno', {'name': 'test_vno'})
        ser = nms_api.create(net, 'service', {'name': 'local', 'stn_vlan': stations[0].get('device_vlan')})
        for i in range(cls.real_stations):
            stn = nms_api.create(vno, 'station', {
                'name': f'{i+1}stn',
                'serial': stations[i].get('serial'),
                'enable': True,
                'mode': StationModes.STAR,
                'rx_controller': mf_hub,

            })
            nms_api.create(stn, 'route', {
                'type': RouteTypes.IP_ADDRESS,
                'service': ser,
                'ip': stations[i].get('device_ip'),
                'id': RouteIds.PRIVATE,
            })
            nms_api.create(stn, 'route', {
                'type': RouteTypes.STATIC_ROUTE,
                'service': ser,
                'ip': '0.0.0.0',
                'mask': '/0',
                'gateway': stations[i].get('device_gateway'),
                'id': RouteIds.PRIVATE,
            })

            stations[i].get('web_driver').star_station(params={
                'rx1_frq': nms_api.get_param(mf_hub, 'tx_frq'),
                'rx1_sr': nms_api.get_param(mf_hub, 'tx_sr'),
                'tx_level': options.get('tx_level'),
            })

        mf_hub_uhp.set_nms_permission(
            vlan=controllers[0].get('device_vlan'),
            password=nms_api.get_param(net, 'dev_password')
        )
        # Adding dummy OFF stations
        for i in range(cls.dummy_off_stations):
            nms_api.create(vno, 'station', {
                'name': f'disabled{i+1}',
                'serial': 20000 + i,
                'enable': False,
                'mode': StationModes.STAR,
                'rx_controller': mf_hub
            })
        # Adding dummy ON stations
        for i in range(cls.dummy_on_stations):
            nms_api.create(vno, 'station', {
                'name': f'dummy_enabled{i+1}',
                'serial': 30000 + i,
                'enable': True,
                'mode': StationModes.STAR,
                'rx_controller': mf_hub
            })

        # Adding unreachable stations
        for i in range(cls.dummy_unr_stations):
            nms_api.create(vno, 'station', {
                'name': f'unreachable{i+1}',
                'serial': 40000 + i,
                'enable': True,
                'mode': StationModes.STAR,
            })

        # Adding dummy stations above `stn_number` limit
        for i in range(cls.dummy_stations_above_limit):
            nms_api.create(vno, 'station', {
                'name': f'fake_stn_num{i+1}',
                'serial': 10000 + i,
                'enable': True,
                'mode': StationModes.STAR,
                'rx_controller': mf_hub,
                'hub_low_cn': 0,  # this let fake station to be Up
                'station_low_cn': 0,
            })
        if not nms_api.wait_up(mf_hub, timeout=60):
            test_api.error('MF hub is not UP')
        for i in range(cls.real_stations):
            if not nms_api.wait_up(f'station:{i}'):
                test_api.error(f'Station {i+1} is not UP')
        nms_api.wait_ticks(3)

    def test_states(self):
        """Check expected stations' states (Up, Down, Off, Idle)"""
        stations = nms_api.list_items('vno:0', 'station')
        states = {}
        for stn in stations:
            state = nms_api.get_param(stn, 'state')
            if state not in states.keys():
                states[state] = 1
            else:
                states[state] = states.get(state) + 1
        self.assertEqual(
            self.dummy_off_stations,
            states.get('Off'),
            msg=f'{self.dummy_off_stations} Off (disabled) stations, NMS reported {states.get("Off")} Off stations'
        )
        self.assertEqual(
            self.dummy_unr_stations + self.dummy_stations_above_limit,
            states.get('Idle'),
            msg=f'{self.dummy_unr_stations + self.dummy_stations_above_limit} Idle (rx_controller is not set) stations,'
                f' NMS reported {states.get("Idle")} Idle stations'
        )
        self.assertEqual(
            self.dummy_on_stations,
            states.get('Down'),
            msg=f'{self.dummy_on_stations} Down fake stations, '
                f'NMS reported {states.get("Down")} Down stations'
        )
        self.assertEqual(
            self.real_stations,
            states.get('Up'),
            msg=f'{self.real_stations} real stations, NMS reported {states.get("Up")} Up stations'
        )
