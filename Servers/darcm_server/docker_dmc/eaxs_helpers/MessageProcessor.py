#############################################################
# 2016-09-28: MessageProcessor.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description:
##############################################################
from email.message import Message
import logging

from eaxs.MultiBodyType import MultiBody
from eaxs.SingleBodyType import SingleBody
from . PayloadProcessor import PayloadProcessor as payprocess


class MessageProcessor:
    """"""

    def __init__(self, message, relpath):
        """Constructor for MessageProcessor
        :type message : Message
        """
        self.message = message  # type: Message
        self.multipart = message.is_multipart()
        self.payloads = message.get_payload()  # type: list[]
        self.single_bodies = []  # type: list[SingleBody]
        self.relpath = relpath
        self.logger = logging.getLogger("MessageProcessor")

    def process_payloads(self):
        pp = payprocess(self.payloads)
        multi_body = MultiBody(self.message)
        multi_body.process_headers()
        for sb in pp.single_bodies:
            if sb.body_only:
                # This SB will need to be manually processed
                sb = self.manual_process_sb(sb)
            self.single_bodies.append(sb)
        multi_body.single_bodies = self.single_bodies
        multi_body.payload = None
        return multi_body

    def manual_process_sb(self, SB):
        """
        :type SB : SingleBody
        :param SB:
        :return SB: SingleBody
        """
        SB.content_type = self.message.get_content_type()
        SB.transfer_encoding = self.message.get('Content-Transfer-Encoding')
        SB.process_body()
        return SB

