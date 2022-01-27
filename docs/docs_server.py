import os
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler

HOST = '10.0.2.154'
PORT = 80
INDEX_DIR = f'{os.path.dirname(os.path.abspath(__file__))}{os.sep}build{os.sep}html'

os.chdir(INDEX_DIR)

try:
    httpd = HTTPServer((HOST, PORT), SimpleHTTPRequestHandler)
    httpd.serve_forever()
except KeyboardInterrupt:
    print("Keyboard interrupt received, exiting.")



