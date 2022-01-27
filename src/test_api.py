# Test API
import importlib.util
from importlib import import_module
from src.exceptions import InvalidOptionsException
from src.options_providers.options_provider import OptionsProvider

_OPT = 'options'
_SYS = 'system'


def _init(message: str):
    """Test case initialization entrance point"""
    pass


def fail(self, message: str):
    self.fail(message)


def error(message: str):
    raise InvalidOptionsException(message)


def get_options(options_path):
    """Get and merge options"""
    # _options = _load_config(_OPT, options_path)
    # _system_options = _load_config(_SYS, options_path)
    # _dict_merge(_options, _system_options)
    return OptionsProvider.get_options(options_path)


def get_system_options(options_path):
    """Get merged system options `global options` -> `global local options` -> `test case options` -> test case local"""
    return OptionsProvider.get_system_options(options_path)


def get_nms(options_path=None):
    if options_path is None:
        options_path = 'global_options'
    _system_options = _load_config(_SYS, options_path)
    _nms_options = {'nms_ip': _system_options.get('nms_ip'), 'username': _system_options.get('username', 'admin'),
                    'password': _system_options.get('password', '12345')}
    return _nms_options


def get_uhp(*, number=None, options_path=None):
    """
    Get a list of dictionaries of UHP modem options.
    Sample output:
        [
            {
                'device_ip': '10.56.24.11',
                'device_vlan': 0,
                'device_gateway': '10.56.24.1',
                'serial': 50135501,
                'model': 'UHP200',
                'options': ()},
            },
            { ...
        ]

    :param int number: required number of UHP modems
    :param str options_path: the package name from which the UHP options are loaded
    :returns list _uhp_list: a list containing dictionaries of UHP modems options
    """
    return OptionsProvider.get_uhp(number=number, options_path=options_path)


def get_uhp_by_model(*args, number=None, options_path=None):
    """
    Get a list containing dictionaries of UHP modems with desired hardware models
    >>> get_uhp_by_model('UHP200')
    >>> get_uhp_by_model('UHP200', 'UHP200X', 'UHP100')
    Sample output:
        [
            {
                'device_ip': '10.56.24.11',
                'device_vlan': 0,
                'device_gateway': '10.56.24.1',
                'serial': 50135501,
                'model': 'UHP200',
                'options': ()},
            },
            { ...
        ]

    :param int number: required number of UHP modems
    :param args: desired UHP models in NMS format: `UHP100`, `UHP100X` etc.
    :param str options_path: the package name from which the UHP options are loaded
    :returns list _uhp_list: a list containing dictionaries of UHP modems' options
    """
    return OptionsProvider.get_uhp_by_model(*args, number=number, options_path=options_path)


def get_uhp_controllers_stations(
        ctrl_number: int, ctrl_model: list, stn_number: int, stn_model: list, *, options_path=None, default=True
):
    """
    Get two lists containing UHP modems for controllers and stations
    Sample usage:
    >>> get_uhp_controllers_stations(2, ['UHP200', 'UHP200X'], 3, ['UHP200', 'UHP100'])
    Sample output:
    [
        {
            'device_ip': '10.56.24.11',
            ...
            'options': ()},
        },
        { ...
    ],
    [
        {
            'device_ip': '10.56.24.11',
            ...
            'options': ()},
        },
        { ...
    ]

    :param int ctrl_number: required number of UHP modems which are used as controllers
    :param list ctrl_model: a list of UHP models for controllers
    :param int stn_number: required number of UHP modems which are used as stations
    :param list stn_model: a list of UHP models for stations
    :param str options_path: the package name from which the UHP options are loaded
    :param bool default: apply default settings to all UHPs
    :returns list _ctrl_list, _stn_list: two lists containing dictionaries of UHP modems
    """
    return OptionsProvider.get_uhp_controllers_stations(
        ctrl_number, ctrl_model, stn_number, stn_model, options_path=options_path, default=default
    )


def _load_config(conf_name: str, package_name: str, section: str = None, options: dict = None):
    if options is None:
        options = {}
    _options = _load_and_merge_options("global_options.options", conf_name, options)
    _options = _load_and_merge_options("global_options.local_options", conf_name, _options)
    if package_name is not None:
        module_name = package_name + ".options"
        _options = _load_and_merge_options(module_name, conf_name, _options)
        module_name = package_name + ".local_options"
        _options = _load_and_merge_options(module_name, conf_name, _options)
    if section is not None:
        if section in _options:
            return _options[section]
        else:
            return None
    return _options


def _load_and_merge_options(module_name: str, dict_name: str, options: dict):
    options_module = _load_module(module_name)
    if options_module is not None and hasattr(options_module, dict_name):
        _dict_merge(options, options_module.__getattribute__(dict_name))
    return options


def _load_module(module_name: str):
    module = None
    if importlib.util.find_spec(module_name):
        module = import_module(module_name)
    return module


def _dict_merge(dct: dict, merge_dct: dict):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.
    :param dct: dict onto which the merge is executed
    :param merge_dct: dct merged into dct
    :returns: None
    """
    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], dict)):
            _dict_merge(dct[k], merge_dct[k])
        else:
            dct[k] = merge_dct[k]


if __name__ == '__main__':
    # print(get_uhp_by_model('UHP100', 'UHP200X'))
    print(get_uhp_by_model('UHP200', number=1))
