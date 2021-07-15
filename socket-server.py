import socket

import logging
import socketserver
import socket
from http import server

PAGE = """\
<html>
<head>
<title>Camera</title>
</head>
<body>
<center><h1>Camera</h1></center>
<center><img src="stream.mjpg" width="320" height="240"></center>
</body>
</html>
"""

data = bytearray()

socketServerPort = 3600
httpServerPort = 3700
bufferSize = 4096*2

udpServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udpServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/index.html':
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
                    data = udpServerSocket.recvfrom(bufferSize)[0]
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(data))
                    self.end_headers()
                    self.wfile.write(data)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('Client is gone %s: %s', self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    udpServerSocket.bind(("0.0.0.0", socketServerPort))
    print('Listening on port %s ...' % socketServerPort)
    allow_reuse_address = True
    daemon_threads = True

try:
    address = ('', httpServerPort)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    print("stopped")
