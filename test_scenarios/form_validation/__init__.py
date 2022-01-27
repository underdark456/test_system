import os


def load_tests(loader, standard_tests, pattern):
    if pattern is None:
        pattern = "case_*.py"

    this_dir = os.path.dirname(__file__)
    package_tests = loader.discover(start_dir=this_dir, pattern=pattern)
    standard_tests.addTests(package_tests)
    return standard_tests
