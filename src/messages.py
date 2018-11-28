#!/usr/bin/env python3

import struct


def generatechoke():
	return struct.pack('!cb', 1, 0)

def generateunchoke():
	return struct.pack('!IB', 1, 1)

def generateinterested():
	return struct.pack('!IB', 1, 2)

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


__all__ = ['generatechoke', 'generateunchoke', 'generateinterested', 'generateuninterested', 'generatehave',\
	'generatebitfield', 'generaterequest', 'generatepiece', 'generatecancel']


"""
-----------------------------------------
| Message Length | Message ID | Payload |
-----------------------------------------
"""
