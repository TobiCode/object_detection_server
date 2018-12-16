#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys
import videoModule
from threading import Thread
#videoModule.testHTTPServer_RequestHandler is in videoModule because otherwise import loop
def run():
    print("Instantiiate video processor")
    videoProcessor = videoModule.VideoProcessor()
    thread = Thread(target=videoProcessor.start_detection)
    thread.start()
    #thread.join()
    print('starting server...')
    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = ('192.168.178.53', 8010)
    httpd = HTTPServer(server_address, videoModule.HTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()
    print("still works")

run()
