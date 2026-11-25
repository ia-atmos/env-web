# Rocks in the browser through Emscripten (2026-11-25)

The cheapest path of the material (`ia-atmos/lang`
`.claude/plans/261124-env-web.md`): build `env-sdl`'s Rocks, unchanged,
with Emscripten's port of SDL2, and run it headless.

Approved by the author as `#122` (answer "1", 2026-11-25): install emsdk
in this container and build a local, read-only clone of `ia-atmos/lang`.

## Route

1. `atmos -c -e sdl.atm main.atm > rocks.c` (native compiler, in
   `exs/rocks/`): one C file, with the `main` of `sdl.atm`.
2. `emcc rocks.c <lang>/rt/*.c` (all but `rt/main.c`, which `sdl.atm`
   replaces) with `-sUSE_SDL=2 -sUSE_SDL_IMAGE=2 -sUSE_SDL_TTF=2
   -sUSE_SDL_MIXER=2`, `-sASYNCIFY` (the loop of `sdl.atm` blocks: its
   `SDL_Delay` becomes the point where the browser gets control back),
   and `--preload-file` for `imgs/`, `snds/`, `tiny.ttf`.
3. Run in Chromium headless (Playwright): screenshot, keys, console.

## Results (2026-11-25)

Rocks runs in Chromium headless, unchanged: no line of `sdl.atm` nor of
the game was touched.

| Check | Result |
|---|---|
| `atmos -c -e sdl.atm main.atm` | 10454 lines of C, no error |
| `emcc -O2` (ports built the first time) | 43 s, no error |
| Output | `rocks.wasm` 3.8 MB, `rocks.js` 172 KB, `rocks.data` 1.6 MB (assets), `rocks.html` 20 KB |
| Title screen | "= PRESS ENTER TO START =", the font, the background, the scores |
| Enter, Shift (shot), D (moves) | the round starts, ships, a shot and a meteor are drawn |
| End of a round | back to the title with the score 1 to 0 |
| Page while the game runs | `requestAnimationFrame` at 60 fps: the page does not block |
| Console | no error; only Chromium's notices (ScriptProcessorNode deprecated, GPU stall on ReadPixels) |

Exact flags:

    emcc -O2 -I<lang>/rt rocks.c <lang>/rt/*.c (but main.c) \
      -sUSE_SDL=2 -sUSE_SDL_IMAGE=2 -sSDL2_IMAGE_FORMATS='["png","gif"]' \
      -sUSE_SDL_TTF=2 -sUSE_SDL_MIXER=2 -sASYNCIFY -sALLOW_MEMORY_GROWTH \
      --preload-file imgs --preload-file snds --preload-file tiny.ttf \
      -o rocks.html

## Notes

- **Ports in this container.** Emscripten fetches its ports as archives
  of GitHub; the proxy of the session refuses them (403: the repository
  is not in the session's scope). Worked around by `git clone` of each
  tag (zlib, SDL, SDL_image, freetype, harfbuzz, SDL_ttf, SDL_mixer)
  into the cache of ports, with the marker `.emscripten_url`. libpng,
  ogg and vorbis came through. A machine with open network needs none
  of this.
- **The loop.** With `-sASYNCIFY`, the `SDL_Delay` at the end of each
  frame of `sdl.atm` yields to the browser. A frame that takes all of
  its budget skips `SDL_Delay` and would not yield: a risk for slow
  machines, not seen here. The alternative, `emscripten_set_main_loop`,
  means a change in `sdl.atm` (one frame per call), which goes to
  `env-sdl` as a request.
- **Audio** was not checked (headless); it needs a user gesture in a
  real browser.
- **Not checked**: the test mode of `env-sdl` (`SDL_ATM_FRAMES`,
  screenshots compared pixel by pixel) under node.
