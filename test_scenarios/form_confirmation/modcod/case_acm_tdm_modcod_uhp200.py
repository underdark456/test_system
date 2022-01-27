import json
import os
import random

from global_options.options import PROJECT_DIR
from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.enum_types_constants import ModelTypesStr, ControllerModes
from src.exceptions import NmsControlledModeException

options_path = 'test_scenarios.form_confirmation.modcod'
backup_name = 'default_config.txt'


class AcmTdmUhp200ConfirmationCase(CustomTestCase):
    """UHP200 gets correct ACM TDM modcods"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 152  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        uhp200_modems = test_api.get_uhp_by_model(ModelTypesStr.UHP200, number=1)
        cls.uhp_ip = uhp200_modems[0].get('device_ip')
        cls.uhp = uhp200_modems[0].get('web_driver')

        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)
        test_options = test_api.get_options(options_path)

        # Getting lists of available TDM ACM modcods for UHP200
        with open(
                f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_tdm_acm_cn_order{os.sep}sf_tdm_acm_cn_order_uhp200.txt', 'r'
        ) as file:
            cls.sf_modcods = json.load(file)

        cls.class_logger.info(f'NMS SW version: {nms_api.get_param("nms:0", "version")}')
        cls.class_logger.info(f'UHP {cls.uhp_ip} SW version: {uhp200_modems[0].get("sw")}')
        cls.uhp.set_nms_permission(password='indeed', vlan=uhp200_modems[0].get('device_vlan'))

        net = nms_api.create('nms:0', 'network', {'name': 'net-0', 'dev_password': 'indeed'})
        tp = nms_api.create(net, 'teleport', params={'name': 'tp-0'})
        cls.mf_hub = nms_api.create(net, 'controller', params={
            'name': 'HM',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
            'device_ip': cls.uhp_ip,
            'device_vlan': uhp200_modems[0].get('device_vlan'),
            'device_gateway': uhp200_modems[0].get('device_gateway'),
            'uhp_model': uhp200_modems[0].get('model'),
            'tx_on': 'ON',
            'tx_level': test_options.get('tx_level'),
        })
        if not nms_api.wait_not_states(cls.mf_hub, ['Unknown', 'Unreachable']):
            raise NmsControlledModeException(f'UHP at {cls.uhp_ip} is not under NMS control')

    def test_mf_hub_tdm_acm_sf(self):
        """Check short frames combinations"""
        for i in range(len(self.sf_modcods) - 8):
            acm_thr = round(random.uniform(0, 5.9), 1)  # getting random valid acm_thr
            tx_modcod, tx_modcod_name = self.sf_modcods[i].get('value'), self.sf_modcods[i].get('name')
            tx_modcod_cn = self.sf_modcods[i].get('acm_thr')
            acm_mc2, acm_mc2_name = self.sf_modcods[i + 1].get('value'), self.sf_modcods[i + 1].get('name')
            acm_mc3, acm_mc3_name = self.sf_modcods[i + 2].get('value'), self.sf_modcods[i + 2].get('name')
            acm_mc4, acm_mc4_name = self.sf_modcods[i + 3].get('value'), self.sf_modcods[i + 3].get('name')
            acm_mc5, acm_mc5_name = self.sf_modcods[i + 4].get('value'), self.sf_modcods[i + 4].get('name')
            acm_mc6, acm_mc6_name = self.sf_modcods[i + 5].get('value'), self.sf_modcods[i + 5].get('name')
            acm_mc2_cn = self.sf_modcods[i + 1].get('acm_thr')
            acm_mc3_cn = self.sf_modcods[i + 2].get('acm_thr')
            acm_mc4_cn = self.sf_modcods[i + 3].get('acm_thr')
            acm_mc5_cn = self.sf_modcods[i + 4].get('acm_thr')
            acm_mc6_cn = self.sf_modcods[i + 5].get('acm_thr')
            with self.subTest(f'tx_modcod={tx_modcod_name} ({tx_modcod_cn}dB), acm_mc2={acm_mc2_name} ({acm_mc2_cn}dB),'
                              f' acm_mc3={acm_mc3_name} ({acm_mc3_cn}dB), acm_mc4={acm_mc4_name}, ({acm_mc4_cn}dB),'
                              f' acm_mc5={acm_mc5_name} ({acm_mc5_cn}dB), acm_mc6={acm_mc6_name}, ({acm_mc6_cn}dB)'):
                nms_api.update(self.mf_hub, {
                    'acm_enable': True,
                    'tx_modcod': tx_modcod,
                    'acm_mc2': acm_mc2,
                    'acm_mc3': acm_mc3,
                    'acm_mc4': acm_mc4,
                    'acm_mc5': acm_mc5,
                    'acm_mc6': acm_mc6,
                    'acm_thr': acm_thr,
                })
                nms_api.wait_ticks(2)
                uhp_values = self.uhp.get_tdm_acm_form()
                self.assertEqual('1', uhp_values.get('acm_enable'), msg=f'ACM is not enabled in UHP')
                uhp_tx_modcod = self.uhp.get_tdm_tx_form().get('tx_modcod')
                self.assertEqual(
                    tx_modcod_name.lower(),
                    uhp_tx_modcod,
                    msg=f'Expected tx_modcod {tx_modcod}, UHP {uhp_tx_modcod}'
                )
                self.assertEqual(
                    str(acm_thr),
                    uhp_values.get('acm_thr'),
                    msg=f'acm_thr expected {acm_thr}, UHP {uhp_values.get("acm_thr")}'
                )
                for j in range(2, 7):
                    self.assertEqual(uhp_values.get(f'acm_mc{j}'), self.sf_modcods[i + j - 1].get("value"))
