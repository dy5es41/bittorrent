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
	payload = torrent.send(CONNECT)

	
	
	#print(*torrent.unpackconnect(payload))
	hexdump(torrent.generateannounce(ANNOUNCE))
	message = torrent.generateannounce(ANNOUNCE)
	IP = socket.gethostbyname(torrent.host)
	PORT = torrent.port
	
	print(torrent.host, IP, PORT)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	sock.sendto(message, (IP, PORT))
	payload, addr = sock.recvfrom(1024)
	hexdump(payload)

