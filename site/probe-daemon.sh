#!/bin/sh
# Probes a host (such as a shared hosting) for what a server that stays
# up needs, as a compile server or a Freechains node: a process that
# survives the end of the SSH session, a TCP port that listens, and one
# that others can reach.
#
#   sh probe-daemon.sh          # starts a small server on the port 8330
#   sh probe-daemon.sh check    # later (after you close the session and
#                               # open another): is it still there?
#   sh probe-daemon.sh stop     # stops it and removes its files
#
# Everything is in ~/atmos-probe/daemon. The server only serves one file
# (ok.txt) from that folder, and `stop` ends it. PORT=<n> changes the
# port (8330 is that of Freechains). Nothing in the output is secret.

PORT=${PORT:-8330}
D=$HOME/atmos-probe/daemon
STAGE=${1:-start}

say () { printf '\n== %s\n' "$*"; }
ok  () { echo "OK   : $*"; }
bad () { echo "FAIL : $*"; }
note() { echo "NOTE : $*"; }
has () { command -v "$1" >/dev/null 2>&1; }

# alive: it exists and is not a zombie (a dead one that nobody reaped)
alive () {
    [ -s "$D/pid" ] || return 1
    kill -0 "$(cat "$D/pid")" 2>/dev/null || return 1
    P=$(cat "$D/pid")
    if [ -r "/proc/$P/status" ]; then
        case "$(sed -n 's/^State:[[:space:]]*//p' "/proc/$P/status")" in Z*) return 1 ;; esac
    else
        case "$(ps -o stat= -p "$P" 2>/dev/null)" in Z*) return 1 ;; esac
    fi
    return 0
}
# is the port answering on this machine?
answers () {
    python3 - "$PORT" <<'EOP' 2>/dev/null
import sys, urllib.request
try:
    print(urllib.request.urlopen('http://127.0.0.1:%s/ok.txt' % sys.argv[1], timeout=3).read().decode().strip())
except Exception as e:
    print('ERR', e); sys.exit(1)
EOP
}

case "$STAGE" in
stop)
    if alive; then kill "$(cat "$D/pid")" && ok "stopped"; else note "it was not running"; fi
    rm -rf "$D"
    exit 0 ;;
check)
    say "is it still there? ($(date '+%F %T'))"
    if [ ! -s "$D/pid" ]; then bad "nothing was started: run 'sh probe-daemon.sh' first"; exit 1; fi
    echo "started at: $(cat "$D/started")"
    if alive; then ok "the process $(cat "$D/pid") is alive"; else bad "the process $(cat "$D/pid") is gone (killed by the host?)"; fi
    R=$(answers) && ok "the port $PORT answers here: $R" || bad "the port $PORT does not answer here: $R"
    echo "To see from outside: curl -m 5 http://$(cat "$D/where"):$PORT/ok.txt"
    exit 0 ;;
esac

say "the machine"
uname -a
echo "user: $(id -un)"
echo "hostname: $(hostname)"
echo "addresses: $(hostname -I 2>/dev/null)"
IP=$(curl -s -m 5 https://ifconfig.me 2>/dev/null || curl -s -m 5 https://api.ipify.org 2>/dev/null)
echo "public address, as the host sees it: ${IP:-unknown}"

say "the tools of a Freechains node (Lua 5.4, LuaRocks, Git)"
for t in lua5.4 lua luarocks git python3 curl; do
    if has $t; then ok "$t ($(command -v $t))"; else bad "$t not found"; fi
done
has lua5.4 && lua5.4 -v 2>&1 | head -1

say "a process that stays up"
if ! has python3; then bad "python3 not found: cannot test"; exit 0; fi
if alive; then note "a server of an earlier run was still alive: stopped first"; kill "$(cat "$D/pid")"; sleep 1; fi
rm -rf "$D"; mkdir -p "$D/www"
echo "ok from $(hostname)" > "$D/www/ok.txt"
# detached from the session: its own session, no terminal, output to a file
setsid nohup python3 -m http.server "$PORT" --bind 0.0.0.0 --directory "$D/www" >"$D/log" 2>&1 </dev/null &
echo $! > "$D/pid"
date '+%F %T' > "$D/started"
echo "${IP:-$(hostname)}" > "$D/where"
sleep 2
if alive; then ok "started: process $(cat "$D/pid") on the port $PORT"; else bad "it died at once:"; cat "$D/log"; exit 0; fi
R=$(answers) && ok "the port $PORT answers here: $R" || { bad "the port $PORT does not answer here: $R"; cat "$D/log"; }

say "limits that matter for a server"
ulimit -a 2>&1 | grep -i 'processes\|open files\|cpu\|memory'
if has ss; then echo "listening here:"; ss -ltn 2>/dev/null | head -8; fi

say "what to do now"
cat <<EOF
1. From ANOTHER machine (your computer, not this host), within 1 minute:
       curl -m 5 http://${IP:-<the address above>}:$PORT/ok.txt
   It must print: ok from $(hostname)
   If it hangs or is refused, the port is closed to the outside.
2. Close this SSH session, wait 15 minutes, open another and run:
       sh probe-daemon.sh check
   It says whether the host kept the process alive.
3. Then: sh probe-daemon.sh stop
Paste the output of the three steps.
EOF
