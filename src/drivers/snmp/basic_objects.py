from typing import Optional, Any

from .abstract_uhp_snmp import _SET_CALL, _GET_CALL


class _ReadLeaf(object):
    def __init__(self, parent_get):
        self._parent_get = parent_get

    def get(self, rtype: int = None, steps: int = None) -> Optional[Any]:
        """
        SNMP param getter

        Params
            rtype: GET_AVG, GET_MAX, GET_MIN, GET_MIN_AVG_MAX constants

            steps: requests count. 10 by default
        Return
          param value or None if error
        """
        return self._parent_get(rtype, steps)


class _WriteLeaf(object):
    def __init__(self, parent_set):
        self._parent_set = parent_set

    def set(self, value=None):
        return self._parent_set(value)


class _ReadWriteLeaf(_ReadLeaf, _WriteLeaf):
    def __init__(self, parent_get, parent_set):
        super().__init__(parent_get)
        self._parent_get = parent_get
        self._parent_set = parent_set


class _Node(object):
    def __init__(self, parent_call):
        self._parent_call = parent_call
        self._oid = None

    def _set(self, value=None):
        return self._parent_call(_SET_CALL, self._oid, value)

    def _get(self, request_type=None, steps=None):
        return self._parent_call(_GET_CALL, self._oid, request_type=request_type, steps=steps)
