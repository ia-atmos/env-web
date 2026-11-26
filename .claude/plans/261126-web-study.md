# How others bind a program to the DOM (2026-11-26)

Asked by the author on `#10`: "Pode estudar outros casos parecidos pra
ver como fizeram?". Sources: `env-iup` and the old plan (read here),
`html5.h` of the installed Emscripten (read here), a measurement in
Chromium (below); the others from memory of their documentation, not
fetched again (marked M).

## The cases

| Case | How an element is named | How an event arrives | How the page is changed | For us |
|---|---|---|---|---|
| Emscripten `html5.h` (C) | a string: a CSS selector (`"#inc"`), or the document/window | a C callback registered per target and per kind (`emscripten_set_click_callback(target, data, useCapture, f)`); it returns a bool: "consumed" (prevents the default) | not covered: `EM_JS` by hand | strings as names are the native way from C; the bool of the default is a need we have not covered |
| Wasmoon / Fengari (Lua; the old plan) (M) | a JS object reflected into Lua (`doc:getElementById`) | a Lua function passed to `addEventListener` | the whole DOM API, line by line as JS | generic and complete, but callbacks, and nothing of the language's own |
| Go `syscall/js`, Rust `web-sys` (M) | a reflected value / a typed handle | a closure that must be kept alive and released by hand | the whole DOM API (typed in Rust) | the cost of handles and of callbacks' lifetime: we have neither with ids and events |
| Tcl/Tk (M) | a string, the path of the widget (`.f.b`) | `bind .b <Button-1> script` | `.b configure -text "x"`: one verb, the text an option as any other | the precedent of names as strings, and of `text` under `set` |
| IUP / `env-iup` | a handle | callbacks, here events `:action [h]` | `IupSetAttribute(h, "TITLE", v)`: one verb, attributes as strings | `set`/`get`/`new` come from here |
| jQuery (M) | a selector (`$("#inc")`, also classes: many at once) | `.on("click", f)`; delegated: `$(document).on("click", "#inc", f)` | split verbs: `.text()`, `.val()`, `.attr()`, `.prop()`, `.css()`, `.addClass()` | the split exists because attribute, property, style and class are four things in the DOM: our `set` needs the prefixes (`class.x`, `style.x`) to say which |
| htmx / hyperscript (M) | selectors written in the HTML | attributes in the HTML (`on click ...`) | `put it into #count` | ids as targets read well |
| Elm (M) | none: the program never touches an element | messages (`onClick Inc`): data, not callbacks; a decoder picks the fields of the event | a `view` rebuilt from the state, diffed | events as data is our model; the declarative view is another style (not Atmos's sequence in time) |
| HipHop.js (Esterel on the web) (M) | attributes bound to signals | DOM events become input signals of a synchronous reaction | output signals bound to attributes of the page | the nearest relative: events in, reactions, effects out; we do the same with `await` and `web.set` |

## Measured: which events reach one listener on the document

Chromium headless, one listener per kind on `document`, bubbling and
capture:

| Event | Bubbling | Capture |
|---|---|---|
| `click`, `input`, `change` | arrives | arrives |
| `toggle`, `focus`, `blur` | does not arrive | arrives |

So the delegation of the proposal must listen in the capture phase.
A click on a `<span>` inside a button has the span as its target: the
"nearest element with an id" of the proposal is needed.

## What changes in the proposal

- Listeners in the capture phase (measured above).
- `web.new` gives back the id: the one given, or a fresh one
  (`web1`, ...) when none is: a child is then named with no invention
  by the program (the lists of Elm and jQuery need a name per item).
- Open, to decide later: preventing the default (a link, the submit of a
  form), which `html5.h` and Elm both have; a selector in place of an id
  (jQuery: many elements at once); `:focus`.
- Kept: ids as strings (html5.h, Tk, htmx), one `set` with `text` as a
  property (Tk, IUP), events as data with fixed fields (Elm), no
  callbacks and so no lifetimes (against Go and Rust).
