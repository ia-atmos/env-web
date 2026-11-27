# env-web

[![Tests](https://github.com/ia-atmos/env-web/actions/workflows/tests.yml/badge.svg)](https://github.com/ia-atmos/env-web/actions/workflows/tests.yml)
[![Published](https://github.com/ia-atmos/env-web/actions/workflows/published.yml/badge.svg)](https://github.com/ia-atmos/env-web/actions/workflows/published.yml)

[Atmos][atmos] in the browser: write the logic of a web page in Atmos,
as a sequence in time, and run it in any page, compiled to WebAssembly.

The site of Atmos, with its tutorials running in the browser, is made
here: **https://ceu-lang.org/new/**

An event of the page becomes an event of the program, and an element is
named by its `id`, as in the HTML:

```
web.set("msg", "text", "running")

watching :click [id="stop"] {
    spawn {
        var s = 0
        loop {
            await 1s
            set s += 1
            web.set("secs", "text", tostring(s))
        }
    }
    var n = 0
    loop on :click [id="inc"] {
        set n += 1
        web.set("count", "text", tostring(n))
    }
}

web.set("msg", "text", "stopped")
```

Status: experimental.

[atmos]: https://github.com/ia-atmos/lang
[emcc]:  https://emscripten.org/
[pico]:  https://github.com/ia-atmos/env-pico

# Use it in your project

## 1. The tools

[Emscripten][emcc], the compiler of Atmos, and this repository, side by
side:

```
git clone https://github.com/emscripten-core/emsdk
(cd emsdk && ./emsdk install latest && ./emsdk activate latest)
. emsdk/emsdk_env.sh                    # emcc in the PATH

git clone https://github.com/ia-atmos/lang
make -C lang                            # the compiler, lang/atmos

git clone https://github.com/ia-atmos/env-web
```

`atmos-web` finds the compiler in `../lang`, or in `ATMOS=<dir>`.

## 2. Build

```
env-web/atmos-web app.atm out
```

This gives `out/app.js` and `out/app.wasm` (and `out/app.html`, a page
for them). The first build also builds the runtime, once. A small
program is about 240 KB of `.wasm`, 95 KB with gzip.

## 3. Put it in your page

Copy `app.js` and `app.wasm` to the same folder of your site, and load
the script at the end of the page, after the elements that the program
uses:

```
<p>count: <span id="count">0</span> <button id="inc">+1</button></p>
...
<script src="js/app.js"></script>
```

The program starts when the script loads, and finds the elements by
their ids. Elements that the program creates itself (`web.new`) need not
be in the page. The files are static: any server of files works, but
not `file://` (the browser does not load WebAssembly from a disk).

To try a program alone, `app.html` beside `app.atm` is used as the page
of `out/app.html`, with the line `{{{ SCRIPT }}}` where the program is
loaded (see [`exs/counter.html`](exs/counter.html)); without it, the
page is empty:

```
env-web/atmos-web env-web/exs/counter.atm out
(cd out && python3 -m http.server)      # http://localhost:8000/counter.html
```

## 4. The interface

The environment is [`web.atm`](web.atm) (its header documents it in
full).

| Event | |
|-------|-|
| `:click [id]` | A click on an element or inside it (`id` of the nearest element that has one) |
| `:input [id,value]` | The text of a field changed |
| `:change [id,value]` | A field, a box or a choice was committed (`value` is a boolean for a box) |
| `:toggle [id,open]` | A `<details>` opened or closed |
| `:key.dn [id,key,code]`, `:key.up [id,key,code]` | A key of the page |

The time is emitted at each frame, so `await 1s` works as usual.

| Function | |
|----------|-|
| `web.set(id, name, v)` | Sets a property: `"text"`, `"class.<c>"`, `"style.<p>"`, `"attr.<a>"`, or a property of the DOM (`"value"`, `"checked"`, `"open"`, `"hidden"`, ...) |
| `web.get(id, name)` | Reads a property |
| `web.new(tag, t)` | Creates an element and gives its id (the field `id`, or a fresh one), in the element `parent` or in the body; the other named fields are properties, the positional ones are the ids of its children |
| `web.del(id)` | Removes an element |
| `await web.fetch(url, t)` | A request to a server (`method`, `body` in `t`), as a task: it ends with `[ok, status, text]`, and is cancelled if the task is aborted |

## Other modes

- `atmos-web --pico app.atm out`: a program of [pico][pico], with
  graphics on a canvas, from a checkout of `env-pico` in `../env-pico`
  (or `PICO=<dir>`). The files that it reads are preloaded:
  `atmos-web --pico main.atm out -- --preload-file imgs`.
- `atmos-web --text app.atm out`: only time and `print`, which writes to
  the page ([`clock.atm`](clock.atm), the default environment of Atmos).

# The site

The site at https://ceu-lang.org/new/ is made here:

- [`site/`](site/): the landing page, the page of Atmos, images and
  papers; `site/build.py` builds the whole site, with every step of the
  guides already compiled, so it is only static files.
- [`guides/`](guides/): the text and the exercises of each guide; the
  programs come from [`exs/`](exs/), `env-pico/exs/birds/` and
  `lang/doc/guide.md`.
- [`ide/`](ide/): the player of the guides and a simple IDE, written in
  Atmos over the DOM. `python3 ide/serve.py` serves it with a compile
  server, at http://127.0.0.1:8080/ (only on the machine: it compiles
  what it receives).

To see the whole site on your machine, as it is published (without the
pages of Céu), with the tools of "Use it in your project" and a checkout
of `env-pico` in `../env-pico`:

```
make site           # then open http://127.0.0.1:8091/
```

The workflows: **Tests** builds the site and runs the tests in Chromium
at each push; **Publish the site** publishes it, by hand (Actions, Run
workflow); **Published** says whether the published site is the current
`main`.

# Tests

```
make tests          # or: tst/run.sh [name ...]
```

They build the examples and `tst/*.atm`, serve them, and drive each page
in Chromium with [Playwright](https://playwright.dev/). The site has its
own (`site/test.js`).
