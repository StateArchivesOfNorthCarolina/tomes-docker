#############################################################
# 2016-09-27: ContentTypeHandler.py 
# Author: Jeremy M. Gibson (State Archives of North Carolina)
# 
# Description: Class to parse the Content-Types of Messages
##############################################################

import re
from email.message import Message


class ContentTypeHandler:
    """"""

    def __init__(self, header=None):
        """Constructor for ContentTypeHandler"""
        self.header = header  # type: Message
        self.ct_str = []  # type: list[str]
        self.is_mixed = False
        self.is_plain = False
        self.is_attachment = False
        self.boundary_string = None
        self.charset = None
        self.content_type = None
        self.content_encoding = None

    def _process_ct(self):
        for header in self.ct_str:
            lst = header.split(";")
            if self.is_content_mixed(lst):
                return
            if self.is_content_plain(lst):
                return
            if self.is_content_attachment(lst):
                return

    def set_content_type_string(self, txt):
        self.ct_str.append(txt)
        self._process_ct()

    def process_single_body_meta(self):
        self.ct_str = self.header.values()
        self._process_ct()

    def is_content_mixed(self, ct_str):
        if re.search("multipart/mixed", ct_str[0]) is not None:
            self.is_mixed = True
            self.content_type = ct_str[0]
            self.boundary_string = ct_str[1].split("=")[1]
            return True
        return False

    def is_content_plain(self, ct_str):
        if re.search("text/plain", ct_str[0]) is not None:
            self.is_plain = True
            self.content_type = ct_str[0]
            self.charset = ct_str[1].split("=")[1]
            return True
        return False

    def is_content_attachment(self, ct_str):
        if re.search("application", ct_str[0]) is not None:
            self.is_attachment = True
            self.process_attachment(ct_str)
            return True
        return False

    def process_attachment(self, ct_str):
        for header, value in self.header.items():
            print()