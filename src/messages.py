#!/usr/bin/env python3

import struct
from enum import Enum

class EVENT(Enum):
  CHOKE = 0
  UNCHOKE = 1
  INTERESTED = 2
  UNINTERESTED = 3

def generatechoke():
	return struct.pack('!iB', 1, 0)

def generateunchoke():
	return struct.pack('!iB', 1, 1)

def generateinterested():
	return struct.pack('!iB', 1, 2)

def generateuninterested():
	return

def generatehave():
	return

def generatebitfield():
	return

def generaterequest():
	return

def generatepiece():
	return

def generatecancel():
	return


def make_interested():
	'''send message to peer of length 1 and ID 2'''
	return struct.pack('!I', 1) + struct.pack('!B', 2) 


__all__ = ['generatechoke', 'generateunchoke', 'generateinterested', 'generateuninterested', 'generatehave',\
	'generatebitfield', 'generaterequest', 'generatepiece', 'generatecancel', 'make_interested']


"""
-----------------------------------------
| Message Length | Message ID | Payload |
-----------------------------------------
"""
