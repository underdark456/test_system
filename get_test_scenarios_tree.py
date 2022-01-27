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


def _process_suite(suite, full_path):
    if hasattr(suite, '__iter__'):
        for x in suite:
            _process_suite(x, full_path)
    else:
        print(suite)
        data = str(suite)
        data_parts = data.split(' ')
        test_name = data_parts[0]
        class_path = 'test_scenarios.' + data_parts[1].strip('()')
        test_class = import_class(class_path)
        if full_path:
            class_hash = class_path + '_|_' + str(test_class.__doc__).strip()
        else:
            class_hash = test_class.__name__ + '_|_' + str(test_class.__doc__).strip()
        if class_hash not in _tests_dict:
            _tests_dict[class_hash] = list()
        _tests_dict[class_hash].append(
            {
                'name': test_name,
                'doc': getattr(test_class, test_name).__doc__
            }
        )
        # print(F"{test_name} : {class_path} : {getattr(test_class, test_name).__doc__}")


def save_tests_list(include_test_methods=True, full_path=True):
    loader = InjectionContainer.get_loader()
    with _suppress_stdout():
        suite = loader.discover('test_scenarios', pattern="case_*.py")
    _process_suite(suite, full_path)
    max_len = 0
    max_len_class = 0
    for test_suite, test_data in _tests_dict.items():
        if max_len_class < len(test_suite.split('_|_')[0]):
            max_len_class = len(test_suite.split('_|_')[0])
        for test in test_data:
            if max_len < len(test['name']):
                max_len = len(test['name'])
    if include_test_methods:
        filename = 'test_scenarios_detailed.txt'
    else:
        filename = 'test_scenarios.txt'

    with open(filename, 'w') as file:
        for test_suite, test_data in _tests_dict.items():
            suite_name, suite_doc = test_suite.split('_|_')
            spaces = max_len - len(test_suite.split('_|_')[0])
            file.write(f'{suite_name} {spaces * " "} {suite_doc}\n')
            if include_test_methods:
                for test in test_data:
                    spaces = max_len - len(test['name'])
                    file.write(F"  {test['name']} {spaces * ' '} {test['doc']}\n")


if __name__ == '__main__':
    # save_tests_list(include_test_methods=False, full_path=False)
    save_tests_list(include_test_methods=False, full_path=False)
