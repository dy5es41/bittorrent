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
	print(torrent.host)
	transaction_id, message  = torrent.generateheader(CONNECT)
	hexdump(message)
	
	ip = socket.gethostbyname(torrent.host)
	port = torrent.port
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print((ip,port))
	sock.sendto(message, (ip, port))
	data, addr = sock.recvfrom(1024)
	hexdump(data)

