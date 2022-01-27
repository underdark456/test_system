_NODE = "node"


class UnpinnedLeavesDetected(Exception):
    pass


class FailAccessDetect(Exception):
    pass


def _is_node(node):
    return _NODE == node['nodetype']


def _is_parent_of(parent_oid, child_oid):
    return -1 != child_oid.find(parent_oid + '.')


def _clear_dict_from_none(dictionary: dict) -> dict:
    return {k: v for k, v in dictionary.items() if v is not None}


class _Leaf(object):
    def __init__(self, node_name, node_value):
        self._node_name = node_name
        self._node_value = node_value

    def get_value(self):
        return self._node_value

    def get_name(self):
        return self._node_name

    def get_oid(self):
        return self._node_value['oid']

    def is_leaf(self):
        return True


class _Node(_Leaf):
    def __init__(self, node_name, node_value):
        super().__init__(node_name, node_value)
        self._nodes = {}
        self._leaves = {}

    def get_nodes(self):
        return self._nodes

    def get_leaves(self):
        return self._leaves

    def add_child(self, node):
        if node.is_leaf():
            self._leaves[node.get_oid()] = node
        else:
            self._add_node(node)

    def _add_node(self, new_node):
        for node_oid, node in self._nodes.items():
            if _is_parent_of(node_oid, new_node.get_oid()):
                node.add_child(new_node)
                return
            elif _is_parent_of(new_node.get_oid(), node_oid):
                new_node.add_child(node)
                self._nodes[new_node.get_oid()] = new_node
                self._nodes[node_oid] = None
                return
        self._nodes = _clear_dict_from_none(self._nodes)
        self._nodes[new_node.get_oid()] = new_node

    def pin_leaves(self):
        for node_oid, node in self._nodes.items():
            for leaf_oid, leaf in self._leaves.items():
                if _is_parent_of(node_oid, leaf_oid):
                    node.add_child(leaf)
                    self._leaves[leaf_oid] = None
            node.pin_leaves()
            self._leaves = _clear_dict_from_none(self._leaves)
        if len(self._nodes) and len(self._leaves):
            raise UnpinnedLeavesDetected(self._leaves)

    def is_leaf(self):
        return False
