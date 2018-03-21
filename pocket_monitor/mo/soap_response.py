from collections import OrderedDict

try:
    import xml.etree.cElementTree as ele_tree
except ImportError:
    import xml.etree.ElementTree as ele_tree


class SoapResponse(object):
    def __init__(self, rep_code=None, rep_content=None):

        self.rep_code = rep_code
        self.rep_content = rep_content

    def get_response_entities(self, entity_root_name):
        root = ele_tree.fromstring(self.rep_content)

        # find entity root
        entity_root = self._match_child_node(root, entity_root_name)

        if entity_root is None:
            return

        ls_ret = []
        if self._has_child(entity_root):
            for child in entity_root:
                if self._has_child(child):
                    ret = self._get_entity(child)
                    if ret:
                        ls_ret.append(ret)
                else:
                    ret = self._get_entity(entity_root)
                    if ret:
                        ls_ret.append(ret)
                    break
        elif entity_root.text is not None:
            ls_ret.append(entity_root.text)
        return ls_ret

    def _has_child(self, node):
        for child in node:
            return True
        return False

    def _get_entity(self, node):
        ret = OrderedDict()
        for child in node:
            child_name = self._get_node_tag_name(child)
            if self._has_child(child):
                ret[child_name] = self._get_entity(child)
            else:
                ret[child_name] = child.text
        return ret

    def _get_node_tag_name(self, node):
        arr = node.tag.split("}")
        return arr[-1].split(":")[-1]

    def _match_child_node(self, node, child_node_name):
        for child in node:
            if self._get_node_tag_name(child) == child_node_name:
                return child
            else:
                return self._match_child_node(child, child_node_name)
