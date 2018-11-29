#!/usr/bin/env python3

import sys, os, requests, struct, random
import bencode, hashlib, json, collections
from src.torrent import torrent
from src.utils import hexdumpwithname, printc
import src.messages as messages

from urllib.parse import urlencode
from urllib.request import urlopen
from hexdump import hexdump
import socket, requests

CHOKE = 0
UNCHOKE = 1
INTERESTED = 2
UNINTERESTED = 3

CONNECT = 0
ANNOUNCE = 1
SCRAP = 2
ERROR = 3

if __name__ == '__main__':
	torrent = torrent('sample/venom.torrent')
	#torrent = torrent('sample/solo.torrent')
	printc('tracker ' + str(torrent.host) + ' '+	str(torrent.port), 'blue')
	
	payload = torrent.send(torrent.generateconnect(CONNECT)[1], [1024], 1 , 'connect',\
		socket.gethostbyname(torrent.host), torrent.port, socket.SOCK_DGRAM)
	torrent.unpackconnect(payload[0]) #needed to set connection_id

	IP, PORT = torrent.gethostipport()
	print(torrent.host, IP, PORT)
	
	payload = torrent.send(torrent.generateannounce(ANNOUNCE), [4096], 1 , 'announce',\
		socket.gethostbyname(torrent.host), torrent.port, socket.SOCK_DGRAM)
	retdict = torrent.unpackannounce(payload[0])	
	
	while True:
		try:

			#peer = retdict['peers'][random.randint(0,180)]
			peer = retdict['peers'][random.randint(0,retdict['seeders'])]
			peerip = peer['addr']
			peerport = peer['port']


			#handshake and bitfield
			payload = torrent.send(torrent.generatehandshake(), [68, 10**6], 2 ,'handshake',\
				peerip, peerport, socket.SOCK_STREAM)
			_, peer_id = torrent.unpackhandshake(payload[0])
			print(peer_id)

			torrent.send(messages.generatemessage(INTERESTED), [10**6], 1, 'interested',\
				peerip, peerport, socket.SOCK_STREAM)


			#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#sock.settimeout(3)
			#sock.connect((peerip, peerport))

			#handshake
			#handshake = torrent.generatehandshake()
			#hexdumpwithname(handshake, 'handshake')
			#sock.send(handshake)
			#handshake_hopefully = sock.recv(68)
			#hexdumpwithname(handshake_hopefully, 'recv handshake')
			
			#bitfield
			#payload = sock.recv(2048)
			#hexdumpwithname(payload, 'bitfield')

			#interested	
			#message = messages.generatemessage(INTERESTED)
			#hexdumpwithname(message, 'interested')
			#sock.send(message)
			#payload = sock.recv(10**6) #unchoke 
			#hexdumpwithname(payload, 'UNCHOKE')
			
			#printc("MADE PEER", 'cyan')

		except socket.timeout:
			printc('timed out', 'red')
			continue
		except ConnectionRefusedError:
			printc('connection refused', 'red')
			continue
		except OSError:
			printc('unreachable?', 'red')
			continue
		except AssertionError:
			printc('assertation error', 'red')
			continue
		break
