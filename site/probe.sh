#!/bin/sh
# Probes a host (such as a shared hosting) for what the compile server of
# the IDE needs: a C compiler, Emscripten, and room to run them.
#
#   sh probe.sh             # installs into ~/atmos-probe (about 1.5 GB)
#
# It changes nothing outside ~/atmos-probe, and removes nothing. It prints
# a report; each step says OK or FAIL and goes on, so that one run shows
# everything. To undo it afterwards: remove the directory ~/atmos-probe.

D=$HOME/atmos-probe
mkdir -p "$D" || exit 1
cd "$D" || exit 1

say  () { printf '\n== %s\n' "$*"; }
try  () { if "$@"; then echo "OK   : $*"; else echo "FAIL : $* (status $?)"; fi; }

say "the machine"
uname -a
(getconf GNU_LIBC_VERSION || ldd --version | head -1) 2>&1
echo "cores: $(nproc 2>/dev/null)"
free -m 2>/dev/null | head -2
df -h "$HOME" | tail -1
echo "limits:"; ulimit -a 2>&1 | grep -i 'cpu\|memory\|process\|file size\|virtual'

say "the tools"
for t in git make cc gcc python3 curl tar xz node; do
    if command -v $t >/dev/null 2>&1; then echo "OK   : $t ($(command -v $t))"; else echo "FAIL : $t not found"; fi
done
python3 --version 2>&1

say "the compiler of Atmos (git clone, make)"
[ -d lang ] || try git clone -q --depth 1 https://github.com/ia-atmos/lang.git lang
try make -C lang CC="${CC:-cc}" atmos
[ -x lang/atmos ] && echo 'print "hello"' > hello.atm && try lang/atmos hello.atm

say "Emscripten (emsdk, about 1 GB)"
[ -d emsdk ] || try git clone -q --depth 1 https://github.com/emscripten-core/emsdk.git emsdk
if [ -d emsdk ]; then
    (cd emsdk && ./emsdk install latest >install.log 2>&1 && ./emsdk activate latest >>install.log 2>&1)
    echo "emsdk install/activate: status $? (log: $D/emsdk/install.log)"
    tail -2 emsdk/install.log
    . ./emsdk/emsdk_env.sh >/dev/null 2>&1
    try emcc --version
fi
du -sh "$D" 2>/dev/null

say "a page of env-web (atmos-web: the first run builds the libraries)"
[ -d env-web ] || try git clone -q --depth 1 https://github.com/ia-atmos/env-web.git env-web
if [ -x env-web/atmos-web ] && command -v emcc >/dev/null 2>&1; then
    T0=$(date +%s)
    ATMOS=$D/lang env-web/atmos-web env-web/exs/counter.atm out >build1.log 2>&1
    echo "first build : status $? in $(( $(date +%s) - T0 )) s"; tail -3 build1.log
    T0=$(date +%s)
    ATMOS=$D/lang env-web/atmos-web --text hello.atm out >build2.log 2>&1
    echo "second build: status $? in $(( $(date +%s) - T0 )) s"; tail -3 build2.log
    ls -la out 2>/dev/null | grep -c 'wasm' | sed 's/^/pages built (wasm files): /'
fi

say "done"
echo "Everything is in $D ($(du -sh "$D" 2>/dev/null | cut -f1)). Nothing else was changed."
