#!/bin/sh
# The second probe: the node of Emscripten died on the host. It looks
# for the reason, tries the options that could work, and builds pages
# with the first that works.
#
#   sh probe-node.sh
#
# It needs ~/atmos-probe from `sh probe.sh full`, and changes nothing
# outside it (it writes ~/atmos-probe/node-*, and the pages it builds).
# Nothing in the output is secret: paste it all.

D=$HOME/atmos-probe
cd "$D" 2>/dev/null || { echo "~/atmos-probe not found: run 'sh probe.sh full' first"; exit 1; }
mkdir -p "$D/tmp"
export TMPDIR="$D/tmp"

say () { printf '\n== %s\n' "$*"; }
ok  () { echo "OK   : $*"; }
bad () { echo "FAIL : $*"; }
note() { echo "NOTE : $*"; }
has () { command -v "$1" >/dev/null 2>&1; }

say "the kernel and what limits memory"
uname -r
echo "PaX / grsecurity flags of this shell (capital letter = restriction on):"
grep -i '^pax' /proc/self/status 2>/dev/null || echo "  (no PaX line in /proc/self/status)"
grep -E 'Max (address space|resident set|processes|locked memory)' /proc/self/limits
echo "overcommit_memory: $(cat /proc/sys/vm/overcommit_memory 2>/dev/null)  max_map_count: $(cat /proc/sys/vm/max_map_count 2>/dev/null)"
for f in /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory.high; do
    [ -r "$f" ] && echo "$f: $(cat $f)"
done

# nodetest <label> <node> [flags...]: runs a JavaScript one-liner
nodetest () {
    L=$1; N=$2; shift 2
    if [ ! -x "$N" ]; then bad "$L: $N not found"; return 1; fi
    TO=""; has timeout && TO="timeout 60"
    $TO "$N" "$@" -e 'console.log("hello from node " + process.version)' >"$TMPDIR/out" 2>"$TMPDIR/err"
    S=$?
    if [ $S -eq 0 ]; then ok "$L: $(cat "$TMPDIR/out")"; return 0; fi
    bad "$L (status $S)"; grep -i 'fatal\|error\|check failed' "$TMPDIR/err" | head -2; return 1
}

SYS=$(command -v node)
EMN=$(ls "$D"/emsdk/node/*/bin/node 2>/dev/null | head -1)

say "which node runs JavaScript here (a one-liner each)"
nodetest "system node"             "$SYS"
nodetest "system node --jitless"   "$SYS" --jitless
nodetest "emsdk node"              "$EMN"
nodetest "emsdk node --jitless"    "$EMN" --jitless

if has strace && [ -x "$EMN" ]; then
    say "what the kernel answers (strace of the failing node, only the failed calls)"
    timeout 60 strace -f -e trace=mprotect,mmap "$EMN" -e 1 2>&1 | grep -E 'EPERM|EACCES|ENOMEM|EAGAIN' | head -5
fi

# the first node that works becomes the one that emcc uses
pick () {
    if nodetest "pick" "$EMN" >/dev/null 2>&1; then echo "$EMN"; return; fi
    if nodetest "pick" "$EMN" --jitless >/dev/null 2>&1; then
        printf '#!/bin/sh\nexec %s --jitless "$@"\n' "$EMN" > "$D/node-jitless"; chmod +x "$D/node-jitless"
        echo "$D/node-jitless"; return
    fi
    if [ -n "$SYS" ] && nodetest "pick" "$SYS" >/dev/null 2>&1; then echo "$SYS"; return; fi
    if [ -n "$SYS" ] && nodetest "pick" "$SYS" --jitless >/dev/null 2>&1; then
        printf '#!/bin/sh\nexec %s --jitless "$@"\n' "$SYS" > "$D/node-jitless"; chmod +x "$D/node-jitless"
        echo "$D/node-jitless"; return
    fi
}
NODE=$(pick)
if [ -z "$NODE" ]; then
    say "result"
    bad "no node runs here: emcc cannot run on this host"
    exit 0
fi
say "emcc with the node that works: $NODE"
export EM_NODE_JS="$NODE"
# what emsdk_env.sh sets (it does not work from a plain `sh` out of its folder)
export EMSDK="$D/emsdk"
export EM_CONFIG="$D/emsdk/.emscripten"
export PATH="$D/emsdk/upstream/emscripten:$D/emsdk/upstream/bin:$PATH"
NICE=""; has nice && NICE="nice -n 19"
if EMV=$(emcc --version 2>&1); then
    ok "emcc runs: $(echo "$EMV" | head -1)"
else
    bad "emcc does not run"; echo "$EMV" | head -3
    exit 0
fi

say "pages (low priority)"
# the clones of the earlier run may be old: bring them to the latest
for r in env-web lang env-pico; do [ -d "$D/$r/.git" ] && git -C "$D/$r" pull -q 2>&1 | tail -1; done
[ -x "$D/lang/atmos" ] && make -s -C "$D/lang" atmos >/dev/null 2>&1
step () {
    T0=$(date +%s); L=$1; shift
    "$@" >"$D/$L.log" 2>&1; S=$?
    echo "$L: status $S in $(( $(date +%s) - T0 )) s"; [ $S -ne 0 ] && tail -3 "$D/$L.log"
}
echo 'print "hello"' > hello.atm
export ATMOS=$D/lang PICO=$D/env-pico
step "web page"  $NICE env-web/atmos-web env-web/exs/counter.atm out
step "text page" $NICE env-web/atmos-web --text hello.atm out
cat > pico.atm <<'EOP'
pico.open()
spawn {
    loop on :draw {
        pico.output.draw.rect ['%', x=0.5, y=0.5, w=0.5, h=0.5]
    }
}
await(:key.dn)
EOP
step "pico page, heavy (about 16 CPU-seconds elsewhere)" $NICE env-web/atmos-web --pico pico.atm out
echo "wasm files built: $(ls out 2>/dev/null | grep -c wasm)"
grep -il 'killed\|cannot allocate\|out of memory' "$D"/*.log 2>/dev/null | sed 's/^/FAIL : a process was killed or ran out of memory: /'

say "done"
echo "To undo everything: rm -rf $D"
