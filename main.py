#!/usr/bin/env python3

import sys, os
import requests, hexdump, struct
import bencode, hashlib, json,collections
from torrent import torrent

def createinfo_hash(odict : collections.OrderedDict):
	if 'info' in odict:
		return hashlib.sha1(bencode.bencode(odict['info'])).hexdigest()
	else:
		sys.stderr.write('info not found in dict (invalid torrent file)')

def createrequest(t : torrent)
	
	payload = {'info_hash': t.info_hash,
								'peer_id' :

	return


if __name__ == '__main__':
	torrent = torrent('sample.torrent')
	print(torrent.info_hash)

