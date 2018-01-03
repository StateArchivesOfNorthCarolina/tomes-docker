#############################################################
# 2016-09-26: IncompleteParseType.py 
# Author: Jeremy M. Gibson (State Archives of North Carolina)
# 
# Description: Implementation of the incomplete-parse-type
##############################################################
from lxml.ElementInclude import etree


class IncompleteParse:
    """"""
    
    def __init__(self, error_type=None, error_location=None):
        """Constructor for IncompleteParse"""
        self.error_type = error_type  # type: str
        self.error_location = error_location  # type: str

    def render(self, parent):
        """
        :type parent: xml.etree.ElementTree.Element
        :param parent:
        :return:
        """
        int_bdy_head = etree.SubElement(parent, "Incomplete")
        child1 = etree.SubElement(int_bdy_head, "ErrorType")
        child1.text = self.error_type
        child2 = etree.SubElement(int_bdy_head, "ErrorLocation")
        child2.text = self.error_location

    def render_json(self):
        ip = {}
        ip['error_type'] = self.error_type
        ip['error_location'] = self.error_location
        return ip