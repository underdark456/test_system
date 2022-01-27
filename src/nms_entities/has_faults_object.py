import time
from abc import ABC, abstractmethod
from src.drivers.abstract_http_driver import API, AbstractHttpDriver
from src.exceptions import NotImplementedException


class HasFaults(ABC):

    _driver: AbstractHttpDriver
    LAN_FAULT = 'LAN'  # LAN down (LAN)
    RX1_FAULT = 'DEMOD1'  # RX1 DVB offset high / CRC (CRC OFFS)
    RX2_FAULT = 'DEMOD2'  # RX2 DVB / TDMA offset high / CRC
    TX_FAULT = 'TX'  # Transmission problems (TLC)
    NET_FAULT = 'NETWORK'  # Service monitoring network reachability problems (NFLT LFLT)
    QOS_FAULT = 'QOS'  # Service monitoring network checks problems (NWRN LWRN)
    SYSTEM_FAULT = 'SYSTEM'  # System fault (SYSTEM)
    DOWN_FAULT = 'DOWN'  # UHP profile is down
    HUB_CN_LOW_FAULT = 'HUB C/N LOW'  # C/N on hub is low
    HUB_CN_HIGH_FAULT = 'HUB C/N HIGH'  # C/N on hub is high
    STN_CN_LOW_FAULT = 'STN C/N LOW'  # C/N on station is low
    STN_CN_HIGH_FAULT = 'STN C/N HIGH'  # C/N on station is high

    _faults_mapping = {
        1: LAN_FAULT,
        2: RX1_FAULT,
        4: RX1_FAULT,
        8: TX_FAULT,
        16: NET_FAULT,
        32: QOS_FAULT,
        64: SYSTEM_FAULT,
        128: DOWN_FAULT,
        256: HUB_CN_LOW_FAULT,
        512: HUB_CN_HIGH_FAULT,
        1024: STN_CN_LOW_FAULT,
        2048: STN_CN_HIGH_FAULT,
    }

    def get_faults(self):
        """
        Get object current faults as a string
        Sample output: 'DOWN HUB C/N LOW'

        :return str: a string containing current fault(s) of the object
        """
        if API == self._driver.get_type():
            faults = self._fault_code_to_list(self.read_param('faults'))
            return self._faults_list_to_string(faults)
        else:
            raise NotImplementedException('Not ready yet for WEB driver - waiting for elements ID (ticket ')

    def wait_faults(self, expected_faults: list, timeout: int = 30, step_timeout: int = 5, strict: bool = True):
        """
        Await for expected faults. The awaiting is blocking

        :param list expected_faults: a list of strings containing
        :param int timeout: how long in seconds await for faults
        :param int step_timeout: time in seconds between fault queries
        :param bool strict: if False other faults apart from the expected ones can be accepted
        """
        begin = time.time()
        while True:
            faults = self.get_faults()
            if strict and ' '.join(expected_faults) == faults:
                return True
            elif not strict:
                for exp_f in expected_faults:
                    if faults.find(exp_f) == -1:
                        break
                else:
                    return True
            t = time.time()
            if timeout < t - begin:
                return False
            time.sleep(step_timeout)

    @staticmethod
    def _fault_code_to_list(fault_code: int) -> list:
        """Transform the composite code to individual fault codes values"""
        faults = []
        try:
            fault_bin = bin(fault_code)[2:][::-1]
        except TypeError:
            raise ValueError(f'Cannot convert {fault_code} to binary')
        for i in range(len(fault_bin)):
            if fault_bin[i] == '1':
                faults.append(2 ** i)
        return faults

    def _faults_list_to_string(self, faults):
        """Join individual codes into a string"""
        return ' '.join(self._faults_mapping.get(f, '') for f in faults)

    @abstractmethod
    def read_param(self, param_name: str):
        pass
