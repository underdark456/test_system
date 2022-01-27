import time

from src import test_api, nms_api
from src.custom_test_case import CustomTestCase
from src.enum_types_constants import ControllerModes, Checkbox, ControllerModesStr
from src.exceptions import NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller

options_path = 'test_scenarios.form_confirmation.tlc'
backup_name = 'default_config.txt'


# TODO: uncomment the rest controlllers when Inroute already exists issue is fixed
class ControllerTlcConfirmation(CustomTestCase):
    """Check TLC settings got by MF Hub, Outroute, Inroute, Hubless Master, DAMA Hub, Gateway """

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.27'
    __execution_time__ = 85
    __express__ = True

    @classmethod
    def set_up_class(cls):
        controllers = test_api.get_uhp_by_model('UHP200', number=6)

        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)
        net = nms_api.create('nms:0', 'network', {'name': 'net', 'dev_password': ''})
        cls.tp = nms_api.create(net, 'teleport', {'name': 'tp', 'rx1_lo': 0, 'rx2_lo': 0, 'tx_lo': 0})
        cls.mf_hub = nms_api.create(net, 'controller', {
            'name': 'mf_hub',
            'mode': ControllerModes.MF_HUB,
            'teleport': cls.tp,
            'uhp_model': controllers[0].get('model'),
            'device_ip': controllers[0].get('device_ip'),
            'device_vlan': controllers[0].get('device_vlan'),
            'device_gateway': controllers[0].get('device_gateway'),
        })
        cls.mf_hub_uhp = controllers[0].get('web_driver')
        cls.mf_hub_uhp.set_nms_permission(vlan=controllers[0].get('device_vlan'), password='')
        # cls.out = nms_api.create(net, 'controller', {
        #     'name': 'out',
        #     'mode': ControllerModes.OUTROUTE,
        #     'teleport': cls.tp,
        #     'uhp_model': controllers[1].get('model'),
        #     'device_ip': controllers[1].get('device_ip'),
        #     'device_vlan': controllers[1].get('device_vlan'),
        #     'device_gateway': controllers[1].get('device_gateway'),
        # })
        # cls.out_uhp = controllers[1].get('web_driver')
        # cls.out_uhp.set_nms_permission(vlan=controllers[1].get('device_vlan'), password='')
        cls.inr = nms_api.create(net, 'controller', {
            'name': 'inr',
            'mode': ControllerModes.INROUTE,
            'teleport': cls.tp,
            'tx_controller': cls.mf_hub,
            'inroute': 24,
            'uhp_model': controllers[2].get('model'),
            'device_ip': controllers[2].get('device_ip'),
            'device_vlan': controllers[2].get('device_vlan'),
            'device_gateway': controllers[2].get('device_gateway'),
        })
        cls.inr_uhp = controllers[2].get('web_driver')
        cls.inr_uhp.set_nms_permission(vlan=controllers[2].get('device_vlan'), password='')
        # cls.hl_mas = nms_api.create(net, 'controller', {
        #     'name': 'hl_mas',
        #     'mode': ControllerModes.HUBLESS_MASTER,
        #     'teleport': cls.tp,
        #     'uhp_model': controllers[3].get('model'),
        #     'device_ip': controllers[3].get('device_ip'),
        #     'device_vlan': controllers[3].get('device_vlan'),
        #     'device_gateway': controllers[3].get('device_gateway'),
        # })
        # cls.hl_mas_uhp = controllers[3].get('web_driver')
        # cls.hl_mas_uhp.set_nms_permission(vlan=controllers[3].get('device_vlan'), password='')
        # cls.dama_hub = nms_api.create(net, 'controller', {
        #     'name': 'dama_hub',
        #     'mode': ControllerModes.DAMA_HUB,
        #     'teleport': cls.tp,
        #     'uhp_model': controllers[4].get('model'),
        #     'device_ip': controllers[4].get('device_ip'),
        #     'device_vlan': controllers[4].get('device_vlan'),
        #     'device_gateway': controllers[4].get('device_gateway'),
        # })
        # cls.dama_hub_uhp = controllers[4].get('web_driver')
        # cls.dama_hub_uhp.set_nms_permission(vlan=controllers[4].get('device_vlan'), password='')
        # cls.gateway = nms_api.create(net, 'controller', {
        #     'name': 'gateway',
        #     'mode': ControllerModes.GATEWAY,
        #     'teleport': cls.tp,
        #     'uhp_model': controllers[5].get('model'),
        #     'device_ip': controllers[5].get('device_ip'),
        #     'device_vlan': controllers[5].get('device_vlan'),
        #     'device_gateway': controllers[5].get('device_gateway'),
        # })
        # cls.gateway_uhp = controllers[5].get('web_driver')
        # cls.gateway_uhp.set_nms_permission(vlan=controllers[1].get('device_vlan'), password='')

        if not nms_api.wait_not_states(cls.mf_hub, [Controller.UNKNOWN, Controller.UNREACHABLE]):
            raise NmsControlledModeException(f'MF Hub is in {nms_api.get_param(cls.mf_hub, "state")}')

        # if not nms_api.wait_not_states(cls.out, [Controller.UNKNOWN, Controller.UNREACHABLE]):
        #     raise NmsControlledModeException(f'Outroute is in {nms_api.get_param(cls.out, "state")}')

        if not nms_api.wait_not_states(cls.inr, [Controller.UNKNOWN, Controller.UNREACHABLE]):
            raise NmsControlledModeException(f'Inroute is in {nms_api.get_param(cls.inr, "state")}')

        # if not nms_api.wait_not_states(cls.hl_mas, [Controller.UNKNOWN, Controller.UNREACHABLE]):
        #     raise NmsControlledModeException(f'Hubless Master is in {nms_api.get_param(cls.hl_mas, "state")}')

        # if not nms_api.wait_not_states(cls.dama_hub, [Controller.UNKNOWN, Controller.UNREACHABLE]):
        #     raise NmsControlledModeException(f'DAMA Hub is in {nms_api.get_param(cls.dama_hub, "state")}')

        # if not nms_api.wait_not_states(cls.gateway, [Controller.UNKNOWN, Controller.UNREACHABLE]):
        #     raise NmsControlledModeException(f'Gateway is in {nms_api.get_param(cls.gateway, "state")}')

    def test_tlc(self):
        """TLC UHP confirmation for MF Hub, Outroute, Hubless Master, DAMA Hub, Gateway"""
        controllers = [self.mf_hub, ]
        uhp_drivers = [self.mf_hub_uhp, ]
        mode = [ControllerModesStr.MF_HUB, ]
        tlc_max_lvl = [1, 2, 23, 45, 46]
        tlc_net_own = [0, 1, 8, 15, 16]
        tlc_avg_min = [0, 1, 8, 15, 16]
        tlc_cn_stn = [0.0, 0.1, 12.4, 23.8, 23.9]
        tlc_cn_hub = [0.0, 0.1, 12.4, 23.8, 23.9]
        for i in range(5):
            for j in range(len(controllers)):
                nms_api.update(controllers[j], {
                    'tlc_enable': Checkbox.ON,
                    'tlc_max_lvl': tlc_max_lvl[i],
                    'tlc_net_own': tlc_net_own[i],
                    'tlc_avg_min': tlc_avg_min[i],
                    'tlc_cn_stn': tlc_cn_stn[i],
                    'tlc_cn_hub': tlc_cn_hub[i],
                })
            nms_api.wait_next_tick()
            time.sleep(1)
            for j in range(len(uhp_drivers)):
                uhp_values = uhp_drivers[j].get_tlc_form()
                self.assertEqual('1', uhp_values.get('tlc_enable'), msg=f'TLC is not enabled in {mode[j]}')
                self.assertEqual(str(tlc_max_lvl[i]), uhp_values.get('tlc_max_lvl'),
                                 msg=f'{mode[j]} tlc_max_lvl is not {str(tlc_max_lvl[i])}')
                self.assertEqual(str(tlc_net_own[i]), uhp_values.get('tlc_net_own'),
                                 msg=f'{mode[j]} tlc_net_own is not {str(tlc_net_own[i])}')
                self.assertEqual(str(tlc_avg_min[i]), uhp_values.get('tlc_avg_min'),
                                 msg=f'{mode[j]} tlc_avg_min is not {str(tlc_avg_min[i])}')
                self.assertEqual(str(tlc_cn_stn[i]), uhp_values.get('tlc_cn_stn'),
                                 msg=f'{mode[j]} tlc_cn_stn is not {str(tlc_cn_stn[i])}')
                self.assertEqual(str(tlc_cn_hub[i]), uhp_values.get('tlc_cn_hub'),
                                 msg=f'{mode[j]} tlc_cn_hub is not {str(tlc_cn_hub[i])}')

    def test_tlc_inroute(self):
        """TLC UHP confirmation for Inroute - only has tlc_cn_hub param"""
        for tlc_cn_hub in (0.0, 12.3, 23.9):
            nms_api.update(self.inr, {'tlc_cn_hub': tlc_cn_hub})
            nms_api.wait_next_tick()
            time.sleep(1)
            uhp_value = self.inr_uhp.get_tlc_form().get('tlc_cn_hub')
            self.assertEqual(
                str(tlc_cn_hub),
                uhp_value,
                msg=f'Inroute UHP expected tlc_cn_hub={tlc_cn_hub}, got {uhp_value}'
            )
