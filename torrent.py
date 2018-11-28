#!/usr/bin/env python3

from hashlib import sha1
from bencode import encode, decode
from six.moves.urllib.parse import urlparse
import sys, bencode, random, math
import struct, socket
from utilities import hexdumpwithname
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

	def generateconnect(self, action):
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
	
	def gethostipport(self):
		return socket.gethostbyname(self.host), self.port

	def send(self, message, recvsize):
		 
		IP = socket.gethostbyname(self.host)
		PORT = self.port
		print((IP, PORT))
		
		hexdump(message)

		#UDP
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		sock.sendto(message, (IP, PORT))
		payload, addr = sock.recvfrom(recvsize)

		hexdump(payload)

		return payload

	def parseurl(self, url):
		parsed = urlparse(url)
		return parsed.hostname, parsed.port

	def unpackconnect(self, payload):
		action, _, self.connection_id = struct.unpack('!LLQ', payload)
		return action, self.transaction_id, self.connection_id
	

	def processannounce(self, payload):

		response = {}

		info_struct = '!LLLLL'
		info_size = struct.calcsize(info_struct)
		info = payload[:info_size]
		action, transaction_id, interval, leechers, seeders = struct.unpack(info_struct, info)
		
		#sanity check
		assert sys.getsizeof(payload) > 20 #<=20 error response
		assert self.transaction_id == transaction_id

		peer_data = payload[info_size:]
		peer_struct = '!LH'
		peer_size = struct.calcsize(peer_struct)
		peer_count = len(peer_data) // peer_size
		peers = []

		for peer_offset in range(peer_count):
				off = peer_size * peer_offset
				peer = peer_data[off:off + peer_size]
				addr, port = struct.unpack(peer_struct, peer)
				peers.append({
					'addr': socket.inet_ntoa(struct.pack('!L', addr)),
					'port': port,
				})

		return dict(interval=interval,
			leechers=leechers,
			seeders=seeders,
			peers=peers)
