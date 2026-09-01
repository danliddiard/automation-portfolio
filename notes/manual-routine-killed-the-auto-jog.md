# Note: the manual routine was stopping every auto jog

**Where this goes:** LinkedIn or a talk track. It is the best kind of bug — two routines that are each correct on their own.

A five-axis conveyor ran its auto sequence, the step timer advanced on schedule, and every axis moved about an inch instead of eighteen. Velocity blipped and died instead of holding at the commanded 10 in/s.

The auto sequencer was not the problem. The **manual** routine was.

`Manual_Conv` has a per-axis "jog release" rung, so the axis stops when the operator lets go of the manual jog button:

```
XIO(Jog_141) XIC(MAJ_141.IP) MAS(Zippy_Axis_141, MAS_141, 1, ...)
```

In auto, the sequencer starts a jog, `MAJ_141.IP` goes true, and `Jog_141` is false because nobody is touching the manual screen. The rung fires and stops the jog. `MainRoutine` calls `Manual_Conv` immediately after the sequencer, so it happened about one scan after every jog started, on every step, on every axis.

The jog *start* rung was gated with `XIC(Mode_Manual)`. The jog *release* rung was not. The "do" was gated and the "undo" was forgotten.

**The clue was that one axis looked different.** Axis 145 appeared to move further than the rest. It is the far end of the run, so its forward and reverse commands land in consecutive steps rather than fourteen seconds apart — two twitches back to back. That pointed at *how many times the instruction was being issued*, not at speed or scaling, which is where the search had been.

Fix / practice:

- Gate the undo wherever you gate the do. Check every "release", "reset" and "clear" rung against the permissive on the rung that started the thing.
- A `.IP` bit is not private to the routine that set it. Any status bit is shared state between routines, and a rung that reads one is coupled to every rung that can cause it.
- When one instance of a repeated block behaves differently from the other four, ask what is different about *its position in the sequence* before you touch tuning or scaling.
- Symptom triage: the step timer running normally while the motion did not is the tell that the sequencer was fine and something else was intervening.

Caveat: diagnosed by reading the ladder and confirmed against the observed behaviour. The one-contact fix has not yet been run on hardware.
