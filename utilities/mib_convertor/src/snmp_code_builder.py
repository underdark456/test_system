from utilities.mib_convertor.src.basic_classes import _Node, _Leaf, FailAccessDetect

_READ_ONLY_CLASS = '_ReadLeaf'
_READ_WRITE_CLASS = '_ReadWriteLeaf'


class SnmpCodeBuilder(object):
    def __init__(self, nodes: dict):
        self._nodes = nodes.copy()
        self._declared_classes = []

    def build(self):
        result = ''
        node_methods = ''
        for node in self._nodes.values():
            result += self._build_node(node)
            method_name = self._get_method_name(node.get_name())
            if not hasattr(node, 'class_name'):
                node.class_name = self._get_class_name(node.get_name())
            child_class_name = node.class_name
            node_methods += \
                F"\n    def {method_name}(self) -> _{child_class_name}:\n" \
                F"        return _{child_class_name}(self._call)\n"
        result += \
            F"\nclass UhpSnmpDriver(AbstractUhpSnmp):\n" \
            F"{node_methods}"
        return 'from src.drivers.snmp.abstract_uhp_snmp import AbstractUhpSnmp\n' \
               'from src.drivers.snmp.basic_objects import _Node, _ReadWriteLeaf, _ReadLeaf\n\n' \
               '"""This code is generated automatically. Consult a psychiatrist before changing.\n' \
               'See utilities/mib_convertor/"""\n\n' \
               + result

    def _build_node(self, node: _Node):
        result = ''
        child_nodes = node.get_nodes()
        leaves = node.get_leaves()
        if not hasattr(node, 'class_name'):
            node.class_name = self._get_class_name(node.get_name())
        node_class_name = node.class_name
        if len(child_nodes):
            node_methods = ''
            for child_node in child_nodes.values():
                result += self._build_node(child_node)
                method_name = self._get_method_name(child_node.get_name())
                if not hasattr(child_node, 'class_name'):
                    child_node.class_name = self._get_class_name(child_node.get_name())
                child_class_name = child_node.class_name
                node_methods += \
                    F"\n    def {method_name}(self) -> _{child_class_name}:\n" \
                    F"        return _{child_class_name}(self._parent_call)\n"
            class_name = node_class_name
            result += \
                F'\nclass _{class_name}(_Node):\n' \
                F'{node_methods}\n'

        elif len(leaves):
            leaf_methods = ''
            for leaf in leaves.values():
                leaf_methods += self._build_leaf(leaf)
            class_name = node_class_name
            result += \
                F'\nclass _{class_name}(_Node):\n' \
                F'{leaf_methods}\n'
        return result

    def _build_leaf(self, leaf: _Leaf):
        leaf_values = leaf.get_value()
        method_name = self._get_method_name(leaf.get_name())
        target = leaf.get_oid()
        return_type, return_def = self._get_access_definitions(leaf_values['access'])
        description = leaf_values['description']
        return F"\n    def {method_name}(self, item_number=0){return_type}:\n" \
               F'        """{description}"""\n' \
               F"        self._oid = '{target}' + '.' + str(item_number)\n" \
               F"        return {return_def}\n"

    def _get_access_definitions(self, access):
        if 'readonly' == access:
            ret_type = F' -> {_READ_ONLY_CLASS}'
            ret_def = F'{_READ_ONLY_CLASS}(self._get)'
            return ret_type, ret_def
        if 'readwrite' == access:
            ret_type = F' -> {_READ_WRITE_CLASS}'
            ret_def = F'{_READ_WRITE_CLASS}(self._get, self._set)'
            return ret_type, ret_def
        raise FailAccessDetect

    def _get_class_name(self, name):
        class_name = name[0].upper() + name[1:]
        i = 1
        while class_name in self._declared_classes:
            class_name = name[0].upper() + name[1:] + str(i)
            i += 1
        self._declared_classes.append(class_name)
        return class_name

    def _get_method_name(self, name):
        res = [name[0].lower()]
        for c in name[1:]:
            if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                res.append('_')
                res.append(c.lower())
            else:
                res.append(c)

        return ''.join(res)
