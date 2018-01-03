#############################################################
# 2016-09-26: MultiBodyType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
# 
# Description: implementation of the multibody type
##############################################################
from collections import OrderedDict
from email.message import Message

from lxml.ElementInclude import etree

from xml_help.CommonMethods import CommonMethods
from eaxs.SingleBodyType import SingleBody
from eaxs.HeaderType import Header
from eaxs.ParameterType import Parameter




class MultiBody:
    """"""
    
    def __init__(self, payload):
        """Constructor for MultiBody
        :type payload : email.message.Message
        """
        self.payload = payload  # type: Message
        self.content_type = None  # type: str
        self.charset = None  # type: str
        self.content_name = None  # type: str
        self.boundary_string = None  # type: str
        self.content_type_comments = None  # type: str
        self.content_type_param = []  # type: [Parameter]
        self.transfer_encoding = None  # type: str
        self.transfer_encoding_comments = None  # type: str
        self.content_id = None  # type: str
        self.content_id_comments = None  # type: str
        self.description = None  # type: str
        self.description_comments = None  # type: str
        self.disposition = None  # type: str
        self.disposition_file_name = None  # type: str
        self.disposition_comments = None  # type: str
        self.disposition_params = []  # type: [Parameter]
        self.other_mime_header = []  # type: [Header]
        self.preamble = None  # type: str
        self.single_bodies = []  # type: list[SingleBody]
        self.multi_bodies = []  # type: list[MultiBody]
        self.epilogue = None  # type: str

    def process_headers(self):
        for header, value in self.payload.items():
            if header == "Content-Type":
                expression = CommonMethods.get_content_type(value)
                if len(expression) == 3:
                    self.content_type = expression[0]
                    self.boundary_string = expression[2]
                else:
                    self.content_type = expression[0]

    def render(self, parent):
        """
        :type parent: xml.etree.ElementTree.Element
        :param parent:
        :return:
        """
        multi_child_head = etree.SubElement(parent, "MultiBody")
        for key, value in CommonMethods.get_multibody_map().items():

            if self.__getattribute__(key) is not None:
                if isinstance(self.__getattribute__(key), list):
                    # TODO: Handle this
                    for item in self.__getattribute__(key):
                        if isinstance(item, SingleBody):
                            item.render(multi_child_head)
                        if isinstance(item, MultiBody):
                            item.render(multi_child_head)
                        continue
                    continue
                child = etree.SubElement(multi_child_head, value)
                child.text = self.__getattribute__(key)
                continue
            if key == 'charset' or key == 'boundary_string':
                # This is stupid but is required by the schema
                child = etree.SubElement(multi_child_head, value)
                child.text = self.__getattribute__(key)

    # The following getters are for the json render

    def _get_content_type(self):
        if self.content_type is not None:
            return self.content_type
        return str()

    def _get_charset(self):
        if self.charset is not None:
            return self.charset
        return str()

    def _get_content_name(self):
        if self.content_name is not None:
            return self.content_name
        return str()

    def _get_content_type_comments(self):
        if self.content_id_comments is not None:
            return self.content_id_comments
        return str()

    def _get_content_type_params(self):
        if len(self.content_type_param) > 0:
            return [x.render_json() for x in self.content_type_param]
        return []

    def _get_transfer_encoding(self):
        if self.transfer_encoding is not None:
            return self.transfer_encoding
        return str()

    def _get_te_comments(self):
        if self.transfer_encoding_comments is not None:
            return self.transfer_encoding_comments
        return str()

    def _get_content_id(self):
        if self.content_id is not None:
            return self.content_id
        return str()

    def _get_content_id_comments(self):
        if self.content_id_comments is not None:
            return self.content_id_comments
        return str()

    def _get_description(self):
        if self.description is not None:
            return self.description
        return str()

    def _get_descrip_comments(self):
        if self.description_comments is not None:
            return self.description_comments
        return str()

    def _get_disposition(self):
        if self.disposition is not None:
            return self.disposition
        return str()

    def _get_disposition_comments(self):
        if self.disposition_comments is not None:
            return self.description_comments
        return str()

    def _get_disposition_filename(self):
        if self.disposition_file_name is not None:
            return self.disposition_file_name
        return str()

    def _get_disposition_params(self):
        if len(self.disposition_params) > 0:
            return [x.render_json() for x in self.disposition_params]
        return []

    def _get_other_mime_header(self):
        if len(self.other_mime_header) > 0:
            return [x.render_json() for x in self.other_mime_header]
        return []

    def _get_single_bodies(self):
        if len(self.single_bodies) > 0:
            return [x.render_json() for x in self.single_bodies]
        return []

    def _get_multibodies(self):
        if len(self.multi_bodies) > 0:
            return [x.render_json() for x in self.multi_bodies]
        return []

    def render_json(self):
        mbody = OrderedDict()
        mbody['content_type'] = self._get_content_type()
        mbody['charset'] = self._get_charset()
        mbody['content_name'] = self._get_content_name()
        mbody['content_type_comments'] = self._get_content_type_comments()
        mbody['content_type_param'] = self._get_content_type_params()
        mbody['transfer_encoding'] = self._get_transfer_encoding()
        mbody['transfer_encoding_comments'] = self._get_te_comments()
        mbody['content_id'] = self._get_content_id()
        mbody['content_id_comments'] = self._get_content_id_comments()
        mbody['description'] = self.description
        mbody['description_comments'] = self.description_comments
        mbody['disposition'] = self.disposition
        mbody['disposition_comments'] = self.disposition_comments
        mbody['disposition_file_name'] = self.disposition_file_name
        mbody['disposition_params'] = self._get_disposition_params()
        mbody['other_mime_header'] = self._get_other_mime_header()
        mbody['single_body_content'] = self._get_single_bodies()
        mbody['multi_body_content'] = self._get_multibodies()
        return OrderedDict({k: v for k, v in mbody.items() if v not in CommonMethods.empties})