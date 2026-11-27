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

- Before writing Atmos, read `ia-atmos/lang` `.claude/plans/IDIOMS.md` (the
  author's "crie", `atmos#29`, 2026-11-26). When he corrects or approves
  an excerpt here and a general rule comes out, send it to `atmos` with
  `env-web#N`, a before and an after.

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
- [x] `paper-web#7`: `await web.fetch(url, t)`, cancelled with its task (`tst/fetch.atm`).
- [x] `#14a`: the IDE (`ide/`), and `atmos-web --pico` (the runtime and pico cached in `.cache/`).
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
| 14 | A simple IDE as the old one (`atmos-lang/web`: a textarea, Run, a runner in an iframe with the source in the `#` of the URL), two modes (pico, web), the editor in Atmos if possible; the author (2026-11-26): maybe a session `web-ide`, maybe no new repo, a directory `ide/` | decided 2026-11-26 ("#14a", no `#`): a server that compiles; done on `main`: `ide/` (`ide.atm`, `ide.html`, `serve.py`, `test.js`), `atmos-web --pico`; compiling in the page (clang in WebAssembly) not tried |
| 15 | Excerpt, idiomatic: `ide/ide.atm:16-33`, Run as a `watching` that a new click restarts, cancelling the request in course | shown 2026-11-26 |
| 16 | Excerpt, bad: `ide/ide.atm:5-8`, the samples read from hidden textareas of the page, with three nested calls; the language has multi-line strings (`"""`), not used | shown 2026-11-26 |
| 17 | Excerpt (review of code not seen): `web.atm:497-505`, the task of `web.fetch`; good: the `defer` cancels; bad: `(int)$n.u.i` reads inside the value in C | shown 2026-11-26 |
| 18 | Excerpt, idiomatic: `tst/fetch.atm:15-20`, a request cancelled by a `watching` | shown 2026-11-26 |
| 19 | Excerpt, bad: `exs/threads.atm:34` and `tst/form.atm:16`, `c && a \|\| b` as a conditional value | shown 2026-11-26 |
| 20 | Excerpt, bad: `tst/form.atm:8-34`, five `spawn { loop ... on ... }` in a row | shown 2026-11-26 |
| 21 | The guides of Atmos and pico as steps on the web, as ceu-lang.org; the site: `atmos/`, then Céu to `ceu/`, a landing for both (`261126-site.md`) | decided 2026-11-26 ("B"): a compile server on the host; it only compiles, the program runs in the browser. The guide of Atmos exists in `atmos-lang/atmos` `doc/guide.md` (11 of its 24 blocks compile here): to port |
| 22 | Who ports the guide of Atmos to the new compiler | decided 2026-11-26 ("A. Envie para sessão atmos-lang"): `doc/guide.md` in ia-atmos/lang; the request sent to `atmos-lang` with the measurement of the 24 blocks; here: the step player and the compile server |
| 23 | The step player and the first guide (the author, 2026-11-26: "ok, pode seguir. Cada passo deve propor 2 exercícios") | done on `main`: `guides/birds.md` (11 steps of `env-pico/exs/birds`, a text and 2 exercises each; the programs stay in env-pico), shown by the IDE at `/guide/birds`; the 11 compile and run in Chromium; the exercises were not solved by the session |
| 24 | Excerpt, idiomatic: `ide/ide.atm:34-48`, the loop of a step: load, then await one of four events and `match` on its id | shown 2026-11-26 |
| 25 | Excerpt, bad: `ide/ide.atm:22-27`, the three lines of `/info` cut with `string.find` and `string.sub` | shown 2026-11-26 |
| 26 | The guide of Atmos as steps (lang 5d5ad76, `doc/guide.md`, 21 examples, from `atmos-lang`) | done on `main`: `guides/atmos.md` has only the 42 exercises; the text and the programs are read from the checkout of lang; `atmos-web --text` and `clock.atm` (the default environment in the browser); the 21 programs print in Chromium what their `.out` files have |
| 27 | The plan of the host of ceu-lang.org | answered 2026-11-26: DreamHost "Shared Unlimited" |
| 28 | How Run works on the site, on a shared host | decided 2026-11-26 ("c"): try to compile on DreamHost itself (CGI); first a probe: `site/probe.sh`, run over SSH by the workflow `probe.yml` (secrets of the repository) or by him |
| 29 | How the probe of the host runs | the author (2026-11-27): "antes de tudo, quero saber se consigo compilar lá. hoje consigo compilar programas ceu e roda-los": the probe has two stages now (`sh site/probe.sh`, quick, installs nothing; `sh site/probe.sh full`); he runs it by SSH and pastes the output (#29b); the workflow `probe.yml` stays for later |
| 30 | Where env-web publishes first (`atmos-beta/` or `atmos/`): the old workflow of atmos-lang/web runs `rsync --delete` into `atmos/` | open, after the probe |
| 31 | A dedicated server in the future (compile server and a Freechains node): sizing measured, offers read from the official pages (`261127-server.md`) | answered 2026-11-27 as information (the author asked for it); the next step is asked as #32 |
| 33 | Result of the quick stage of the probe on the shared DreamHost (pdx1-shared-a1-41), run by the author on 2026-11-27 | glibc 2.39, 128 cores, 515 GB, gcc 13, python3, node 18, git, make: all present; 1 GB in a process and 6 processes: OK; the only FAIL was a flaw of the probe (it ran the test program in `/tmp`, which is `noexec`): fixed, with the quota and the usage of the user added. Next: the full stage (`sh probe.sh full`) |
| 34 | Result of the full stage of the probe on the shared DreamHost, run by the author on 2026-11-27 | the C side works (gcc 13, glibc 2.39, 43 GB used in his home, `lang` builds, emsdk installs in 34 s, 1.6 GB); **the node of Emscripten dies** at start with a V8 fatal error in `OS::SetPermissions` (its check expects ENOMEM and got another errno), so `emcc` cannot run; no page was built. Cause not confirmed: the kernel is `grsec` (PaX can forbid the memory permission changes of a JIT); the system node 18 was not tried. `atmos prog.atm` also failed (status 127): lang builds in a hard-coded `/tmp`, which is `noexec` there. Measured here: `--jitless` gives byte-identical pages (web 1.4 s to 2.3 s, pico about the same). Next: `sh probe-node.sh` (a second probe: the cause, and the options) |
