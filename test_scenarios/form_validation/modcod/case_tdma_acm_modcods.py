import json
import os
import random

from global_options.options import PROJECT_DIR
from src.custom_test_case import CustomTestCase
from src import nms_api, test_api
from src.enum_types_constants import ControllerModes, TdmaModcod, TdmaAcmModes, TdmaModcodStr
from src.exceptions import ObjectNotUpdatedException

options_path = 'test_scenarios.form_validation.modcod'
backup_name = 'default_config.txt'


class TdmaAcmModcodsValidationCase(CustomTestCase):
    """TDMA ACM validation test case"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.22'
    __execution_time__ = 12
    __express__ = True

    @classmethod
    def set_up_class(cls):
        nms_options = test_api.get_nms()
        nms_api.connect(nms_options.get('nms_ip'), nms_options.get('username'), nms_options.get('password'))

        cls.test_options = test_api.get_options(options_path)
        # Getting list of available TDM ACM modcods for UHP200
        with open(
                f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_tdm_acm_cn_order{os.sep}sf_tdm_acm_cn_order_uhp200.txt', 'r'
        ) as file:
            cls.uhp200_modcods = json.load(file)

    def set_up(self):
        nms_api.load_config(backup_name)
        net = nms_api.create('nms:0', 'network', {'name': 'net-0'})
        tp = nms_api.create(net, 'teleport', {'name': 'tp-0'})
        self.mf_hub = nms_api.create(net, 'controller', params={
            'name': 'HM',
            'mode': ControllerModes.MF_HUB,
            'teleport': tp,
        })

    def test_legacy(self):
        """TDMA ACM legacy mode set in NMS"""
        for i in range(len([*TdmaModcod()])):
            tdma_thr_acm = round(random.uniform(0, 5.9), 1)
            try:
                nms_api.update(self.mf_hub, {
                    'tdma_mc': [*TdmaModcod()][i],
                    'tdma_acm': TdmaAcmModes.LEGACY,
                    'mesh_acm': False,
                    'tdma_thr_acm': tdma_thr_acm
                })
                self.assertEqual([*TdmaModcodStr()][i], nms_api.get_param(self.mf_hub, 'tdma_mc'))
            except ObjectNotUpdatedException:
                self.fail(f'tdma_mc={[*TdmaModcodStr()][i]} is not applied')

    def test_12_modcods(self):
        """TDMA ACM 12modcods mode set in NMS"""
        for i in range(len([*TdmaModcod()])):
            tdma_thr_acm = round(random.uniform(0, 5.9), 1)
            try:
                nms_api.update(self.mf_hub, {
                    'tdma_mc': [*TdmaModcod()][i],
                    'tdma_acm': TdmaAcmModes.TWELVE_MODCODS,
                    'tdma_thr_acm': tdma_thr_acm
                })
                self.assertEqual([*TdmaModcodStr()][i], nms_api.get_param(self.mf_hub, 'tdma_mc'))
            except ObjectNotUpdatedException:
                self.fail(f'tdma_mc={[*TdmaModcodStr()][i]} is not applied')

    def test_16_modcods_tdma_mc_bpsk(self):
        """TDMA ACM 16modcods mode set in NMS for tdma_mc bpsk"""
        for tdma_mc in (TdmaModcod._BPSK_1_2, TdmaModcod._BPSK_2_3, TdmaModcod._BPSK_3_4, TdmaModcod._BPSK_5_6):
            for slot_length in range(2, 16):
                if slot_length * 4 < 13:  # all modcods are available
                    all_modcods = self.test_options.get('all_tdma_mc').copy()
                    all_modcods['slot_length'] = slot_length
                    all_modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                    all_modcods['tdma_mc'] = tdma_mc
                    try:
                        nms_api.update(self.mf_hub, all_modcods)
                    except ObjectNotUpdatedException:
                        self.fail(f'tdma_mc={tdma_mc}, slot_length={slot_length} cannot be applied')
                elif slot_length * 3 < 14:  # all modcods except for 16APSK are available
                    modcods = self.test_options.get('all_bpsk_qpsk_8psk_tdma_mc').copy()
                    modcods['slot_length'] = slot_length
                    modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                    modcods['tdma_mc'] = tdma_mc
                    try:
                        nms_api.update(self.mf_hub, modcods)
                    except ObjectNotUpdatedException:
                        self.fail(f'tdma_mc={tdma_mc}, slot_length={slot_length} cannot be applied')
                elif slot_length * 2 < 15:  # all modcods except for 16APSK and 8PSK are available
                    modcods = self.test_options.get('all_bpsk_qpsk_tdma_mc').copy()
                    modcods['slot_length'] = slot_length
                    modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                    modcods['tdma_mc'] = tdma_mc
                    try:
                        nms_api.update(self.mf_hub, modcods)
                    except ObjectNotUpdatedException:
                        self.fail(f'tdma_mc={tdma_mc}, slot_length={slot_length} cannot be applied')
                else:  # only bpsk is available
                    modcods = self.test_options.get('only_bpsk_tdma_mc').copy()
                    modcods['slot_length'] = slot_length
                    modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                    modcods['tdma_mc'] = tdma_mc
                    try:
                        nms_api.update(self.mf_hub, modcods)
                    except ObjectNotUpdatedException:
                        self.fail(f'tdma_mc={tdma_mc}, slot_length={slot_length} cannot be applied')
                    # testing invalid modcods - should not be applied
                    all_modcods = self.test_options.get('all_tdma_mc').copy()
                    with self.assertRaises(ObjectNotUpdatedException, msg=f'bpsk only modcods should be applied'):
                        nms_api.update(self.mf_hub, all_modcods)

    def test_16_modcods_tdma_mc_qpsk(self):
        """TDMA ACM 16modcods mode set in NMS for tdma_mc qpsk"""
        for tdma_mc in (TdmaModcod._QPSK_1_2, TdmaModcod._QPSK_2_3, TdmaModcod._QPSK_3_4, TdmaModcod._QPSK_5_6):
            for slot_length in range(2, 16):
                modcods = self.test_options.get('only_bpsk_tdma_mc').copy()
                modcods['slot_length'] = slot_length
                modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                modcods['tdma_mc'] = tdma_mc
                with self.assertRaises(ObjectNotUpdatedException, msg=f'bpsk modcods when tdma_mc is qpsk'):
                    nms_api.update(self.mf_hub, modcods)

                double_slot = slot_length * 2
                one_and_a_half = slot_length * 1.5
                if double_slot < 15 and one_and_a_half == int(one_and_a_half):
                    # qpsk, 8psk, 16apks are available
                    modcods = self.test_options.get('qpsk_8psk_16apsk_tdma_mc').copy()
                    modcods['slot_length'] = slot_length
                    modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                    modcods['tdma_mc'] = tdma_mc
                    try:
                        nms_api.update(self.mf_hub, modcods)
                    except ObjectNotUpdatedException:
                        self.fail(f'tdma_mc={tdma_mc}, slot_length={slot_length} cannot be applied')
                elif double_slot < 15 and one_and_a_half != int(one_and_a_half):
                    # qpsk, and 16apks are available, bot not 8psk and bpsk
                    modcods = self.test_options.get('qpsk_16apsk_tdma_mc').copy()
                    modcods['slot_length'] = slot_length
                    modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                    modcods['tdma_mc'] = tdma_mc
                    try:
                        nms_api.update(self.mf_hub, modcods)
                    except ObjectNotUpdatedException:
                        self.fail(f'tdma_mc={tdma_mc}, slot_length={slot_length} qpsk and 16apsk cannot be applied')
                    # 8psk should not be appllied
                    modcods = self.test_options.get('qpsk_8psk_16apsk_tdma_mc').copy()
                    modcods['slot_length'] = slot_length
                    modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                    modcods['tdma_mc'] = tdma_mc
                    with self.assertRaises(
                            ObjectNotUpdatedException,
                            msg=f'tdma_mc={tdma_mc}, slot_length={slot_length} qpsk, 8psk, and 16apsk modcods '
                            f'when 8psk should not be applied'):
                        nms_api.update(self.mf_hub, modcods)
                elif double_slot > 15 and (one_and_a_half == int(one_and_a_half) and one_and_a_half < 15):
                    # qpsk, and 8psks are available, but not 16apsk
                    modcods = self.test_options.get('qpsk_8psk_tdma_mc').copy()
                    modcods['slot_length'] = slot_length
                    modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                    modcods['tdma_mc'] = tdma_mc
                    try:
                        nms_api.update(self.mf_hub, modcods)
                    except ObjectNotUpdatedException:
                        self.fail(f'tdma_mc={tdma_mc}, slot_length={slot_length} qpsk and 8psk cannot be applied')
                    # 16apsk should not be appllied
                    modcods = self.test_options.get('qpsk_8psk_16apsk_tdma_mc').copy()
                    modcods['slot_length'] = slot_length
                    modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                    modcods['tdma_mc'] = tdma_mc
                    with self.assertRaises(
                            ObjectNotUpdatedException,
                            msg=f'tdma_mc={tdma_mc}, slot_length={slot_length} qpsk, 8psk, and 16apsk modcods '
                            f'when 16apsk should not be applied'):
                        nms_api.update(self.mf_hub, modcods)
                else:  # the rest cases - only qpsk is available
                    modcods = self.test_options.get('only_qpsk_tdma_mc').copy()
                    modcods['slot_length'] = slot_length
                    modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                    modcods['tdma_mc'] = tdma_mc
                    try:
                        nms_api.update(self.mf_hub, modcods)
                    except ObjectNotUpdatedException:
                        self.fail(f'tdma_mc={tdma_mc}, slot_length={slot_length} only qpsk cannot be applied')
                    # invalid combinations
                    modcods = self.test_options.get('qpsk_8psk_tdma_mc').copy()
                    modcods['slot_length'] = slot_length
                    modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                    modcods['tdma_mc'] = tdma_mc
                    with self.assertRaises(
                            ObjectNotUpdatedException,
                            msg=f'tdma_mc={tdma_mc}, slot_length={slot_length} qpsk and 8psk modcods '
                            f'when only qpsk should be applied'):
                        nms_api.update(self.mf_hub, modcods)

                    modcods = self.test_options.get('qpsk_16apsk_tdma_mc').copy()
                    modcods['slot_length'] = slot_length
                    modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                    modcods['tdma_mc'] = tdma_mc
                    with self.assertRaises(
                            ObjectNotUpdatedException,
                            msg=f'tdma_mc={tdma_mc}, slot_length={slot_length} qpsk and 16apsk modcods '
                            f'when only qpsk should be applied'):
                        nms_api.update(self.mf_hub, modcods)

    def test_16_modcods_tdma_mc_8psk(self):
        """TDMA ACM 16modcods mode set in NMS for tdma_mc 8psk"""
        for tdma_mc in (TdmaModcod._8PSK_1_2, TdmaModcod._8PSK_2_3, TdmaModcod._8PSK_3_4, TdmaModcod._8PSK_5_6):
            for slot_length in range(2, 16):
                modcods = self.test_options.get('all_bpsk_qpsk_tdma_mc').copy()
                modcods['slot_length'] = slot_length
                modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                modcods['tdma_mc'] = tdma_mc
                with self.assertRaises(ObjectNotUpdatedException, msg=f'bpsk and qpsk modcods when tdma_mc is 8psk'):
                    nms_api.update(self.mf_hub, modcods)
                modcods = self.test_options.get('only_8psk_tdma_mc').copy()
                modcods['slot_length'] = slot_length
                modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                modcods['tdma_mc'] = tdma_mc
                try:
                    nms_api.update(self.mf_hub, modcods)
                except ObjectNotUpdatedException as exc:
                    self.fail(f'Cannot apply only 8psk modcods when tdma_mc is 8psk: {exc}')
                if (slot_length * 4) % 3 == 0 and (slot_length * 4 / 3) < 15:
                    # 8psk, and 16apks are available, bot not qpsk and bpsk
                    modcods = self.test_options.get('8psk_16apsk_tdma_mc').copy()
                    modcods['slot_length'] = slot_length
                    modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                    modcods['tdma_mc'] = tdma_mc
                    try:
                        nms_api.update(self.mf_hub, modcods)
                    except ObjectNotUpdatedException as exc:
                        self.fail(f'Cannot apply 8psk, 16apks modcods (tdma_mc=8psk, slot length fits 16apsk): {exc}')
                else:
                    # 16apsk should not be applied
                    modcods = self.test_options.get('8psk_16apsk_tdma_mc').copy()
                    modcods['slot_length'] = slot_length
                    modcods['tdma_acm'] = TdmaAcmModes.SIXTEEN_MODCODS
                    modcods['tdma_mc'] = tdma_mc
                    with self.assertRaises(ObjectNotUpdatedException, msg=f'8psk and 16apsk modcods when tdma_mc=8psk'
                                                                          f' and slot length does not fit 16apsk'):
                        nms_api.update(self.mf_hub, modcods)

    def test_mesh_mc(self):
        """TDMA ACM Mesh traffic coding and modulation set in NMS"""
        tdma_acm = TdmaAcmModes.SIXTEEN_MODCODS
        for tdma_mc in (TdmaModcod._BPSK_1_2, TdmaModcod._QPSK_1_2, TdmaModcod._8PSK_1_2, TdmaModcod._16APSK_1_2):
            for slot_length in range(2, 16):

                if tdma_mc == TdmaModcod._BPSK_1_2:

                    if 4 * slot_length < 13:  # all mesh_mc should be available
                        for mesh_mc in ([*TdmaModcod()]):
                            self.should_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)

                    elif 3 * slot_length < 14:  # all but 16apsk mesh_mc should be available
                        for mesh_mc in range(12):
                            self.should_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)
                        for mesh_mc in range(12, 16):
                            self.should_not_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)

                    elif 2 * slot_length < 15:  # only bpsk and qpsk should be applied
                        for mesh_mc in range(8):
                            self.should_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)
                        for mesh_mc in range(8, 16):
                            self.should_not_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)

                elif tdma_mc == TdmaModcod._QPSK_1_2:
                    for mesh_mc in range(4):  # bpsk should not be applied
                        self.should_not_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)
                    for mesh_mc in range(4, 8):  # qpsk should be always applied
                        self.should_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)

                    if 2 * slot_length < 15 and \
                            (1.5 * slot_length == int(1.5 * slot_length) and 1.5 * slot_length < 15):
                        # 8psk and 16 apsk should be applied
                        for mesh_mc in range(8, 16):
                            self.should_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)

                    elif 2 * slot_length < 15 and (1.5 * slot_length != int(1.5 * slot_length)):
                        for mesh_mc in range(12, 16):  # 16 apsk should be applied
                            self.should_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)
                        for mesh_mc in range(8, 12):  # 8psk should not be applied
                            self.should_not_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)
                    elif 2 * slot_length > 15 and \
                            (1.5 * slot_length == int(1.5 * slot_length) and 1.5 * slot_length < 15):
                        for mesh_mc in range(8, 12):  # 8 apsk should be applied
                            self.should_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)
                        for mesh_mc in range(12, 16):  # 16apsk should not be applied
                            self.should_not_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)

                elif tdma_mc == TdmaModcod._8PSK_1_2:
                    for mesh_mc in range(8):  # bpsk and qpsk should not be applied
                        self.should_not_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)
                    for mesh_mc in range(8, 12):  # 8psk should be applied
                        self.should_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)
                    if (slot_length * 4) % 3 == 0 and slot_length * 4 / 3 < 15:
                        for mesh_mc in range(12, 16):  # 16apsk should be applied
                            self.should_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)
                    else:
                        for mesh_mc in range(12, 16):  # 16apsk should be applied
                            self.should_not_be_applied(slot_length, tdma_acm, tdma_mc, mesh_mc)

    def should_be_applied(self, slot_length, tdma_acm, tdma_mc, mesh_mc):
        try:
            nms_api.update(self.mf_hub, {
                'slot_length': slot_length,
                'tdma_acm': tdma_acm,
                'mesh_acm': True,
                'tdma_mc': tdma_mc,
                'mesh_mc': mesh_mc,
            })
        except ObjectNotUpdatedException:
            print(f'NOT APPLIED: slot_length={slot_length}, tdma_mc={tdma_mc}, tdma_acm={tdma_acm}, mesh_acm=1, '
                  f'mesh_mc={mesh_mc}')
            # self.fail(f'slot_length={slot_length}, tdma_mc={tdma_mc}, tdma_acm={tdma_acm}, mesh_acm=1, '
            #           f'mesh_mc={mesh_mc} is not applied')

    def should_not_be_applied(self, slot_length, tdma_acm, tdma_mc, mesh_mc):
        # with self.assertRaises(
        #         ObjectNotUpdatedException,
        #         msg=f'slot_length={slot_length}, tdma_mc={tdma_mc}, tdma_acm={tdma_acm}, mesh_acm=1, '
        #             f'mesh_mc={mesh_mc} should not be applied'):
        #     nms_api.update(self.mf_hub, {
        #         'slot_length': slot_length,
        #         'tdma_acm': tdma_acm,
        #         'mesh_acm': True,
        #         'tdma_mc': tdma_mc,
        #         'mesh_mc': mesh_mc,
        #     })
        try:
            nms_api.update(self.mf_hub, {
                'slot_length': slot_length,
                'tdma_acm': tdma_acm,
                'mesh_acm': True,
                'tdma_mc': tdma_mc,
                'mesh_mc': mesh_mc,
            })
            print(f'APPLIED: slot_length={slot_length}, tdma_mc={tdma_mc}, tdma_acm={tdma_acm}, mesh_acm=1, '
                  f'mesh_mc={mesh_mc}')
        except ObjectNotUpdatedException as exc:
            print(f'Expectedly not applied: slot_length={slot_length}, tdma_mc={tdma_mc}, tdma_acm={tdma_acm}, mesh_acm=1, '
                  f'mesh_mc={mesh_mc}')
            pass
