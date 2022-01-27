import os.path
from importlib import import_module

from src.drivers.drivers_provider import DriversProvider
from src.options_providers.options_provider import OptionsProvider, API_CONNECT


def create_all():
    connection_options = OptionsProvider.get_connection('global_options', API_CONNECT)
    api = DriversProvider.get_driver_instance(connection_options)
    files = os.listdir(os.path.dirname(__file__))
    for file in files:
        if file.startswith('create'):
            print(f'Running create config for {file}')
            module = import_module(file[:-3])
            try:
                module.create_config(driver=api)
            except Exception as exc:
                print(f'Create config unsuccessful for {file}, reason: {exc}')
            print('#########################')


if __name__ == '__main__':
    create_all()
