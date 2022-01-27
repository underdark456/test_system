import ipaddress
import time

from selenium.webdriver.common.by import By
from src import nms_api, test_api
from src.drivers.drivers_provider import DriversProvider
from src.enum_types_constants import StationModes, RouteTypes
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT
from utilities.network_up.mf_hub_1stn_up import MfHub1StnUp

backup_name = 'default_config.txt'
options_path = 'test_scenarios.web.realtime'


class WebRealtimeCase(MfHub1StnUp):
    """WEB Realtime page for MF_hub and stn: start of output of buttons, refresh, direct command (ticket 8254)"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.25'
    __execution_time__ = 455  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        super().set_up_class()

        # Adding dummy stations to fill controller UHP tables
        nms_api.update('controller:0', {'stn_number': 2040})
        for i in range(2, 2040):
            nms_api.create('vno:0', 'station', {
                'name': f'stn{i}',
                'enable': False,
                'serial': i,
                'mode': StationModes.STAR,
                'rx_controller': 'controller:0'
            })
        if not nms_api.wait_up('controller:0', timeout=60):
            test_api.error('Controller is not Up after adding dummy stations and setting stn_number to 2040')
        if not nms_api.wait_up('station:0', timeout=60):
            test_api.error('Station1 is not Up after adding dummy stations and setting stn_number to 2040')

        cls.web_driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT),
            driver_id='case_web_realtime',
            store_driver=False
        )
        cls.options = OptionsProvider.get_options(options_path)

    def test_controller_refresh(self):
        """Controller Realtime refresh checkbox should trigger auto update of output"""
        self.check_refresh(entity='controller', tick_to_wait=1)

    def test_station_refresh(self):
        """Station Realtime refresh checkbox should trigger auto update of output"""
        self.check_refresh(entity='station', tick_to_wait=1)

    def test_controller_realtime(self):
        """Controller Realtime output of pressed buttons (all except for config section)"""
        self.check_realtime_output(entity='controller', tick_to_wait=1)

    def test_station_realtime(self):
        """Station Realtime output of pressed buttons (all except for config section)"""
        self.check_realtime_output(entity='station', tick_to_wait=1)

    def test_controller_direct_command(self):
        """Controller Realtime direct command send"""
        self.check_direct_command(entity='controller', tick_to_wait=1)

    def test_station_direct_command(self):
        """Station Realtime direct command send"""
        self.check_direct_command(entity='station', tick_to_wait=1)

    def check_realtime_output(self, entity='controller', tick_to_wait=1):
        rt_path = PathsManager._REALTIME.format(entity, '0')
        self.web_driver.load_data(rt_path)
        for key, value in self.options.get('realtime').items():
            if entity == 'station' and key in ('stations', 'stations rf', 'stations tr'):
                continue
            element_id = value.get('command')
            element = self.web_driver._get_element_by(By.ID, element_id)
            if not element:
                self.fail(f'Button id={element_id} cannot be located in Realtime')
            self.assertEqual(key.lower(), element.text.lower(), msg=f'Button id={element_id} text is not {key.lower()}')
            element.click()
            # Checking output of the realtime text field after some waiting for the response
            nms_api.wait_ticks(tick_to_wait)
            output = self.web_driver._get_element_by(By.CLASS_NAME, 'realtime__text')
            if not output:
                self.fail(f'Cannot locate realtime text element after clicking {element_id} button')
            self.assertTrue(
                output.text.startswith(value.get('startswith')),
                msg=f'Output of the {element_id} button does not starts with {value.get("startswith")}')

        # Checking presence of setting buttons
        for key, value in self.options.get('realtime_set').items():
            element_id = value.get('command')
            element = self.web_driver._get_element_by(By.ID, element_id)
            if not element:
                self.fail(f'Button id={element_id} cannot be located in Realtime')
            self.assertEqual(key.lower(), element.text.lower(), msg=f'Button id={element_id} text is not {key.lower()}')

    def check_refresh(self, entity='controller', tick_to_wait=1):
        rt_path = PathsManager._REALTIME.format(entity, '0')
        self.web_driver.load_data(rt_path)
        lan = self.web_driver._get_element_by(By.ID, 'show int eth')
        if not lan:
            self.fail('Cannot locate lan button for refresh test')
        lan.click()
        nms_api.wait_ticks(tick_to_wait)
        output = self.web_driver._get_element_by(By.CLASS_NAME, 'realtime__text')
        if not output:
            self.fail(f'Cannot locate realtime text element for refresh test')
        initial_value = output.text
        refresh = self.web_driver._get_element_by(By.ID, 'refreshCheckbox')
        if not refresh:
            self.fail('Cannot locate refresh checkbox')
        refresh.click()
        time.sleep(tick_to_wait * 5)
        output = self.web_driver._get_element_by(By.CLASS_NAME, 'realtime__text')
        if not output:
            self.fail(f'Cannot locate realtime text element for refresh test')
        refreshed_value = output.text
        self.assertNotEqual(initial_value, refreshed_value, msg=f'lan output has not been changed')

        refresh_500 = self.web_driver._get_element_by(By.ID, '500DelayCheckbox')
        if not refresh_500:
            self.fail('Cannot locate refresh 500 radio button')
        refresh_1000 = self.web_driver._get_element_by(By.ID, '1000DelayCheckbox')
        if not refresh_1000:
            self.fail('Cannot locate refresh 1000 radio button')
        refresh_3000 = self.web_driver._get_element_by(By.ID, '3000DelayCheckbox')
        if not refresh_3000:
            self.fail('Cannot locate refresh 3000 radio button')

    def check_direct_command(self, entity='controller', tick_to_wait=1):
        rt_path = PathsManager._REALTIME.format(entity, '0')
        self.web_driver.load_data(rt_path)
        input_field = self.web_driver._get_element_by(By.ID, 'realtimeDirectCommandInput')
        if not input_field:
            self.fail(f'Cannot locate realtime direct command input field')
        input_field.send_keys('show system')
        send_btn = self.web_driver._get_element_by(By.ID, 'sendButton')
        if not send_btn:
            self.fail(f'Cannot locate send button')
        send_btn.click()
        nms_api.wait_ticks(tick_to_wait)
        output = self.web_driver._get_element_by(By.CLASS_NAME, 'realtime__text')
        if not output:
            self.fail(f'Cannot locate realtime text element for direct command test')
        self.assertTrue(output.text.startswith('UHP-'), msg=f'Expected LAN output after sending `show system`')
