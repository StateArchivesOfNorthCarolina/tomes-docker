#############################################################
# 2016-09-26: MboxType.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Implementation of the mbox-type
##############################################################
from eaxs.HashType import Hash


class Mbox:
    """"""

    def __init__(self, rel_path=None, eol=None, hsh=None):
        """Constructor for Mbox"""
        self.rel_path = rel_path  # type: str
        self.eol = eol  # type: str
        self.hsh = hsh  # type: Hash
