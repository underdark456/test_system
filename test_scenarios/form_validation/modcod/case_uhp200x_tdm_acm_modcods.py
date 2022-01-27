import json
import os
import random

from global_options.options import PROJECT_DIR
from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, ModelTypes
from src.exceptions import ObjectNotUpdatedException

options_path = 'test_scenarios.form_validation.modcod'
backup_name = 'default_config.txt'


class Uhp200xTdmAcmModcodsValidationCase(CustomTestCase):
    """UHP200X model TDM ACM validation"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 6
    __express__ = True

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))
        nms_api.load_config(backup_name)

        # Getting list of available TDM ACM modcods for UHP200
        with open(
            f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_tdm_acm_cn_order{os.sep}sf_tdm_acm_cn_order_uhp200x.txt', 'r'
        ) as file:
            cls.uhp200x_modcods = json.load(file)

        with open(
            f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_tdm_acm_cn_order{os.sep}lf_tdm_acm_cn_order_uhp200x.txt', 'r'
        ) as file:
            cls.uhp200x_modcods_lf = json.load(file)
        net = nms_api.create('nms:0', 'network', {'name': 'net-0'})
        tp = nms_api.create(net, 'teleport', {'name': 'tp-0', 'sat_name': 'sat'})
        cls.mf_hub = nms_api.create(net, 'controller', params={
            'name': 'HM',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
            'uhp_model': ModelTypes.UHP200X,
        })

    def test_8_tdm_acm_sf_modcods_uhp200x(self):
        """Applying 8 TDM SF ACM modcods for UHP200X in the right cn order"""
        for i in range(len(self.uhp200x_modcods) - 8):
            tx_modcod, tx_modcod_name = self.uhp200x_modcods[i].get('value'), self.uhp200x_modcods[i].get('name')
            tx_modcod_cn = self.uhp200x_modcods[i].get('acm_thr')
            acm_mc2, acm_mc2_name = self.uhp200x_modcods[i + 1].get('value'), self.uhp200x_modcods[i + 1].get('name')
            acm_mc3, acm_mc3_name = self.uhp200x_modcods[i + 2].get('value'), self.uhp200x_modcods[i + 2].get('name')
            acm_mc4, acm_mc4_name = self.uhp200x_modcods[i + 3].get('value'), self.uhp200x_modcods[i + 3].get('name')
            acm_mc5, acm_mc5_name = self.uhp200x_modcods[i + 4].get('value'), self.uhp200x_modcods[i + 4].get('name')
            acm_mc6, acm_mc6_name = self.uhp200x_modcods[i + 5].get('value'), self.uhp200x_modcods[i + 5].get('name')
            acm_mc7, acm_mc7_name = self.uhp200x_modcods[i + 6].get('value'), self.uhp200x_modcods[i + 6].get('name')
            acm_mc8, acm_mc8_name = self.uhp200x_modcods[i + 7].get('value'), self.uhp200x_modcods[i + 7].get('name')
            acm_mc2_cn = self.uhp200x_modcods[i + 1].get('acm_thr')
            acm_mc3_cn = self.uhp200x_modcods[i + 2].get('acm_thr')
            acm_mc4_cn = self.uhp200x_modcods[i + 3].get('acm_thr')
            acm_mc5_cn = self.uhp200x_modcods[i + 4].get('acm_thr')
            acm_mc6_cn = self.uhp200x_modcods[i + 5].get('acm_thr')
            acm_mc7_cn = self.uhp200x_modcods[i + 6].get('acm_thr')
            acm_mc8_cn = self.uhp200x_modcods[i + 7].get('acm_thr')
            with self.subTest(f'tx_modcod={tx_modcod_name} ({tx_modcod_cn}dB), acm_mc2={acm_mc2_name} ({acm_mc2_cn}dB),'
                              f' acm_mc3={acm_mc3_name} ({acm_mc3_cn}dB), acm_mc4={acm_mc4_name}, ({acm_mc4_cn}dB),'
                              f' acm_mc5={acm_mc5_name} ({acm_mc5_cn}dB), acm_mc6={acm_mc6_name}, ({acm_mc6_cn}dB),'
                              f' acm_mc7={acm_mc7_name} ({acm_mc7_cn}dB), acm_mc8={acm_mc8_name}, ({acm_mc8_cn}dB)'):
                try:
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
                except ObjectNotUpdatedException:
                    self.fail('Modcod\' combination is not applied')

    def test_8_tdm_acm_sf_modcods_uhp200x_wrong_order(self):
        """Applying 8 TDM SF ACM modcods for UHP200X in the wrong cn order"""
        # Getting a list of modcods in the random cn order
        shuffled = random.sample(self.uhp200x_modcods, len(self.uhp200x_modcods))
        for i in range(len(shuffled) - 8):
            tx_modcod, tx_modcod_name = shuffled[i].get('value'), shuffled[i].get('name')
            tx_modcod_cn = shuffled[i].get('acm_thr')
            acm_mc2, acm_mc2_name = shuffled[i + 1].get('value'), shuffled[i + 1].get('name')
            acm_mc3, acm_mc3_name = shuffled[i + 2].get('value'), shuffled[i + 2].get('name')
            acm_mc4, acm_mc4_name = shuffled[i + 3].get('value'), shuffled[i + 3].get('name')
            acm_mc5, acm_mc5_name = shuffled[i + 4].get('value'), shuffled[i + 4].get('name')
            acm_mc6, acm_mc6_name = shuffled[i + 5].get('value'), shuffled[i + 5].get('name')
            acm_mc7, acm_mc7_name = shuffled[i + 6].get('value'), shuffled[i + 6].get('name')
            acm_mc8, acm_mc8_name = shuffled[i + 7].get('value'), shuffled[i + 7].get('name')
            acm_mc2_cn = shuffled[i + 1].get('acm_thr')
            acm_mc3_cn = shuffled[i + 2].get('acm_thr')
            acm_mc4_cn = shuffled[i + 3].get('acm_thr')
            acm_mc5_cn = shuffled[i + 4].get('acm_thr')
            acm_mc6_cn = shuffled[i + 5].get('acm_thr')
            acm_mc7_cn = shuffled[i + 6].get('acm_thr')
            acm_mc8_cn = shuffled[i + 7].get('acm_thr')
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

    def test_8_tdm_acm_lf_modcods_uhp200x(self):
        """Applying 8 TDM LF ACM modcods for UHP200X in the right cn order"""
        for i in range(len(self.uhp200x_modcods_lf) - 8):
            tx_modcod, tx_modcod_name = self.uhp200x_modcods_lf[i].get('value'), self.uhp200x_modcods_lf[i].get('name')
            tx_modcod_cn = self.uhp200x_modcods_lf[i].get('acm_thr')
            acm_mc2, acm_mc2_name = self.uhp200x_modcods_lf[i+1].get('value'), self.uhp200x_modcods_lf[i+1].get('name')
            acm_mc3, acm_mc3_name = self.uhp200x_modcods_lf[i+2].get('value'), self.uhp200x_modcods_lf[i+2].get('name')
            acm_mc4, acm_mc4_name = self.uhp200x_modcods_lf[i+3].get('value'), self.uhp200x_modcods_lf[i+3].get('name')
            acm_mc5, acm_mc5_name = self.uhp200x_modcods_lf[i+4].get('value'), self.uhp200x_modcods_lf[i+4].get('name')
            acm_mc6, acm_mc6_name = self.uhp200x_modcods_lf[i+5].get('value'), self.uhp200x_modcods_lf[i+5].get('name')
            acm_mc7, acm_mc7_name = self.uhp200x_modcods_lf[i+6].get('value'), self.uhp200x_modcods_lf[i+6].get('name')
            acm_mc8, acm_mc8_name = self.uhp200x_modcods_lf[i+7].get('value'), self.uhp200x_modcods_lf[i+7].get('name')
            acm_mc2_cn = self.uhp200x_modcods_lf[i + 1].get('acm_thr')
            acm_mc3_cn = self.uhp200x_modcods_lf[i + 2].get('acm_thr')
            acm_mc4_cn = self.uhp200x_modcods_lf[i + 3].get('acm_thr')
            acm_mc5_cn = self.uhp200x_modcods_lf[i + 4].get('acm_thr')
            acm_mc6_cn = self.uhp200x_modcods_lf[i + 5].get('acm_thr')
            acm_mc7_cn = self.uhp200x_modcods_lf[i + 6].get('acm_thr')
            acm_mc8_cn = self.uhp200x_modcods_lf[i + 7].get('acm_thr')
            with self.subTest(f'tx_modcod={tx_modcod_name} ({tx_modcod_cn}dB), acm_mc2={acm_mc2_name} ({acm_mc2_cn}dB),'
                              f' acm_mc3={acm_mc3_name} ({acm_mc3_cn}dB), acm_mc4={acm_mc4_name}, ({acm_mc4_cn}dB),'
                              f' acm_mc5={acm_mc5_name} ({acm_mc5_cn}dB), acm_mc6={acm_mc6_name}, ({acm_mc6_cn}dB),'
                              f' acm_mc7={acm_mc7_name} ({acm_mc7_cn}dB), acm_mc8={acm_mc8_name}, ({acm_mc8_cn}dB)'):
                try:
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
                except ObjectNotUpdatedException:
                    self.fail('Modcod\' combination is not applied')

    def test_8_tdm_acm_lf_modcods_uhp200x_wrong_order(self):
        """Applying 8 TDM LF ACM modcods for UHP200X in the wrong cn order"""
        # Getting a list of modcods in the random cn order
        shuffled = random.sample(self.uhp200x_modcods_lf, len(self.uhp200x_modcods_lf))
        for i in range(len(shuffled) - 8):
            tx_modcod, tx_modcod_name = shuffled[i].get('value'), shuffled[i].get('name')
            tx_modcod_cn = shuffled[i].get('acm_thr')
            acm_mc2, acm_mc2_name = shuffled[i + 1].get('value'), shuffled[i + 1].get('name')
            acm_mc3, acm_mc3_name = shuffled[i + 2].get('value'), shuffled[i + 2].get('name')
            acm_mc4, acm_mc4_name = shuffled[i + 3].get('value'), shuffled[i + 3].get('name')
            acm_mc5, acm_mc5_name = shuffled[i + 4].get('value'), shuffled[i + 4].get('name')
            acm_mc6, acm_mc6_name = shuffled[i + 5].get('value'), shuffled[i + 5].get('name')
            acm_mc7, acm_mc7_name = shuffled[i + 6].get('value'), shuffled[i + 6].get('name')
            acm_mc8, acm_mc8_name = shuffled[i + 7].get('value'), shuffled[i + 7].get('name')
            acm_mc2_cn = shuffled[i + 1].get('acm_thr')
            acm_mc3_cn = shuffled[i + 2].get('acm_thr')
            acm_mc4_cn = shuffled[i + 3].get('acm_thr')
            acm_mc5_cn = shuffled[i + 4].get('acm_thr')
            acm_mc6_cn = shuffled[i + 5].get('acm_thr')
            acm_mc7_cn = shuffled[i + 6].get('acm_thr')
            acm_mc8_cn = shuffled[i + 7].get('acm_thr')
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

    def test_8_tdm_acm_sf_lf_modcods_mixed(self):
        """Applying 8 mixed TDM SF and LF ACM modcods for UHP200X"""
        # Getting a list of all modcods in the cn ascending order
        all_modcods = self.uhp200x_modcods + self.uhp200x_modcods_lf
        all_modcods.sort(key=lambda x: float(x.get('acm_thr')))
        for i in range(len(self.uhp200x_modcods_lf) - 8):
            tx_modcod, tx_modcod_name = self.uhp200x_modcods_lf[i].get('value'), self.uhp200x_modcods_lf[i].get('name')
            tx_modcod_cn = self.uhp200x_modcods_lf[i].get('acm_thr')
            acm_mc2, acm_mc2_name = self.uhp200x_modcods_lf[i+1].get('value'), self.uhp200x_modcods_lf[i+1].get('name')
            acm_mc3, acm_mc3_name = self.uhp200x_modcods_lf[i+2].get('value'), self.uhp200x_modcods_lf[i+2].get('name')
            acm_mc4, acm_mc4_name = self.uhp200x_modcods_lf[i+3].get('value'), self.uhp200x_modcods_lf[i+3].get('name')
            acm_mc5, acm_mc5_name = self.uhp200x_modcods_lf[i+4].get('value'), self.uhp200x_modcods_lf[i+4].get('name')
            acm_mc6, acm_mc6_name = self.uhp200x_modcods_lf[i+5].get('value'), self.uhp200x_modcods_lf[i+5].get('name')
            acm_mc7, acm_mc7_name = self.uhp200x_modcods_lf[i+6].get('value'), self.uhp200x_modcods_lf[i+6].get('name')
            acm_mc8, acm_mc8_name = self.uhp200x_modcods_lf[i+7].get('value'), self.uhp200x_modcods_lf[i+7].get('name')
            acm_mc2_cn = self.uhp200x_modcods_lf[i + 1].get('acm_thr')
            acm_mc3_cn = self.uhp200x_modcods_lf[i + 2].get('acm_thr')
            acm_mc4_cn = self.uhp200x_modcods_lf[i + 3].get('acm_thr')
            acm_mc5_cn = self.uhp200x_modcods_lf[i + 4].get('acm_thr')
            acm_mc6_cn = self.uhp200x_modcods_lf[i + 5].get('acm_thr')
            acm_mc7_cn = self.uhp200x_modcods_lf[i + 6].get('acm_thr')
            acm_mc8_cn = self.uhp200x_modcods_lf[i + 7].get('acm_thr')
            with self.subTest(f'tx_modcod={tx_modcod_name} ({tx_modcod_cn}dB), acm_mc2={acm_mc2_name} ({acm_mc2_cn}dB),'
                              f' acm_mc3={acm_mc3_name} ({acm_mc3_cn}dB), acm_mc4={acm_mc4_name}, ({acm_mc4_cn}dB),'
                              f' acm_mc5={acm_mc5_name} ({acm_mc5_cn}dB), acm_mc6={acm_mc6_name}, ({acm_mc6_cn}dB),'
                              f' acm_mc7={acm_mc7_name} ({acm_mc7_cn}dB), acm_mc8={acm_mc8_name}, ({acm_mc8_cn}dB)'):
                try:
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
                except ObjectNotUpdatedException:
                    self.fail('Modcod\' combination is not applied')
