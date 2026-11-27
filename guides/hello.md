@title Atmos: the first program
@mode text
@base WEB:exs

# A countdown

@code hello.atm

The program counts down from 5, one number per second, and then prints
`Liftoff!`. Click **Run** to see it.

`loop i` repeats its body forever, with `i` counting from 0: it prints
`5 - i` and awaits one second. `watching 5s` runs its block for 5
seconds, and then aborts it, wherever it is: here, while the loop awaits
its fifth second, so `0` is never printed. Nothing in the loop knows
about the 5 seconds. Then the program goes on after the block, and
prints `Liftoff!`.

This is the idea of Atmos: a block that ends takes everything inside it
along.

### Exercises

1. Count down from 10, one number every half second.
2. Change only the `watching`, so that the countdown stops after `3`.

### Where to go next

1. [Birds](guide/birds/): a small game, built in 11 steps, with
   graphics. The fastest way to see the features of Atmos, one at a
   time. **Recommended.**
2. [A tour of Atmos](guide/atmos/): the guide of the language, one step
   for each example of its documentation.
3. The guide of pico, the graphics library of the tutorial (soon).
