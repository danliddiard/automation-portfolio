# The auto sequencer's jogs were being killed by the manual routine

Found on the bench, the first time the cell actually ran in auto. Symptom: each step took
its full 1.8 s, but the axis twitched an inch or two instead of traversing, and
`Act_Vel_14x` blipped up and died instead of holding at 10 in/s.

## The interaction

`Manual_Conv` has a "jog release" rung per axis, meant to stop a manual jog when the
operator lets go of the button:

```
XIO(Jog_141) XIC(MAJ_141.IP) MAS(Zippy_Axis_141,MAS_141,1,...)
 │            │               └ stop the jog
 │            └ a jog is in process
 └ but nobody is pressing the manual jog button
```

Read it in auto mode and the flaw is plain. `AutoSeq_V5` starts a jog, `MAJ_141.IP` goes
true, and `Jog_141` is false because no operator is touching the manual screen — so the rung
is true and issues an MAS. `MainRoutine` calls `Manual_Conv` immediately after `AutoSeq_V5`,
so the auto jog is stopped roughly one scan after it starts. Every step. Every axis.

The **start** rung was gated correctly:

```
XIC(Mode_Manual) XIC(Enable_141) XIC(Jog_141) MAJ(...)
```

The **release** rung was not. The "do" was gated and the "undo" was forgotten — the same
asymmetry that produces most cross-mode bugs.

## The fix

One contact, five rungs (9, 19, 29, 39, 49):

```
XIC(Mode_Manual) XIO(Jog_141) XIC(MAJ_141.IP) MAS(...)
```

That is the rung's actual intent — release a *manual* jog — and it matches how every other
manual rung in the routine is written.

The `Stop_14x` rungs are deliberately left ungated. They fire only on a deliberate operator
press, and a stop that works in auto as well as manual is worth keeping.

## Why axis 145 looked different

The clue that made this findable. Every axis gets one forward jog and one reverse jog per
cycle, and for four of them those are about fourteen seconds apart. 145 is the far end of the
run, so its two commands land in consecutive steps:

| Step 6 | MAS 144, **MAJ 145 forward** |
| Step 7 | **MAJ 145 reverse** |

Two twitches back to back reads as "145 moves more." It was the only axis whose behaviour
differed, and the difference pointed straight at *how many times a MAJ gets issued*, rather
than at speeds or scaling.

## `Stop_PB` also shipped latched

Separately, `Stop_PB` was stored as `1` in every earlier file — the original `V6_1` export was
taken with the stop button held, which is also why `Seq_Step` was 99 and `Stop_TMR` was
mid-hold. Resetting `Seq_Step` and `Stop_TMR` in an earlier pass fixed the symptoms and missed
the cause; `AutoSeq_V5` rung 1 then unlatched `Auto_Running` on every scan and no start press
could ever hold. `V7_6` ships `Stop_PB = 0`.

`Mode_Manual` still ships as `1`. That one is deliberate — powering up in manual is a correct
default, and selecting auto should be an explicit act.

## Expected after the fix

| | Before | After |
|---|---|---|
| `Act_Vel_14x` mid-step | blips to ~2, dies | holds ~10 for most of the step |
| Travel per step | an inch or two | ~18 in |
| Step duration | 1.8 s | 1.8 s, unchanged |
| 145 vs the others | 145 moves more | all five alike |

The last row is the clean confirmation: once jogs are not being killed, the
two-commands-in-a-row asymmetry stops being visible.
