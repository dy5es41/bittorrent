#!/usr/bin/env python3

import struct
from enum import Enum

#CHOKE = 0
#UNCHOKE = 1
#INTERESTED = 2
#UNINTERESTED = 3

def generatemessage(ACTION):
	return struct.pack('!iB', 1, ACTION)

__all__ = ['generatemessage']

