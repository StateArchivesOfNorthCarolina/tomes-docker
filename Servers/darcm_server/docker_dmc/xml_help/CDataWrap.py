#############################################################
# 2016-09-23: CDataWrap.py
# Author: Jeremy M. Gibson (State Archives of North Carolina)
#
# Description: Wraps CDATA text
#############################################################

def cdata_wrap(data):
    return '<![CDATA[{}]>'.format(data)
