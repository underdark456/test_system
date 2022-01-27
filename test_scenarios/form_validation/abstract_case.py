from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.exceptions import NoSuchParamException
from src.options_providers.options_provider import OptionsProvider
from src.values_presenters import CHECK_BOX_TEST_VALUES_ENABLE

options_path = "test_scenarios.form_validation"


class _AbstractCase(CustomTestCase):
    test_values = {}
    valid_values = {}
    options = {}
    _driver = None
    _object = None

    @classmethod
    def _init_params(cls, options):
        cls._driver = DriversProvider.get_driver_instance(OptionsProvider.get_connection(options_path))
        cls.test_values = options.get('test_values')
        cls.valid_values = options.get('valid_values')
        cls.first_values = options.get('first_values')
        cls.second_values = options.get('second_values')
        cls.checkboxes = options.get('checkboxes')

    @classmethod
    def set_up_class(cls):
        options = OptionsProvider.get_options(options_path)
        cls._init_params(options)

    def _test_validate_fields(self):
        if len(self.test_values) == 0:
            self.fail(F'Empty testing values')

        for field_name, values in self.test_values.items():
            valid_values = self.valid_values.get(field_name)
            if len(values) == 0:
                self.fail(F'Empty testing values list for {field_name}')
            for value in values:
                with self.subTest(field_name, field_name=field_name, value=value):
                    # для не валидных значений выпадающих списов нужно пропускать сравнение значений
                    skip_equal = False
                    try:
                        self.dbg(f'Value={value}')
                        self._object.send_param(field_name, value)
                        has_error = self._object.has_param_error(field_name)
                        new_value = self._object.read_param(field_name)
                        self.dbg(f'new value={new_value}')
                        equal = self._compare_values(new_value, value)
                    except NoSuchParamException:
                        has_error = True
                        skip_equal = True
                    if value in valid_values:
                        self.assertFalse(has_error,
                                         F"Valid {field_name} value {type(value)} {value} not applied"
                                         )
                        if not skip_equal:
                            msg = F"{field_name} not equal, sent {type(value)} {value}" \
                                  F" returned {type(new_value)} {new_value}"
                            self.assertTrue(equal, msg)
                    else:
                        self.assertTrue(has_error,
                                        F"Invalid {field_name} value {type(value)} {value} is applied"
                                        )
                        # skip_equal or self.assertTrue(equal, cmp_msg)

    def _validate_checkboxes(self):
        if len(self.checkboxes) == 0:
            self.fail(f'Empty checkboxes test values')
        for field_name, values in self.checkboxes.items():
            for value in values:
                with self.subTest(field_name, field_name=field_name, value=value):
                    try:
                        self._object.send_param(field_name, value)
                        has_error = self._object.has_param_error(field_name)
                        new_value = self._object.read_param(field_name)
                        equal = self._compare_checkbox_values(new_value, value)
                    except NoSuchParamException:
                        has_error = True
                    self.assertFalse(
                        has_error,
                        f'`{field_name}` value {type(value)} {value} not applied'
                    )
                    msg = f'`{field_name}` not equal, sent {type(value)} {value} returned {type(new_value)} {new_value}'
                    self.assertTrue(equal, msg)

    def _compare_values(self, new, old):
        try:
            if bool == type(new):
                return new == bool(old)
            # Handle returned 'ON ' with a space at the end
            elif str == type(new):
                return new.strip() == old
            elif float == type(new):
                return float(new) == float(old)
            else:
                return new == old
        except ValueError:
            return str(new) == str(old)

    def _compare_checkbox_values(self, new_value, sent_value):
        if sent_value in CHECK_BOX_TEST_VALUES_ENABLE:
            if isinstance(new_value, str) and new_value.strip() == 'ON' or new_value.strip() == 'on':
                return True
            return False
        else:
            if isinstance(new_value, str) and new_value.strip() == 'OFF' or new_value.strip() == 'off':
                return True
            return False

    def _test_depending_values(self):
        """Test two depending parameters where the second one must be greater or equal to the first parameter"""
        if self.first_values is None or self.second_values is None:
            self.fail(f'Empty testing values')
        if len(self.first_values) != len(self.second_values):
            self.fail(f'Depending values\' dicts must be of equal size')

        first_param = list(self.first_values.keys())[0]
        first_valid_values = self.valid_values.get(first_param)
        second_param = list(self.second_values.keys())[0]
        second_valid_values = self.valid_values.get(second_param)

        for i in range(len(self.first_values[first_param])):
            first_value = self.first_values[first_param][i]
            second_value = self.second_values[second_param][i]
            with self.subTest(f'{first_param}={first_value} '
                              f'{second_param}={second_value}'):
                # Probably catch NoSuchParamException?
                self._object.send_params({
                    first_param: first_value,
                    second_param: second_value,
                })
                has_error1 = self._object.has_param_error(first_param)
                has_error2 = self._object.has_param_error(second_param)

                if first_value not in first_valid_values:
                    self.assertTrue(has_error1, f'Invalid {first_param} value {type(first_value)}'
                                                f' {first_value} is applied')

                if second_value not in second_valid_values:
                    self.assertTrue(has_error2, f'Invalid {second_param} value {type(second_value)}'
                                                f' {second_value} is applied')

                if first_value in first_valid_values and second_value in second_valid_values \
                        and second_value < first_value:
                    self.assertTrue(has_error2, f'{first_param} value {first_value} bigger than '
                                                f'{second_param} value {second_value} is applied')

                else:
                    if first_value in first_valid_values:
                        self.assertFalse(has_error1, f'Valid {first_param} value {type(first_value)}'
                                                     f' {first_value} is not applied')
                    if second_value in second_valid_values:
                        self.assertFalse(has_error2, f'Valid {second_param} value {type(second_value)}'
                                                    f' {second_value} is not applied')

                    if first_value in first_valid_values and second_value in second_valid_values:
                        new_first_value = self._object.read_param(first_param)
                        new_second_value = self._object.read_param(second_param)

                        equal1 = self._compare_values(new_first_value, first_value)
                        equal2 = self._compare_values(new_second_value, second_value)

                        msg = f'{first_param} not equal, sent {type(first_value)} {first_value} ' \
                              f'returned {type(new_first_value)} {new_first_value}'
                        self.assertTrue(equal1, msg)

                        msg = f'{second_param} not equal, sent {type(second_value)} {second_value} ' \
                              f'returned {type(new_second_value)} {new_second_value}'
                        self.assertTrue(equal2, msg)
