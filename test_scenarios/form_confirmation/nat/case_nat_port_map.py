import ipaddress
from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, Checkbox, StationModes, RouteTypes, TtsModes, RouteIds

options_path = 'test_scenarios.form_confirmation.nat'
backup_name = 'default_config.txt'


class NatPortMapConfirmationCase(CustomTestCase):
    """One line string describing the test case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 110  # approximate case execution time in seconds

    @classmethod
    def set_up_class(cls):
        cls.controllers, cls.stations = test_api.get_uhp_controllers_stations(1, ['UHP200', 'UHP200X'], 1, ['ANY', ])

        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        cls.options = test_api.get_options(options_path)
        net = nms_api.create('nms:0', 'network', {'name': 'test_net'})
        tp = nms_api.create(net, 'teleport', {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0})
        cls.mf_hub = nms_api.create(net, 'controller', {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
            'device_ip': cls.controllers[0].get('device_ip'),
            'device_vlan': cls.controllers[0].get('device_vlan'),
            'device_gateway': cls.controllers[0].get('device_gateway'),
            'uhp_model': cls.controllers[0].get('model'),
            'tx_on': Checkbox.ON,
            'tx_level': cls.options.get('tx_level'),
            'hub_tts_mode': TtsModes.VALUE,
            'tts_value': 0,
        })
        stn_service = nms_api.create(net, 'service', {
            'name': 'stn_service',
            'stn_vlan': cls.stations[0].get('device_vlan'),
        })
        vno = nms_api.create(net, 'vno', {'name': 'test_vno'})
        cls.stn = nms_api.create(vno, 'station', {
            'name': 'test_stn',
            'enable': Checkbox.ON,
            'serial': cls.stations[0].get('serial'),
            'mode': StationModes.STAR,
            'rx_controller': cls.mf_hub,
        })
        nms_api.create(cls.stn, 'route', {
            'type': RouteTypes.IP_ADDRESS,
            'service': stn_service,
            'ip': cls.stations[0].get('device_ip'),
            'id': RouteIds.PRIVATE,
        })
        nms_api.create(cls.stn, 'route', {
            'type': RouteTypes.STATIC_ROUTE,
            'service': stn_service,
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': cls.stations[0].get('device_gateway'),
        })

        cls.mf_hub_uhp = cls.controllers[0].get('web_driver')
        cls.stn_uhp = cls.stations[0].get('web_driver')

        cls.mf_hub_uhp.set_nms_permission(
            vlan=cls.controllers[0].get('device_vlan'),
            password=nms_api.get_param(net, 'dev_password')
        )
        cls.stn_uhp.star_station(params={
            'rx1_frq': nms_api.get_param(cls.mf_hub, 'rx1_frq'),
            'rx1_sr': nms_api.get_param(cls.mf_hub, 'rx1_sr'),
            'tx_level': cls.options.get('tx_level'),
        })
        if not nms_api.wait_up(cls.mf_hub, timeout=60):
            test_api.error('MF hub is not in UP state')
        if not nms_api.wait_up(cls.stn, timeout=60):
            test_api.error('Station is not in UP state')
        nms_api.wait_ticks(2)

    def test_nat_mf_hub(self):
        """Check NAT settings and port mappings in UHP controller"""
        self.check_nat(self.mf_hub, self.mf_hub_uhp, 'MF hub')

    def test_nat_star_station(self):
        """Check NAT settings and port mappings in UHP station"""
        self.check_nat(self.stn, self.stn_uhp, 'Star station')

    def check_nat(self, nms_obj, uhp_driver, obj_name):
        # Looks like UHP cannot handle more than 511 port_maps
        number_of_maps = 511
        nat_ext_ip = self.options.get('nat_ext_ip')
        nat_int_ip = self.options.get('nat_int_ip')
        nat_int_mask = self.options.get('nat_int_mask')
        first_ip = self.options.get('first_int_ip')
        nms_api.update(nms_obj, {
            'nat_enable': Checkbox.ON,
            'nat_ext_ip': nat_ext_ip,
            'nat_int_ip': nat_int_ip,
            'nat_int_mask': nat_int_mask,
        })
        next_int_ip = ipaddress.IPv4Address(first_ip)
        for i in range(number_of_maps):
            nms_api.create(nms_obj, 'port_map', {
                'external_port': i,
                'internal_ip': str(next_int_ip),
                'internal_port': 16000 + i,
            })
            next_int_ip += 1
        nms_api.wait_ticks(5)
        # Comparing uhp values
        uhp_values = uhp_driver.get_nat_form()
        self.assertEqual('1', uhp_values.get('nat_enable'), msg=f'NAT is not enabled in UHP {obj_name}')
        self.assertEqual(nat_ext_ip, uhp_values.get('nat_ext_ip'), msg=f'NAT external IP is not {nat_ext_ip}')
        self.assertEqual(nat_int_ip, uhp_values.get('nat_int_ip'), msg=f'NAT internal IP net is not {nat_int_ip}')
        self.assertEqual(
            nat_int_mask,
            uhp_values.get('nat_int_mask'),
            msg=f'NAT internal IP mask is not {nat_int_mask}'
        )

        uhp_port_maps = uhp_values.get('port_map')
        # for m in range(800):
        #     for u in uhp_port_maps:
        #         if u.get('external_port') == str(m):
        #             break
        #     else:
        #         print(m)

        self.assertEqual(
            number_of_maps,
            len(uhp_port_maps),
            msg=f'UHP {obj_name} got {len(uhp_port_maps)}, expected {number_of_maps}'
        )
        next_int_ip = ipaddress.IPv4Address(first_ip)
        for i in range(number_of_maps):
            for uhp_map in uhp_port_maps:
                if uhp_map.get('external_port') == str(i) and uhp_map.get('internal_ip') == str(next_int_ip) \
                        and uhp_map.get('internal_port') == str(16000 + i):
                    break
            else:
                test_api.fail(self, f'Port map {str(i)} {str(next_int_ip)} {16000 + i} not found')
            next_int_ip += 1
