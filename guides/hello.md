@title Atmos: the first program
@mode pico
@base WEB:exs

# Hello World!

@code hello.atm

The program draws an `X`, pixel by pixel, in 3 seconds. Click **Run** to
see it.

`pico.open()` opens the screen: 100 by 100 pixels, with a grid to help
see where each one goes. The loop counts `i` from 0 to 99 and, at each
turn, draws two pixels: one going down to the right (`x=i`), the other
going down to the left (`x=99-i`). `pico.input.delay(30)` waits 30
milliseconds before the next turn, so that the `X` appears little by
little. Each pixel shows up as soon as it is drawn.

### Exercises

1. Draw the `X` in 1 second.
2. Draw also a horizontal line across the middle of the screen, growing
   from the left at the same time as the `X`.

### Where to go next

1. [Birds](guide/birds/): a small game, built in 11 steps, with
   graphics. The fastest way to see the features of Atmos, one at a
   time. **Recommended.**
2. [A tour of Atmos](guide/atmos/): the guide of the language, one step
   for each example of its documentation.
3. The guide of pico, the graphics library of the tutorial (soon).
