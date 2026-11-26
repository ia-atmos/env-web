# env-web

An environment of the browser for [Atmos][atmos]: the page (the DOM) as
events and properties, with the program compiled to WebAssembly through
[Emscripten][emcc].

An event of the page becomes an event of the program, and an element is
named by its `id`, as in the HTML, so the logic of a page is written as
a sequence in time:

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

- [`web.atm`](web.atm): the environment (its header documents the API).
- [`atmos-web`](atmos-web): builds a page from a program.
- [`exs/`](exs/): `counter` (the program above, over `counter.html`) and
  `threads` (a tree of threads that the program creates).
- [`tst/`](tst/): the tests, in Chromium (`make tests`).

Status: experimental. The plan is in [`.claude/plans/`](.claude/plans/).

[atmos]: https://github.com/ia-atmos/lang
[emcc]:  https://emscripten.org/

# Run

It needs `emcc` in the PATH, and the compiler built in `../lang` (or
`ATMOS=<dir>`):

```
git clone https://github.com/ia-atmos/lang
make -C lang
./atmos-web exs/counter.atm out      # out/counter.html, .js, .wasm
(cd out && python3 -m http.server)   # open http://localhost:8000/counter.html
```

If `<prog>.html` exists beside the program, it is the page, with the
line `{{{ SCRIPT }}}` where the program is loaded. Otherwise the page is
empty, and the program creates its elements with `web.new`.

# Interface

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
| `web.set(id, name, v)` | Sets a property: `"text"`, `"class.<c>"`, `"style.<p>"`, or a property of the DOM (`"value"`, `"checked"`, `"open"`, `"hidden"`, ...) |
| `web.get(id, name)` | Reads a property |
| `web.new(tag, t)` | Creates an element and gives its id (the field `id`, or a fresh one), in the element `parent` or in the body; the other named fields are properties, the positional ones are the ids of its children |
| `web.del(id)` | Removes an element |
| `await web.fetch(url, t)` | A request to a server (`method`, `body` in `t`), as a task: it ends with `[ok, status, text]`, and is cancelled if the task is aborted |

# Tests

```
make tests          # or: tst/run.sh [name ...]
```

They build the examples and `tst/*.atm`, serve them, and drive each page
in Chromium with [Playwright][pw].

[pw]: https://playwright.dev/
