#!/usr/bin/env python3
# Serves the built site on this machine, as the host does: the files, and
# the compile server (atmos/run.cgi) run once per request, as CGI.
#
#   python3 site/serve.py [dir] [port]      (site/out and 8091 by default)
#
# run.cgi finds the tools in the environment: emcc (EMSDK, from
# emsdk_env.sh), ATMOS (a built checkout of lang, ../lang by default) and
# PICO (../env-pico by default); env-web is this repository.

import os, subprocess, sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DIR  = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out'))
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8091

class Handler (SimpleHTTPRequestHandler):
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_POST (self):
        url = urlparse(self.path)
        if url.path != '/atmos/run.cgi':
            self.send_error(404)
            return
        body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        env = dict(os.environ)
        env.update({
            'REQUEST_METHOD': 'POST',
            'QUERY_STRING':   url.query,
            'CONTENT_LENGTH': str(len(body)),
            'ATMOS':          os.environ.get('ATMOS', os.path.join(REPO, '..', 'lang')),
            'PICO':           os.environ.get('PICO',  os.path.join(REPO, '..', 'env-pico')),
            'ATMOS_WEB':      REPO,
        })
        p = subprocess.run([sys.executable, os.path.join(DIR, 'atmos', 'run.cgi')],
                           input=body, env=env, capture_output=True)
        head, _, text = p.stdout.partition(b'\r\n\r\n')
        status = 500
        for line in head.decode().split('\r\n'):
            if line.startswith('Status:'):
                status = int(line.split()[1])
        if p.returncode != 0 and not head:
            text = p.stderr
        self.send_response(status)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(text)))
        self.end_headers()
        self.wfile.write(text)

    def log_message (self, *args):
        pass

if __name__ == '__main__':
    print('The site at http://127.0.0.1:%d/' % PORT, flush=True)
    ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
