import inspect
import logging
import sys
from functools import wraps
from inspect import ismethod, isfunction

from global_options.options import PROJECT_DIR

LOGGING_ENABLED = True

_logger = logging.getLogger('sys_logger')

_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(F'{PROJECT_DIR}system.log', 'w+')
file_format = logging.Formatter(
    fmt='%(asctime)s : %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_format)
_logger.addHandler(file_handler)

_log_methods = ['debug', 'info', 'warning', 'error', 'critical']


def logger_set_level(level):
    _logger.setLevel(level)


def debug(msg, *args, **kwargs):
    if not LOGGING_ENABLED:
        return
    _logger.debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    if not LOGGING_ENABLED:
        return
    _logger.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    if not LOGGING_ENABLED:
        return
    _logger.warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    if not LOGGING_ENABLED:
        return
    _logger.error(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    if not LOGGING_ENABLED:
        return
    _logger.critical(msg, *args, **kwargs)


def class_logger_decorator(wrapped_class):
    if not LOGGING_ENABLED:
        return wrapped_class
    wrapped_class.__init__ = _wrap_method(wrapped_class.__init__, wrapped_class, '__init__', '')
    for i in dir(wrapped_class):
        if i.startswith('__'):
            continue
        item = getattr(wrapped_class, i)
        static = ''
        is_static = _is_static_method(wrapped_class, i, item)
        if ismethod(item):
            static = 'class_'
        elif is_static:
            static = 'static '
        if static or isfunction(item):
            scope = 'public '
            if i.startswith('_'):
                scope = 'private '
            if static or isfunction(item):
                setattr(wrapped_class, i, _wrap_method(item, wrapped_class, i, F'{scope}{static}', is_static))
    return wrapped_class


def _is_static_method(klass, attr, value=None):
    if value is None:
        value = getattr(klass, attr)
    assert getattr(klass, attr) == value

    for cls in inspect.getmro(klass):
        if inspect.isroutine(value):
            if attr in cls.__dict__:
                bound_value = cls.__dict__[attr]
                if isinstance(bound_value, staticmethod):
                    return True
    return False


def _wrap_method(func, klass, method_name, scope, is_static_method=False):
    class_name = klass.__name__

    @wraps(func)
    def wrapper(*args, **kwargs):
        msg = F'{scope}method {class_name}.{method_name}(args:{args[1:]}, kwargs:{kwargs})'

        if is_static_method and isinstance((args[0]), klass):
            arguments = args[1:]
        else:
            arguments = args
        _logger.info(F'call {msg}')
        try:
            result = func(*arguments, **kwargs)
            _logger.info(F'{class_name}.{method_name}: return {result}')
        except Exception as e:
            _logger.critical(F'{msg}: {sys.exc_info()[:2]}')
            raise e
        return result

    return wrapper
