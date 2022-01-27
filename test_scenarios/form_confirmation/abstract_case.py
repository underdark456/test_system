from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import TdmaModcodStr, ModcodModesStr
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = "test_scenarios.form_confirmation"
backup_name = 'default_config.txt'


class _AbstractCase(CustomTestCase):

    @classmethod
    def set_up_class(cls) -> None:
        cls.uhp_option = OptionsProvider.get_uhp_by_model('UHP200', 'UHP200X', number=1)[0]
        cls.uhp = cls.uhp_option.get('web_driver')

        cls.nms_values = {}
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)  # the default empty config
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.system_options = OptionsProvider.get_system_options('test_scenarios.form_confirmation')
        cls.options = OptionsProvider.get_options('test_scenarios.form_confirmation')

        cls.network = Network.create(cls.driver, 0, params=cls.options.get('network'))
        cls.teleport = Teleport.create(cls.driver, 0, params={
            'name': 'test_teleport',
            'tx_lo': 0,
            'rx1_lo': 0,
            'rx2_lo': 0,
        })
        cls.shaper = Shaper.create(cls.driver, cls.network.get_id(), {'name': 'test_shaper'})
        cls.vno = Vno.create(cls.driver, cls.network.get_id(), {'name': 'test_vno'})

        cls.uhp.set_nms_permission(
            vlan=cls.uhp_option.get('device_vlan'),
            password=cls.network.read_param('dev_password'),
        )

    def _test_teleport(self):
        uhp_values = self.uhp.get_teleport_values()
        uhp_values.update(self.uhp.get_demodulator_form())
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_modulator(self):
        uhp_values = self.uhp.get_modulator_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_tlc(self):
        uhp_values = self.uhp.get_tlc_form()
        for key, value in self.nms_values.items():
            if key == 'tlc_max_lvl':
                #  UHP supports only integer TLC level values
                value = str(int(float(value)))
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_demodulator1(self):
        uhp_values = self.uhp.get_demodulator_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_demodulator2(self):
        uhp_values = self.uhp.get_demodulator_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_tdma_protocol(self):
        uhp_values = self.uhp.get_tdma_protocol_form()
        for key, value in self.nms_values.items():
            if key == 'stn_number':
                # NMS always reserves one station for its needs, therefore number_of_station = number_of_stations + 1
                value = str(int(value) + 1)
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_tdma_rf_setup(self):
        uhp_values = self.uhp.get_tdma_rf_form()
        for key, value in self.nms_values.items():
            if key == 'tdma_mc':
                value = TdmaModcodStr._8PSK_3_4
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}')

    def _test_tdma_bw_allocation(self):
        uhp_values = self.uhp.get_tdma_bw_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_master_settings(self):
        uhp_values = self.uhp.get_realtime_bw_form()
        uhp_values.update(self.uhp.get_station_edit_form())  # Master settings are taken from two sources in UHP
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_ip_screening(self):
        uhp_values = self.uhp.get_ip_routing_stats()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_snmp(self):
        uhp_values = self.uhp.get_snmp_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_dhcp(self):
        uhp_values = self.uhp.get_dhcp_stats()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_dns(self):
        uhp_values = self.uhp.get_dns_stats()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_arp(self):
        uhp_values = self.uhp.get_arp_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_tftp(self):
        uhp_values = self.uhp.get_tftp_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_nat(self):
        uhp_values = self.uhp.get_nat_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_rip(self):
        uhp_values = self.uhp.get_rip_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_sntp(self):
        uhp_values = self.uhp.get_sntp_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_multicast(self):
        uhp_values = self.uhp.get_multicast_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_traffic_protection(self):
        uhp_values = self.uhp.get_security_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_tcpa(self):
        uhp_values = self.uhp.get_tcpa_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_service_monitoring(self):
        uhp_values = self.uhp.get_service_monitoring_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_modulator_queues(self):
        uhp_values = self.uhp.get_interfaces_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_roaming(self):
        uhp_values = self.uhp.get_roaming_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key, None),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_timing(self):
        uhp_values = self.uhp.get_timing_values()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    str(uhp_values.get(key)).lower(),
                    msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def _test_tdm_tx(self):
        uhp_values = self.uhp.get_tdm_tx_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                if key == 'tx_modcod':
                    self.assertEqual(
                        [*ModcodModesStr()][int(value) - 1].lower(),
                        uhp_values.get(key),
                        msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                    )
                elif key == 'tx_rolloff':
                    value = '1' if value == 'R5' else '0'
                    self.assertEqual(
                        value,
                        uhp_values.get(key),
                        msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                    )
                else:
                    self.assertEqual(
                        str(value).lower(),
                        uhp_values.get(key),
                        msg=f'controller {key}={value}, uhp {key}={uhp_values.get(key)}'
                    )

    def _test_check_rx(self):
        uhp_values = self.uhp.get_demodulator_form()
        self.assertEqual(
            str(self.nms_values),
            uhp_values.get('check_rx'),
            msg=f'Check RX expected {self.nms_values}, got {uhp_values.get("check_rx")}'
        )

    def _test_return_channel(self, channel=1):
        uhp_return_channel_values = self.uhp.get_dama_return_channel_form(return_channel=channel)
        uhp_tdm_rx_values = self.uhp.get_demodulator_form()
        for key, value in self.nms_values.items():
            if key == 'a_dama_rx_frq':
                self.assertEqual(
                    str(value),
                    uhp_tdm_rx_values.get('rx1_frq'),
                    msg=f'NMS {key}={value}, UHP TDM/SCPC RX rx1_frq={uhp_tdm_rx_values.get("rx1_frq")}'
                )
            elif key == 'b_dama_rx_frq':
                self.assertEqual(
                    str(value),
                    uhp_tdm_rx_values.get('rx2_frq'),
                    msg=f'NMS {key}={value}, UHP TDM/SCPC RX rx2_frq={uhp_tdm_rx_values.get("rx2_frq")}'
                )
            else:
                uhp_key = key.lstrip('a_').lstrip('b_')
                self.assertEqual(
                    str(value),
                    uhp_return_channel_values.get(uhp_key),
                    msg=f'NMS {key}={value}, '
                        f'UHP Return Channel {channel} {uhp_key}={uhp_return_channel_values.get(uhp_key)}'
                )

            if key == 'a_dama_sr':
                self.assertEqual(
                    str(value),
                    uhp_tdm_rx_values.get('rx1_sr'),
                    msg=f'NMS {key}={value}, UHP TDM/SCPC RX rx1_sr={uhp_tdm_rx_values.get("rx1_sr")}'
                )
            if key == 'b_dama_sr':
                self.assertEqual(
                    str(value),
                    uhp_tdm_rx_values.get('rx2_sr'),
                    msg=f'NMS {key}={value}, UHP TDM/SCPC RX rx2_sr={uhp_tdm_rx_values.get("rx2_sr")}'
                )

    def _test_tdm_acm_settings(self):
        uhp_values = self.uhp.get_tdm_acm_form()
        for key, value in self.nms_values.items():
            self.assertEqual(
                str(value),
                uhp_values.get(key),
                msg=f'NMS {key}={value}, UHP TDM ACM {key}={uhp_values.get(key)}'
            )
