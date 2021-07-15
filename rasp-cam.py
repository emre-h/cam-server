import io
import picamera
import logging
import socketserver
import socket
from threading import Condition
from http import server

import io
from PIL import Image

serverAddressPort   = ('63.33.239.182', 3600)

bufferSize          = 4096*2

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

with picamera.PiCamera(resolution='80x60', framerate=12) as camera:
    output = StreamingOutput()
    # Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    camera.start_recording(output, format='mjpeg')

    try:
        try:
            while True:
                with output.condition:
                    output.condition.wait()
                    frame = output.frame
                try:
                    UDPClientSocket.sendto(frame, serverAddressPort)
                except Exception as e:
                    print("error")
        except Exception as e:
            logging.warning('Removed streaming client %s: %s',self.client_address, str(e))
    finally:
        camera.stop_recording()
