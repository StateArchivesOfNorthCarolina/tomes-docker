#############################################################
# 2016-09-26: RefAccountType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Implementation of the ref-account-type
##############################################################


class RefAccount:
    """"""

    def __init__(self, href=None, ref=None):
        """Constructor for RefAccount"""
        self.href = href  # type: str
        self.email_address = None  # type: [str]
        self.ref_type = ref  # type: str
