#!/usr/bin/env python3

import struct
from enum import Enum
from src.torrent import torrent
from hexdump import hexdump

class STATE(Enum):
  CHOKE = 0
  UNCHOKE = 1
  INTERESTED = 2
  UNINTERESTED = 3

class FAST(Enum):
  MUST = 0
  MUST_NOT = 1
  REQUIRED = 2
  SHALL = 3
  SHALL_NOT = 4
  SHOULD = 5
  SHOULD_NOT = 6
  RECOMMENDED = 7
  MAY = 8
  OPTIONAL = 9

#fast extension

def generatehavenone():
  return struct.pack('!iB', 1, 15)

def generatehandshakefast(t: torrent):
  temp = b'\x13'
  temp += b'BitTorrent protocol'
  temp += b'\x00'*6
  temp += b'\x04'
  temp += b'\x00'
  temp += t.info_hash
  temp += t.peer_id.encode('utf8')
  return temp

#messages

def generatemessage():
  return struct.pack('!I', 1) + struct.pack('!B', 2) 

def generatehave():
  return struct.pack('!iBi',5, 4, 2 )

#request: <len=0013><id=6><index><begin><length>
def generaterequest():
  return struct.pack('!iBiii', 13, 6, 0, 0, 1024)



__all__ = ['generatemessage', 'generatehandshakefast']

