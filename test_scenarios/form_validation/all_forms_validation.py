import test_scenarios.form_validation.subtests as subtests
from src.custom_test_case import CustomTestCase
from src.drivers.drivers_provider import DriversProvider
from src.injection_container import InjectionContainer
from src.options_providers.options_provider import OptionsProvider
from utilities.create_typical_nms_config.basic_nms_config import create_basic_nms_config

option_path = "test_scenarios.form_validation"


class FormValidationRunner(CustomTestCase):
    @classmethod
    def set_up_class(cls):
        create_basic_nms_config()
        cls.options = OptionsProvider.get_options(option_path)

    def test_run_all_tests_in_subtests(self):
        """Run all tests in folder subtests"""
        loader = InjectionContainer.get_loader(option_path)
        suite = loader.loadTestsFromModule(subtests)
        runner = InjectionContainer.get_runner(option_path)
        runner.run(suite)

    def test_all_forms_validation(self):
        """All forms validation test"""
        loader = InjectionContainer.get_loader(option_path)
        runner = InjectionContainer.get_runner(option_path)
        subtests_path = 'test_scenarios.form_validation.subtests.'
        suite = loader.loadTestsFromNames([
            # 'test_scenarios.form_validation.subtests.access',
            F'{subtests_path}vno.test_vno_form',
            F'{subtests_path}mf_hub.test_mf_hub_form',
        ])
        print(suite)
        runner.run(suite)
