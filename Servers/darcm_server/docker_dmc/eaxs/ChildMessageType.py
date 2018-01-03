#############################################################
# 2016-09-26: ChildMessageType.py 
# Author: Jeremy M. Gibson (State Archives of North Carolina)
# 
# Description: Implementation of the ChildMessageType
##############################################################

from eaxs.MessageIdType import MessageId
from eaxs.HeaderType import Header

class ChildMessage:
    """"""
    
    def __init__(self, ):
        """Constructor for ChildMessageType"""
        pass
        self.local_id = None  # type: int
        self.message_id = None  # type: MessageIdType
        self.headers = None  # type: [HeaderType]
