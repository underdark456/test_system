import json
import os

from global_options.options import PROJECT_DIR
from src import nms_api, test_api
from src.custom_test_case import CustomTestCase
from src.enum_types_constants import ControllerModes, ModelTypes
from src.exceptions import ObjectNotUpdatedException

options_path = 'test_scenarios.form_validation.modcod'
backup_name = 'default_config.txt'


class AcmTdmSfLfValidationCase(CustomTestCase):
    """Short frames cannot be mixed with long frames"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 6  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        # Getting lists of available TDM ACM modcods for UHP200X
        with open(
                f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_tdm_acm_cn_order{os.sep}sf_tdm_acm_cn_order_uhp200x.txt', 'r'
        ) as file:
            cls.sf_modcods = json.load(file)
        with open(
                f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_tdm_acm_cn_order{os.sep}lf_tdm_acm_cn_order_uhp200x.txt', 'r'
        ) as file:
            cls.lf_modcods = json.load(file)

        cls.class_logger.info(f'NMS SW version: {nms_api.get_param("nms:0", "version")}')
        net = nms_api.create('nms:0', 'network', {'name': 'net-0'})
        tp = nms_api.create(net, 'teleport', params={'name': 'tp-0'})
        cls.mf_hub = nms_api.create(net, 'controller', params={
            'name': 'HM',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
            'uhp_model': ModelTypes.UHP200X,
        })

    def test_sf_lf_tdm_acm(self):
        """Check if short frames cannot be mixed with long frames in TDM ACM"""
        # Getting a list of all modcods sorted by C/N, new list is making in a manner avoiding making shallow copies
        all_modcods = []
        for m in self.sf_modcods:
            all_modcods.append({key: value for key, value in m.items()})
        for m in self.lf_modcods:
            all_modcods.append({key: value for key, value in m.items()})
        all_modcods.sort(key=lambda x: float(x.get('acm_thr')))
        # in one case there are 8 consecutive long frames modcods in the cn ascending list - the last eight ones
        for i in range(len(all_modcods) - 9):
            tx_modcod, tx_modcod_name = all_modcods[i].get('value'), all_modcods[i].get('name')
            tx_modcod_cn = all_modcods[i].get('acm_thr')
            acm_mc2, acm_mc2_name = all_modcods[i + 1].get('value'), all_modcods[i + 1].get('name')
            acm_mc3, acm_mc3_name = all_modcods[i + 2].get('value'), all_modcods[i + 2].get('name')
            acm_mc4, acm_mc4_name = all_modcods[i + 3].get('value'), all_modcods[i + 3].get('name')
            acm_mc5, acm_mc5_name = all_modcods[i + 4].get('value'), all_modcods[i + 4].get('name')
            acm_mc6, acm_mc6_name = all_modcods[i + 5].get('value'), all_modcods[i + 5].get('name')
            acm_mc7, acm_mc7_name = all_modcods[i + 6].get('value'), all_modcods[i + 6].get('name')
            acm_mc8, acm_mc8_name = all_modcods[i + 7].get('value'), all_modcods[i + 7].get('name')
            acm_mc2_cn = all_modcods[i + 1].get('acm_thr')
            acm_mc3_cn = all_modcods[i + 2].get('acm_thr')
            acm_mc4_cn = all_modcods[i + 3].get('acm_thr')
            acm_mc5_cn = all_modcods[i + 4].get('acm_thr')
            acm_mc6_cn = all_modcods[i + 5].get('acm_thr')
            acm_mc7_cn = all_modcods[i + 6].get('acm_thr')
            acm_mc8_cn = all_modcods[i + 7].get('acm_thr')
            with self.subTest(f'tx_modcod={tx_modcod_name} ({tx_modcod_cn}dB), acm_mc2={acm_mc2_name} ({acm_mc2_cn}dB),'
                              f' acm_mc3={acm_mc3_name} ({acm_mc3_cn}dB), acm_mc4={acm_mc4_name}, ({acm_mc4_cn}dB),'
                              f' acm_mc5={acm_mc5_name} ({acm_mc5_cn}dB), acm_mc6={acm_mc6_name}, ({acm_mc6_cn}dB),'
                              f' acm_mc7={acm_mc7_name} ({acm_mc7_cn}dB), acm_mc8={acm_mc8_name}, ({acm_mc8_cn}dB)'):
                with self.assertRaises(ObjectNotUpdatedException):
                    nms_api.update(self.mf_hub, {
                        'acm_enable': True,
                        'tx_modcod': tx_modcod,
                        'acm_mc2': acm_mc2,
                        'acm_mc3': acm_mc3,
                        'acm_mc4': acm_mc4,
                        'acm_mc5': acm_mc5,
                        'acm_mc6': acm_mc6,
                        'acm_mc7': acm_mc7,
                        'acm_mc8': acm_mc8,
                    })
