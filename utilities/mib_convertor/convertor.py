import os
import subprocess
from importlib import import_module

from utilities.mib_convertor.src.modem_class_generator import ModemClassGenerator


def convert(input_name, output_name):
    _smidump(input_name, output_name)
    mib = _import_mib(output_name)
    if not mib:
        print('UHP_MIB not found')
        quit(-2)  # TODO: replace with return?
    code = _generate_modem_class(mib)
    _write_driver_file(code)


def _write_driver_file(data):
    snmp_dir = os.path.abspath('../../src/drivers/snmp/')
    driver_file = snmp_dir + '/uhp_snmp_driver.py'
    with open(driver_file, 'w') as f:
        f.write(data)


def _smidump(input_name, output_name):
    cmd = F"smidump -f python {input_name} > {output_name}.py"
    # os.system(cmd)
    # If return code is not 0, raises CalledProcessError
    subprocess.check_output(cmd, shell=True)


def _import_mib(lib):
    try:
        module = import_module(lib)
    except ModuleNotFoundError:
        module = None
    return module


def _generate_modem_class(mib_dict):
    return ModemClassGenerator(mib_dict).generate()


if __name__ == '__main__':
    input_name = 'uhp3.6.mib'

