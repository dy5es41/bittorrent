#!/usr/bin/env python3

import sys, os, requests, struct, random, time
import bencode, hashlib, json, collections
from src.torrent import torrent
from src.utils import hexdumpwithname, printc
import src.messages as messages

from urllib.parse import urlencode
from urllib.request import urlopen
from hexdump import hexdump
import socket, requests
import asyncio

CHOKE = 0
UNCHOKE = 1
INTERESTED = 2
UNINTERESTED = 3

CONNECT = 0
ANNOUNCE = 1
SCRAP = 2
ERROR = 3


if __name__ == '__main__':
	
	torrent_name = sys.argv[1] if len(sys.argv) > 1 else 'sample/solo.torrent'
	torrent = torrent(torrent_name)
	
	torrent.send(torrent.generateconnect(CONNECT)[1],  'connect',\
		socket.gethostbyname(torrent.host), torrent.port, socket.SOCK_DGRAM, 5)
	payload = torrent.recv(1024)
	print(payload)
	torrent.unpackconnect(payload) #needed to set connection_id

	IP, PORT = torrent.gethostipport()
	print(torrent.host, IP, PORT)
	
	torrent.send(torrent.generateannounce(ANNOUNCE), 'announce',\
		socket.gethostbyname(torrent.host), torrent.port, socket.SOCK_DGRAM, 10)
	payload = torrent.recv(4096)
	retdict = torrent.unpackannounce(payload)	
	
	while True:
		try:


			peer = retdict['peers'][random.randint(0,180)]
			#peer = retdict['peers'][random.randint(0,retdict['seeders'])]
			peerip = peer['addr']
			peerport = peer['port']

			#payload = torrent.send(torrent.generatehandshake(), 68, 1 ,'handshake',\
			#	peerip, peerport, socket.SOCK_STREAM)
			#_, peer_id = torrent.unpackhandshake(payload[0])
			#print(peer_id)
	
			#change to 2 when have pieces
			#printc(payload[1],'yellow')
			#print(sys.getsizeof(messages.generateunchoke()))
			#torrent.send(messages.generateinterested(), 10**6, 1, 'interested',\
			#	peerip, peerport, socket.SOCK_STREAM)


			handshake = torrent.generatehandshake()
			hexdump(handshake)
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.settimeout(3)
			sock.connect((peerip, peerport))

			sock.send(handshake)
			handshake_hopefully = sock.recv(68)
			hexdump(handshake_hopefully)
			# Todo: check that handshake back takes correct form
			# self.receive_data() This should definitely not be happening on init.
			
			cur = messages.generatemessage()
			hexdump(cur)
			sock.send(cur)
			payload = sock.recv(10**6)
			payload2 = sock.recv(1024)
			printc('MAKE PEER', 'yellow')
			hexdump(payload)
			
			hexdump(payload2)
			print("Made peer")


		except socket.timeout:
			printc('timed out', 'red')
			continue
		except ConnectionRefusedError:
			printc('connection refused', 'red')
			continue
		except OSError:
			printc('unreachable?', 'red')
			continue
		except AssertionError as e:
			printc('assertation error', 'red')
			print(e)
			continue
		break
