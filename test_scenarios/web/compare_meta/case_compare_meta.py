import json
import os

from global_options.options import PROJECT_DIR
from src.backup_manager.backup_manager import BackupManager
from src.constants import NO_ERROR
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.exceptions import NoSuchParamException
from src.nms_entities.basic_entities.nms import Nms
from src.options_providers.options_provider import OptionsProvider

options_path = 'test_scenarios.web.compare_meta'
backup_name = 'each_entity.txt'


class CompareMetaCase(CustomTestCase):
    """Compare already existed meta data with the current version meta"""

    __author__ = 'dkudryashov'
    __version__ = '4.0.0.26'
    __execution_time__ = 25

    @classmethod
    def set_up_class(cls):
        cls.driver = DriversProvider.get_driver_instance(
            OptionsProvider.get_connection()
        )
        cls.backup = BackupManager()
        cls.backup.apply_backup(backup_name)

        nms = Nms(cls.driver, 0, 0)
        nms_version = nms.get_param('version').split()[1].replace('.', '_')
        if nms_version is None:
            raise NoSuchParamException('Cannot determine current NMS version')
        prev_nms_version = f'{nms_version[:nms_version.rfind("_")]}_{int(nms_version[nms_version.rfind("_") + 1:]) - 1}'
        try:
            with open(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}meta_{prev_nms_version}.txt',
                      'r') as file:
                cls.meta_version = prev_nms_version
                cls.meta = json.load(file)
        except FileNotFoundError:
            cls.meta_version = '4_0_0_11'
            with open(f'{PROJECT_DIR}{os.sep}utilities{os.sep}get_meta{os.sep}meta_{prev_nms_version}.txt',
                      'r') as file:
                cls.meta = json.load(file)
        cls.class_logger.info(f'Current NMS version {nms_version}, comparing with NMS version {cls.meta_version}')

        options = OptionsProvider.get_options(options_path)
        path = 'api/form/edit/{}=0'
        cls.new_meta = {}
        for entity in options.get('entities'):
            meta_path = path.format(entity)
            reply, error, error_code = cls.driver.custom_get(meta_path)
            if error_code != NO_ERROR or error != '' or reply == '' or reply is None:
                raise Exception(f'Cannot get {entity} meta')
            cls.new_meta[entity] = reply

    def compare_options(self, entity_name, section_key, option):
        for entity_name_test in self.new_meta.keys():
            if entity_name_test == entity_name:
                for sections_json_test in self.new_meta.get(entity_name):
                    for section_key_test, section_value_test in sections_json_test.items():
                        if section_key == section_key_test:
                            for var in section_value_test:
                                for var_key_test, var_value_test in var.items():
                                    if var_key_test == 'select':
                                        for option_test in var_value_test:
                                            if option_test == option:
                                                return True
        return False

    def compare_var(self, entity_name, section_key, var_key, var_value, name):
        for entity_name_test in self.new_meta.keys():
            if entity_name_test == entity_name:
                for sections_json_test in self.new_meta.get(entity_name):
                    for section_key_test, section_value_test in sections_json_test.items():
                        if section_key == section_key_test:
                            for var_test in section_value_test:
                                if var_test.get('name') == name:
                                    for var_key_test, var_value_test in var_test.items():
                                        if var_key == var_key_test and var_value == var_value_test:
                                            return True
        return False

    def compare_simple_var(self, entity_name, section_key, section_value, section_name):
        for entity_name_test in self.new_meta.keys():
            if entity_name_test == entity_name:
                for sections_json_test in self.new_meta.get(entity_name):
                    if sections_json_test.get('section') is not None:
                        section_name_test = sections_json_test.get('section')
                    elif sections_json_test.get('table') is not None:
                        section_name_test = sections_json_test.get('table')
                    else:
                        return False
                    if section_name == section_name_test:
                        for section_key_test, section_value_test in sections_json_test.items():
                            if section_key == section_key_test and section_value == section_value_test:
                                return True
        return False

    def compare_new_options(self, entity_name, section_key, option):
        for entity_name_test in self.meta.keys():
            if entity_name_test == entity_name:
                for sections_json_test in self.meta.get(entity_name):
                    for section_key_test, section_value_test in sections_json_test.items():
                        if section_key == section_key_test:
                            for var in section_value_test:
                                for var_key_test, var_value_test in var.items():
                                    if var_key_test == 'select':
                                        for option_test in var_value_test:
                                            if option_test == option:
                                                return True
        return False

    def compare_new_var(self, entity_name, section_key, var_key, var_value, name):
        for entity_name_test in self.meta.keys():
            if entity_name_test == entity_name:
                for sections_json_test in self.meta.get(entity_name):
                    for section_key_test, section_value_test in sections_json_test.items():
                        if section_key == section_key_test:
                            for var_test in section_value_test:
                                if var_test.get('name') == name:
                                    for var_key_test, var_value_test in var_test.items():
                                        if var_key == var_key_test and var_value == var_value_test:
                                            return True
        return False

    def compare_new_simple_var(self, entity_name, section_key, section_value, section_name):
        for entity_name_test in self.meta.keys():
            if entity_name_test == entity_name:
                for sections_json_test in self.meta.get(entity_name):
                    if sections_json_test.get('section') is not None:
                        section_name_test = sections_json_test.get('section')
                    elif sections_json_test.get('table') is not None:
                        section_name_test = sections_json_test.get('table')
                    else:
                        return False
                    if section_name == section_name_test:
                        for section_key_test, section_value_test in sections_json_test.items():
                            if section_key == section_key_test and section_value == section_value_test:
                                return True
        return False

    def test_new_fields_and_vars(self):
        """Compare all key-value pairs in new meta data according to the reference meta data"""
        for entity_name in self.new_meta.keys():
            # If there is a new entity in new meta data
            self.assertIn(entity_name, self.meta.keys(), msg=f'New meta: entity={entity_name} not in the reference meta')
            for sections_json in self.new_meta.get(entity_name):
                for section_key, section_value in sections_json.items():
                    if section_key == 'vars':
                        for var in section_value:
                            # Skip backup options and script file as their size may differ
                            if var.get('name') in ('load_filename', 'load_bkp_file', 'script_file'):
                                continue

                            for var_key, var_value in var.items():

                                if var_key == 'select':
                                    for option in var_value:
                                        test_ = self.compare_new_options(entity_name, section_key, option)
                                        with self.subTest(f'New meta: entity={entity_name}, param={var.get("name")},'
                                                          f' selector option={option}'):
                                            self.assertTrue(test_, msg='Difference in the reference meta')
                                else:
                                    test_ = self.compare_new_var(entity_name, section_key, var_key, var_value, var.get('name'))
                                    with self.subTest(f'New meta: entity={entity_name}, param={var.get("name")}, '
                                                      f'var_key={var_key}, var_value={var_value}'):
                                        self.assertTrue(test_, msg='Difference in the reference meta')
                    # simple section vars (`from`, `to` etc.)
                    else:
                        if sections_json.get('section') is not None:
                            section_name = sections_json.get('section')
                        elif sections_json.get('table') is not None:
                            section_name = sections_json.get('table')
                        else:
                            self.fail(f'New meta: entity={entity_name}. '
                                      f'Unexpectedly cannot get `section` or `table`')

                        test_ = self.compare_new_simple_var(entity_name, section_key, section_value, section_name)
                        with self.subTest(f'New meta: entity={entity_name}, section={section_name}, '
                                          f'section_key={section_key}, section_value={section_value}'):
                            self.assertTrue(test_, msg='Difference in the reference meta')

    def test_reference_meta(self):
        """Compare all key-value pairs in the reference meta according to the new meta data"""
        # Check all currently existing keys-values pairs in the gotten meta
        for entity_name in self.meta.keys():
            self.assertIn(entity_name, self.new_meta.keys(), msg=f'Reference meta: entity={entity_name} not in new meta')
            for sections_json in self.meta.get(entity_name):
                for section_key, section_value in sections_json.items():
                    if section_key == 'vars':
                        for var in section_value:

                            # Skip backup options and script file as their sizes may differ
                            if var.get('name') in ('load_filename', 'load_bkp_file', 'script_file'):
                                continue

                            for var_key, var_value in var.items():

                                if var_key == 'select':
                                    for option in var_value:
                                        test_ = self.compare_options(entity_name, section_key, option)
                                        with self.subTest(f'Reference meta: entity={entity_name},'
                                                          f' param={var.get("name")}'
                                                          f' selector option={option}'):
                                            self.assertTrue(test_, msg='Difference in new meta')
                                else:
                                    test_ = self.compare_var(entity_name, section_key, var_key, var_value, var.get('name'))
                                    with self.subTest(f'Reference meta: entity={entity_name}, param={var.get("name")} '
                                                      f'var_key={var_key} var_value={var_value}'):
                                        self.assertTrue(test_, msg='Difference in new meta')
                    # simple section vars (`from`, `to` etc.)
                    else:
                        if sections_json.get('section') is not None:
                            section_name = sections_json.get('section')
                        elif sections_json.get('table') is not None:
                            section_name = sections_json.get('table')
                        else:
                            self.fail(f'Reference meta: entity={entity_name}. '
                                      f'Unexpectedly cannot get next `section` or `table` key')

                        test_ = self.compare_simple_var(entity_name, section_key, section_value, section_name)
                        with self.subTest(f'Reference meta: entity={entity_name}, section={section_name}, '
                                          f'section_key={section_key}, section_value={section_value}'):
                            self.assertTrue(test_, msg=f'Difference in new meta')
