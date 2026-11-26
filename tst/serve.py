# The server of the tests: the files of a directory, and `slow.txt`,
# which takes 1s to answer: python3 serve.py <dir> <port>
import sys, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial

class H(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/slow.txt':
            time.sleep(1)
            body = b'slow'
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            try:
                self.wfile.write(body)
            except OSError:
                pass            # the page cancelled the request
        else:
            super().do_GET()
    def log_message(self, *a):
        pass

ThreadingHTTPServer(('127.0.0.1', int(sys.argv[2])), partial(H, directory=sys.argv[1])).serve_forever()
