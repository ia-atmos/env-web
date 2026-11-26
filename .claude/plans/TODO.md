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

- `#2`: scope of `env-web` (SDL as a build of `env-sdl`, `env-web` only the DOM; or both here).

## Decided

- `#1` (2026-11-25, "1"; indexed by `atmos` as its `#122`): install emsdk here, build lang locally.

## Work

- [x] Rocks built with emcc, run headless in Chromium (`261125-rocks-emscripten.md`): works, unchanged.
- [ ] Audio in a real browser; the test mode of env-sdl under node or Chromium.
- [x] The old plans of the DOM found and summarized (`261125-dom.md`).
- [x] Prototype of the DOM, branch `proto-dom`: an environment with no step, driven by the page; works in Chromium, no change to lang.
- [ ] Report what works; then the questions of the material, section 3
      (scope, loop, building, assets, DOM, tests, editor), one at a time.

## Index of items

| # | Item | State |
|---|---|---|
| 1 | Install emsdk here, build lang locally | decided 2026-11-25 ("1") |
| 2 | Scope of env-web: (a) SDL as a build of env-sdl, env-web only the DOM; (b) both here | open, recommended (a) |
| 3 | Excerpt, idiomatic: `proto/dom/counter.atm:18-27` (branch `proto-dom`), a parallel clock and the end awaiting an event | shown 2026-11-26 |
| 4 | Excerpt, bad: `proto/dom/counter.atm:10-14`, all clicks in one `:click` filtered by an `if` on a string id; better: elements as values in `web.atm`, the filter in the await | shown 2026-11-26 |
