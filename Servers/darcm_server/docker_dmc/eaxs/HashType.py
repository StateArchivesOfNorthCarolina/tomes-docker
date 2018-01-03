#############################################################
# 2016-09-26: HashType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Implementation of the HashType
##############################################################
from lxml.ElementInclude import etree

class Hash:
    """"""

    def __init__(self, value, function):
        """Constructor for Hash"""
        self.value = value  # type: str
        self.function = function  # type: str

    def render(self, parent):
        """
        :type parent: xml.etree.ElementTree.Element
        :param parent:
        :return:
        """
        child = etree.SubElement(parent, "Hash")
        child1 = etree.SubElement(child, "Value")
        child1.text = self.value
        child2 = etree.SubElement(child, "Function")
        child2.text = self.function

    def render_json(self):
        hsh = {}
        hsh['value'] = self.value
        hsh['function'] = self.function
        return hsh