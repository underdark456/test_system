import os
import sys
from contextlib import contextmanager
from importlib import import_module

from src.injection_container import InjectionContainer

_tests_dict = {}


def import_class(class_path):
    tmp = class_path.split('.')
    class_name = tmp[-1]
    del tmp[-1]
    module = import_module('.'.join(tmp))
    if module is not None and hasattr(module, class_name):
        return getattr(module, class_name)


@contextmanager
def _suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout


def _process_suite(suite):
    if hasattr(suite, '__iter__'):
        for x in suite:
            _process_suite(x)
    else:
        data = str(suite)
        data_parts = data.split(' ')
        test_name = data_parts[0]
        class_path = 'test_scenarios.' + data_parts[1].strip('()')
        test_class = import_class(class_path)
        class_hash = class_path + '_|_' + str(test_class.__doc__).strip()
        if class_hash not in _tests_dict:
            _tests_dict[class_hash] = list()
        _tests_dict[class_hash].append(
            {
                'name': test_name,
                'doc': getattr(test_class, test_name).__doc__
            }
        )
        # print(F"{test_name} : {class_path} : {getattr(test_class, test_name).__doc__}")


def print_tests_list():
    loader = InjectionContainer.get_loader()
    with _suppress_stdout():
        suite = loader.discover('test_scenarios', pattern="case_*.py")
    _process_suite(suite)
    max_len = 0
    for test_suite, test_data in _tests_dict.items():
        for test in test_data:
            if max_len < len(test['name']):
                max_len = len(test['name'])
    for test_suite, test_data in _tests_dict.items():
        suite_name, suite_doc = test_suite.split('_|_')
        print('\n', suite_name)
        print('     ', suite_doc)
        for test in test_data:
            spaces = max_len - len(test['name'])
            print(F"  {test['name']} {spaces * ' '} {test['doc']}")


if __name__ == '__main__':
    print_tests_list()
