#!/usr/bin/env python3

from hashlib import sha1
from bencode import encode, decode
from six.moves.urllib.parse import urlparse
import sys, bencode, random, math
import struct, socket
from hexdump import hexdump
from src.utils import hexdumpwithname, printc
from bitstring import BitArray, BitStream

CLIENT_NAME = "python"
CLIENT_ID = "PY"
CLIENT_VERSION = "0001"

DEFAULT_CONNECTION_ID = 0x41727101980

HANDSHAKE_PSTR_V1 = 'BitTorrent protocol'

class torrent():
	def __init__(self, filename):
		#file
		self.data = self.getmetainfo(filename) 
		self.announce = self.data['announce']
		self.creation_data = self.data.get('creation date', None)
		self.announce_list = self.data.get('announce-list', None)
		self.comment = self.data.get('comment', None)
		self.created_by = self.data.get('created by', None)
		self.encoding = self.data.get('encoding', None)
		self.private = self.data['info'].get('private', 0)
		self.file_name = self.data['info']['name']

		multiple_files = self.data.get('files', None)
		self.number_files = len(multiple_files) if multiple_files else 1

		try:
			self.length = self.data['info']['length']
		except KeyError:
			self.length = sum(eachfile['length'] for eachfile in self.data['info']['files'])

		#pieces
		self.pieces = self.data['info']['pieces']
		self.piece_length = self.data['info']['piece length']
		assert len(self.pieces) % 20 == 0
		self.number_of_pieces = len(self.pieces) / 20
		
		#blocks
		self.block_length = max(2**14, self.piece_length)
		self.whole_blocks_per_piece = self.piece_length / self.block_length
		self.last_block_size = self.piece_length % self.block_length # will often be zero

		#torrent
		self.info_hash = sha1(encode(self.data['info'])).digest()
		self.peer_id = self.generatepeerid() 
		self.connection_id = DEFAULT_CONNECTION_ID
		self.transaction_id = math.floor(random.random()*100000)
		self.transaction = {}
		self.timout = 2
		self.handshake = self.generatehandshake() 
		self.tracker_url = dict(self.getmetainfo(filename))['announce']

		#socket
		self.host, self.port = self.parseurl(self.data['announce'])
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defaults tcp 

	def getmetainfo(self, fname : str): 
		try: 
			with open(fname, 'rb') as fh: 
				bstruct = bencode.bdecode(fh.read()) 
				return bstruct 
		except IOError as exception: print(exception)

	def gethostipport(self):
		return socket.gethostbyname(self.host), self.port

	def parseurl(self, url):
		parsed = urlparse(url)
		return parsed.hostname, parsed.port

	def generatepeerid(self):
		random_string = ""
		while len(random_string) != 12:
			random_string = random_string + random.choice("1234567890")
		return "-" + CLIENT_ID + CLIENT_VERSION + "-" + random_string

	#messages

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
		temp += struct.pack('!Q', 10000)
		temp += struct.pack('!Q', 0)
		temp += struct.pack('!L', 0)
		temp += struct.pack('!L', 0)
		temp += struct.pack('!L', 0)
		temp += struct.pack('!i', -1)
		temp += struct.pack('!h', self.port)
		return temp

	def generatehandshake(self):
		temp = b'\x13'
		temp += b'BitTorrent protocol'
		temp += b'\x00'*8
		temp += self.info_hash
		temp += self.peer_id.encode('utf8')
		return temp

	#send/recieve

	#both send and revieve include a hexdump
	def send(self, message: bytes,	name : str, address, port, sockettype,\
		timout: int):
		
		#update socket type
		if self.socket.type != sockettype:
			self.socket = socket.socket(socket.AF_INET, sockettype)
			
		printc((address, port), 'green')
		hexdumpwithname(message, name)

		self.socket.settimeout(timout)

		self.socket.connect((address, port))
		self.socket.send(message)
		return
	
	def recv(self, size):
		payload = self.socket.recv(size)
		hexdumpwithname(payload, 'payload')
		return payload
	
	#unpack

	def unpackconnect(self, payload):
		action, _, self.connection_id = struct.unpack('!LLQ', payload)
		return action, self.transaction_id, self.connection_id
	
	def unpackannounce(self, payload):

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

		return dict(action=action,
			transaction_id=transaction_id,
			interval=interval,
			leechers=leechers,
			seeders=seeders,
			peers=peers)

	def unpackhandshake(self, payload):
		#not concerned about ptsr or protocol, just infohash and the peerid, no unpack lazy xd
		info_hash = payload[28:48]
		peer_id = payload[48:68]
		assert info_hash == self.info_hash
		return info_hash, peer_id

	def unpackbitfield(self, payload):
		
		length = payload[0:4]
		msgtype = payload[4:5]
		payload = payload[5:]
		
		length = struct.unpack('>i',length)	
		length = length[0] # tuple -> int		
		
		#checks that we actually have a complete payload
		#assert msgtype != b'\x05'
		#assert length > sys.getsizeof(payload)
		
		arr = []
		for i in range(0,(length-1)//4):
			arr.append(payload[i])
		return arr

#taken from https://github.com/akaptur/bitTorrent/blob/master/torrent_main.py
class peer(object):
	def __init__(self, torrent, socket, handshake, interested):
		self.socket = socket
		self.data = ''
		self.bitfield = BitArray(torrent.number_of_pieces)
		self.sock.send(handshake)
		payload = self.sock.recv(68)
		self.sock.send(interested)
		selt.data += self.sock.recv(10**6)
		self.parse_data()

	def receive_data(self):
		self.data += self.socket.recv(2 * 10**6)
		self.parse_data()

	def parse_data(self):
		message_types = {	0 : 'choke',
							1 : 'unchoke',
							2 : 'interested',
							3 : 'not interested',
							4 : 'have',
							5 : 'bitfield',
							6 : 'request',
							7 : 'piece',
							8 : 'cancel'
							 }

		while len(self.data) > 0:
			if len(self.data) < 4:
				break
			length = struct.unpack('!I', self.data[:4])[0]
			if length == 0:
				msg_type = 'keep alive'
				self.data = self.data[4:]
			else: #data type anything but 'keep alive'
				try:
					msg_type = message_types[ord(self.data[4])]
				except KeyError:
					self.receive_data()
				length -= 1 #subtract one for message-type byte
				if msg_type == 'choke':
					pass
				elif msg_type == 'unchoke':
					self.unchoke = True
				elif msg_type == 'interested':
					pass
				elif msg_type == 'not interested':
					pass
				elif msg_type == 'have':
					self.complete_bitfield(struct.unpack('!I', self.data[5:5+length])[0])
				elif msg_type == 'bitfield':
					expected_bitfield_length = torrent.number_of_pieces
					self.bitfield = BitArray(bytes=self.data[5:5+length])[:expected_bitfield_length]
				elif msg_type == 'request':
					pass
				elif msg_type == 'piece':
					pass
				elif msg_type == 'cancel':
					pass
				else:
					break
				self.data = self.data[5+length:]


	def complete_bitfield(self, have_index):
		self.bitfield[have_index] = 1

	def get_data(self, tracker_bitfield, block_length, last_block_size):
		for piece_num in range(len(tracker_bitfield)):
			if not tracker_bitfield[piece_num]:
				piece_data = self.returns_a_piece(tracker_bitfield, piece_num, block_length, last_block_size)
				self.write_piece_to_file(piece_data, piece_num)
				self.update_bitfield(self.index)

	def returns_a_piece(self, tracker_bitfield, piece_num, block_length, last_block_size):
		if self.bitfield[piece_num]:
			piece_data = ''
			for block_num in range(torrent.whole_blocks_per_piece):
				block = self.get_block(piece_num, block_num, block_length)
				piece_data += block
			if last_block_size:
				block = self.get_block(piece_num, block_num, last_block_size)
				piece_data += block
			return piece_data

	def get_block(self, piece_num, block_num, block_length):
		block_data = ''
		request_msg = self.make_request_msg(13, 6, piece_num, block_num*block_length, block_length)
		self.sock.send(request_msg)
		while len(block_data) < block_length + 13: #todo: learn why 13
			block_data += self.sock.recv(2**15)
		return block_data

	def make_request_msg(self, thirteen, six, piece_num, start_point, block_length):
		request_message = (struct.pack('!I', thirteen) + struct.pack('!B', six) +
						  struct.pack('!I', piece_num) +
						  struct.pack('!I', start_point) +
			  			  struct.pack('!I', block_length))
		return request_message

	def check_piece(self, file):
		return hashlib.sha1(self.current_piece[13:]).digest() == torrent.pieces[20*self.index:20*(self.index+1)]

	def send_cancel(self):
		cancel = (struct.pack('!I', 13) + struct.pack('!B', 8) +
			      struct.pack('!I', self.index) +
			      struct.pack('!I', self.begin) +
			      struct.pack('!I', self.length))
		self.sock.send(cancel)
