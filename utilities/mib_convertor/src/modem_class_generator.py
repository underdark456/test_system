from utilities.mib_convertor.src.basic_classes import _is_node, _Node, _Leaf, _is_parent_of, _clear_dict_from_none
from utilities.mib_convertor.src.snmp_code_builder import SnmpCodeBuilder


class ModemClassGenerator(object):
    def __init__(self, mib: dict):

        self._mib_data = mib.MIB['nodes']
        self._mib2_data = {}
        self._nodes = {}

    def generate(self):
        self._init_mib2_nodes()
        self._create_nodes(self._mib2_data)
        self._create_nodes(self._mib_data)
        self._pin_leaves()
        builder = SnmpCodeBuilder(self._nodes)
        return builder.build()

    def _create_nodes(self, mib_data):
        for node_name, node_value in mib_data.items():
            if node_name in ['uhp', 'uhpV32']:
                continue
            if _is_node(node_value):
                new_node = _Node(node_name, node_value)
            else:
                new_node = _Leaf(node_name, node_value)
            self._add_node(new_node)

    def _create_node(self, node_name, node_value):
        pass

    def _add_node(self, new_node):
        node_added = False
        for node_oid, node in self._nodes.items():
            if _is_parent_of(node_oid, new_node.get_oid()):
                node.add_child(new_node)
                node_added = True
            elif _is_parent_of(new_node.get_oid(), node_oid):
                new_node.add_child(node)
                self._nodes[new_node.get_oid()] = new_node
                self._nodes[node_oid] = None
                node_added = True
        self._nodes = _clear_dict_from_none(self._nodes)
        if not node_added:
            self._nodes[new_node.get_oid()] = new_node

    def _pin_leaves(self):
        for node_oid, node in self._nodes.items():
            node.pin_leaves()

    def _init_mib2_nodes(self):
        from utilities.mib_convertor.src.RFC_MIB import MIB
        self._mib2_data = MIB['nodes']
