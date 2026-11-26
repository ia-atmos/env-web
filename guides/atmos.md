@title A tour of Atmos
@mode text
@source ATMOS:doc/guide.md
@base ATMOS:tst/guide
@link https://github.com/ia-atmos/lang/blob/main/doc/

The text and the programs of this guide are those of `doc/guide.md` of
[the compiler](https://github.com/ia-atmos/lang), one step for each of
its examples: this file only adds the exercises, under the name of each
example.

# 01-tasks

1. Spawn a third task, and see the three lines.
2. Emit `:Y` before `:X`. Why does nothing print at that point?

# 02-clock

1. Count 5 half seconds (`500ms`) instead of 3 seconds.
2. Print the number of each second: `1`, `2`, `3` (a loop gives its
   counter with `loop i in 3`, from 0).

# 03-scheduling

1. Swap the two `spawn`s in the source. Write down the output you
   expect before you run it.
2. Add a second `emit :X` before the last line. What does it print, and
   why?

# 04-timers

1. Make the first branch await `20ms`. Which lines print now?
2. Emit the 30ms as three ticks of `10ms`, one after the other. Does the
   output change?

# 05-hierarchy

1. Swap the two `emit`s, so that `:Y` comes first. What prints now?
2. Move the nested `spawn` out of the outer task, to the top of the
   program. What prints now?

# 06-pin

1. Spawn a second task, `u`, in the same block. In which order are the
   two aborted?
2. Remove the `do` and its braces, and keep the lines inside. When is
   `t` aborted now?

# 07-defer

1. Give the outer task a `defer` of its own. Which of the two runs
   first?
2. Make the nested task end by itself: it awaits `:Y`, and the program
   emits `:Y` before `:X`. Does its `defer` still run?

# 08-defer-block

1. Add a third `defer` at the end of the block. Where does its line
   appear in the output?
2. Move the `spawn` to after the two `defer`s. How does the order
   change?

# 09-loop-on

1. Change one number so that the line prints exactly 5 times.
2. Count the iterations in a variable, and print the count in each
   line.

# 10-watching

1. Remove the `emit :X`, and end the program with `await 2s`. What
   prints, and when?
2. Watch for an event, `:Stop`, in place of `1s`, and emit `:Stop`
   before `:X`. What prints?

# 11-par-all

1. Change `par :all` to `par :any`. What prints?
2. Emit only two of the three events. Which line is missing?

# 12-pub

1. Expose a table with two fields, as `[x=1, y=2]`, and print one of
   them.
2. Give the task a parameter that becomes its `pub`, spawn two tasks,
   and print the sum of their `pub`s.

# 13-pools

1. Wait `350ms` in place of `250ms`. Which tasks are still pending?
2. After the loop over the pool, wait `100ms` more and traverse the
   pool again.

# 14-mute

1. Remove the line `mute t(false)`. What prints?
2. Spawn a second task that is never muted. Which one awakes at the
   first `emit`?

# 15-mute-on

1. Pause for `1s` in place of `300ms`. Does the output change?
2. Add a second loop, outside the `mute on`, that prints `tick` every
   100ms, and see it go on during the pause.

# 16-errors

1. Throw `:Z` in place of `:Y`. What happens to the program?
2. Move the `catch` into the task `T`, around its nested `spawn`.

# 17-traces

1. Catch the error in the main body, with `catch :negative`, and print
   it in place of the trace.
2. Call `check` with a positive number. What prints?

# 18-loop-on-events

1. Print only the values greater than 2.
2. Keep the sum of all the values, and print it at each occurrence.

# 19-task-sequence

1. Count 3 complete executions of `XY`, with the `emit`s for the third.
2. Change `XY` so that it needs two `:X` before a `:Y`.

# 20-iter

1. Keep only the even values, and print their sum.
2. Find the first value greater than 6, with `iter.find`.

# 21-iter-pool

1. Print the `pub` of every task, with a loop over the pool
   (`loop _, t in ts`).
2. Emit `:Stop`, and then count the tasks that are left in the pool.
