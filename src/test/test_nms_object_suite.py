import unittest
from unittest.mock import patch

from src.constants import NEW_OBJECT_ID
from src.exceptions import ObjectNotFoundException, InvalidIdException
from src.nms_entities.basic_entities.network import Network

DEFINED_OBJECT_ID = 1


@patch('src.drivers.http.nms_web_driver.NmsWebDriver')
class NmsObjectSuite(unittest.TestCase):

    def set_up(self):
        pass

    def test_load_undefined_object(self, driver):
        driver.reset_mock()
        driver.load_data.side_effect = ObjectNotFoundException
        with self.assertRaises(ObjectNotFoundException, msg='Exception not raises for undefined object'):
            Network(driver, 1, DEFINED_OBJECT_ID, {"some_param": 1})

    def test_expected_load(self, driver):
        driver.reset_mock()
        Network(driver, 1, DEFINED_OBJECT_ID, {"some_param": 1})
        driver.load_data.assert_called_once()

    def test_not_expected_load(self, driver):
        driver.reset_mock()
        Network(driver, 1, NEW_OBJECT_ID)
        driver.load_data.assert_not_called()

        Network(driver, 1, 1)
        driver.load_data.assert_not_called()

    def test_apply_loaded_data(self, driver):
        driver.reset_mock()
        params = {'a': 1, 'b': 2, 'c': '3', 'd': 'asd'}

        def get_data(key_name):
            return params[key_name]

        driver.get_value.side_effect = get_data
        n = Network(driver, 1, DEFINED_OBJECT_ID, dict.fromkeys(params.keys()))
        with self.subTest():
            for key, value in params.items():
                self.assertEqual(n.get_param(key), params[key])

    def test_fail_load_for_new_object(self, driver):
        driver.reset_mock()
        n = Network(driver, 1, NEW_OBJECT_ID)
        with self.assertRaises(InvalidIdException):
            n.load()

        # raise not expected for exists objects
        n = Network(driver, 1, DEFINED_OBJECT_ID)
        n.load()

    def test_only_one_load_call(self, driver):
        driver.reset_mock()
        driver.get_current_path.side_effect = lambda: 'form/edit/network=1'
        driver.load_data.assert_not_called()
        n = Network(driver, 1, DEFINED_OBJECT_ID, {"a": 1})
        driver.load_data.assert_called_once()
        n.set_param('a', 2)
        driver.load_data.assert_called_once()

    def test_some_load_calls(self, driver):
        driver.reset_mock()
        driver.load_data.assert_not_called()
        n = Network(driver, 1, DEFINED_OBJECT_ID, {"a": 1})
        driver.load_data.assert_called_once()
        n.set_param('a', 2)
        self.assertEqual(2, driver.load_data.call_count)

    def test_call_driver_set_value(self, driver):
        driver.reset_mock()
        n = Network(driver, 1, NEW_OBJECT_ID)
        driver.set_value.assert_not_called()
        n.set_param('a', 1)
        driver.set_value.assert_called_once()
        n.set_param('b', 2)
        self.assertEqual(2, driver.set_value.call_count)

    def test_not_has_id_before_save(self, driver):
        driver.reset_mock()
        n = Network(driver, 1, NEW_OBJECT_ID)
        self.assertIsNone(n.get_id())

    def test_has_id_after_save(self, driver):
        driver.reset_mock()
        driver.create_object = lambda: 1
        n = Network(driver, 1, NEW_OBJECT_ID)
        self.assertIsNone(n.get_id())
        n.save()
        self.assertEqual(1, n.get_id())
