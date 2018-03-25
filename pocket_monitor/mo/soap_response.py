import logging
import traceback
from collections import OrderedDict

try:
    import xml.etree.cElementTree as ele_tree
except ImportError:
    import xml.etree.ElementTree as ele_tree

logger = logging.getLogger("mo.soap")

class SoapResponse(object):
    def __init__(self, rep_code=None, rep_content=None):
        self.rep_code = rep_code
        self.rep_content = rep_content

    def get_response_entities(self, entity_root_name, page_count_pro_name=None, record_count_pro_name=None):
        if not self.rep_content:
            return {"content": []}
        try:
            root = ele_tree.fromstring(self.rep_content)

            # find entity root
            parent, entity_root = self._match_child_node(root, entity_root_name, True)
            if entity_root is None:
                return

            ls_ret = []
            page_info = {}
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
                if page_count_pro_name is not None:
                    parent, page_count = self._match_child_node(parent, page_count_pro_name)
                    if page_count.text:
                        page_info["page_count"] = int(page_count.text)
                if record_count_pro_name is not None:
                    parent, record_count = self._match_child_node(parent, record_count_pro_name)
                    if record_count.text:
                        page_info["record_count"] = int(record_count.text)
            elif entity_root.text is not None:
                ls_ret.append(entity_root.text)

            ret = {"content": ls_ret}
            if page_info:
                ret["page_info"] = page_info
            return ret
        except Exception as e:
            exstr = traceback.format_exc()
            logger.error('Parse soap response [%s] error: %s %s' % (self.rep_content, type(e), exstr))
            raise e

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

    def _match_child_node(self, node, child_node_name, recursive=False):
        for child in node:
            if self._get_node_tag_name(child) == child_node_name:
                return node, child
            else:
                if recursive:
                    return self._match_child_node(child, child_node_name, recursive)
