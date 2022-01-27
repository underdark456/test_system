import unittest

from runtest import TextTestRunner
from src.options_providers.options_provider import OptionsProvider


class InjectionContainer(object):
    @classmethod
    def get_loader(cls, options_path='global_options'):
        loader = OptionsProvider.get_system_options(options_path, 'loader')
        if loader is None:
            loader = unittest.TestLoader()
        return loader

    @classmethod
    def get_runner(cls, options_path='global_options'):
        runner = OptionsProvider.get_system_options(options_path, 'runner')
        if runner is None:
            runner = TextTestRunner(verbosity=1, failfast=False)
        return runner
