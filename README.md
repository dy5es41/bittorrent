## bittorrent
implements the bittorrent protocol
### resources
- https://github.com/akaptur/bitTorrent/blob/master/torrent_main.py
- https://www.cs.swarthmore.edu/~aviv/classes/f12/cs43/labs/lab5/lab5.pdf
- http://bittorrent.org/bittorrentecon.pdf
- https://github.com/borzunov/bit-torrent
- http://www.bittorrent.org/beps/bep_0003.html
- http://jonas.nitro.dk/bittorrent/bittorrent-rfc.html
- https://github.com/JosephSalisbury/python-bittorrent
- https://github.com/sourcepirate/python-udptracker
- http://www.bittorrent.org/beps/bep_0015.html
- http://markuseliasson.se/article/bittorrent-in-python/
- https://allenkim67.github.io/programming/2016/05/04/how-to-make-your-own-bittorrent-client.html
- http://dandylife.net/docs/BitTorrent-Protocol.pdf
- https://wiki.theory.org/index.php/BitTorrentSpecification#Messages
- https://open.spotify.com/track/5J5oiQbDiGed52WKnU259b?si=qsIHmrZGR1Sh06tjn93mGQ
### problems
- announce doesnt work -> announce packet needs info_hash
- i dont really know how to structure this project, should i put all messages ina  a seperate messages.py or should i just split messages from main.py(client) and peer.py
- handshake doesnt work -> handshake struct incorrect
- my unchoke message doesnt work
- socket has been implemented into torrent class so that we are not constantly opening and closing it everytime we call send
