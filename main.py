#!/usr/bin/env python3

import sys, os
import requests, struct
import bencode, hashlib, json,collections
from torrent import torrent
from urllib.parse import urlencode
from urllib.request import urlopen
from hexdump import hexdump
import socket, requests

CONNECT = 0
ANNOUNCE = 1
SCRAP = 2
ERROR = 3

if __name__ == '__main__':
	torrent = torrent('venom.torrent')
	print(torrent.host, torrent.port)
	
	payload = torrent.send(torrent.generateconnect(CONNECT)[1], 1024)
	torrent.unpackconnect(payload) #needed to set connection_id

	IP, PORT = torrent.gethostipport()
	print(torrent.host, IP, PORT)
	
	payload = torrent.send(torrent.generateannounce(ANNOUNCE), 2048)
	retdict = torrent.processannounce(payload)	
	print(retdict)
