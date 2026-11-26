# TODO (env-web)

Items put to the author are local to this session (`#1`, `#2`, ...;
`env-web#N` from outside), rule `#71` of `ia-atmos/lang` `TODO.md`.

## Standing

- At each big step (a milestone, a change of what is on screen), show the
  author a few screenshots in the report (his recommendation of
  2026-11-26, relayed by `atmos`).
- For each group of changes, show one pair of short Atmos excerpts from
  that work, with file and line: one idiomatic, one bad (awkward,
  verbose, a workaround) (his rule of 2026-11-26, relayed by `atmos`).
  Each excerpt takes a `#N` of this session, listed in the index below;
  each bad one says why, and what would make it better.

## Open with the author

- `#5`: where the browser build of pico lives (`261126-pico.md`).

## Decided

- `#1` (2026-11-25, "1"; indexed by `atmos` as its `#122`): install emsdk here, build lang locally.

## Work

- [x] Rocks built with emcc, run headless in Chromium (`261125-rocks-emscripten.md`): works, unchanged.
- [ ] Audio in a real browser; the test mode of env-sdl under node or Chromium.
- [x] The old plans of the DOM found and summarized (`261125-dom.md`).
- [x] Prototype of the DOM, branch `proto-dom`: an environment with no step, driven by the page; works in Chromium, no change to lang.
- [x] `#10a`: `web.atm` with `set`, `get`, `new`, `del` and the events by capture; `exs/counter`, `exs/threads`, `tst/form`; 26 checks pass in Chromium.
- [ ] Open in the API: preventing the default, selectors, `:focus`, the clock in a hidden tab (`requestAnimationFrame` stops), `atm_quit` at the end.
- [x] `paper-web#11`: sizes and time to start (`261126-measures.md`).
- [ ] `paper-web#7`: a request to a server (`fetch`) as an await, cancelled by a `defer` (for the type-ahead example of the paper).
- [ ] `paper-web#6`: the seven 7GUIs on the web (`exs/7guis/`), close to those of env-iup; report what the API lacked.
- [ ] Report what works; then the questions of the material, section 3
      (scope, loop, building, assets, DOM, tests, editor), one at a time.

## Index of items

| # | Item | State |
|---|---|---|
| 1 | Install emsdk here, build lang locally | decided 2026-11-25 ("1") |
| 2 | Scope of env-web: (a) SDL as a build of env-sdl, env-web only the DOM; (b) both here | answered 2026-11-26: Rocks is the one of pico, and web has pico; asked again as `#5` |
| 3 | Excerpt, idiomatic: `proto/dom/counter.atm:18-27` (branch `proto-dom`), a parallel clock and the end awaiting an event | shown 2026-11-26 |
| 4 | Excerpt, bad: `proto/dom/counter.atm:10-14`, all clicks in one `:click` filtered by an `if` on a string id; better: elements as values in `web.atm`, the filter in the await | shown 2026-11-26; the author: "Veja como iup faz"; redone as env-iup (`proto-dom` cbdce53) |
| 5 | Where the browser build of pico lives: (a) env-web: builds pico.atm and pico-sdl of a checkout of env-pico at a fixed commit, and adds the DOM; (b) env-pico: a target `web` of its Makefile, env-web only the DOM | the author (2026-11-26): two envs, web and pico, one pico only, maybe flags in the original; asked as `#8`; then: no builds in env-pico, only ifdefs set from outside; `SDL_INIT_EVERYTHING` stays, with an ifdef of emcc |
| 6 | Excerpt, idiomatic: `proto/dom/counter.atm:12-25` (`proto-dom` cbdce53), the counter in the style of env-iup | shown 2026-11-26 |
| 7 | Excerpt, bad: `proto/dom/counter.atm:4-8`, five `pin x = web.get("id")` that repeat the ids of the HTML | the author: why `new`, why not the id instead of `h`? Done: `proto/dom-id` (841a304), `:click [id="inc"]`, test passes; asked as `#9` |
| 8 | Repos: env-web (ia-atmos/env-web) the DOM, env-pico (ia-atmos/env-pico) pico, its browser build as flags/target in its own Makefile | corrected 2026-11-26: env-pico has no build of the browser, only ifdefs set from outside (`__EMSCRIPTEN__`); the build is outside (env-web) |
| 9 | The DOM by ids (`:click [id="inc"]`, `web.text("count", s)`) instead of handles | the author asked for the whole API: `261126-web-api.md` |
| 10 | The API of `261126-web-api.md` as the base of env-web | the author: "Text e set parecem colidir": `web.text` removed, `text` a property of `set`/`get`; then (2026-11-26): "A princípio a proposta parece boa", and asked a study of similar cases: `261126-web-study.md`; decided 2026-11-26 ("#10a"): implemented on `main` (`web.atm`, `atmos-web`, `exs/`, `tst/`) |
| 11 | A session `paper-web` (the author, 2026-11-26: "Depois criar uma sessão paper-web ... comparar com elm,hiphop e outros. Mande um plano pra lá") | plan written (`261126-paper-web.md`); created by `atmos` on 2026-11-26: session_011eECoei7PA2fA6jzUtWpqz, in ia-atmos/lang (the plan copied to its `.claude/plans/261126-paper-web.md`, d0d1c80); it writes `papers/web.md`; this session answers its questions and takes the requests of section 6 |
| 12 | Excerpt, idiomatic: `exs/threads.atm:13-26`, a thread as a task whose `defer` removes its element | shown 2026-11-26 |
| 13 | Excerpt, bad: `exs/threads.atm:40-45`, `loop _,t in threads { abort t ; break }` to abort the first task of a pool | the author (2026-11-26): "nao poderia guardar a 1a por fora? pq remover a 1a mesmo?": the case was artificial; redone: each thread has its own button and ends itself (`watching :click [id=x]`), no iteration of the pool; then he explained: spawn in the pool and keep the reference outside (`val first = spawn @threads Thread(1)`, `abort first`): tested, works; nothing missing in the language; acknowledged |
| 14 | A simple IDE as the old one (`atmos-lang/web`: a textarea, Run, a runner in an iframe with the source in the `#` of the URL), two modes (pico, web), the editor in Atmos if possible; the author (2026-11-26): maybe a session `web-ide`, maybe no new repo, a directory `ide/` | open: where the compilation runs (the old one interpreted Lua in the page; Atmos needs a C compiler: a server, or clang in the page) |
