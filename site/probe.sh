#!/bin/sh
# Probes a host (such as a shared hosting) for what compiling a page of
# env-web needs: a C compiler, the glibc that Emscripten's binaries need,
# memory, and room for the tools.
#
#   sh probe.sh          # the quick stage: about 1 minute, installs nothing
#   sh probe.sh full     # the full stage: installs into ~/atmos-probe
#                        # (about 1.5 GB) and builds two pages
#
# The quick stage only reads the machine and compiles a small C program
# in a temporary directory that it removes. The full stage changes
# nothing outside ~/atmos-probe; to undo it, remove that directory.
# Each step says OK, FAIL or NOTE and goes on, so one run shows
# everything. Nothing in the output is secret: paste it all.

STAGE=${1:-quick}

say () { printf '\n== %s\n' "$*"; }
ok  () { echo "OK   : $*"; }
bad () { echo "FAIL : $*"; }
note() { echo "NOTE : $*"; }
has () { command -v "$1" >/dev/null 2>&1; }

#
say "the machine"
#
uname -a
LIBC=$( (getconf GNU_LIBC_VERSION 2>/dev/null | sed 's/glibc //') || true)
[ -n "$LIBC" ] || LIBC=$(ldd --version 2>&1 | head -1 | grep -o '[0-9]*\.[0-9]*$')
echo "glibc: ${LIBC:-unknown}"
echo "cores: $(nproc 2>/dev/null || echo unknown)"
echo "memory (MB):"; free -m 2>/dev/null | head -2
echo "disk of \$HOME (the whole filesystem, not your share):"; df -h "$HOME" | tail -1
if has timeout; then DU=$(timeout 60 du -sh "$HOME" 2>/dev/null | cut -f1); else DU=$(du -sh "$HOME" 2>/dev/null | cut -f1); fi
echo "your usage in \$HOME: ${DU:-unknown}"
if has quota; then echo "quota:"; quota -s 2>&1 | head -5; else echo "quota: the command does not exist"; fi
echo "limits:"; ulimit -a 2>&1 | grep -i 'cpu\|memory\|processes\|file size\|virtual'
echo "user: $(id -un), $(id -Gn | tr ' ' ',')"
echo "load: $(cut -d' ' -f1-3 /proc/loadavg 2>/dev/null)"

#
say "glibc for the binaries of Emscripten (clang needs 2.18, its node 2.28)"
#
if [ -n "$LIBC" ]; then
    if [ "$(printf '%s\n2.28\n' "$LIBC" | sort -V | head -1)" = "2.28" ]; then
        ok "glibc $LIBC >= 2.28"
    elif [ "$(printf '%s\n2.18\n' "$LIBC" | sort -V | head -1)" = "2.18" ]; then
        note "glibc $LIBC: clang runs, the node of Emscripten does not (2.28); a node of the system would do"
    else
        bad "glibc $LIBC < 2.18: the binaries of Emscripten do not run"
    fi
fi

#
say "the tools"
#
for t in cc gcc make git python3 curl tar xz gzip node; do
    if has $t; then ok "$t ($(command -v $t))"; else bad "$t not found"; fi
done
has python3 && python3 --version 2>&1
has gcc && gcc --version 2>&1 | head -1
has node && node --version 2>&1

#
say "a C program: compile and run"
#
T="$HOME/.probe-tmp-$$"
mkdir -p "$T"
cat > "$T/t.c" <<'EOC'
#include <stdio.h>
int main (void) { printf("hello from C\n"); return 0; }
EOC
CC=cc; has cc || CC=gcc
if "$CC" -O2 "$T/t.c" -o "$T/t" 2>"$T/err" && "$T/t"; then
    ok "compiled and ran with $CC"
else
    bad "the C program did not build or run in \$HOME"; cat "$T/err"
fi
# the system temporary directory is often mounted noexec: a build can
# then only run its tools from \$HOME (the full stage sets TMPDIR there)
TT=$(mktemp -d 2>/dev/null)
if [ -n "$TT" ] && [ -x "$T/t" ]; then
    cp "$T/t" "$TT/t" 2>/dev/null
    if "$TT/t" >/dev/null 2>&1; then
        ok "programs also run from $TT"
    else
        note "$TT does not allow running programs (noexec): the build must use a TMPDIR in \$HOME"
    fi
fi
[ -n "$TT" ] && rm -rf "$TT"

#
say "memory: can one process hold 1 GB? (a compile of Emscripten needs several hundred MB)"
#
if has python3; then
    python3 - <<'EOP'
import sys
try:
    b = bytearray(1024 * 1024 * 1024)
    for i in range(0, len(b), 4096):
        b[i] = 1
    print("OK   : 1 GB allocated and touched")
except MemoryError:
    print("FAIL : MemoryError at 1 GB")
EOP
    echo "status of that process: $?"
else
    note "python3 not found: not tested"
fi

#
say "several processes at once (a build of Emscripten starts clang, node and others)"
#
OKS=0
for i in 1 2 3 4 5 6; do (sleep 1) & done
wait && ok "6 processes at once" || bad "could not start 6 processes at once"

rm -rf "$T"

if [ "$STAGE" != "full" ]; then
    say "done: the quick stage"
    echo "Nothing was installed. Paste all of this output."
    echo "If the checks above are OK, run the full stage: sh probe.sh full"
    exit 0
fi

# ------------------------------------------------------------------
# the full stage
# ------------------------------------------------------------------
D=$HOME/atmos-probe
mkdir -p "$D" || exit 1
cd "$D" || exit 1
mkdir -p "$D/tmp"
export TMPDIR="$D/tmp"                  # the system one may be noexec
NICE=""; has nice && NICE="nice -n 19"  # a shared machine: low priority
try () { if "$@"; then ok "$*"; else bad "$* (status $?)"; fi; }

say "the compiler of Atmos (git clone, make)"
[ -d lang ] || try git clone -q --depth 1 https://github.com/ia-atmos/lang.git lang
try make -C lang CC="${CC:-cc}" atmos
if [ -x lang/atmos ]; then
    echo 'print "hello"' > hello.atm
    # `atmos prog.atm` builds in /tmp and runs from there (it fails where
    # /tmp is noexec, status 127); building to a file in $HOME does not
    try lang/atmos -o hello hello.atm
    try ./hello
fi

say "Emscripten (emsdk, about 1 GB)"
[ -d emsdk ] || try git clone -q --depth 1 https://github.com/emscripten-core/emsdk.git emsdk
if [ -d emsdk ]; then
    T0=$(date +%s)
    (cd emsdk && $NICE ./emsdk install latest >install.log 2>&1 && ./emsdk activate latest >>install.log 2>&1)
    echo "emsdk install/activate: status $? in $(( $(date +%s) - T0 )) s (log: $D/emsdk/install.log)"
    tail -2 emsdk/install.log
    # what emsdk_env.sh sets (it does not work from a plain `sh`)
    export EMSDK="$D/emsdk" EM_CONFIG="$D/emsdk/.emscripten"
    export PATH="$D/emsdk/upstream/emscripten:$D/emsdk/upstream/bin:$PATH"
    try emcc --version
fi
du -sh "$D" 2>/dev/null

say "two pages of env-web (the first build also builds the libraries)"
[ -d env-web ] || try git clone -q --depth 1 https://github.com/ia-atmos/env-web.git env-web
if [ -x env-web/atmos-web ] && has emcc; then
    T0=$(date +%s)
    ATMOS=$D/lang $NICE env-web/atmos-web env-web/exs/counter.atm out >build1.log 2>&1
    echo "web page, first build : status $? in $(( $(date +%s) - T0 )) s"; tail -3 build1.log
    T0=$(date +%s)
    ATMOS=$D/lang $NICE env-web/atmos-web --text hello.atm out >build2.log 2>&1
    echo "text page, second build: status $? in $(( $(date +%s) - T0 )) s"; tail -3 build2.log
    echo "wasm files built: $(ls out 2>/dev/null | grep -c wasm)"
    # a heavier build, to see whether a long one is killed (about 16 CPU-seconds)
    cp "$D/env-web/exs/counter.atm" pico.atm 2>/dev/null
    if [ -d "$HOME/env-pico" ] || git clone -q --depth 1 https://github.com/ia-atmos/env-pico.git env-pico 2>/dev/null; then
        cat > pico.atm <<'EOP'
pico.open()
spawn {
    loop on :draw {
        pico.output.draw.rect ['%', x=0.5, y=0.5, w=0.5, h=0.5]
    }
}
await(:key.dn)
EOP
        T0=$(date +%s)
        ATMOS=$D/lang PICO=$D/env-pico $NICE env-web/atmos-web --pico pico.atm out >build3.log 2>&1
        echo "pico page (heavy): status $? in $(( $(date +%s) - T0 )) s"; tail -3 build3.log
    else
        note "env-pico could not be cloned: the pico build was not tried"
    fi
    grep -il 'killed\|cannot allocate\|out of memory' build*.log emsdk/install.log 2>/dev/null | sed 's/^/FAIL : a process was killed or ran out of memory, see /'
fi

say "done: the full stage"
echo "Everything is in $D ($(du -sh "$D" 2>/dev/null | cut -f1)). Nothing else was changed."
echo "To undo: rm -rf $D"
