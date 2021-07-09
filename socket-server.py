import socket
import struct
import pickle

import threading
from threading import Thread

import logging
import socketserver
import socket
from threading import Condition
from http import server
import time
import os
import io
import image

import base64

from array import array

PAGE="""\
<html>
<head>
<title>Raspberry Pi - Camera</title>
</head>
<body>
<center><h1>Raspberry Pi - Camera</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

data = bytearray()

bufferSize = 2048

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def rec():
    while True:
        data = UDPServerSocket.recvfrom(bufferSize)[0]
        server.handle_request()
        print("data has been taken")

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    frame = data

                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    UDPServerSocket.bind(("0.0.0.0", 3500))
    print('Listening on port %s ...' % 3500)

    allow_reuse_address = True
    daemon_threads = True
    
try:
    thread = threading.Thread(target=rec, args=[])
    thread.start()

    address = ('', 3306)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()

finally:
    print("stopped")

    #address = bytesAddressPair[1]

    #f = open('myimage.jpeg', 'wb')
    #f.write(bytearray(data))
    #f.close()
