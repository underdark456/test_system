from src.drivers.abstract_http_driver import AbstractHttpDriver
from src.exceptions import NmsErrorResponseException
from src.nms_entities.abstract_basic_object import AbstractBasicObject
from src.nms_entities.paths_manager import PathsManager


class PolicyRule(AbstractBasicObject):
    """
    NMS Policy rule class.
    Can be used to either create a new Policy rule instance or manage an existing one.
    If policy_id > `src.constants.NEW_OBJECT_ID` the values of the parameters
    are loaded from NMS using the passed `policy_id` and `rule_id`

    >>> rule = PolicyRule(driver, 0, -1, params={'sequence': '1', 'type': 'Check'})
    >>> rule.save()
    Instantiates a new Policy rule of type `Check` in the Policy ID 0.
    Applies the rule to NMS.

    >>> rule = PolicyRule(driver, 0, 3)
    Loads the parameters of Policy rule ID 3 from NMS. Raises an exception if the given ID is not found.

    See the rest methods in the Base class.

    :param AbstractHttpDriver driver: an inherited instance of the driver
    :param int policy_id: ID of the parent policy object
    :param int rule_id: ID of the rule. If ID equals to `src.constants.NEW_OBJECT_ID`,
                              a new rule is created. Otherwise, the parameters are loaded from NMS.
    :param dict params: a dictionary that contains the parameters of the rule.
                        Initial dictionary is not changed.
    :raises src.exceptions.ObjectNotFoundException:  if Policy rule ID is not found
    """

    # the parameters' names of checkboxes and dropdowns that change form
    _FIRST_QUEUE_FIELDS = [
        'type',
        'check_type',
        'action_type',
    ]

    def __init__(self, driver: AbstractHttpDriver, policy_id: int, rule_id: int, params: dict = None):
        """
        Policy rule class constructor.

        :param AbstractHttpDriver driver: an inherited instance of the driver
        :param int policy_id: ID of the parent policy object
        :param int rule_id: ID of the rule. If ID equals to `src.constants.NEW_OBJECT_ID`,
                                  a new rule is created. Otherwise, the parameters are loaded from NMS.
        :param dict params: a dictionary that contains the parameters of the rule.
                            Initial dictionary is not changed.
        :raises src.exceptions.ObjectNotFoundException:  if Policy rule ID is not found
        """
        super().__init__(driver, policy_id, rule_id, params)

    def _get_create_path(self) -> str:
        """
        Private method that returns the path for creating a new policy rule NMS object. The path is driver dependent.

        :returns str: full driver dependent path for creating a new policy rule NMS object
        """
        return PathsManager.policy_rule_create(self._driver.get_type(), self._parent_id)

    def _get_read_path(self) -> str:
        """
        Private method that returns the path for reading a policy rule NMS object. The path is driver dependent.

        :returns str: full driver dependent path for reading a policy rule NMS object
        """
        return PathsManager.policy_rule_read(self._driver.get_type(), self._object_id)

    def _get_update_path(self) -> str:
        """
        Private method that returns the path for updating a policy rule NMS object. The path is driver dependent.

        :returns str: full driver dependent path for updating a policy rule NMS object
        """
        return PathsManager.policy_rule_update(self._driver.get_type(), self._object_id)

    def _get_delete_path(self) -> str:
        """
        Private method that returns the path for deleting a policy rule NMS object. The path is driver dependent.

        :returns str: full driver dependent path for deleting a policy rule NMS object
        """
        return PathsManager.policy_rule_delete(self._driver.get_type(), self._object_id)

    @classmethod
    def policy_rules_list(cls, driver: AbstractHttpDriver, policy_id: int, skip=None, max_=None, vars_=None):
        """
        Class method that returns a tuple containing policy rule ids of the policy.

        :param AbstractHttpDriver driver: an instance of the driver
        :param int policy_id: the ID of the network
        :param int skip: (optional) how many how many entries should be skipped from list start
        :param int max_: (optional) max number of entries to output
        :param list vars_: (optional) list of vars to output in each entry (if not specified, output all vars)
        :returns tuple: a tuple containing the IDs of the policy rules
        :raises NmsErrorResponseException: if there is an error in the response
        """
        _path = PathsManager.policy_rule_list(driver.get_type(), policy_id, skip, max_, vars_)
        _res, _err, _code = driver.custom_get(_path)
        if _err not in (None, '') or _code not in (None, 0) or _res is None:
            raise NmsErrorResponseException(f'Cannot get station routes list: error {_err}, error_code {_code}')
        _rule_ids = set()
        for r in _res:
            _rule_ids.add(r.get('%row'))
        return _rule_ids
