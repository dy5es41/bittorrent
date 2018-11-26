#!/usr/bin/env python3

from hashlib import sha1
from bencode import encode, decode
from six.moves.urllib.parse import urlparse
import bencode, random
import struct, socket
from hexdump import hexdump

CLIENT_NAME = "python"
CLIENT_ID = "PY"
CLIENT_VERSION = "0001"

CONNECT = 0
ANNOUNCE = 1
SCRAP = 2
ERROR = 3

DEFAULT_CONNECTION_ID = 0x41727101980

class torrent():
	def __init__(self, filename):
		self.running = False
		self.data = self.getmetainfo(filename) 
		self.info_hash = sha1(encode(self.data['info'])).digest()
		self.peer_id = self.generatepeerid() 
		self.connection_id = DEFAULT_CONNECTION_ID
		self.transaction = {}
		self.timout = 2
		self.handshake = self.generatehandshake() 
		self.tracker_url = dict(self.getmetainfo(filename))['announce']
		self.host, self.port = self.parseurl(self.data['announce'])

	def getmetainfo(self, fname : str): 
		try: 
			with open(fname, 'rb') as fh: 
				bstruct = bencode.bdecode(fh.read()) 
				return bstruct 
		except IOError as exception: print(exception)

	def generatepeerid(self):
		random_string = ""
		while len(random_string) != 12:
			random_string = random_string + random.choice("1234567890")
			return "-" + CLIENT_ID + CLIENT_VERSION + "-" + random_string

	def generatehandshake(self):
		protocol_id = "BitTorrent protocol"
		len_id = str(len(protocol_id))
		reserved = "00000000"
		return len_id + protocol_id + reserved + self.info_hash.hex() + self.peer_id

	def generateheader(self, action):
		transaction_id = random.randint(0, 1 << 32 - 1)
		return transaction_id, struct.pack('!QLL', self.connection_id, action, transaction_id)
	def send(self, action):
		 
		IP = socket.gethostbyname(self.host)
		PORT = self.port
		print((IP, PORT))
		
		_, message	= self.generateheader(action)
		hexdump(message)
	
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		sock.sendto(message, (IP, PORT))
		payload, addr = sock.recvfrom(1024)
		hexdump(payload)
		return payload

	def recv(self, size):
		return

	def parseurl(self, url):
		parsed = urlparse(url)
		return parsed.hostname, parsed.port
