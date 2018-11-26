#!/usr/bin/env python3

import sys, os
import requests, struct
import bencode, hashlib, json,collections
from torrent import torrent
from urllib.parse import urlencode
from urllib.request import urlopen
from hexdump import hexdump
import socket

CONNECT = 0
ANNOUNCE = 1
SCRAP = 2
ERROR = 3

if __name__ == '__main__':
  torrent = torrent('venom.torrent')
  torrent.send(CONNECT)
  torrent.recv(1024)
