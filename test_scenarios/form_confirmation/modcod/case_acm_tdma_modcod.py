from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, ModelTypesStr, TdmaAcmModes, TdmaModcod
from src.exceptions import NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.form_confirmation.modcod'
backup_name = 'default_config.txt'


class AcmTdmaModcodConfirmationCase(CustomTestCase):
    """TDMA ACM Legacy, 12modcods, 16modcods confirm UHP gets correct settings"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 255  # approximate test case execution time in seconds

    @classmethod
    def set_up_class(cls):
        cls.uhp200x_modems = OptionsProvider.get_uhp_by_model(ModelTypesStr.UHP200X, number=1)
        cls.uhp_ip = cls.uhp200x_modems[0].get('device_ip')
        cls.uhp = cls.uhp200x_modems[0].get('web_driver')

        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)

        cls.nms = Nms(cls.driver, 0, 0)
        cls.class_logger.info(f'NMS SW version: {cls.nms.get_param("version")}')

        cls.thresholds = OptionsProvider.get_options(options_path).get('tdma_acm_threshold')
        cls.modcod = OptionsProvider.get_options(options_path).get('nms_to_uhp')

        cls.class_logger.info(f'UHP {cls.uhp_ip} SW version: {cls.uhp.get_software_version()}')
        cls.uhp.set_nms_permission(password='indeed', vlan=cls.uhp200x_modems[0].get('device_vlan'))

        cls.net = Network.create(cls.driver, 0, params={'name': 'net-0', 'dev_password': 'indeed'})
        cls.vno = Vno.create(cls.driver, cls.net.get_id(), params={'name': 'vno-0'})
        cls.tp = Teleport.create(cls.driver, cls.net.get_id(), params={
            'name': 'tp-0',
            'sat_name': 'sat-0',
            'tx_lo': 0,
            'rx1_lo': 0,
            'rx2_lo': 0,
        })
        cls.mf_hub = Controller.create(cls.driver, cls.net.get_id(), params={
            'name': 'HM',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{cls.tp.get_id()}',
            'device_ip': cls.uhp_ip,
            'device_vlan': cls.uhp200x_modems[0].get('device_vlan'),
            'device_gateway': cls.uhp200x_modems[0].get('device_gateway'),
            'uhp_model': cls.uhp200x_modems[0].get('model'),
            'tx_on': 'ON',
            'tx_level': cls.options.get('tx_level'),
        })
        if not cls.mf_hub.wait_not_states(['Unknown', 'Unreachable']):
            raise NmsControlledModeException(f'UHP at {cls.uhp_ip} is not under NMS control')

    def test_tdma_legacy(self):
        """TDMA ACM legacy mode confirmation, iterating over modulation (and thresholds for UHP 3.6 only)"""
        # Iterating over tdma_mc
        for modcod in (TdmaModcod._BPSK_1_2, TdmaModcod._QPSK_1_2, TdmaModcod._8PSK_1_2, TdmaModcod._16APSK_1_2,):
            # Iterating over tdma_thr_acm from lowes to highest with additional in the middle
            for thresh in (0, 3.1, 5.9):
                self.mf_hub.send_params({
                    'tdma_mc': modcod,
                    'tdma_acm': TdmaAcmModes.LEGACY,
                    'tdma_thr_acm': thresh
                })
                self.nms.wait_ticks(2)
                mod_type = self.mf_hub.read_param('tdma_mc').split()[0].lower()  # modulation type lowercased w/o FEC
                uhp_values = self.uhp.get_tdma_acm_form()
                self.assertEqual('1', uhp_values.get('tdma_acm'), msg=f'TDMA ACM is not ON in UHP')
                self.assertEqual('0', uhp_values.get('mode'), msg=f'TDMA ACM mode is not Legacy in UHP')
                for fec in ('1_2', '2_3', '3_4', '5_6'):
                    self.assertEqual('1', uhp_values.get(f'{mod_type}{fec}'), msg=f'{mod_type}{fec} is not ON in UHP')
                    if not self.uhp200x_modems[0].get('sw').startswith('3.7'):
                        self.assertEqual(
                            str(float(self.thresholds.get(f'{mod_type}{fec}_thr') + thresh)),
                            uhp_values.get(f'{mod_type}{fec}_thr'),
                            msg=f'{mod_type}{fec}_thr differs from expected'
                        )

    def test_tdma_12_modcods(self):
        """TDMA ACM 12modcods mode confirmation (for UHP ver.3.6 only, 3.7 is skipped)"""
        if self.uhp200x_modems[0].get('sw').startswith('3.7'):
            self.info(f'UHP sw {self.uhp200x_modems[0].get("sw")}, 12modcods mode is not tested')
            return
        for thr in (0, 3.1, 5.9):
            self.mf_hub.send_params({
                'slot_length': 4,
                'tdma_mc': TdmaModcod._QPSK_1_2,
                'tdma_acm': TdmaAcmModes.TWELVE_MODCODS,
                'tdma_thr_acm': thr,
                'bpsk1_2': False,
                'bpsk2_3': False,
                'bpsk3_4': False,
                'bpsk5_6': False,
                'qpsk1_2': False,
                'qpsk2_3': True,
                'qpsk3_4': True,
                'qpsk5_6': False,
                'epsk1_2': False,
                'epsk2_3': False,
                'epsk3_4': True,
                'epsk5_6': True,
                'apsk1_2': True,
                'apsk2_3': False,
                'apsk3_4': True,
                'apsk5_6': False,
            })
            self.nms.wait_ticks(2)
            uhp_values = self.uhp._get_tdma_acm_form36()
            self.assertEqual('1', uhp_values.get('tdma_acm'), msg=f'TDMA ACM is not ON in UHP')
            self.assertEqual('1', uhp_values.get('mode'), msg=f'TDMA ACM mode is not 12modcods in UHP')
            # Checking checkboxes:
            for m in self.modcod.keys():
                if m.startswith('bpsk'):
                    continue
                nms_value = self.mf_hub.read_param(m)
                if m == 'qpsk1_2':  # tdma_mc should be also ON TDMA ACM
                    self.assertEqual('1', uhp_values.get(m), msg=f'{m} (tdma_mc) is not ON in UHP')
                elif nms_value is None or nms_value.lower() == 'off':
                    self.assertEqual('0', uhp_values.get(f'{self.modcod.get(m)}'), msg=f'{m} is not OFF in UHP')
                else:
                    self.assertEqual('1', uhp_values.get(f'{self.modcod.get(m)}'), msg=f'{m} is not ON in UHP')
            # Checking threshold
            self.assertEqual(
                str(float(thr)),
                uhp_values.get(f'tdma_acm_thr'),
                msg=f'tdma_acm_thr should be {thr}, UHP value {uhp_values.get(f"tdma_acm_thr")}'
            )

    def test_mf_hub_16modcod_acm_uhp(self):
        """TDMA ACM 16modcods mode confirmation"""
        if not self.uhp200x_modems[0].get('sw').startswith('3.7'):
            self.info(f'UHP sw {self.uhp200x_modems[0].get("sw")}, 16modcods mode is not tested')
            return
        self.mf_hub.send_params(self.options.get('16modcods_test_values'))
        self.assertEqual('16modcods', self.mf_hub.read_param('tdma_acm'), msg=f'NMS tdma_acm is not set to 16modcods')
        self.nms.wait_ticks(2)
        uhp_values = self.uhp.get_tdma_acm_form()
        self.assertEqual('1', uhp_values.get('tdma_acm'), msg=f'TDMA ACM is not ON in UHP')
        self.assertEqual('1', uhp_values.get('mode'), msg=f'TDMA ACM mode is not 16modcods in UHP')
        # Checking checkboxes:
        for m in self.modcod.keys():
            nms_value = self.mf_hub.read_param(m)
            if nms_value.lower() == 'off':
                self.assertEqual('0', uhp_values.get(f'{self.modcod.get(m)}'), msg=f'{m} is not OFF in UHP')
            else:
                self.assertEqual('1', uhp_values.get(f'{self.modcod.get(m)}'), msg=f'{m} is not ON in UHP')
                # Checking thresholds
                self.assertEqual(
                    str(self.options.get('16modcods_test_values').get(f't_{m}')),
                    uhp_values.get(f'{self.modcod.get(m)}_thr'),
                    msg=f'threshold for {m} should be {self.options.get("16modcods_test_values").get(f"t_{m}")}, '
                        f'UHP value {uhp_values.get(f"{self.modcod.get(m)}_thr")}'
                )

    def test_tdma_mesh_acm(self):
        """TDMA mesh_acm confirmation (UHP gets correct values)"""
        # Probably do not check all valid combinations?
        # ~ 3250 seconds
        for mode in (TdmaAcmModes.SIXTEEN_MODCODS, ):
            for tdma_mc in (TdmaModcod._BPSK_1_2, TdmaModcod._QPSK_1_2, TdmaModcod._8PSK_1_2, TdmaModcod._16APSK_1_2):
                for slot_length in range(2, 16):
                    for mesh_mc in (TdmaModcod._BPSK_2_3, TdmaModcod._QPSK_2_3, TdmaModcod._8PSK_3_4, TdmaModcod._16APSK_5_6):
                        for hub_rx_mesh in ('0', '1'):
                            # Ignoring non-valid combinations as long as form validation test exists
                            if tdma_mc == TdmaModcod._BPSK_1_2:
                                if 4 * slot_length > 13 and mesh_mc in range(12, 16):
                                    continue
                                elif 3 * slot_length > 14 and mesh_mc in range(8, 12):
                                    continue
                                elif 2 * slot_length > 15 and mesh_mc in range(4, 8):
                                    continue
                            elif tdma_mc == TdmaModcod._QPSK_1_2:
                                if mesh_mc in range(4):
                                    continue
                                elif 2 * slot_length > 15 and mesh_mc in range(12, 16):
                                    continue
                                elif (1.5 * slot_length != int(1.5 * slot_length) or 1.5 * slot_length >= 15) \
                                        and mesh_mc in range(8, 12):
                                    continue
                            elif tdma_mc == TdmaModcod._8PSK_1_2:
                                if mesh_mc in range(8):
                                    continue
                                elif ((slot_length * 4) % 3 != 0 or (slot_length * 4 / 3) >= 15) \
                                        and mesh_mc in range(12, 16):
                                    continue
                            else:
                                if mesh_mc in range(12):
                                    continue
                            self.mf_hub.send_params({
                                'slot_length': slot_length,
                                'tdma_mc': tdma_mc,
                                'tdma_acm': mode,
                                'mesh_acm': True,
                                'mesh_mc': mesh_mc,
                                'hub_rx_mesh': hub_rx_mesh,
                            })
                            self.nms.wait_ticks(3)
                            uhp_values = self.uhp.get_tdma_acm_form()
                            self.assertEqual('1', uhp_values.get('tdma_acm'), msg=f'TDMA ACM is OFF in UHP')
                            self.assertEqual('1', uhp_values.get('mode'), msg=f'TDMA ACM mode is not 16modcods in UHP')
                            self.assertEqual(
                                hub_rx_mesh,
                                uhp_values.get('hub_rx_mesh'),
                                msg=f'hub_rx_mesh should be {hub_rx_mesh}, UHP values {uhp_values.get("hub_rx_mesh")}'
                            )
                            self.assertEqual(
                                str(mesh_mc),
                                str(int(uhp_values.get('mesh_mc')) - 1),
                                msg=f'mesh_mc should be {mesh_mc}, '
                                    f'UHP values {int(uhp_values.get("mesh_mc")) - 1}'
                            )
