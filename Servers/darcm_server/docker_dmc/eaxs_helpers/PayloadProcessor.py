#############################################################
# 2017-03-02: PayloadProcessor.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Takes a message's payloads and builds into
#              singlebodies and multibodies
##############################################################
from email.message import Message

from eaxs.SingleBodyType import SingleBody as SB


class PayloadProcessor:
    """"""

    def __init__(self, payload):
        """Constructor for PayloadProcessor
        :type payload : Message
        """
        self.single_bodies = []  # type: list[SB]
        self._inspect(payload)

    def _inspect(self, payloads):
        if isinstance(payloads, list):
            for mes in payloads:
                if isinstance(mes.get_payload(), list):
                    # There is a deeper structure here
                    self._inspect(mes.get_payload())
                else:
                    # this is the end of the line build a singlebody
                    sb = SB(mes)
                    sb.process_headers()
                    sb.process_body()
                    self.single_bodies.append(sb)
        else:
            # This is a single body that was uncaught.
            # Check to see if its a body only with no metadata
            if isinstance(payloads, str):
                # Yes it is instantiate SingleBody without Payload
                sb = SB()
                sb.body_only = True
            else:
                sb = SB(payloads)
            sb.body_content = payloads
            self.single_bodies.append(sb)