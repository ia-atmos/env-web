#!/bin/sh
# Builds the examples and the tests into tst/out, serves them, and runs
# tst/run.js in Chromium: tst/run.sh [name ...]
# It needs emcc, node with Playwright, python3, and ATMOS (see atmos-web).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=$HERE/out
PORT=${PORT:-8771}
for f in "$HERE"/../exs/*.atm "$HERE"/*.atm; do
    "$HERE/../atmos-web" "$f" "$OUT" 2>&1 | grep -v '^cache:\|system_libs:' || true
done
(cd "$OUT" && exec python3 -m http.server "$PORT" >/dev/null 2>&1) &
SRV=$!
trap 'kill $SRV' EXIT
sleep 1
URL=http://127.0.0.1:$PORT node "$HERE/run.js" "$@"
