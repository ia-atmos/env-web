#!/usr/bin/env python3
# The server of the IDE: python3 ide/serve.py [port]   (8080 by default)
#
# It builds the IDE itself (ide.atm, an Atmos program over the DOM),
# serves it at http://127.0.0.1:<port>/, and compiles each program that
# the IDE sends:
#
#   POST /run?mode=web|pico     the body is the program
#       200: the address of its page (under /run/)
#       400: the errors of the compiler
#
# A program is built once: its page is kept in ide/run/, under the hash
# of its mode and text. It needs what `atmos-web` needs: emcc in the
# PATH, ATMOS (a built checkout of ia-atmos/lang, `../lang` by default),
# and, for the mode pico, PICO (a checkout of ia-atmos/env-pico).
#
# It only listens on this machine (127.0.0.1): it runs a compiler on
# whatever it receives.

import hashlib, os, subprocess, sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, '..', 'atmos-web')
OUT  = os.path.join(HERE, 'out')        # the IDE
RUN  = os.path.join(HERE, 'run')        # the programs
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

def build (args):
    p = subprocess.run([TOOL] + args, capture_output=True, text=True, timeout=300)
    err = '\n'.join(l for l in (p.stdout + p.stderr).splitlines()
                    if not l.startswith(('cache:', 'system_libs:', 'ports:')))
    return (p.returncode == 0), err

class Handler (SimpleHTTPRequestHandler):
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, directory=HERE, **kwargs)

    def translate_path (self, path):
        path = urlparse(path).path
        if path == '/':
            return os.path.join(OUT, 'ide.html')
        if path.startswith('/run/'):
            return os.path.join(RUN, os.path.normpath(path[5:]).lstrip('./'))
        return os.path.join(OUT, os.path.normpath(path).lstrip('./'))

    def answer (self, status, text):
        body = text.encode()
        self.send_response(status)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST (self):
        url = urlparse(self.path)
        mode = parse_qs(url.query).get('mode', ['web'])[0]
        if url.path != '/run' or mode not in ('web', 'pico'):
            return self.answer(404, 'not found')
        src = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        key = hashlib.sha256(mode.encode() + b'\n' + src).hexdigest()[:16]
        dir = os.path.join(RUN, key)
        if not os.path.exists(os.path.join(dir, 'main.html')):
            os.makedirs(dir, exist_ok=True)
            with open(os.path.join(dir, 'main.atm'), 'wb') as f:
                f.write(src)
            flags = ['--pico'] if mode == 'pico' else []
            try:
                ok, err = build(flags + [os.path.join(dir, 'main.atm'), dir])
            except subprocess.TimeoutExpired:
                ok, err = False, 'the compilation took too long'
            if not ok:
                return self.answer(400, err.replace(dir + '/', ''))
        self.answer(200, '/run/' + key + '/main.html')

    def log_message (self, *args):
        pass

if __name__ == '__main__':
    ok, err = build([os.path.join(HERE, 'ide.atm'), OUT])
    if not ok:
        sys.exit('serve.py : the IDE did not build :\n' + err)
    print('Atmos IDE at http://127.0.0.1:%d/' % PORT, flush=True)
    ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
