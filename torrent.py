#!/usr/bin/env python3

from hashlib import sha1
from bencode import encode, decode
from six.moves.urllib.parse import urlparse
import bencode, random, math
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
		self.transaction_id = math.floor(random.random()*100000)
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

	def _generatepeerid(self):
		return '-PC0001-' + ''.join([str(random.randint(0, 9)) for _ in range(12)])
	def generatehandshake(self):
		protocol_id = "BitTorrent protocol"
		len_id = str(len(protocol_id))
		reserved = "00000000"
		return len_id + protocol_id + reserved + self.info_hash.hex() + self.peer_id

	def generateheader(self, action):
		transaction_id = random.randint(0, 1 << 32 - 1)
		return transaction_id, struct.pack('!QLL', self.connection_id, action, transaction_id)

	#will refactor to single struct.pack call
	def generateannounce(self, action):
		temp = struct.pack('!Q', self.connection_id)
		temp += struct.pack('!L', action)
		temp += struct.pack('!L', self.transaction_id)
		temp += struct.pack('!20s', self.info_hash)
		temp += struct.pack('!20s', self.peer_id.encode('utf8'))
		temp += struct.pack('!Q', 0)
		temp += struct.pack('!Q', 0)
		temp += struct.pack('!Q', 0)
		temp += struct.pack('!L', 0)
		temp += struct.pack('!L', 0)
		temp += struct.pack('!L', 0)
		temp += struct.pack('!i', -1)
		temp += struct.pack('!h', self.port)
		return temp

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

	def parseurl(self, url):
		parsed = urlparse(url)
		return parsed.hostname, parsed.port

	def unpackconnect(self, payload):
		action, _, self.connection_id = struct.unpack('!LLQ', payload)
		return action, self.transaction_id, self.connection_id

"""
Offset	Size		Name		Value
0				64-bit integer	connection_id
8				32-bit integer	action					1 // announce
12			32-bit integer	transaction_id
16			20-byte string	info_hash
36			20-byte string	peer_id
56			64-bit integer	downloaded
64			64-bit integer	left
72			64-bit integer	uploaded
80			32-bit integer	event						0 // 0: none; 1: completed; 2: started; 3: stopped
84			32-bit integer	IP address			0 // default
88			32-bit integer	key
92			32-bit integer	num_want				-1 // default
96			16-bit integer	port
98

"""
