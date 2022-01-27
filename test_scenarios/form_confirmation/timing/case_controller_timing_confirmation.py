import time

from src import test_api, nms_api
from src.custom_test_case import CustomTestCase
from src.enum_types_constants import ControllerModes, TtsModesStr
from src.exceptions import NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller

options_path = 'test_scenarios.form_confirmation.timing'
backup_name = 'default_config.txt'


# TODO: uncomment Outroute when Inroute already exists issue is fixed
class ControllerTimingConfirmation(CustomTestCase):
    """Check hub_tts settings got by MF Hub and Outroute"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.27'
    __execution_time__ = 95
    __express__ = True

    @classmethod
    def set_up_class(cls):
        controllers = test_api.get_uhp_by_model('UHP200', number=2)

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
        # cls.out = nms_api.create(net, 'controller', {
        #     'name': 'out',
        #     'mode': ControllerModes.OUTROUTE,
        #     'teleport': cls.tp,
        #     'uhp_model': controllers[1].get('model'),
        #     'device_ip': controllers[1].get('device_ip'),
        #     'device_vlan': controllers[1].get('device_vlan'),
        #     'device_gateway': controllers[1].get('device_gateway'),
        # })

        cls.mf_hub_uhp = controllers[0].get('web_driver')
        # cls.out_uhp = controllers[1].get('web_driver')

        cls.mf_hub_uhp.set_nms_permission(vlan=controllers[0].get('device_vlan'), password='')
        # cls.out_uhp.set_nms_permission(vlan=controllers[1].get('device_vlan'), password='')

        if not nms_api.wait_not_states(cls.mf_hub, [Controller.UNKNOWN, Controller.UNREACHABLE]):
            raise NmsControlledModeException(f'MF Hub is in {nms_api.get_param(cls.mf_hub, "state")}')

        # if not nms_api.wait_not_states(cls.out, [Controller.UNKNOWN, Controller.UNREACHABLE]):
        #     raise NmsControlledModeException(f'Outroute is in {nms_api.get_param(cls.out, "state")}')

    def test_hub_tts_measure(self):
        nms_api.update(self.mf_hub, {'hub_tts_mode': TtsModesStr.MEASURE})
        # nms_api.update(self.out, {'hub_tts_mode': TtsModesStr.MEASURE})
        nms_api.wait_next_tick()
        time.sleep(2)
        mf_hub_uhp_timing = self.mf_hub_uhp.get_timing_values()
        self.assertEqual(
            TtsModesStr.MEASURE,
            mf_hub_uhp_timing.get('hub_tts_mode'),
            msg=f'Expected {TtsModesStr.MEASURE} timing mode in MF Hub, actual {mf_hub_uhp_timing.get("hub_tts_mode")}'
        )

        # out_uhp_timing = self.out_uhp.get_timing_values()
        # self.assertEqual(
        #     TtsModesStr.MEASURE,
        #     out_uhp_timing.get('hub_tts_mode'),
        #     msg=f'Expected {TtsModesStr.MEASURE} timing mode in Outroute, actual {out_uhp_timing.get("hub_tts_mode")}'
        # )

    def test_hub_tts_value(self):
        for tts_value in (0, 1, 78235, 149_999, 150_000):
            nms_api.update(self.mf_hub, {'hub_tts_mode': TtsModesStr.VALUE, 'tts_value': tts_value})
            # nms_api.update(self.out, {'hub_tts_mode': TtsModesStr.VALUE, 'tts_value': tts_value})
            nms_api.wait_next_tick()
            time.sleep(1)
            mf_hub_uhp_timing = self.mf_hub_uhp.get_timing_values()
            self.assertEqual(
                TtsModesStr.VALUE,
                mf_hub_uhp_timing.get('hub_tts_mode'),
                msg=f'Expected {TtsModesStr.VALUE} tts mode in MF Hub, got {mf_hub_uhp_timing.get("hub_tts_mode")}'
            )
            self.assertEqual(
                str(tts_value),
                mf_hub_uhp_timing.get('tts_value'),
                msg=f'Expected {tts_value} tts_value in MF Hub, actual {mf_hub_uhp_timing.get("tts_value")}'
            )

            # out_uhp_timing = self.out_uhp.get_timing_values()
            # self.assertEqual(
            #     TtsModesStr.VALUE,
            #     out_uhp_timing.get('hub_tts_mode'),
            #     msg=f'Expected {TtsModesStr.VALUE} timing mode in Outroute, actual {out_uhp_timing.get("hub_tts_mode")}'
            # )
            # self.assertEqual(
            #     str(tts_value),
            #     out_uhp_timing.get('tts_value'),
            #     msg=f'Expected {tts_value} tts_value in Outroute, actual {out_uhp_timing.get("tts_value")}'
            # )

    def test_hub_tts_location(self):
        nms_api.update(self.mf_hub, {'hub_tts_mode': TtsModesStr.LOCATION})
        # nms_api.update(self.out, {'hub_tts_mode': TtsModesStr.LOCATION})
        for sat_lon_deg, sat_lon_min in ([-179, 0], [-1, 1], [0, 30], [1, 58], [179, 59]):
            nms_api.update(self.tp, {'sat_lon_deg': sat_lon_deg, 'sat_lon_min': sat_lon_min})
            nms_api.wait_next_tick()
            time.sleep(1)
            mf_hub_uhp_timing = self.mf_hub_uhp.get_timing_values()
            self.assertEqual(
                TtsModesStr.LOCATION,
                mf_hub_uhp_timing.get('hub_tts_mode'),
                msg=f'Expected {TtsModesStr.LOCATION} tts mode in MF Hub, got {mf_hub_uhp_timing.get("hub_tts_mode")}'
            )
            self.assertEqual(
                str(sat_lon_deg),
                mf_hub_uhp_timing.get('sat_lon_deg'),
                msg=f'Expected {sat_lon_deg} tts_value in MF Hub, actual {mf_hub_uhp_timing.get("sat_lon_deg")}'
            )
            self.assertEqual(
                str(sat_lon_min),
                mf_hub_uhp_timing.get('sat_lon_min'),
                msg=f'Expected {sat_lon_min} tts_value in MF Hub, actual {mf_hub_uhp_timing.get("sat_lon_min")}'
            )

            # out_uhp_timing = self.out_uhp.get_timing_values()
            # self.assertEqual(
            #     TtsModesStr.LOCATION,
            #     out_uhp_timing.get('hub_tts_mode'),
            #     msg=f'Expected {TtsModesStr.LOCATION} timing mode in Outroute, actual {out_uhp_timing.get("hub_tts_mode")}'
            # )
            # self.assertEqual(
            #     str(sat_lon_deg),
            #     out_uhp_timing.get('sat_lon_deg'),
            #     msg=f'Expected {sat_lon_deg} tts_value in Outroute, actual {out_uhp_timing.get("sat_lon_deg")}'
            # )
            # self.assertEqual(
            #     str(sat_lon_min),
            #     out_uhp_timing.get('sat_lon_min'),
            #     msg=f'Expected {sat_lon_min} tts_value in Outroute, actual {out_uhp_timing.get("sat_lon_min")}'
            # )