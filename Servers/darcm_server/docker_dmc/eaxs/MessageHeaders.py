########################################################################################################################
# 2017-03-02: MessageHeaders.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: These are the headers that can be used for a top-level message or for a child message. Top-level
# messages should have the "From", "Date", and at least one destination header ("To" "Cc", or "Bcc"); child messages
# should have at least one of "From", "Subject", or "Date".
########################################################################################################################


class MessageHeaders:
    """"""

    def __init__(self, headers):
        """Constructor for MessageHeaders"""
        pass

    def get_header(self, header_id):
        pass

    def get_orig_date(self):
        pass

