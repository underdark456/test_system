from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from src.backup_manager.backup_manager import BackupManager
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.nms_entities.paths_manager import PathsManager
from src.options_providers.options_provider import OptionsProvider, CHROME_CONNECT

options_path = 'test_scenarios.web.stations'
backup_name = '10000_stations_in_1_network.txt'


class WebStationsCase(CustomTestCase):
    """WEB stations interface expected elements: table/graph, filters etc. Included clicks"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.27'
    __execution_time__ = 60  # approximate case execution time in seconds
    __express__ = True

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection(options_path, CHROME_CONNECT),
            driver_id='case_web_stations',
            store_driver=False
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)
        cls.options = OptionsProvider.get_options(options_path)
        cls.buttons = cls.options.get('buttons')
        cls.checkboxes = cls.options.get('checkboxes')  # filters checkboxes
        cls.first_select_id = cls.options.get('graph').get('graph_first')
        cls.second_select_id = cls.options.get('graph').get('graph_second')

    def test_network(self):
        """Network stations interface"""
        self.check_stations_interface('network')

    def test_vno(self):
        """Vno stations interface"""
        self.check_stations_interface('vno')
        self.assertIsNotNone(
            self.driver._get_element_by(By.CLASS_NAME, 'seclist__button'),
            msg=f'Cannot locate Group btn'
        )

    def test_controller(self):
        """Controller stations interface"""
        self.check_stations_interface('controller')

    def check_stations_interface(self, parent):
        path = PathsManager._OBJECT_STATION.format(parent, 0)
        self.driver.load_data(path)
        for key, value in self.buttons.items():
            self.assertIsNotNone(
                self.driver._get_element_by(By.ID, value),
                msg=f'No {key} btn for {parent}'
            )
        self.check_quick_filters()
        self.check_filters()
        self.check_graph()

    def check_quick_filters(self):
        for key, value in self.buttons.items():
            if key in ('toggle', 'filters'):
                continue
            next_btn = self.driver._get_element_by(By.ID, value)
            next_btn.click()

    def check_graph(self):
        toggle_btn = self.driver._get_element_by(By.ID, self.options.get('buttons').get('toggle'))
        toggle_btn.click()

        for key, value in self.options.get('graph').items():
            self.assertIsNotNone(
                self.driver._get_element_by(By.ID, value, timeout=2),
                msg=f'No {key} selector (id={value})'
            )

        graph_x_sel = self.driver._get_element_by(By.ID, self.options.get('graph').get('graph_x_axis'))
        selector = Select(graph_x_sel)
        for opt in self.options.get('graph_x_options'):
            selector.select_by_visible_text(opt)

        graph_y1_sel = self.driver._get_element_by(By.ID, self.options.get('graph').get('graph_first'))
        selector = Select(graph_y1_sel)
        for opt in self.options.get('first_select_options'):
            selector.select_by_visible_text(opt)

        graph_y2_sel = self.driver._get_element_by(By.ID, self.options.get('graph').get('graph_second'))
        selector = Select(graph_y2_sel)
        for opt in self.options.get('second_select_options'):
            selector.select_by_visible_text(opt)

    def check_filters(self):
        filters_btn = self.driver._get_element_by(By.ID, self.buttons.get('filters'))
        filters_btn.click()
        for c_text, c_id in self.checkboxes.items():
            el = self.driver._get_element_by(By.ID, c_id)
            el.click()
        self.assertIsNotNone(
            self.driver._get_element_by(By.ID, self.options.get('filters_apply')),
            msg='No Apply for filters'
        )
        self.assertIsNotNone(
            self.driver._get_element_by(By.ID, self.options.get('filters_close')),
            msg='No Close for filters'
        )
        apply_btn = self.driver._get_element_by(By.ID, self.options.get('filters_apply'))
        apply_btn.click()

    def get_all_filters_ids(self):
        # Has been used once to obtain ver.4.0.0.23 filters
        """Get all filters IDs and their respective text"""
        path = PathsManager._OBJECT_STATION.format('vno', 0)
        self.driver.load_data(path)
        filters = self.driver.driver.find_elements_by_class_name('filtersgroups__group')
        for gr in filters:
            ids = gr.find_elements_by_xpath('*[@id]')
            for i in ids:
                inner_div = i.find_element_by_class_name('filtersgroups__title')
                print(f"{inner_div.get_attribute('innerHTML')}: {i.get_attribute('id')},")

    def get_graph_options(self):
        # Has been used once to obtain ver.4.0.0.23 graph options
        """Get all options in graph selectors"""
        path = PathsManager._OBJECT_STATION.format('vno', 0)
        self.driver.load_data(path)
        toggle_btn = self.driver._get_element_by(By.ID, self.options.get('buttons').get('toggle'))
        toggle_btn.click()

        first_select = self.driver._get_element_by(By.ID, self.first_select_id)
        selector = Select(first_select)
        for op in selector.options:
            print(op.text)
        print('#########################')

        second_select = self.driver._get_element_by(By.ID, self.second_select_id)
        selector = Select(second_select)
        for op in selector.options:
            print(op.text)
