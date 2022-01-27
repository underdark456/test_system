import os


def load_tests(loader, standard_tests, pattern):
    if pattern is None:
        pattern = "test*.py"
    # top level directory cached on loader instance
    this_dir = os.path.dirname(__file__)
    print(this_dir)
    package_tests = loader.discover(start_dir=this_dir, pattern=pattern)
    standard_tests.addTests(package_tests)
    return standard_tests
