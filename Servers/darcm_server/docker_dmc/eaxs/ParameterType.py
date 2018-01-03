#############################################################
# 2016-09-26: ParameterType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Implementation of the parameter-type
##############################################################
from lxml.ElementInclude import etree


class Parameter:
    """"""

    def __init__(self, name=None, value=None):
        """Constructor for Parameter"""
        self.name = name  # type: str
        self.value = value  # type: str

    def render(self, parent):
        """
        :type parent: xml.etree.ElementTree.Element
        :param parent:
        :return:
        """
        child = etree.SubElement(parent, "Parameter")
        child1 = etree.SubElement(child, "Name")
        child1.text = self.value
        child2 = etree.SubElement(child, "Value")
        child2.text = self.value

    def render_json(self):
        param = {}
        param['name'] = self.name
        param['value'] = self.value
        return param