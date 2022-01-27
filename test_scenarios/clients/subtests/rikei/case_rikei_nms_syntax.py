import json
import random
from http import HTTPStatus
from ipaddress import IPv4Address
from json import JSONDecodeError
from time import sleep

import requests
import xmltodict
from selenium.webdriver.common.by import By

from src.constants_nms3 import HUBLESS_MASTER, UHP_200X
from src.custom_test_case import CustomTestCase
from src.drivers.abstract_http_driver import CHROME
from src.drivers.http.web_driver import WebDriver
from src.exceptions import InvalidOptionsException, ObjectNotCreatedException, ObjectNotFoundException
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

__author__ = 'dkudryashov'
__version__ = '0.1'

WEB_LOGIN_PATH = 'login'
options_path = 'test_scenarios.clients.subtests.rikei'
_wait_time_out = 1


class RikeiNmsSyntaxCase(CustomTestCase):
    """NMS 3.5 API requests in XML format syntax case"""

    nms35 = None
    address = None
    modem2_id = None
    modem_id = None
    rffeed_id = None
    sat_id = None
    tp_id = None
    net_id = None
    ctrl_id = None
    nms_token = None
    options = None
    driver = None
    nms_ip_address = None
    system_options = None

    @classmethod
    def set_up_class(cls):
        cls.options = OptionsProvider.get_options(options_path)
        cls.system_options = OptionsProvider.get_system_options(options_path)
        cls.nms_ip_address = cls.options.get('nms_ip_address', None)
        if cls.nms_ip_address is None:
            raise InvalidOptionsException('NMS IP-address is not provided in the options')
        cls.nms_token = cls.options.get('nms_token', None)
        if cls.nms_token is None:
            raise InvalidOptionsException('NMS token is not provided in the options')
        cls.driver = WebDriver._create_chrome_driver(
            CHROME, {
                'no_gui':  True,
                'driver_path': cls.system_options.get(CHROME_CONNECT).get('driver_path'),
                'address': f'http://{cls.nms_ip_address}'
            }
        )
        cls.login()
        cls.nms_sw = cls.get_nms_version()
        if cls.nms_sw.startswith('3.5'):
            cls.nms35 = True
        else:
            cls.nms35 = False
        cls.class_logger.info(f'NMS SW: {cls.nms_sw}')
        # TODO: find a better way to preconfigure NMS for the tests
        # Creating a new network
        result, error, cls.net_id, data, warnings = cls.post_request_json(
            obj_name="network", action="insert", params={
                "name": f"net-{random.randint(1000000, 9999999)}"
            }
        )
        # If no license to create a new network
        if not result or cls.net_id is None:
            result, error, cls.net_id, data, warnings = cls.post_request_json(
                obj_name="network", action="list"
            )
            if not result:
                raise ObjectNotCreatedException('Cannot create a network for the test case')
            cls.net_id = 1
        # Creating a new teleport
        result, error, cls.tp_id, data, warnings = cls.post_request_json(
            obj_name="teleport", action="insert", params={
                "name": f"tp-{random.randint(1000000, 9999999)}"
            }
        )
        if not result or cls.tp_id is None:
            raise ObjectNotCreatedException('Cannot create a teleport for the test case')
        # Creating a new satellite
        result, error, cls.sat_id, data, warnings = cls.post_request_json(
            obj_name="satellite", action="insert", params={
                "name": f"sat-{random.randint(1000000, 9999999)}",
                "longitude_deg": "60",
                "longitude_min": "15",
             }
        )
        if result is None or cls.sat_id is None:
            raise ObjectNotCreatedException('Cannot create a satellite for the test case')
        if cls.tp_id is None:
            raise ObjectNotCreatedException('Cannot create a teleport for the test case')

        # Creating a new rffeed
        result, error, cls.rffeed_id, data, warnings = cls.post_request_json(
            obj_name="rffeed", action="insert", params={
                "name": f"rffeed-{random.randint(1000000, 9999999)}",
                "teleport_id": cls.tp_id,
                "satellite_id": cls.sat_id
             }
        )
        if not result or cls.rffeed_id is None:
            raise ObjectNotCreatedException('Cannot create an rffeed for the test case')

        # Creating a new modem
        result, error, cls.modem_id, data, warnings = cls.post_request_json(
            obj_name="modem", action="insert", params={
                "name": f"modem-{random.randint(1000000, 9999999)}",
                "teleport_id": cls.tp_id,
                "ip_addr": str(IPv4Address(random.getrandbits(32))),
                "rffeed_id": cls.rffeed_id,
                "platform": UHP_200X,
             }
        )
        if not result or cls.modem_id is None:
            raise ObjectNotCreatedException('Cannot create a modem for the test case')

        # Creating another modem
        result, error, cls.modem2_id, data, warnings = cls.post_request_json(
            obj_name="modem", action="insert", params={
                "name": f"modem-{random.randint(1000000, 9999999)}",
                "teleport_id": cls.tp_id,
                "ip_addr": str(IPv4Address(random.getrandbits(32))),
                "rffeed_id": cls.rffeed_id,
                "platform": UHP_200X,
             }
        )
        if not result or cls.modem2_id is None:
            raise ObjectNotCreatedException('Cannot create a modem for the test case')

        # Creating a new controller
        result, error, cls.ctrl_id, data, warnings = cls.post_request_json(
            obj_name="controller",
            action="insert",
            params={
                    "name": f"ctrl-{random.randint(1000000, 9999999)}",
                    "network_id": cls.net_id,
                    "id_net": "255",
                    "id_rf": "255",
                    "type": HUBLESS_MASTER,
                    "uhp_model": UHP_200X,
                    "teleport_id": cls.tp_id,
                    "rffeed_id": cls.rffeed_id,
                    "modem_id": cls.modem_id,
                    "modulator_txon": "1"
            }
        )
        if not result or cls.ctrl_id is None:
            raise ObjectNotCreatedException('Cannot create a controller for the test case')

    def test_controller_select(self):
        """1. Check current controller settings"""
        # Confirm that controller select API response contains the following fields:
        # `tdmrf_rxfreq_0`, `tdmrf_txfreq_0`, `tdmrf_rxfreq_1`, `tdmrf_txfreq_1`, `modulator_txlvl`,
        # `tdmaproto_slotsnum`, `modulator_txon`, `modem_id`, `enabled`.

        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_xml(
            f"""<?xml version="1.0"?>
            <xml>
                <request>
                    <object>controller</object>
                    <action>select</action>
                    <id>{self.ctrl_id}</id>
                </request>
            </xml>""",
        )
        self.assertTrue(result, 'Controller select API')
        if warnings is not None:
            for _, warning in warnings.items():
                self.warning(warning)
        for value in self.options.get('controller_values'):
            with self.subTest(value=value):
                self.assertIn(value, data.keys())

    def test_satellite_select(self):
        """2. Check current settings Satellite"""
        # Confirm that satellite select API response contains the following field:
        # `id`, `name`, `longitude`, `longitude_deg`, `longitude_min`, `longitude_dir`

        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_xml(
            f"""<?xml version="1.0"?>
            <xml>
                <request>
                    <object>satellite</object>
                    <action>select</action>
                    <id>{self.sat_id}</id>
                </request>
                <data><longitude>60.25</longitude></data>
            </xml>""",
        )
        self.assertTrue(result, 'Satellite select API')
        if warnings is not None:
            for _, warning in warnings.items():
                self.warning(warning)
        for value in self.options.get('satellite_values'):
            with self.subTest(value=value):
                self.assertIn(value, data.keys())
        self.assertEqual('60.25', data.get('longitude'))

    def test_controller_update_sr(self):
        """3. Update Controller Symbol rate(ksps)"""
        # Confirm that controller update API `tdmrf_symrate` updates the symbol rate.
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_xml(
            f"""<?xml version="1.0"?>
            <xml>
                <request>
                    <object>controller</object>
                    <action>update</action>
                    <id>{self.ctrl_id}</id>
                </request>
                <data>
                    <tdmrf_symrate>1423</tdmrf_symrate>
                </data>
            </xml>""",
        )
        if warnings is not None:
            for _, warning in warnings.items():
                self.warning(warning)
        self.assertTrue(result, 'Controller update API `tdmrf_symrate`')
        # Getting the data after changing the symbol rate
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_json(
            obj_name="controller", action="select", obj_id=self.ctrl_id
        )
        self.assertIn(data.get('tdmrf_symrate'), (1423, '1423'))

    def test_controller_update_fec(self):
        """4. Update Controller FEC (`tdmrf_fec`)"""
        # Confirm that controller update API `tdmrf_fec` updates the FEC.

        for i in (1, 2, 3, 4, 7, 8, 11, 12):
            result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_xml(
                f"""<?xml version="1.0"?>
                <xml>
                    <request>
                        <object>controller</object>
                        <action>update</action>
                        <id>{self.ctrl_id}</id>
                    </request>
                    <data>
                        <tdmrf_fec>{i}</tdmrf_fec>
                    </data>
                </xml>""",
            )
            if warnings is not None:
                for _, warning in warnings.items():
                    self.warning(warning)
            self.assertTrue(result, f'Controller update API `tdmrd_fec` value={i}')
            # Getting the data after changing FEC
            result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_json(
                obj_name="controller", action="select", obj_id=self.ctrl_id
            )
            with self.subTest(f'Confirm setting symbol rate value={i}'):
                self.assertIn(data.get('tdmrf_fec'), (i, str(i)))

    def test_controller_update_rxfreq(self):
        """5. Update Controller Receive frequency(kHz) (`tdmrf_rxfreq`)"""
        # Confirm that controller update API `tdmrf_rxfreq` updates the RX frequency.

        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_xml(
            f"""<?xml version="1.0"?>
                <xml>
                    <request>
                        <object>controller</object>
                        <action>update</action>
                        <id>{self.ctrl_id}</id>
                    </request>
                    <data>
                        <tdmrf_rxfreq_0>1011220</tdmrf_rxfreq_0>
                    </data>
                </xml>""",
        )
        if warnings is not None:
            for _, warning in warnings.items():
                self.warning(warning)
        self.assertTrue(result, 'Controller update API `tdmrd_rxfreq_0`')
        # Getting the data after changing the RX frequency
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_json(
            obj_name="controller", action="select", obj_id=self.ctrl_id
        )
        self.assertIn(data.get('tdmrf_rxfreq_0'), (1011220, '1011220'))

    def test_controller_update_multiple_rxfreq(self):
        """6. Update Controller multiple Receive frequency(kHz) (`tdmrf_rxfreq`)"""
        # Confirm that controller update API multiple `tdmrf_rxfreq` updates the RX frequencies.

        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_xml(
            f"""<?xml version="1.0"?>
                <xml>
                    <request>
                        <object>controller</object>
                        <action>update</action>
                        <id>{self.ctrl_id}</id>
                    </request>
                    <data><tdmrf_rxfreq_0>1020500</tdmrf_rxfreq_0>
                    <tdmrf_rxfreq_1>1030500</tdmrf_rxfreq_1></data>
                </xml>""",
        )
        if warnings is not None:
            for _, warning in warnings.items():
                self.warning(warning)
        self.assertTrue(result, 'Controller update API `tdmrd_rxfreq_0` and `tdmrd_rxfreq_1`')
        # Getting the data after changing multiple RX frequencies
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_json(
            obj_name="controller", action="select", obj_id=self.ctrl_id
        )
        self.assertIn(data.get('tdmrf_rxfreq_0'), (1020500, '1020500'))
        self.assertIn(data.get('tdmrf_rxfreq_1'), (1030500, '1030500'))

    def test_controller_update_txfreq(self):
        """7. Update Controller Transmit frequency (`tdmrf_txfreq_0`)"""
        # Confirm that controller update API `tdmrf_txfreq` updates the TX frequency.
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_xml(
            f"""<?xml version="1.0"?>
                <xml>
                    <request>
                        <object>controller</object>
                        <action>update</action>
                        <id>{self.ctrl_id}</id>
                    </request>
                    <data><tdmrf_txfreq_0>1100201</tdmrf_txfreq_0></data>
                </xml>""",
        )
        if warnings is not None:
            for _, warning in warnings.items():
                self.warning(warning)
        self.assertTrue(result, 'Controller update API `tdmrd_txfreq_0`')
        # Getting the data after changing the TX frequency
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_json(
             obj_name="controller", action="select", obj_id=self.ctrl_id
        )
        self.assertIn(data.get('tdmrf_txfreq_0'), (1100201, '1100201'))

    def test_controller_update_multiple_txfreq(self):
        """8. Update Controller multiple Transmit frequencies (`tdmrf_txfreq_0`, `tdmrf_txfreq_1`)"""
        # Confirm API update multiple `tdmrf_txfreq` TX frequencies.

        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_xml(
            f"""<?xml version="1.0"?>
                <xml>
                    <request>
                        <object>controller</object>
                        <action>update</action>
                        <id>{self.ctrl_id}</id>
                    </request>
                    <data><tdmrf_txfreq_0>1072000</tdmrf_txfreq_0>
                    <tdmrf_txfreq_1>1082000</tdmrf_txfreq_1></data>
                </xml>""",
        )
        if warnings is not None:
            for _, warning in warnings.items():
                self.warning(warning)
        self.assertTrue(result, 'Controller update API `tdmrd_txfreq_0` and `tdmrd_txfreq_0`')
        # Getting the data after changing multiple TX frequencies
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_json(
             obj_name="controller", action="select", obj_id=self.ctrl_id
        )
        with self.subTest('Confirm setting multiple TX frequencies'):
            self.assertIn(data.get('tdmrf_txfreq_0'), (1072000, '1072000'))
            self.assertIn(data.get('tdmrf_txfreq_1'), (1082000, '1082000'))

    def test_controller_update_output_level(self):
        """9. Update Controller Outbound output level（-dB）(`modulator_txlvl`)"""
        # Confirm that controller update API `modulator_txlvl` updates the level.

        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_xml(
            f"""<?xml version="1.0"?>
                <xml>
                    <request>
                        <object>controller</object>
                        <action>update</action>
                        <id>{self.ctrl_id}</id>
                    </request>
                    <data><modulator_txlvl>33.9</modulator_txlvl></data>
                </xml>""",
        )
        if warnings is not None:
            for _, warning in warnings.items():
                self.warning(warning)
        self.assertTrue(result, 'Controller update API `modulator_txlvl`')
        # Getting the data after changing the output level
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_json(
            obj_name="controller", action="select", obj_id=self.ctrl_id
        )
        self.assertIn(data.get('modulator_txlvl'), (33.9, '33.9', 339, '339'))

    def test_satellite_update_longitude(self):
        """10. Update Satellite  location information"""
        # Confirm that satellite update API `longitude` updates the longitude.

        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_xml(
            f"""<?xml version="1.0"?>
                <xml>
                    <request>
                        <object>satellite</object>
                        <action>update</action>
                        <id>{self.sat_id}</id>
                    </request>
                    <data>
                        <longitude>32.1</longitude>
                    </data>
                </xml>""",
        )
        if warnings is not None:
            for _, warning in warnings.items():
                self.warning(warning)
        self.assertTrue(result, 'Satellite update API `longitude`')
        # Getting the data after changing the sat longitude
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_json(
            obj_name="satellite", action="select", obj_id=self.sat_id
        )
        self.assertIn(data.get('longitude'), (32.1, '32.1'))

    def test_controller_update_frame_length(self):
        """11. Update Controller TDMA frame length (`tdmaproto_slotsnum`)"""
        # Confirm that controller update API `tdmaproto_slotsnum` updates the frame length.

        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_xml(
            f"""<?xml version="1.0"?>
                <xml>
                    <request>
                        <object>controller</object>
                        <action>update</action>
                        <id>{self.ctrl_id}</id>
                    </request>
                    <data>
                        <tdmaproto_slotsnum>104</tdmaproto_slotsnum>
                    </data>
                </xml>""",
        )
        if warnings is not None:
            for _, warning in warnings.items():
                self.warning(warning)
        self.assertTrue(result, 'Controller update API `tdmaproto_slotsnum`')
        # Getting the data after changing the frame length
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_json(
            obj_name="controller", action="select", obj_id=self.ctrl_id
        )
        self.assertIn(data.get('tdmaproto_slotsnum'), (104, '104'))

    def test_controller_update_carrier(self):
        """12. Update Controller Carrier ON/OFF (`modulator_txon`)"""
        # Confirm that controller update API `modulator_txon` updates the state of modulator.

        # Getting the current state of the modulator
        # Getting the data after switching ON the carrier
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_json(
            obj_name="controller", action="select", obj_id=self.ctrl_id
        )
        self.assertIn(data.get('modulator_txon'), (0, 1, '0', '1'))
        if str(data.get('modulator_txon')) == '1':
            new_state = 0
        else:
            new_state = 1
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_xml(
            f"""<?xml version="1.0"?>
                <xml>
                    <request>
                        <object>controller</object>
                        <action>update</action>
                        <id>{self.ctrl_id}</id>
                    </request>
                    <data><modulator_txon>{new_state}</modulator_txon></data>
                </xml>
                """,
        )
        if warnings is not None:
            for _, warning in warnings.items():
                self.warning(warning)
        self.assertTrue(result, 'Controller update API `modulator_txon`')
        # Getting the data after switching ON the carrier
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_json(
            obj_name="controller", action="select", obj_id=self.ctrl_id
        )
        self.assertIn(data.get('modulator_txon'), (new_state, str(new_state)))

    def test_controller_update_enable(self):
        """13. Update Controller Controller function ON/OFF (`enable`)"""
        # Confirm that controller update API `enable` updates the controller's enable mode.

        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_json(
            obj_name="controller", action="select", obj_id=self.ctrl_id
        )
        self.assertIn(data.get('enabled'), (0, 1, '0', '1'))
        if str(data.get('enabled')) == '1':
            new_state = 0
        else:
            new_state = 1

        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_xml(
            f"""<?xml version="1.0"?>
                <xml>
                    <request>
                        <object>controller</object>
                        <action>update</action>
                        <id>{self.ctrl_id}</id>
                    </request>
                    <data><enabled>{new_state}</enabled></data>
                </xml>
                """,
        )
        if warnings is not None:
            for _, warning in warnings.items():
                self.warning(warning)
        self.assertTrue(result, 'Controller update API `enable`')
        # Getting the data after changing the enable mode
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_json(
            obj_name="controller", action="select", obj_id=self.ctrl_id
        )
        self.assertIn(data.get('enabled'), (new_state, str(new_state)))

    def test_controller_update_modem_id(self):
        """14. Update Controller Select Model for hardware (`modem_id`)"""
        # Confirm that controller update API `modem_id` updates the controller's modem.

        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_xml(
            f"""<?xml version="1.0"?>
                <xml>
                    <request>
                        <object>controller</object>
                        <action>update</action>
                        <id>{self.ctrl_id}</id>
                    </request>
                    <data><modem_id>{self.modem2_id}</modem_id></data>
                </xml>
                """,
        )
        if warnings is not None:
            for _, warning in warnings.items():
                self.warning(warning)
        self.assertTrue(result, 'Controller update API `modem_id`')
        # Getting the data after changing the modem_id
        result, error, obj_id, data, warnings = RikeiNmsSyntaxCase.post_request_json(
            obj_name="controller", action="select", obj_id=self.ctrl_id
        )
        self.assertIn(data.get('modem_id'), (str(self.modem2_id), int(self.modem2_id)))

    @classmethod
    def post_request_json(cls, obj_name='network', action='select', obj_id='0', **params):
        error = ''
        _obj_id = None
        result = False
        data = None
        warnings = None
        if cls.nms35:
            payload = {
                    "request": {
                        "object": obj_name,
                        "action": action,
                        "id": obj_id
                    },
                    "data": params.get('params', {})
                }
        else:
            payload = {
                "object": obj_name,
                "action": action,
                "id": obj_id,
                "params": params.get('params', {})
            }
        resp = requests.post(
            f'http://{cls.nms_ip_address}/jsonapi/?token={cls.nms_token}&out=json',
            data=json.dumps(payload)
        )
        if HTTPStatus.OK != resp.status_code:
            error = F"{resp.status_code} : {resp.reason}"
        elif 0 == len(resp.content):
            error = 'Empty response body'
        else:
            try:
                result_obj = json.loads(resp.content)
                if result_obj.get('result').get('errno') == 0 or result_obj.get('result').get('errno') == '0':
                    result = True
                    data = result_obj.get('data')
                    _obj_id = result_obj.get('result').get('id', None)
                    if result_obj.get('warnings', None) is not None:
                        warnings = result_obj.get('warnings')
                else:
                    error = result_obj.get('result').get('message')
            except JSONDecodeError:
                error = 'Invalid json in response'
            except KeyError:
                error = 'Not found error_code in response'
        return result, error, _obj_id, data, warnings

    @classmethod
    def post_request_xml(cls, payload):
        error = ''
        obj_id = None
        result = False
        data = None
        warnings = None
        headers = {'Content-Type': 'application/xml'}
        resp = requests.post(
            f'http://{cls.nms_ip_address}/xmlapi/?token={cls.nms_token}&out=xml',
            data=payload,
            headers=headers
        )
        if HTTPStatus.OK != resp.status_code:
            error = F"{resp.status_code} : {resp.reason}"
        elif 0 == len(resp.content):
            error = 'Empty response body'
        else:
            try:
                ordered_dict = xmltodict.parse(resp.content)
                result_obj = json.loads(json.dumps(ordered_dict)).get('xml')
                if result_obj.get('result').get('errno') == 0 or result_obj.get('result').get('errno') == '0':
                    result = True
                    data = result_obj.get('data')
                    obj_id = result_obj.get('result').get('id', None)
                    if result_obj.get('warnings', None) is not None:
                        warnings = result_obj.get('warnings')
                else:
                    error = result_obj.get('result').get('message')
            except JSONDecodeError:
                error = 'Invalid json in response'
            except KeyError:
                error = 'Not found error_code in response'
        return result, error, obj_id, data, warnings

    @classmethod
    def login(cls):
        cls.driver.driver.get(f'{cls.driver.address}/{WEB_LOGIN_PATH}/')
        cls.driver.set_value('login[login]', cls.options.get('nms_username'))
        cls.driver.set_value('login[password]', cls.options.get('nms_password'))
        cls.driver.driver.find_element_by_xpath('//button[normalize-space()="Login"]').click()
        sleep(1)

    @classmethod
    def get_nms_version(cls):
        cls.driver.load_data(path='/#/maintenance/')
        version = cls.driver._get_element_by(By.XPATH, '//p[contains(text(), "Version")]')
        if version is None:
            raise ObjectNotFoundException('Cannot find NMS SW version')
        version_number = version.find_element_by_tag_name('span')
        return version_number.text

    @classmethod
    def tear_down_class(cls) -> None:
        if cls.ctrl_id is not None:
            cls.delete_object('controller', cls.ctrl_id)
        if cls.net_id is not None:
            cls.delete_object('network', cls.net_id)
        if cls.modem_id is not None:
            cls.delete_object('modem', cls.modem_id)
        if cls.modem2_id is not None:
            cls.delete_object('modem', cls.modem2_id)
        if cls.rffeed_id is not None:
            cls.delete_object('rffeed', cls.rffeed_id)
        if cls.sat_id is not None:
            cls.delete_object('satellite', cls.sat_id)
        if cls.tp_id is not None:
            cls.delete_object('teleport', cls.tp_id)

    @classmethod
    def delete_object(cls, obj_name, obj_id):
        cls.post_request_json(
            obj_name=obj_name,
            action='delete',
            obj_id=obj_id
        )
