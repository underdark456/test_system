from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import ControllerModes, CheckboxStr, StationModes, RouteTypes, PriorityTypes, RuleTypes, \
    ActionTypes, QueueTypes
from src.exceptions import NmsControlledModeException
from src.nms_entities.basic_entities.controller import Controller
from src.nms_entities.basic_entities.controller_rip import ControllerRip
from src.nms_entities.basic_entities.network import Network
from src.nms_entities.basic_entities.nms import Nms
from src.nms_entities.basic_entities.policy import Policy
from src.nms_entities.basic_entities.policy_rule import PolicyRule
from src.nms_entities.basic_entities.qos import Qos
from src.nms_entities.basic_entities.service import Service
from src.nms_entities.basic_entities.shaper import Shaper
from src.nms_entities.basic_entities.station import Station
from src.nms_entities.basic_entities.station_rip import StationRip
from src.nms_entities.basic_entities.station_route import StationRoute
from src.nms_entities.basic_entities.teleport import Teleport
from src.nms_entities.basic_entities.vno import Vno
from src.options_providers.options_provider import OptionsProvider, API_CONNECT

options_path = 'test_scenarios.form_confirmation.rip_router'
backup_name = 'default_config.txt'


class RipRouterConfirmationCase(CustomTestCase):
    """Confirm RIP router settings in UHP controller and station"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.20'
    __execution_time__ = 90  # approximate test case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        controllers, stations = OptionsProvider.get_uhp_controllers_stations(1, ['UHP200', 'UHP200X'], 1, ['ANY', ])
        cls.mf_hub_uhp = controllers[0].get('web_driver')
        cls.star_uhp = stations[0].get('web_driver')

        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, API_CONNECT)
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)

        cls.nms = Nms(cls.driver, 0, 0)

        cls.net = Network.create(cls.driver, 0, {'name': 'test_net'})
        cls.tp = Teleport.create(cls.driver, 0, {'name': 'test_tp', 'tx_lo': 0, 'rx1_lo': 0, 'rx2_lo': 0})
        cls.ctrl = Controller.create(cls.driver, 0, {
            'name': 'test_ctrl',
            'mode': ControllerModes.MF_HUB,
            'teleport': 'teleport:0',
            'device_ip': controllers[0].get('device_ip'),
            'device_vlan': controllers[0].get('device_vlan'),
            'device_gateway': controllers[0].get('device_gateway'),
            'tx_on': CheckboxStr.ON,
            'tx_level': cls.options.get('tx_level'),
        })
        cls.vno = Vno.create(cls.driver, 0, {'name': 'test_vno'})
        cls.ser = Service.create(cls.driver, 0, {'name': 'test_ser', 'stn_vlan': stations[0].get('device_vlan')})

        cls.stn = Station.create(cls.driver, 0, {
            'name': 'test_stn',
            'serial': stations[0].get('serial'),
            'enable': CheckboxStr.ON,
            'mode': StationModes.STAR,
            'rx_controller': 'controller:0',
        })

        cls.stn_route = StationRoute.create(cls.driver, 0, {
            'type': RouteTypes.IP_ADDRESS,
            'service': 'service:0',
            'ip': stations[0].get('device_ip'),
        })
        cls.stn_default = StationRoute.create(cls.driver, 0, {
            'type': RouteTypes.STATIC_ROUTE,
            'service': 'service:0',
            'ip': '0.0.0.0',
            'mask': '/0',
            'gateway': stations[0].get('device_gateway'),
        })

        # Preparing RIP router
        cls.shaper1 = Shaper.create(cls.driver, cls.net.get_id(), {'name': 'shp1'})
        cls.shaper2 = Shaper.create(cls.driver, cls.net.get_id(), {'name': 'shp2'})
        cls.policy1 = Policy.create(cls.driver, cls.net.get_id(), {'name': 'pol1'})
        cls.rule1 = PolicyRule.create(cls.driver, cls.policy1.get_id(), {
            'sequence': 1,
            'type': RuleTypes.ACTION,
            'action_type': ActionTypes.SET_QUEUE,
            'queue': QueueTypes.P6,
            'terminate': CheckboxStr.ON,
        })
        cls.policy2 = Policy.create(cls.driver, cls.net.get_id(), {'name': 'pol2'})
        cls.rule2 = PolicyRule.create(cls.driver, cls.policy2.get_id(), {
            'sequence': 1,
            'type': RuleTypes.ACTION,
            'action_type': ActionTypes.SET_QUEUE,
            'queue': QueueTypes.P3,
            'terminate': CheckboxStr.ON,
        })
        cls.service = Service.create(cls.driver, cls.net.get_id(), {
            'name': 'rip_service',
            'hub_vlan': 206,
            'stn_vlan': 306,
            'rip_announced': CheckboxStr.ON,
        })
        cls.ctrl_qos = Qos.create(cls.driver, 0, {
            'name': 'ctrl_rip_qos',
            'priority': PriorityTypes.POLICY,
            'policy': f'policy:{cls.policy1.get_id()}',
            'shaper': f'shaper:{cls.shaper1.get_id()}',
        })
        cls.stn_qos = Qos.create(cls.driver, 0, {
            'name': 'stn_rip_qos',
            'priority': PriorityTypes.POLICY,
            'policy': f'policy:{cls.policy2.get_id()}',
            'shaper': f'shaper:{cls.shaper2.get_id()}',
        })
        cls.rip_ctrl = ControllerRip.create(cls.driver, cls.ctrl.get_id(), {
            'service': f'service:{cls.service.get_id()}',
            'forward_qos': f'qos:{cls.ctrl_qos.get_id()}',
            'return_qos': f'qos:{cls.stn_qos.get_id()}',
            'rip_next_hop': '172.17.76.87',
            'lan_rx': CheckboxStr.ON,
            'lan_default': CheckboxStr.ON,
            'sat_rx': CheckboxStr.ON,
            'sat_default': CheckboxStr.ON,
            'announce': CheckboxStr.ON,
        })
        cls.rip_stn = StationRip.create(cls.driver, cls.stn.get_id(), {
            'service': f'service:{cls.service.get_id()}',
            'forward_qos': f'qos:{cls.ctrl_qos.get_id()}',
            'return_qos': f'qos:{cls.stn_qos.get_id()}',
            'rip_next_hop': '172.11.32.65',
            'lan_rx': CheckboxStr.ON,
            'lan_default': CheckboxStr.ON,
            'sat_rx': CheckboxStr.ON,
            'sat_default': CheckboxStr.ON,
            'announce': CheckboxStr.ON,
        })

        # Preconfiguring station
        cls.star_uhp.star_station(
            params={
                'rx1_frq': cls.ctrl.read_param("tx_frq"),
                'rx1_sr': cls.ctrl.get_param("tx_sr"),
                'tx_level': cls.options.get('tx_level')
            }
        )
        cls.mf_hub_uhp.set_nms_permission(
            vlan=controllers[0].get('device_vlan'),
            password=cls.net.read_param('dev_password')
        )

        if not cls.ctrl.wait_up(timeout=60):
            raise NmsControlledModeException('Controller is not in UP state')

        if not cls.stn.wait_up(timeout=60):
            raise NmsControlledModeException('Station is not in UP state')

        cls.nms.wait_ticks(3)

    def test_controller_rip_entry(self):
        """Make sure that controller UHP get correct RIP router values"""
        uhp_values = self.mf_hub_uhp.get_rip_router()
        # Checking RIP router values
        nms_value = self.rip_ctrl.get_param('rip_next_hop')
        uhp_value = uhp_values.get('rip_next_hop')
        self.assertEqual(
            nms_value,
            uhp_value,
            msg=f'Controller rip_next_hop nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.rip_ctrl.get_param('lan_rx')
        uhp_value = uhp_values.get('lan_rx')
        if uhp_value is False:
            uhp_value = 'OFF'
        elif uhp_value:
            uhp_value = 'ON'
        self.assertEqual(
            nms_value.lower().strip(),
            uhp_value.lower(),
            msg=f'Controller lan_rx nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.rip_ctrl.get_param('lan_default')
        uhp_value = uhp_values.get('lan_default')
        if uhp_value is False:
            uhp_value = 'OFF'
        elif uhp_value:
            uhp_value = 'ON'
        self.assertEqual(
            nms_value.lower().strip(),
            uhp_value.lower(),
            msg=f'Controller lan_default nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.rip_ctrl.get_param('sat_rx')
        uhp_value = uhp_values.get('sat_rx')
        if uhp_value is False:
            uhp_value = 'OFF'
        elif uhp_value:
            uhp_value = 'ON'
        self.assertEqual(
            nms_value.lower().strip(),
            uhp_value.lower(),
            msg=f'Controller sat_rx nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.rip_ctrl.get_param('sat_default')
        uhp_value = uhp_values.get('sat_default')
        if uhp_value is False:
            uhp_value = 'OFF'
        elif uhp_value:
            uhp_value = 'ON'
        self.assertEqual(
            nms_value.lower().strip(),
            uhp_value.lower(),
            msg=f'Controller sat_default nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.rip_ctrl.get_param('announce')
        uhp_value = uhp_values.get('announce')
        if uhp_value is False:
            uhp_value = 'OFF'
        elif uhp_value:
            uhp_value = 'ON'
        self.assertEqual(
            nms_value.lower().strip(),
            uhp_value.lower(),
            msg=f'Controller announce nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.service.get_param('hub_vlan')
        uhp_value = uhp_values.get('hub_vlan')
        self.assertEqual(
            str(nms_value),
            str(uhp_value),
            msg=f'Controller hub_vlan nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.service.get_param('stn_vlan')
        uhp_value = uhp_values.get('stn_vlan')
        self.assertEqual(
            str(nms_value),
            str(uhp_value),
            msg=f'Controller stn_vlan nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.ctrl_qos.get_param('priority')
        uhp_value = uhp_values.get('priority')
        self.assertEqual(
            str(nms_value),
            str(uhp_value),
            msg=f'Controller priority nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.policy1.get_param('name')
        uhp_value = uhp_values.get('policy')
        self.assertTrue(
            uhp_value.find(nms_value) != -1,
            msg=f'Controller policy nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.shaper1.get_param('name')
        uhp_value = uhp_values.get('shaper')
        self.assertTrue(
            uhp_value.find(nms_value) != -1,
            msg=f'Controller shaper nms value={nms_value}, uhp value={uhp_value}'
        )

    def test_station_rip_entry(self):
        """Make sure that station UHP get correct RIP router values"""
        uhp_values = self.star_uhp.get_rip_router()
        # Checking RIP router values
        nms_value = self.rip_stn.get_param('rip_next_hop')
        uhp_value = uhp_values.get('rip_next_hop')
        self.assertEqual(
            nms_value,
            uhp_value,
            msg=f'Station rip_next_hop nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.rip_stn.get_param('lan_rx')
        uhp_value = uhp_values.get('lan_rx')
        if uhp_value is False:
            uhp_value = 'OFF'
        elif uhp_value:
            uhp_value = 'ON'
        self.assertEqual(
            nms_value.lower().strip(),
            uhp_value.lower(),
            msg=f'Station lan_rx nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.rip_stn.get_param('lan_default')
        uhp_value = uhp_values.get('lan_default')
        if uhp_value is False:
            uhp_value = 'OFF'
        elif uhp_value:
            uhp_value = 'ON'
        self.assertEqual(
            nms_value.lower().strip(),
            uhp_value.lower(),
            msg=f'Station lan_default nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.rip_stn.get_param('sat_rx')
        uhp_value = uhp_values.get('sat_rx')
        if uhp_value is False:
            uhp_value = 'OFF'
        elif uhp_value:
            uhp_value = 'ON'
        self.assertEqual(
            nms_value.lower().strip(),
            uhp_value.lower(),
            msg=f'Station sat_rx nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.rip_stn.get_param('sat_default')
        uhp_value = uhp_values.get('sat_default')
        if uhp_value is False:
            uhp_value = 'OFF'
        elif uhp_value:
            uhp_value = 'ON'
        self.assertEqual(
            nms_value.lower().strip(),
            uhp_value.lower(),
            msg=f'Station sat_default nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.rip_stn.get_param('announce')
        uhp_value = uhp_values.get('announce')
        if uhp_value is False:
            uhp_value = 'OFF'
        elif uhp_value:
            uhp_value = 'ON'
        self.assertEqual(
            nms_value.lower().strip(),
            uhp_value.lower(),
            msg=f'Station announce nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.service.get_param('hub_vlan')
        uhp_value = uhp_values.get('hub_vlan')
        self.assertEqual(
            str(nms_value),
            str(uhp_value),
            msg=f'Station hub_vlan nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.service.get_param('stn_vlan')
        uhp_value = uhp_values.get('stn_vlan')
        self.assertEqual(
            str(nms_value),
            str(uhp_value),
            msg=f'Station stn_vlan nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.stn_qos.get_param('priority')
        uhp_value = uhp_values.get('priority')
        self.assertEqual(
            str(nms_value),
            str(uhp_value),
            msg=f'Station priority nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.policy2.get_param('name')
        uhp_value = uhp_values.get('policy')
        self.assertTrue(
            uhp_value.find(nms_value) != -1,
            msg=f'Station policy nms value={nms_value}, uhp value={uhp_value}'
        )

        nms_value = self.shaper2.get_param('name')
        uhp_value = uhp_values.get('shaper')
        self.assertTrue(
            uhp_value.find(nms_value) != -1,
            msg=f'Station shaper nms value={nms_value}, uhp value={uhp_value}'
        )
