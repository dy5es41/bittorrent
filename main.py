#!/usr/bin/env python3

import sys, os, requests, struct 
import bencode, hashlib, json, collections

from src.torrent import torrent
from src.utils import hexdumpwithname

from urllib.parse import urlencode
from urllib.request import urlopen
from hexdump import hexdump
import socket, requests

#pls enum
NONE = 0
COMPLETED = 1
STARTED = 2
STOPPED = 3

CONNECT = 0
ANNOUNCE = 1
SCRAP = 2
ERROR = 3

if __name__ == '__main__':
	torrent = torrent('sample/venom.torrent')
	print(torrent.host, torrent.port)
	
	payload = torrent.send(torrent.generateconnect(CONNECT)[1], 1024, 'connect')
	torrent.unpackconnect(payload) #needed to set connection_id

	IP, PORT = torrent.gethostipport()
	print(torrent.host, IP, PORT)
	
	payload = torrent.send(torrent.generateannounce(ANNOUNCE), 2048, 'announce')
	retdict = torrent.unpackannounce(payload)	
	
	peer = retdict['peers'][11]
	peerip = peer['addr']
	peerport = peer['port']
	print(peerip, peerport)

	hexdumpwithname(torrent.generatehandshake(), 'handshake')
	message = torrent.generatehandshake()
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((peerip, peerport))
	s.send(message)
	data = s.recv(2048)
	hexdumpwithname(data, 'back')
	s.close()



