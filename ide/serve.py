#!/usr/bin/env python3
# The server of the IDE: python3 ide/serve.py [port]   (8080 by default)
#
# It builds the IDE itself (ide.atm, an Atmos program over the DOM),
# serves it at http://127.0.0.1:<port>/, and compiles each program that
# the IDE sends:
#
#   POST /run?mode=web|pico|text        the body is the program
#       200: the address of its page (under /run/)
#       400: the errors of the compiler
#
# A guide (../guides/<name>.md) is shown at /guide/<name>: its steps, each
# with a text, a program and two exercises, beside the editor:
#
#   GET /g/<name>/info          its title, mode and number of steps (3 lines)
#   GET /g/<name>/<i>/text      the text of the step `i` (from 1), as HTML
#   GET /g/<name>/<i>/code      its program
#   POST /run?mode=..&guide=<name>      compiles with the files of the guide
#
# A program is built once: its page is kept in ide/run/, under the hash
# of its mode and text. It needs what `atmos-web` needs: emcc in the
# PATH, ATMOS (a built checkout of ia-atmos/lang, `../lang` by default),
# and, for the mode pico, PICO (a checkout of ia-atmos/env-pico).
#
# It only listens on this machine (127.0.0.1): it runs a compiler on
# whatever it receives.

import hashlib, html, os, re, subprocess, sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(HERE, '..', 'atmos-web')
OUT  = os.path.join(HERE, 'out')        # the IDE
RUN  = os.path.join(HERE, 'run')        # the programs
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

GUIDES = os.path.join(HERE, '..', 'guides')
ROOTS  = {
    'PICO':  os.environ.get('PICO',  os.path.join(HERE, '..', '..', 'env-pico')),
    'ATMOS': os.environ.get('ATMOS', os.path.join(HERE, '..', '..', 'lang')),
    'WEB':   os.path.join(HERE, '..'),
}

def inline (s, link=''):
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', s)
    def a (m):
        url = m.group(2)
        if not re.match(r'[a-z]+:', url):
            url = link + url        # relative to the source of the guide
        return '<a href="%s" target="_blank">%s</a>' % (url, m.group(1))
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', a, s)

# A small part of Markdown: paragraphs, titles, lists, fenced blocks.
def md (text, link=''):
    out = []
    parts = re.split(r'(?ms)^```[^\n]*\n(.*?)^```[ \t]*$', text)
    for n, part in enumerate(parts):
        if n % 2 == 1:
            out.append('<pre>%s</pre>' % html.escape(part, quote=False))
            continue
        for blk in re.split(r'\n\s*\n', part.strip()):
            blk = blk.strip()
            if not blk:
                continue
            m = re.match(r'(#+) (.*)', blk)
            if m:
                out.append('<h3>%s</h3>' % inline(m.group(2), link))
            elif re.match(r'(\d+\.|-) ', blk):
                tag = 'ol' if blk[0].isdigit() else 'ul'
                items = re.split(r'\n(?=\s*(?:\d+\.|-) )', blk)
                out.append('<%s>%s</%s>' % (tag, ''.join(
                    '<li>%s</li>' % inline(re.sub(r'^\s*(\d+\.|-) ', '', i).replace('\n', ' '), link)
                    for i in items), tag))
            else:
                out.append('<p>%s</p>' % inline(blk.replace('\n', ' '), link))
    return '\n'.join(out)

def root (spec):
    r, _, sub = spec.strip().partition(':')
    return os.path.join(ROOTS[r], sub)

# A guide: lines `@key value` (title, mode, base, preload, source, link),
# a text, and its steps.
#
# Without `@source`, each step is in the file: a line `# <title>`, a
# line `@code <file>`, its text and its exercises.
#
# With `@source <file>`, the text and the programs are those of that
# file, one step for each of its examples (a marker `<!-- <dir>/NAME.atm
# -->`, a fenced block with the program, `Output:`, a fenced block), and
# the file of the guide only has the exercises, under `# NAME`.
def guide (name):
    if not re.fullmatch(r'[a-z0-9-]+', name):
        return None
    path = os.path.join(GUIDES, name + '.md')
    if not os.path.exists(path):
        return None
    g = { 'title': name, 'mode': 'web', 'base': None, 'preload': [], 'steps': [], 'link': '' }
    intro, cur = [], None
    for line in open(path, encoding='utf-8').read().split('\n'):
        m = re.match(r'@(\w+)\s+(.*)', line)
        if line.startswith('# '):
            cur = { 'title': line[2:].strip(), 'code': '', 'text': [] }
            g['steps'].append(cur)
        elif m and m.group(1) == 'code':
            cur['code'] = m.group(2).strip()
        elif m and m.group(1) == 'preload':
            g['preload'].append(m.group(2).strip())
        elif m and m.group(1) in ('base', 'source'):
            g[m.group(1)] = root(m.group(2))
        elif m:
            g[m.group(1)] = m.group(2).strip()
        elif cur is None:
            intro.append(line)
        else:
            cur['text'].append(line)
    g['intro'] = md('\n'.join(intro))
    for step in g['steps']:
        step['html'] = md('\n'.join(step['text']))
    if 'source' in g:
        sourced(g)
    return g

# The steps of a guide from its source: the text before an example leads
# to it, and the text after its output, up to the next title or to the
# paragraph that introduces the next example (it ends with a colon), is
# about it.
def sourced (g):
    exs = { s['title']: s['html'] for s in g['steps'] }
    src = open(g['source'], encoding='utf-8').read()
    src = src[src.index('\n# 1.'):]         # after the table of contents
    mark = re.compile(r'(?ms)^<!-- \S*?([\w-]+)\.atm -->\s*^```\n(.*?)^```\s*^Output:\s*^```\n(.*?)^```[ \t]*$')
    steps, pos, lead, title, seen = [], 0, '', '', {}
    ms = list(mark.finditer(src))
    for i, m in enumerate(ms):
        lead += src[pos:m.start()]
        hs = re.findall(r'(?m)^#+ (.*)$', lead)
        if hs:
            title = hs[-1]
        seen[title] = seen.get(title, 0) + 1
        end = ms[i+1].start() if i+1 < len(ms) else len(src)
        rest = src[m.end():end]
        h = re.search(r'(?m)^#+ ', rest)
        ending = ''
        if i+1 == len(ms):                          # the last one keeps the ending
            trail, nxt = (rest[:h.start()], '') if h else (rest, '')
            ending = rest[h.start():] if h else ''
        elif h:
            trail, nxt = rest[:h.start()], rest[h.start():]
        else:
            # same section: the next example starts at the first paragraph
            # that ends with a colon
            blks = re.split(r'(\n\s*\n)', rest)
            k = next((j for j in range(0, len(blks), 2) if blks[j].rstrip().endswith(':')), len(blks))
            trail, nxt = ''.join(blks[:k]), ''.join(blks[k:])
        steps.append({
            'title': title if seen[title] == 1 else '%s (%d)' % (title, seen[title]),
            'code':  m.group(1) + '.atm',
            # the title of the step is shown apart
            'html':  md(re.sub(r'(?m)^#+ %s\s*$' % re.escape(title), '', lead), g['link'])
                     + '\n<h3>Output</h3>\n<pre>%s</pre>\n' % html.escape(m.group(3), quote=False)
                     + md(trail, g['link'])
                     + ('\n<h3>Exercises</h3>\n' + exs[m.group(1)] if m.group(1) in exs else '')
                     + md(ending, g['link']),
        })
        pos, lead = end, nxt
    g['steps'] = steps

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
        if path.startswith('/run/'):
            return os.path.join(RUN, os.path.normpath(path[5:]).lstrip('./'))
        return os.path.join(OUT, os.path.normpath(path).lstrip('./'))

    def do_GET (self):
        path = urlparse(self.path).path
        # the page of the IDE, with the name of its guide (or none)
        m = re.fullmatch(r'/guide/([a-z0-9-]+)', path)
        if path == '/' or (m and guide(m.group(1))):
            page = open(os.path.join(OUT, 'ide.html'), encoding='utf-8').read()
            name = m.group(1) if m else ''
            page = page.replace('<head>', '<head><base href="/"><meta id="guide" content="%s">' % name, 1)
            return self.answer(200, page, 'text/html')
        m = re.fullmatch(r'/g/([a-z0-9-]+)/(info|(\d+)/(text|code))', path)
        if m:
            g = guide(m.group(1))
            if g is None:
                return self.answer(404, 'no guide')
            if m.group(2) == 'info':
                return self.answer(200, '%s\n%s\n%d' % (g['title'], g['mode'], len(g['steps'])))
            i = int(m.group(3))
            if i < 1 or i > len(g['steps']):
                return self.answer(404, 'no step')
            step = g['steps'][i-1]
            if m.group(4) == 'code':
                return self.answer(200, open(os.path.join(g['base'], step['code']), encoding='utf-8').read())
            text = '<h2>%s</h2>\n%s' % (inline(step['title']), step['html'])
            if i == 1:
                text = g['intro'] + '\n' + text
            return self.answer(200, text)
        super().do_GET()

    def answer (self, status, text, type='text/plain'):
        body = text.encode()
        self.send_response(status)
        self.send_header('Content-Type', type + '; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST (self):
        url = urlparse(self.path)
        mode = parse_qs(url.query).get('mode', ['web'])[0]
        if url.path != '/run' or mode not in ('web', 'pico', 'text'):
            return self.answer(404, 'not found')
        src = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        g = guide(parse_qs(url.query).get('guide', [''])[0])
        key = hashlib.sha256(mode.encode() + b'\n' + (g['title'].encode() if g else b'') + b'\n' + src).hexdigest()[:16]
        dir = os.path.join(RUN, key)
        if not os.path.exists(os.path.join(dir, 'main.html')):
            os.makedirs(dir, exist_ok=True)
            with open(os.path.join(dir, 'main.atm'), 'wb') as f:
                f.write(src)
            flags = { 'pico': ['--pico'], 'text': ['--text'], 'web': [] }[mode]
            extra = []
            if g and g['preload']:
                # the files of the guide, beside the program
                extra = ['--']
                for f in g['preload']:
                    if not os.path.exists(os.path.join(dir, f)):
                        os.symlink(os.path.abspath(os.path.join(g['base'], f)), os.path.join(dir, f))
                    extra += ['--preload-file', f]
            try:
                ok, err = build(flags + [os.path.join(dir, 'main.atm'), dir] + extra)
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
