import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT


backup_name = 'each_entity.txt'
options_path = 'test_scenarios.web.graph'


class WebGraphCase(CustomTestCase):
    """WEB Graph page for Network, Vno, MF_hub and stn control elements and options (fixed ticket 8329)"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __execution_time__ = 45  # approximate case execution time in seconds
    __express__ = True
    _wait_time_out = 3

    @classmethod
    def set_up_class(cls):
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        time.sleep(5)
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT),
            driver_id='case_web_graph',
            store_driver=False
        )
        cls.options = OptionsProvider.get_options(options_path)
        cls.sidepanel_box_class = cls.options.get('sidepanel_box_class')
        cls.last_statistics = cls.options.get('last_statistics')

    def set_up(self):
        self.driver.expand_tree()

    def test_network(self):
        """Network Graphs control elements check"""
        self.click_element_by_id('net:0')
        self.click_element_by_id('Graphs')
        self.selector_options = [
            self.options.get('first_selector_options_net'),
            self.options.get('second_selector_options_net'),
        ]
        self.check_sidepanel_content()

    def test_controller(self):
        """Controller Graphs control elements check"""
        self.click_element_by_id('chb:0')
        self.click_element_by_id('Graphs')
        self.selector_options = [
            self.options.get('first_selector_options_ctrl'),
            self.options.get('second_selector_options_ctrl'),
        ]
        self.check_sidepanel_content()

    def test_vno(self):
        """Vno Graphs control elements check"""
        self.click_element_by_id('vno:0')
        self.click_element_by_id('Graphs')
        self.selector_options = [
            self.options.get('first_selector_options_vno'),
            self.options.get('second_selector_options_vno'),
        ]
        self.check_sidepanel_content()

    def test_station(self):
        """Station Graphs control elements check"""
        self.click_element_by_id('stn:0')
        self.click_element_by_id('Graphs')
        self.selector_options = [
            self.options.get('first_selector_options_stn'),
            self.options.get('second_selector_options_stn'),
        ]
        self.check_sidepanel_content()

    def check_sidepanel_content(self):
        """Make sure that all expected control elements are in place in side panel"""
        self.check_graph_selects()
        # Last statistics
        for key, value in self.last_statistics.items():
            btn = self.driver._get_element_by(By.ID, key, timeout=self._wait_time_out)
            self.assertIsNotNone(btn, msg=f'Cannot locate last statistics id={key} {value}')
            self.assertEqual(
                value.lower(),
                btn.text.lower(),
                msg=f'Last statistics id={key} expected text={value.lower()}, got {btn.text.lower()}'
            )
            btn.click()
        # Range selection elements
        for key, value in self.options.get('range_selection').items():
            el = self.driver._get_element_by(By.ID, key)
            self.assertIsNotNone(el, msg=f'Cannot locate range selection element {key} {value}')
            el.click()
        # Storage section elements
        for key, value in self.options.get('storage').items():
            el = self.driver._get_element_by(By.ID, key)
            self.assertIsNotNone(el, msg=f'Cannot locate storage element {key} {value}')
            self.assertEqual(value, el.text, msg=f'Expected storage button {key} text {value}, got {el.text}')

    def check_graph_selects(self):
        """Check expected options in graphs' select elements"""
        sidepanel_box = self.driver._get_element_by(
            By.CLASS_NAME,
            self.sidepanel_box_class,
            timeout=self._wait_time_out
        )
        self.assertIsNotNone(sidepanel_box, msg=f'Cannot locate sidepanel box')
        self.driver._get_element_by(By.ID, 'firstSelect', timeout=self._wait_time_out)
        self.driver._get_element_by(By.ID, 'secondSelect', timeout=self._wait_time_out)
        try:
            selectors = [
                sidepanel_box.find_element_by_id('firstSelect'),
                sidepanel_box.find_element_by_id('secondSelect'),
            ]
        except NoSuchElementException:
            self.fail(f'Cannot locate graph type selector')

        for i in range(2):  # Checking and clicking options in both graph selectors
            _id = selectors[i].get_attribute('id')
            selector = Select(selectors[i])
            options = [option.text for option in selector.options]
            self.assertEqual(
                len(self.selector_options[i]),
                len(options),
                msg=f'Expected {len(self.selector_options[i])} {_id} options, got {len(options)}'
            )
            for j in self.selector_options[i]:  # iteration over all expected options in a selector
                self.assertIn(j, options, msg=f'{j} not in {_id} selector options')
                selector.select_by_visible_text(j)
                time.sleep(0.1)
                # Make sure that the graph title corresponds to the expected one
                graph_title_elements = self.driver._get_elements_by(
                    By.CLASS_NAME,
                    self.options.get('graph_title_class'),
                    timeout=self._wait_time_out
                )
                self.assertIsNotNone(graph_title_elements, msg=f'Cannot locate graph title element')
                if i > 0 and j != 'None':
                    self.assertEqual(
                        2,
                        len(graph_title_elements),
                        msg=f'Expected 2 graphs, got {len(graph_title_elements)}'
                    )
                elif j == 'None':
                    continue
                with self.subTest(msg=f'Graph title for graph number {i + 1} expected {j}'):
                    self.assertEqual(
                        j,
                        graph_title_elements[i].text,
                        msg=f'Expected {j} graph title, actual {graph_title_elements[i].text}'
                    )

    def click_element_by_id(self, _id):
        el = self.driver._get_element_by(By.ID, _id, timeout=self._wait_time_out)
        if el is None:
            self.fail(f'WEB element id={_id} cannot be located and clicked at {self.driver.get_current_url()}')
        el.click()
        time.sleep(1)
