# Sizes and start of a page (2026-11-26)

For `paper-web#11`. env-web `main` a46d0fb, lang d76b547, emcc 7.0.1,
Chromium headless (Playwright), a local `python3 -m http.server`.

Command (what `atmos-web` runs; `-O2` is its default, `ATMOS_CFLAGS`
changes it):

    atmos -c -e web.atm prog.atm > prog.c
    emcc -O2 -I<lang>/rt prog.c <lang>/rt/*.c \
        -sALLOW_MEMORY_GROWTH -sEXPORTED_FUNCTIONS=_main,_malloc,_free \
        --shell-file page.html -o prog.html

| Page | File | Bytes | gzip -9 |
|---|---|---|---|
| counter, `-O2` | `.wasm` | 237060 | 94487 |
| counter, `-O2` | `.js` | 63791 | 18041 |
| threads, `-O2` | `.wasm` | 261493 | 102469 |
| threads, `-O2` | `.js` | 63791 | 18042 |
| counter, `-Oz` | `.wasm` | 167674 | 76046 |
| counter, `-Oz` | `.js` | 62700 | 17664 |

Not tried: `--closure 1` for the JS, `-flto`, a runtime without the
libraries a program does not use (`lio`, `los`, `lload`).

Time to start: from the start of the navigation to the first reaction
of the program on the page (`#msg` becomes "running", seen by a
`MutationObserver`), counter with `-O2`, 10 loads of a fresh page:
min 20.5 ms, median 26.4 ms, max 43.7 ms. Local server, so no network;
the cache of compiled code of Chromium was not controlled.
