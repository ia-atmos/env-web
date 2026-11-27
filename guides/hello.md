@title Atmos: the first program
@mode text
@base WEB:exs

# Hello World!

@code hello.atm

During 5 seconds, the program prints `Hello World!` every second. Click
**Run** to see it.

`loop on 1s` runs its body every second, forever. `watching 5s` runs its
block for 5 seconds, and then aborts it: the loop inside stops, wherever
it is. Nothing in the loop knows about the 5 seconds. This is the idea
of Atmos: a block that ends takes everything inside it along.

### Exercises

1. Print `Hello World!` every half second, during 3 seconds.
2. After the `watching`, print `Bye!`. When does it appear?

### Where to go next

1. [Birds](guide/birds/): a small game, built in 11 steps, with
   graphics. The fastest way to see the features of Atmos, one at a
   time. **Recommended.**
2. [A tour of Atmos](guide/atmos/): the guide of the language, one step
   for each example of its documentation.
3. The guide of pico, the graphics library of the tutorial (soon).
