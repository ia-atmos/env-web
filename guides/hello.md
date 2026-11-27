@title Atmos: the first program
@mode pico
@base WEB:exs

# Hello World!

@code hello.atm

The program draws an `X`, gradually, in 3 seconds. Click **Run** to see
it.

Two things happen at the same time. A task, started with `spawn`, draws
the two lines of the `X` at every frame of the screen (`loop on :draw`),
up to the point `n`. The main program advances `n` by one every 30
milliseconds (`await 30ms`). Neither knows about the other's timing:
the task only draws, and the loop only counts.

At the end, `await :key.dn` keeps the picture until a key is pressed
(click on the picture first), and the program ends, with the task
inside it.

### Exercises

1. Draw the `X` in 1 second.
2. Add a third line, across the middle of the screen, that grows with
   the other two.

### Where to go next

1. [Birds](guide/birds/): a small game, built in 11 steps, with
   graphics. The fastest way to see the features of Atmos, one at a
   time. **Recommended.**
2. [A tour of Atmos](guide/atmos/): the guide of the language, one step
   for each example of its documentation.
3. The guide of pico, the graphics library of the tutorial (soon).
