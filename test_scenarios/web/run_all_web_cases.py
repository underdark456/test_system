import os

import test_scenarios.web as subtests
from src.injection_container import InjectionContainer

option_path = "test_scenarios"

if __name__ == '__main__':
    loader = InjectionContainer.get_loader(option_path)
    suite = loader.loadTestsFromModule(subtests)
    runner = InjectionContainer.get_runner(option_path)
    runner.run(suite, suite_name=__file__.split(os.sep)[-1])
