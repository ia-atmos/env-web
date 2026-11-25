#!/bin/sh
# Builds the prototype: proto/dom/build.sh <lang> [out]
# <lang> is a built checkout of ia-atmos/lang; emcc must be in the PATH.
set -e
L=$1
O=${2:-out}
D=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$O"
"$L/atmos" -c -e "$D/web.atm" "$D/counter.atm" > "$O/counter.c"
emcc -O2 -I"$L/rt" "$O/counter.c" "$L"/rt/[!m]*.c "$L/rt/main.c" \
    -sEXPORTED_RUNTIME_METHODS=cwrap -sEXPORTED_FUNCTIONS=_main,_web_time,_web_event \
    --shell-file "$D/shell.html" -o "$O/counter.html"
# Test: (cd "$O" && python3 -m http.server 8766 &) ; node "$D/test.js"
