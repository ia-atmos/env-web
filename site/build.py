#!/usr/bin/env python3
# Builds the static site: python3 site/build.py [outdir] [jobs]
#
#   <outdir>/index.html                  the landing page (site/index.html)
#   <outdir>/imgs/, pdfs/               its images and papers
#   <outdir>/atmos/index.html            sends to github.com/ia-atmos/lang
#   <outdir>/atmos/ide.{html,js,wasm}    the player (ide/ide.atm)
#   <outdir>/atmos/guide/<name>/         the player for a guide
#   <outdir>/atmos/g/<name>/info         its title, mode and number of steps
#   <outdir>/atmos/g/<name>/<i>/{text,code}    a step
#   <outdir>/atmos/g/<name>/<i>/main.html ...  its program, compiled
#   <outdir>/atmos/run.cgi, guides.json  the compile server (site/run.cgi)
#   <outdir>/atmos/run/                  what it compiled (made on the host)
#
# The page of Céu (<outdir>/ceu/) is not made here: it is the current
# site of Céu, copied as it is on the host.
#
# Each program of each step is compiled here, so the steps are only files
# (Run shows the compiled page); an edited program goes to run.cgi, which
# compiles it on the host, once per request. The marker file
# `.env-web-site` says that the folder belongs to this build (see
# `.github/workflows/site.yml`).
#
# It needs what `atmos-web` needs: emcc in the PATH, ATMOS (a built
# checkout of ia-atmos/lang) and PICO (a checkout of ia-atmos/env-pico).

import json, os, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out'))
OUT  = os.path.join(SITE, 'atmos')
JOBS = int(sys.argv[2]) if len(sys.argv) > 2 else 2

sys.argv = sys.argv[:1]                       # serve.py reads a port from it
sys.path.insert(0, os.path.join(HERE, '..', 'ide'))
import serve                                    # the parser of the guides

TOOL = serve.TOOL
GUIDES = sorted(f[:-3] for f in os.listdir(serve.GUIDES) if f.endswith('.md'))

def put (path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

def compile_step (job):
    g, name, i, step = job
    dir = os.path.join(OUT, 'g', name, str(i))
    src = open(os.path.join(g['base'], step['code']), encoding='utf-8').read()
    put(os.path.join(dir, 'text'), '<h2>%s</h2>\n%s' % (serve.inline(step['title']),
        (g['intro'] + '\n' if i == 1 else '') + step['html']))
    put(os.path.join(dir, 'code'), src)
    put(os.path.join(dir, 'main.atm'), src)
    flags = { 'pico': ['--pico'], 'text': ['--text'], 'web': [] }[g['mode']]
    extra = []
    if g['preload']:
        extra = ['--']
        for f in g['preload']:
            link = os.path.join(dir, f)
            if not os.path.exists(link):
                os.symlink(os.path.abspath(os.path.join(g['base'], f)), link)
            extra += ['--preload-file', f]
    ok, err = serve.build(flags + [os.path.join(dir, 'main.atm'), dir] + extra)
    for f in g['preload']:
        os.path.islink(os.path.join(dir, f)) and os.unlink(os.path.join(dir, f))
    for f in ('main.atm', 'main.c'):
        os.path.exists(os.path.join(dir, f)) and os.unlink(os.path.join(dir, f))
    return name, i, ok, err.replace(dir + '/', '')

def main ():
    os.makedirs(SITE, exist_ok=True)
    marker = os.path.join(SITE, '.env-web-site')
    if os.listdir(SITE) and not os.path.exists(marker):
        sys.exit('build.py : %s is not empty and was not made by this build' % SITE)
    for d in ('imgs', 'pdfs', 'atmos'):
        shutil.rmtree(os.path.join(SITE, d), ignore_errors=True)
    open(marker, 'w').write('the files of this folder are made by site/build.py of ia-atmos/env-web\n')
    # the static pages
    shutil.copy(os.path.join(HERE, 'index.html'), SITE)
    for d in ('imgs', 'pdfs', 'atmos'):
        shutil.copytree(os.path.join(HERE, d), os.path.join(SITE, d))
    shutil.copy(os.path.join(HERE, 'favicon.ico'), SITE)
    shutil.copy(os.path.join(HERE, '.htaccess'), SITE)      # no stale copies after a publish

    ok, err = serve.build([os.path.join(HERE, '..', 'ide', 'ide.atm'), OUT])
    if not ok:
        sys.exit('build.py : the player did not build :\n' + err)
    os.unlink(os.path.join(OUT, 'ide.c'))
    page = open(os.path.join(OUT, 'ide.html'), encoding='utf-8').read()

    jobs, known = [], {}
    for name in GUIDES:
        g = serve.guide(name)
        # for the compile server: what an edited program of the guide needs
        known[name] = { 'mode': g['mode'], 'base': g.get('base_spec'), 'preload': g['preload'] }
        n = len(g['steps'])
        put(os.path.join(OUT, 'g', name, 'info'), '%s\n%s\n%d' % (g['title'], g['mode'], n))
        put(os.path.join(OUT, 'guide', name, 'index.html'),
            page.replace('<head>', '<head><base href="../../"><link rel="icon" href="../imgs/atmos-icon.png">'
                                   '<meta id="guide" content="%s">'
                                   '<meta id="static" content="1"><meta id="server" content="run.cgi">' % name, 1)
                .replace('<option>GUIDES</option>', serve.options(), 1))
        jobs += [(g, name, i+1, s) for i, s in enumerate(g['steps'])]

    put(os.path.join(OUT, 'guides.json'), json.dumps(known, indent=1))
    shutil.copy(os.path.join(HERE, 'run.cgi'), OUT)
    os.chmod(os.path.join(OUT, 'run.cgi'), 0o755)

    # the first build of each mode makes its libraries (cached): alone
    first, seen = [], set()
    for j in jobs:
        if j[0]['mode'] not in seen:
            seen.add(j[0]['mode']); first.append(j)
    rest = [j for j in jobs if j not in first]
    fails = 0
    def report (r):
        nonlocal fails
        name, i, ok, err = r
        print('%s %s/%d' % ('ok  ' if ok else 'FAIL', name, i), flush=True)
        if not ok:
            fails += 1
            print(err, file=sys.stderr)
    for j in first:
        report(compile_step(j))
    with ThreadPoolExecutor(JOBS) as ex:
        for r in ex.map(compile_step, rest):
            report(r)

    print('%d steps, %d failed' % (len(jobs), fails))
    sys.exit(1 if fails else 0)

main()
