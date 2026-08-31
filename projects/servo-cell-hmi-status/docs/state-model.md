# Seq_Status state model

`Seq_Status` is a **DINT written by exactly one routine** (`HMI_Status`) and read by
exactly one HMI object (the multistate indicator). Nothing else writes it. Nothing in
the machine reads it. That is the whole contract — the pill is a view, not an interlock.

## The four states

| Value | Caption | True when | Comes from |
|---|---|---|---|
| 0 | STOPPED | Default. Sequencer idle (`Seq_Step = 0`) or the cell is in manual. | Unconditional `MOVE(0,Seq_Status)` |
| 1 | RUNNING | `Auto_Running` **and** `Seq_Step` is 2–11 | The motion steps, forward and reverse |
| 2 | HOLDING | `Seq_Step = 1` (MSO settle) **or** `Seq_Step = 99` (decel + hold before MSF) | Commanded transitions |
| 3 | FAULTED | `Axis_Faulted` **or** `Seq_Cmd_Error` | Drive fault word, or a refused motion command |

## How it is written: priority encoder, not a chain of exclusive rungs

Rungs 5–8 all write the same DINT. That is deliberate.

```
Rung 5   MOVE(0,Seq_Status)                       <- unconditional default
Rung 6   ...RUNNING conditions... MOVE(1,...)
Rung 7   ...HOLDING conditions... MOVE(2,...)
Rung 8   ...FAULTED conditions... MOVE(3,...)     <- last write wins
```

Read the block bottom-up: **the highest-priority true rung is the one that survives the
scan.** Two properties fall out of this that mutually-exclusive rungs do not give you
for free:

- **No gap.** Every scan writes the tag. There is no combination of inputs that leaves
  the pill showing last cycle's state.
- **No overlap bug.** Adding a fifth state later means inserting one rung at the right
  priority, not re-deriving every other rung's `XIO` guards.

Do not reorder rungs 5–8. Do not add a second writer to `Seq_Status` anywhere else in
the project.

> Studio 5000 flags a duplicate *OTE* on a BOOL. It will not flag this, because these
> are MOVEs to a DINT. The rung comments carry the warning instead.

## Why RUNNING is steps 2–11 and not "Auto_Running"

`Auto_Running` latches on the start pushbutton, before any axis is enabled. If the pill
followed that bit, it would go green while the drives were still off — the one moment an
operator most needs to see something other than green.

Step 12 is excluded on purpose: it exists for a single scan before the wrap rung folds
it back to step 2.

## Why the shutdown step is HOLDING, not STOPPED

`Seq_Step = 99` is decelerating five axes and holding 600 ms before it drops servo power.
The conveyor is still moving. Showing STOPPED there teaches operators that the pill lies,
and the next thing they do is reach into a moving machine.

Note that rung 7's step-99 leg is **not** gated by `Auto_Running` — `Stop_PB` drops that
bit on the same scan it forces the shutdown step. This mirrors the existing comment in
`AutoSeq_V5` rung 1.

## Fault sourcing

Two independent sources, OR'd:

| Tag | Source | Clears when |
|---|---|---|
| `Axis_Faulted` | `Zippy_Axis_141..145.AxisFault ≠ 0` | Operator MAFRs that axis (`Reset_14x`) |
| `Seq_Cmd_Error` | `.ER` on any sequencer MSO / MAJ / MAS | The instruction re-executes on the next cycle |

There is **no separate acknowledge latch**, and that is a design decision rather than an
omission. Both sources are already latched where they belong — the drive latches its own
fault word until an MAFR, and a `MOTION_INSTRUCTION` holds `.ER` until the instruction is
re-issued. Adding a third latch in the HMI layer would create a fourth place to go look
when the pill and the drive disagree.

The practical consequence: after a rejected command, the pill **stays FAULTED through the
stop and clears on a successful restart**, not the moment the operator hits stop. That is
the behaviour you want. A fault that erases itself when someone presses stop is a fault
nobody ever diagnoses.

`MSO_Error` / `MAJ_Error` / `MAS_Error` are broken out separately so the fault can be
narrowed to a command family without going online. `MAJ_Error` is the valuable one: a
refused jog is the only failure here that is otherwise **silent** — the step timer keeps
counting, the sequence keeps advancing, and the conveyor simply never moves.

## What this model deliberately does not do

- **No PackML.** Four states, not seventeen. If this cell ever needs Idle / Starting /
  Execute / Holding / Held / Suspended, that is a state machine in the PLC that
  `Seq_Status` reports on — not more captions bolted onto an indicator.
- **No manual-mode RUNNING.** Jogging an axis from the manual screen leaves the pill at
  STOPPED. The pill is the *auto sequencer's* status and is labelled that way on screen.
- **No heartbeat.** Comms loss is the indicator's Error state, handled by the client. See
  [ftview-me-multistate-indicator.md](ftview-me-multistate-indicator.md).

## Scan-order note

`JSR(HMI_Status,0)` is the **last** rung of `MainRoutine`, after both `AutoSeq_V5` and
`Manual_Conv`. The pill therefore reports the state the scan actually ended in. Called
first, it would report the previous scan's state and lag every transition by one scan —
invisible on a 20 ms display update, but wrong, and wrong in a way that bites when
somebody later trends `Seq_Status` against `Seq_Step`.
