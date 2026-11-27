#!/usr/bin/python3
# The compile server of the site, run once per request (CGI), as the
# try.php of Céu: it compiles an edited program of a guide and answers
# with the address of its page, which the player shows. The program runs
# in the browser of the reader; here it is only compiled.
#
#   POST run.cgi?mode=web|pico|text&guide=<name>    the body is the program
#       200: the address of its page (run/<key>/main.html, under atmos/)
#       400: the errors of the compiler, or why it was refused
#       413, 503: too big, or the server is busy
#
# The tools are those of the probes (site/probe-node.sh), in ~/atmos-probe
# of the host: emsdk, lang, env-pico, env-web, and node-jitless (the node
# of emsdk dies on that kernel without --jitless). Each can be moved with
# an environment variable: ATMOS_TOOLS (all), EMSDK, ATMOS, PICO,
# ATMOS_WEB, EM_NODE_JS.
#
# Limits: the program has at most 32 KB; no native C (`...`) and no
# include, which could read files of the host; one compile at a time (the
# others wait up to 60 s); a compile has at most 120 s; at most 300 pages
# are kept, the oldest are removed.

import fcntl, hashlib, json, os, pwd, re, shutil, subprocess, sys, time
from urllib.parse import parse_qs

HOME  = pwd.getpwuid(os.getuid()).pw_dir
TOOLS = os.environ.get('ATMOS_TOOLS', os.path.join(HOME, 'atmos-probe'))
HERE  = os.path.dirname(os.path.abspath(__file__))     # the folder atmos/ of the site
RUN   = os.path.join(HERE, 'run')
MAX_SRC, MAX_KEEP, TIMEOUT, WAIT = 32 * 1024, 300, 120, 60

def answer (status, text):
    sys.stdout.write('Status: %d\r\nContent-Type: text/plain; charset=utf-8\r\nCache-Control: no-store\r\n\r\n%s' % (status, text))
    sys.stdout.flush()
    sys.exit(0)

def tools ():
    emsdk = os.environ.get('EMSDK', os.path.join(TOOLS, 'emsdk'))
    env = dict(os.environ)
    env.update({
        'EMSDK':     emsdk,
        'EM_CONFIG': os.environ.get('EM_CONFIG', os.path.join(emsdk, '.emscripten')),
        'PATH':      '%s:%s:%s' % (os.path.join(emsdk, 'upstream', 'emscripten'),
                                   os.path.join(emsdk, 'upstream', 'bin'),
                                   os.environ.get('PATH', '/usr/bin:/bin')),
        'ATMOS':     os.environ.get('ATMOS', os.path.join(TOOLS, 'lang')),
        'PICO':      os.environ.get('PICO',  os.path.join(TOOLS, 'env-pico')),
        'TMPDIR':    os.environ.get('TMPDIR_ATMOS', os.path.join(TOOLS, 'tmp')),
        'HOME':      HOME,
    })
    jitless = os.path.join(TOOLS, 'node-jitless')
    if 'EM_NODE_JS' not in env and os.access(jitless, os.X_OK):
        env['EM_NODE_JS'] = jitless
    os.makedirs(env['TMPDIR'], exist_ok=True)
    web = os.environ.get('ATMOS_WEB', os.path.join(TOOLS, 'env-web'))
    roots = { 'PICO': env['PICO'], 'ATMOS': env['ATMOS'], 'WEB': web }
    return env, os.path.join(web, 'atmos-web'), roots

def refused (src):
    code = re.sub(r';;[^\n]*', '', src)                 # comments may have anything
    if '`' in code:
        return 'this server does not compile native code (`...`)'
    if re.search(r'(?m)^\s*include\b', code):
        return 'this server does not compile an include'
    return None

def prune ():
    dirs = [os.path.join(RUN, d) for d in os.listdir(RUN) if not d.startswith('.')]
    dirs.sort(key=lambda d: os.path.getmtime(d))
    for d in dirs[:max(0, len(dirs) - MAX_KEEP)]:
        shutil.rmtree(d, ignore_errors=True)

def main ():
    if os.environ.get('REQUEST_METHOD') != 'POST':
        answer(405, 'POST a program')
    q = parse_qs(os.environ.get('QUERY_STRING', ''))
    mode = q.get('mode', ['web'])[0]
    name = q.get('guide', [''])[0]
    if mode not in ('web', 'pico', 'text'):
        answer(400, 'unknown mode')
    n = int(os.environ.get('CONTENT_LENGTH') or 0)
    if n > MAX_SRC:
        answer(413, 'the program is too big (at most %d bytes)' % MAX_SRC)
    src = sys.stdin.buffer.read(n)
    why = refused(src.decode('utf-8', 'replace'))
    if why:
        answer(400, why)
    guides = json.load(open(os.path.join(HERE, 'guides.json')))
    g = guides.get(name) if name else None
    if name and g is None:
        answer(400, 'unknown guide')

    key = hashlib.sha256(mode.encode() + b'\n' + name.encode() + b'\n' + src).hexdigest()[:16]
    dir = os.path.join(RUN, key)
    url = 'run/%s/main.html' % key
    if os.path.exists(os.path.join(dir, 'main.html')):
        os.utime(dir)
        answer(200, url)

    os.makedirs(RUN, exist_ok=True)
    lock = open(os.path.join(RUN, '.lock'), 'w')
    t0 = time.time()
    while True:                                         # one compile at a time
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            break
        except BlockingIOError:
            if time.time() - t0 > WAIT:
                answer(503, 'the server is busy: try again in a minute')
            time.sleep(0.5)
    if os.path.exists(os.path.join(dir, 'main.html')):  # done while waiting
        answer(200, url)

    env, tool, roots = tools()
    shutil.rmtree(dir, ignore_errors=True)
    os.makedirs(dir)
    with open(os.path.join(dir, 'main.atm'), 'wb') as f:
        f.write(src)
    args = { 'pico': ['--pico'], 'text': ['--text'], 'web': [] }[mode] + [os.path.join(dir, 'main.atm'), dir]
    links = []
    if g and g.get('preload'):
        r, _, sub = g['base'].partition(':')
        base = os.path.join(roots[r], sub)
        args.append('--')
        for p in g['preload']:
            os.symlink(os.path.join(base, p), os.path.join(dir, p))
            links.append(os.path.join(dir, p))
            args += ['--preload-file', p]
    try:
        p = subprocess.run(['nice', '-n', '19', tool] + args, env=env, cwd=dir,
                           capture_output=True, text=True, timeout=TIMEOUT)
        ok, out = p.returncode == 0, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        ok, out = False, 'the compilation took too long'
    for l in links:
        os.unlink(l)
    for f in ('main.atm', 'main.c'):
        if os.path.exists(os.path.join(dir, f)):
            os.unlink(os.path.join(dir, f))
    if not ok:
        shutil.rmtree(dir, ignore_errors=True)
        err = '\n'.join(l for l in out.splitlines()
                        if not l.startswith(('cache:', 'system_libs:', 'ports:', 'shared:')))
        answer(400, err.replace(dir + '/', ''))
    prune()
    answer(200, url)

main()
