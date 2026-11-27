@title Birds: a tutorial of Atmos with pico
@mode pico
@base PICO:exs/birds
@preload res

The programs of this guide are those of `exs/birds/` of
[env-pico](https://github.com/ia-atmos/env-pico): this file only has
the text of each step and its exercises. Click on the picture before
using the keyboard.

# 1. A task

@code birds-01.atm

A bird is a **task**: a piece of the program with its own variables
(`xx`, `yy`, `img`) that lives in time. `task Bird (y, speed)` declares
it, and each `spawn Bird(...)` starts one. Two birds are two instances
of the same code, each at its height and with its speed.

Inside the task, a `par` keeps two loops alive together. One awaits the
clock (`loop us on :clock`) and moves the bird by the time that passed.
The other awaits the moment of drawing (`loop on :draw`) and draws the
image of the bird, wings up or down, where it is.

The last line, `await false`, awaits what never happens: the program
stays alive while its tasks run.

### Exercises

1. Spawn a third bird, between the two, faster than both.
2. Make the birds cross the screen at half of their speed, without
   changing the arguments of the `spawn`s.

# 2. A scope

@code birds-02.atm

The two birds are now spawned inside a `loop`, and the loop awaits a
click of the mouse (`await :mouse.button.dn`) before it turns.

A task belongs to the block that spawns it. When the click arrives, the
turn of the loop ends, its block ends, and the two birds are aborted
with it. The next turn spawns two new ones, from the left. Nothing in
the program removes a bird by hand: the **scope** does it.

### Exercises

1. Restart the birds with any key instead of the mouse (the event is
   `:key.dn`).
2. Restart them by themselves, every 3 seconds, with no input.

# 3. A pool

@code birds-03.atm

Five birds, spawned in a loop. A task spawned in a loop would be
aborted at the end of each turn, as in the last step. To keep them, the
program creates a **pool**, `pin birds = tasks()`, and spawns each bird
into it: `spawn @birds Bird(...)`. The birds now live as long as the
pool, which lives as long as the block that declares it.

The height and the speed of each bird come from the counter of the
loop.

### Exercises

1. Spawn 8 birds, evenly spaced, that still fit on the screen.
2. Make the bird at the top the fastest, and the one at the bottom the
   slowest.

# 4. A bounded pool

@code birds-04.atm

A new bird every half second (`loop on 500ms`), at a random height and
with a random speed. The `where` gives names to the arguments of the
`spawn`, computed just for it.

The pool is now **bounded**: `tasks(5)` holds at most 5 birds. While it
is full, a `spawn` into it fails and no bird is created. As no bird
ever ends, the first five are the only ones.

### Exercises

1. Let the pool hold 10 birds.
2. Spawn a bird every 2 seconds, and see how long the pool takes to
   fill.

# 5. Termination

@code birds-05.atm

The body of the bird is now inside `watching until (xx>1)`: the block
runs until the condition holds, that is, until the bird leaves the
screen on the right. Then the `watching` ends, the task ends, and its
place in the pool is free for the next `spawn`.

The program never deletes a bird: a task that reaches its end is
removed from its pool.

### Exercises

1. End a bird when it reaches the middle of the screen.
2. End a bird 3 seconds after it is born, wherever it is (a `watching`
   also accepts a time, as `watching 3s`).

# 6. A pool in a scope

@code birds-06.atm

Steps 2 and 5 together. The pool is declared inside a `watching
:mouse.button.dn`, inside a `loop`. A click ends the `watching`, the
pool goes with its block, and every bird goes with the pool. The next
turn of the loop starts with an empty sky.

### Exercises

1. Clear the sky with the key `C` instead of the mouse (the pattern is
   `:key.dn [key='C']`).
2. After a click, wait 1 second with an empty sky before the birds come
   back.

# 7. Collisions

@code birds-07.atm

Each bird now publishes its rectangle: `set pub = [rect=rect]`. The
**public data** of a task is read from outside as `b.pub`.

A third branch of the main `par` checks, at each tick of the clock,
every pair of birds of the pool (`loop _,b1 in birds`). When two
rectangles overlap, it emits `:collided` to each of the two tasks only
(`emit @b1 :collided`).

The bird watches for it: `watching <:collided || until (rect.x>1)>`
ends on the event or when the bird leaves the screen, whichever comes
first. Two birds that touch disappear.

### Exercises

1. Make a collision remove only one of the two birds.
2. Count the collisions and print the total at each one (`print`
   writes to the console of the browser).

# 8. A fall

@code birds-08.atm

A bird that collides no longer disappears: it falls. The life of the
bird is now a **sequence**: first it flies, inside `watching
:collided`; when that ends, the task goes on to the next lines, and the
bird falls until it reaches the ground (`watching until (rect.y>0.9)`).
The outer `watching until (rect.x>1)` still covers both phases.

Between the two, `set pub.alive = false` tells the others that this
bird no longer counts, and the check of collisions skips it.

### Exercises

1. Make the fall twice as fast.
2. Make a bird that falls also drift to the left while it goes down.

# 9. A blink

@code birds-09.atm

After the fall, the bird stays on the ground for one second, blinking,
and only then ends. The blink is written as it happens: inside
`watching 1s`, a loop awaits 100ms showing nothing, and then draws the
bird for 100ms (`watching 100ms { loop on :draw {...} }`).

No variable holds "which phase am I in": the phase is the line where
the task is.

### Exercises

1. Make the bird blink for 3 seconds.
2. Make it blink slowly: half a second on, half a second off.

# 10. Tracking

@code birds-10.atm

A click on a bird draws a line from the bottom of the screen to it,
while it lives.

The block `do :Track {...}` awaits clicks and looks for a living bird
under the mouse; when it finds one, `escape(:Track, b)` leaves the block
with that bird as its value. Then `watching (bird)` runs until that
task ends: the line follows the bird, by its public rectangle, and
disappears with it. The loop goes back to await the next click.

### Exercises

1. Start the line at the top left corner of the screen.
2. Stop tracking a bird as soon as it collides, and not only when it
   ends (its `pub.alive` says it).

# 11. A pause

@code birds-11.atm

The key `P` pauses the game and shows an image; `P` again resumes it.

Everything of the game is now inside `mute on :Pause {...}`. A task
beside it awaits the key, emits `:Pause [true]`, draws the image until
the key comes again, and emits `:Pause [false]`. While it is muted, the
block receives no events: no clock, no drawing, no clicks. The birds
stop where they are, and continue from there.

The game itself has no line about pausing.

### Exercises

1. Pause with the space bar (see how the key is named in the event
   with a `print`).
2. Leave the birds flying during the pause, and freeze only the
   creation of new ones.
