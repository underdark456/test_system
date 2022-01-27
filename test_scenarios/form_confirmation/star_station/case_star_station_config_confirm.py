from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, Checkbox, RouteTypes, TtsModes, RouteIds
from src.exceptions import NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.profile import Profile
from src.nms_entities.basic_entities.scheduler import Scheduler
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.form_confirmation.star_station'
backup_name = 'default_config.txt'


class StarStationConfirmationCase(CustomTestCase):
    """Confirm that UHP Star station gets correct settings from NMS"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 85
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.controllers, cls.stations = OptionsProvider.get_uhp_controllers_stations(1, ['UHP200', 'UHP200X'], 1, ['ANY', ])
        cls.mf_hub_uhp = cls.controllers[0].get('web_driver')
        cls.star_uhp = cls.stations[0].get('web_driver')

        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        cls.options = OptionsProvider.get_options(options_path)

        cls.nms = Nms(cls.driver, 0, 0)
        cls.net = Network.create(cls.driver, 0, {'name': 'test_net'})

        cls.tp = Teleport.create(cls.driver, cls.net.get_id(), {
            'name': 'test_net',
            'tx_lo': 0,
            'rx1_lo': 0,
            'rx2_lo': 0,
        })
        cls.vno = Vno.create(cls.driver, cls.net.get_id(), {'name': 'test_vno'})
        cls.ctrl = Controller.create(cls.driver, cls.net.get_id(), {
            'name': 'test_ctrl',
            'mode': ControllerModes.MF_HUB,
            'teleport': f'teleport:{cls.tp.get_id()}',
            'device_ip': cls.controllers[0].get('device_ip'),
            'device_vlan': cls.controllers[0].get('device_vlan'),
            'device_gateway': cls.controllers[0].get('device_gateway'),
            'tx_on': Checkbox.ON,
            'tx_level': cls.options.get('tx_level'),
            'hub_tts_mode': TtsModes.VALUE,
            'tts_value': 0,
        })
        cls.profile = Profile.create(cls.driver, cls.net.get_id(), {'name': 'test_pro'})
        cls.hub_shp = Shaper.create(cls.driver, cls.net.get_id(), {'name': 'hub_shp'})
        cls.stn_shp = Shaper.create(cls.driver, cls.net.get_id(), {'name': 'stn_shp'})
        cls.sch = Scheduler.create(cls.driver, cls.net.get_id(), {'name': 'test_scheduler'})
        cls.ser = Service.create(cls.driver, cls.net.get_id(), {
            'name': 'test_ser',
            'stn_vlan': cls.stations[0].get('device_vlan'),
        })

        cls.station_options = cls.options.get('star_station', {})
        # Formatting controller options to pass them to the station instance.
        station_options = {}
        for key, value in cls.station_options.items():
            if dict == type(value):
                station_options.update(value)

        cls.stn = Station.create(cls.driver, cls.vno.get_id(), station_options)
        cls.stn.send_param('serial', cls.stations[0].get('serial'))

        cls.stn_route = StationRoute.create(cls.driver, cls.stn.get_id(), {
            'type': RouteTypes.IP_ADDRESS,
            'service': f'service:{cls.ser.get_id()}',
            'ip': cls.stations[0].get('device_ip'),
        })
        cls.stn_default = StationRoute.create(cls.driver, cls.stn.get_id(), {
            'type': RouteTypes.STATIC_ROUTE,
            'service': f'service:{cls.ser.get_id()}',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': cls.stations[0].get('device_gateway'),
            'id': RouteIds.PRIVATE,
        })

        cls.star_uhp.star_station(params={
            'rx1_frq': cls.ctrl.read_param('tx_frq'),
            'rx1_sr': cls.ctrl.read_param('tx_sr'),
            'tx_level': cls.options.get('tx_level')
        })

        cls.mf_hub_uhp.set_nms_permission(
            vlan=cls.controllers[0].get('device_vlan'),
            password=cls.net.get_param('dev_password')
        )

        if not cls.ctrl.wait_up(timeout=60):
            raise NmsControlledModeException('MF HUB is not in UP state')
        if not cls.stn.wait_up():
            raise NmsControlledModeException('Star station is not in UP state')

        cls.nms.wait_next_tick()
        cls.nms.wait_next_tick()

    def test_ip_screening(self):
        """Test IP screening values"""
        self.nms_values = self.station_options.get('ip_screening')
        uhp_values = self.star_uhp.get_ip_routing_stats()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key),
                    msg=f'Station {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def test_snmp(self):
        """Test SNMP settings values"""
        self.nms_values = self.station_options.get('snmp')
        uhp_values = self.star_uhp.get_snmp_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key),
                    msg=f'Station {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def test_dhcp(self):
        """Test DHCP settings values"""
        self.nms_values = self.station_options.get('dhcp')
        uhp_values = self.star_uhp.get_dhcp_stats()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key),
                    msg=f'Station {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def test_dns(self):
        """Test DNS settings values"""
        self.nms_values = self.station_options.get('dns')
        uhp_values = self.star_uhp.get_dns_stats()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key),
                    msg=f'Station {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def test_arp(self):
        """Test ARP settings values"""
        self.nms_values = self.station_options.get('arp')
        uhp_values = self.star_uhp.get_arp_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key),
                    msg=f'Station {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def test_tftp(self):
        """Test TFTP settings values"""
        self.nms_values = self.station_options.get('tftp')
        uhp_values = self.star_uhp.get_tftp_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key),
                    msg=f'Station {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def test_nat(self):
        """Test NAT settings values"""
        self.nms_values = self.station_options.get('nat')
        uhp_values = self.star_uhp.get_nat_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key),
                    msg=f'Station {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def test_rip(self):
        """Test RIP settings values"""
        self.nms_values = self.station_options.get('rip')
        uhp_values = self.star_uhp.get_rip_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key),
                    msg=f'Station {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def test_sntp(self):
        """Test SNTP settings values"""
        self.nms_values = self.station_options.get('sntp')
        uhp_values = self.star_uhp.get_sntp_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key),
                    msg=f'Station {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def test_multicast(self):
        """Test Multicast settings values"""
        self.nms_values = self.station_options.get('mcast')
        uhp_values = self.star_uhp.get_multicast_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key),
                    msg=f'Station {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def test_tcpa(self):
        """Test TCPA settings values"""
        self.nms_values = self.station_options.get('tcpa')
        uhp_values = self.star_uhp.get_tcpa_form()
        for key, value in self.nms_values.items():
            # TCPA enable may be not set in station TCPA form
            if key == 'tcpa_enable':
                continue
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key),
                    msg=f'Station {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def test_service_monitoring(self):
        """Test Service monitoring settings values"""
        self.nms_values = self.station_options.get('service_monitoring')
        uhp_values = self.star_uhp.get_service_monitoring_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key),
                    msg=f'Station {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def test_modulator_queues(self):
        """Test Modulator queues settings values"""
        self.nms_values = self.station_options.get('queue')
        uhp_values = self.star_uhp.get_interfaces_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key),
                    msg=f'Station {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def test_realtime(self):
        """Test realtime BW allocation settings"""
        self.nms_values = self.station_options.get('realtime')
        uhp_values = self.star_uhp.get_realtime_bw_form()
        for key, value in self.nms_values.items():
            with self.subTest(field_name=key, value=value):
                self.assertEqual(
                    str(value).lower(),
                    uhp_values.get(key),
                    msg=f'Station {key}={value}, uhp {key}={uhp_values.get(key)}'
                )

    def test_station_table_settings(self):
        """Confirm settings that station goes to the stations' table in hub"""
        uhp_values = self.mf_hub_uhp.get_stations().get('2')
        self.assertEqual('1', uhp_values.get('enable'), msg=f'Station is not enabled in hub stations table')
        self.assertEqual(
            self.stations[0].get('serial')[-5:],
            uhp_values.get('serial'),
            msg=f'Station serial number is not as expected in hub station table'
        )
        self.assertEqual(
            str(self.stn.read_param('red_serial'))[-5:],
            uhp_values.get('red_serial'),
            msg=f'Station redundant serial number is not as expected in hub station table'
        )
        self.assertEqual(
            self.stn.read_param('rq_profile'),
            int(uhp_values.get('rq_profile')) + 1,
            msg=f'Rq_profile is not as expected in hub station table'
        )
        tcpa_enable = self.stn.read_param('tcpa_enable')
        if tcpa_enable in ('ON', 'ON ', 'On ', 'On', 'on', 'on ', '1', 1):
            tcpa_enable = '1'
        else:
            tcpa_enable = '0'
        self.assertEqual(
            tcpa_enable,
            uhp_values.get('tcpa_enable'),
            msg=f'TCPA enable is not as expected in hub station table'
        )
