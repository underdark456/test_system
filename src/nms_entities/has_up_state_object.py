import asyncio
from abc import ABC, abstractmethod
from time import sleep, time
from typing import Tuple, Union, List

from src.exceptions import InvalidOptionsException


class HasUpState(ABC):
    UNKNOWN = "Unknown"
    OFF = "Off"
    UP = "Up"
    WARNING = "Warning"
    FAULT = "Fault"
    REDUNDANT = "Redundant"
    DOWN = "Down"
    UNREACHABLE = "Unreachable"
    SERVICE = "Service"
    IDLE = "Idle"
    UNSPECIFIED = "Unspecified"

    _valid_states = (UNKNOWN, OFF, UP, WARNING, FAULT, REDUNDANT, DOWN, UNREACHABLE, SERVICE, IDLE, UNSPECIFIED)

    def wait_up(self, timeout=30, step_timeout=5):
        """
        Wait for UP state. The awaiting is blocking

        :param int timeout: the amount of time in seconds to wait the UP state
        :param int step_timeout: the amount of time in seconds between queries of the state
        :returns bool: True if the UP state is reached, otherwise False
        """

        begin = int(time())
        while True:
            # state = self.get_state()
            # if state['state'] == self.UP:
            if self.read_param('state') == self.UP:
                return True
            t = int(time())
            if timeout < t - begin:
                return False
            sleep(step_timeout)

    def wait_fault(self, timeout=30, step_timeout=5):
        """
        Wait for FAULT state. The awaiting is blocking

        :param int timeout: the amount of time in seconds to wait the FAULT state
        :param int step_timeout: the amount of time in seconds between queries of the state
        :returns bool: True if the FAULT state is reached, otherwise False
        """

        begin = int(time())
        while True:
            # state = self.get_state()
            # if state['state'] == self.FAULT:
            if self.read_param('state') == self.FAULT:
                return True
            t = int(time())
            if timeout < t - begin:
                return False
            sleep(step_timeout)

    def wait_fault_or_up(self, timeout=30, step_timeout=5):
        """
        Wait for either FAULT or UP state. The awaiting is blocking

        :param int timeout: the amount of time in seconds to wait for one of the states
        :param int step_timeout: the amount of time in seconds between queries of the state
        :returns bool: True if either FAULT or UP state is reached, otherwise False
        """

        begin = int(time())
        while True:
            # state = self.get_state()
            # if state['state'] in (self.FAULT, self.UP):
            if self.read_param('state') in (self.FAULT, self.UP):
                return True
            t = int(time())
            if timeout < t - begin:
                return False
            sleep(step_timeout)

    def wait_state(self, expected_state=None, timeout=30, step_timeout=5):
        """
        Wait for the passed expected state. The awaiting is blocking

        :param str expected_state: the expected state
        :param int timeout: the amount of time in seconds to wait for the expected state
        :param int step_timeout: the amount of time in seconds between queries of the state
        :returns bool: True if the expected state is reached, otherwise False
        """
        if expected_state not in self._valid_states:
            raise InvalidOptionsException(f'Expected state {expected_state} is not a valid one. '
                                          f'Valid states: {self._valid_states}')
        begin = int(time())
        while True:
            # state = self.get_state()
            # if state['state'] == expected_state:
            if self.read_param('state') == expected_state:
                return True
            t = int(time())
            if timeout < t - begin:
                return False
            sleep(step_timeout)

    def wait_states(self, expected_states=None, timeout=30, step_timeout=5):
        """
        Wait for the state to be any of the passed ones. The awaiting is blocking

        :param list expected_states: the states that are expected
        :param int timeout: the amount of time in seconds to wait for the states
        :param int step_timeout: the amount of time in seconds between queries of the state
        :returns bool: True if any of the states is reached, otherwise False
        """
        for _state in expected_states:
            if _state not in self._valid_states:
                raise InvalidOptionsException(f'Expected state {_state} is not a valid one. '
                                              f'Valid states: {self._valid_states}')
        begin = int(time())
        while True:
            # state = self.get_state()
            # if state['state'] not in not_expected_states:
            if self.read_param('state') in expected_states:
                return True
            t = int(time())
            if timeout < t - begin:
                return False
            sleep(step_timeout)

    def wait_not_state(self, not_expected_state=None, timeout=30, step_timeout=5):
        """
        Wait for the state to be any but not the passed one. The awaiting is blocking

        :param str not_expected_state: the state that is not expected
        :param int timeout: the amount of time in seconds to wait for any state that but not the passed one
        :param int step_timeout: the amount of time in seconds between queries of the state
        :returns bool: True if any state but not the passed one is reached, otherwise False
        """
        if not_expected_state not in self._valid_states:
            raise InvalidOptionsException(f'Not expected state {not_expected_state} is not a valid one. '
                                          f'Valid states: {self._valid_states}')
        begin = int(time())
        while True:
            # state = self.get_state()
            # if state['state'] != not_expected_state:
            if self.read_param('state') != not_expected_state:
                return True
            t = int(time())
            if timeout < t - begin:
                return False
            sleep(step_timeout)

    def wait_not_states(self, not_expected_states=None, timeout=30, step_timeout=5):
        """
        Wait for the state to be any but not the passed ones. The awaiting is blocking

        :param list not_expected_states: the states that are not expected
        :param int timeout: the amount of time in seconds to wait for any state that but not the passed ones
        :param int step_timeout: the amount of time in seconds between queries of the state
        :returns bool: True if any state but not the passed ones is reached, otherwise False
        """
        for _state in not_expected_states:
            if _state not in self._valid_states:
                raise InvalidOptionsException(f'Not expected state {_state} is not a valid one. '
                                              f'Valid states: {self._valid_states}')
        begin = int(time())
        while True:
            # state = self.get_state()
            # if state['state'] not in not_expected_states:
            if self.read_param('state') not in not_expected_states:
                return True
            t = int(time())
            if timeout < t - begin:
                return False
            sleep(step_timeout)

    async def await_up(self, timeout, step_timeout=5, prefix=''):
        begin = int(time())
        waiting = 0
        while True:
            state = self.get_state()
            if state['state'] == self.UP:
                return {
                    'id': self.get_id(),
                    'type': prefix,
                    'up_after': waiting
                }
            waiting += int(time()) - begin
            if timeout < waiting:
                return False
            await asyncio.sleep(step_timeout)

    @classmethod
    def wait_all(cls, timeout: int = 30, step_timeout: int = 5, *, controllers: list = None, stations: list = None) \
            -> Tuple[list, list]:
        """
        Асинхронное ожидание выхода объектов из списков controllers, stations в состояние Up


        Params
            timeout : `int`
                Время ожидания объектов
            step_timeout : `int`
                Задержка между проверками состояния
            controllers : `list<Controller>`
                Список контроллеров
            stations : `list<Station>`
                Список станций

        Returns
            {
                'up': [{
                        'up_after':`int`,

                        'instance': `AbstractBasicObject`

                }...],

                'fail': [{
                        'up_after':`None`,

                        'instance': `AbstractBasicObject`

                }...]],
            }
        """
        done, pending = asyncio.run(cls._run_wait(controllers, stations, timeout, step_timeout))
        result = {
            'up': [],
            'fail': []
        }
        c_list = []
        if controllers is not None:
            c_list = controllers
        s_list = []
        if stations is not None:
            s_list = stations
        c = dict((i.get_id(), i) for i in c_list)
        s = dict((i.get_id(), i) for i in s_list)
        for task in done:
            if task.result():
                r = task.result()
                instance = None
                if 'station' == r['type']:
                    instance = s[r['id']]
                    del s[r['id']]
                elif 'controller' == r['type']:
                    instance = c[r['id']]
                    del c[r['id']]
                result['up'].append(
                    {
                        'up_after': r['up_after'],
                        'instance': instance
                    }
                )

        result['fail'] = [
            {'up_after': None, 'instance': obj}
            for obj in [*c.values(), *s.values()]
        ]
        return result.get('up'), result.get('fail')

    @classmethod
    async def _run_wait(cls, controllers: list = None, stations: list = None, timeout: int = 30, step_timeout: int = 5):
        controllers_tasks = []
        if controllers is not None:
            controllers_tasks = cls._get_tasks(controllers, 'controller', timeout, step_timeout)
        stations_tasks = []
        if stations is not None:
            stations_tasks = cls._get_tasks(stations, 'station', timeout, step_timeout)
        tasks = [*controllers_tasks, *stations_tasks]
        return await asyncio.wait(tasks)

    @classmethod
    def _get_tasks(cls, objects, prefix, timeout, step_timeout):
        tasks = []
        for obj in objects:
            tasks.append(obj.await_up(timeout, step_timeout, prefix))
        return tasks

    @abstractmethod
    def get_state(self) -> dict:
        pass

    @abstractmethod
    def get_id(self) -> int:
        pass

    @abstractmethod
    def read_param(self, param_name: str):
        pass
