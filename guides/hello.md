@title Atmos: the first program
@mode text
@base WEB:exs

# Ticks

@code hello.atm

During 5 seconds, the program counts a tick every second, and then
prints `Bye!`. Click **Run** to see it.

`loop i` repeats its body forever, with `i` counting from 0: it prints
`Tick` and `i`, and awaits one second. On its own, the loop never ends.
`watching 5s` runs its block for 5 seconds, and then aborts it,
wherever it is: here, while the loop awaits, after `Tick 4`. Nothing in
the loop knows about the 5 seconds. Then the program goes on after the
block, and prints `Bye!`.

This is the idea of Atmos: a block that ends takes everything inside it
along.

### Exercises

1. Count a tick every half second, during 3 seconds.
2. Change only the `watching`, so that the program stops after `Tick 2`.

### Where to go next

1. [Birds](guide/birds/): a small game, built in 11 steps, with
   graphics. The fastest way to see the features of Atmos, one at a
   time. **Recommended.**
2. [A tour of Atmos](guide/atmos/): the guide of the language, one step
   for each example of its documentation.
3. The guide of pico, the graphics library of the tutorial (soon).
