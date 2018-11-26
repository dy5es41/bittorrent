#!/usr/bin/env python3

from hashlib import sha1
from bencode import encode, decode
import bencode

CLIENT_NAME = "pythonnice"
CLIENT_ID = "PY"
CLIENT_VERSION = "0001"

class torrent():
	def __init__(self, filename):
		self.running = False
		self.data = self.getmetainfo(filename) 
		self.info_hash = sha1(encode(self.data['info'])).digest()
		self.peer_id = generatepeerid() 
		self.handshake = generatehandshake() 
	
	@classmethod
	def getmetainfo(self, fname : str): 
		try: 
			with open(fname, 'rb') as fh: 
				bstruct = bencode.bdecode(fh.read()) 
				return bstruct 
		except IOError as exception: print(exception)

	@classmethod
	def generatepeerid(self):

		# As Azureus style seems most popular, we'll be using that.
		# Generate a 12 character long string of random numbers.
		random_string = ""
		while len(random_string) != 12:
			random_string = random_string + choice("1234567890")
			return "-" + CLIENT_ID + CLIENT_VERSION + "-" + random_string

	@classmethod
	def generatehandshake(self,info_hash, peer_id):
		protocol_id = "BitTorrent protocol"
		len_id = str(len(protocol_id))
		reserved = "00000000"
		return len_id + protocol_id + reserved + info_hash + peer_id
