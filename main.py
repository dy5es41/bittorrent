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
			
			peer = retdict['peers'][random.randint(0,len(retdict['peers']))]
			peerip = peer['addr']
			peerport = peer['port']

			#handshake and idc about ur bitfield pal
			torrent.send(torrent.generatehandshake(),'handshake',\
				peerip, peerport, socket.SOCK_STREAM, 3)
			payload = torrent.recv(68) 
			_, peer_id = torrent.unpackhandshake(payload)
			print(peer_id)
			
			#sometimes we dont recieve a full bitfield because peers are lazy
			# int size (excluding this own size), byte msg type, payload!
			bitfield = torrent.recv(10**6)
			while struct.unpack('>i',bitfield[0:4])[0] > sys.getsizeof(bitfield[5:]):
				bitfield += torrent.recv(10**6)

			hexdumpwithname(bitfield, 'final bitfield')
			peerpieces = torrent.unpackbitfield(bitfield)
			print(peerpieces)
			


			torrent.send(messages.generatemessage(INTERESTED), 'interested',\
				peerip, peerport, socket.SOCK_STREAM, 5)
			torrent.recv(10**6)

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
		except AssertionError as e:
			printc('assertation error', 'red')
			print(e)
			continue
		break
