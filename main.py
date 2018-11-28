#!/usr/bin/env python3

import sys, os, requests, struct, random
import bencode, hashlib, json, collections

from src.torrent import torrent
from src.utils import hexdumpwithname, printc

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
	torrent = torrent('sample/solo.torrent')
	print(torrent.host, torrent.port)
	
	payload = torrent.send(torrent.generateconnect(CONNECT)[1], 1024, 1 , 'connect',\
		socket.gethostbyname(torrent.host), torrent.port, socket.SOCK_DGRAM)
	torrent.unpackconnect(payload) #needed to set connection_id

	IP, PORT = torrent.gethostipport()
	print(torrent.host, IP, PORT)
	
	payload = torrent.send(torrent.generateannounce(ANNOUNCE), 40960, 1 , 'announce',\
		socket.gethostbyname(torrent.host), torrent.port, socket.SOCK_DGRAM)
	retdict = torrent.unpackannounce(payload)	
	
	peer = retdict['peers'][random.randint(0,90)]
	#peer = retdict['peers'][random.randint(0,retdict['seeders'])]
	peerip = peer['addr']
	peerport = peer['port']


	#change amount of payload to 2 when you cna handle it correctly
	payload = torrent.send(torrent.generatehandshake(), 2048, 1 ,'handshake',\
		peerip, peerport, socket.SOCK_STREAM)
	
	printc(payload, 'blue')
	torrent.unpackhandshake(payload)
