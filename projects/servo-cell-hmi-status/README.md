# Servo cell — HMI status pill

**Status:** source in repo, runs in the class cell · demo clip TBD
**Platform:** Studio 5000 v38 · CompactLogix 1769-L33ERM · 5× Kinetix 6500 · FactoryTalk View ME v16
**Why it is here:** one small, complete, honest piece of HMI work — the operator-facing
state of a machine, derived once in the PLC instead of five times on the screen.

![Seq_Status pill states](docs/seq-status-pill.svg)

## The problem

The cell is a five-axis conveyor with a step sequencer (`AutoSeq_V5`): step 0 idle, step 1
servo-on, steps 2–11 forward then reverse, step 99 controlled shutdown. The operator screen
had no single place to answer *what is this machine doing right now.*

The tempting fix is to put the answer on the HMI — a few animation expressions on
`Auto_Running`, `Seq_Step` and the drive faults, evaluated per object, per display. That
scatters one piece of logic across every screen that shows it, puts it somewhere that
cannot be tested offline, and guarantees two screens will eventually disagree.

## The fix

One DINT, `Seq_Status`, derived in one routine and displayed by one object.

| Value | Caption | Meaning |
|---|---|---|
| 0 | STOPPED | idle, or the cell is in manual |
| 1 | RUNNING | auto latched, inside motion steps 2–11 |
| 2 | HOLDING | commanded transition — servo-on settle, or shutdown decel |
| 3 | FAULTED | drive fault word set, or a motion command was refused |

The three decisions worth defending are in [docs/state-model.md](docs/state-model.md):

- **A priority encoder, not exclusive rungs.** Rungs 5–8 all write `Seq_Status`; the
  default is written unconditionally and the highest-priority true rung wins. The tag can
  never be stale, and adding a state later is one rung, not a re-derivation of every
  `XIO` guard in the block.
- **The shutdown ramp is HOLDING, not STOPPED.** Step 99 is still decelerating five axes.
  A pill that says STOPPED while the conveyor is moving is how people get hurt.
- **No acknowledge latch.** The drive latches its own fault word until an MAFR and a
  `MOTION_INSTRUCTION` holds `.ER` until re-issued. A third latch in the HMI layer would
  only add a fourth place to look when the pill and the drive disagree.

`MAJ_Error` is broken out on its own because a refused jog is the one failure mode here
that is otherwise completely silent — the step timer keeps counting, the sequence keeps
advancing, and the conveyor just never moves.

## Files

Staged in two imports on purpose. Step 1 is low risk and touches nothing that moves. Step 2
changes five live MAJ instructions, so it goes second.

### Step 1 — the status pill

| File | What it is |
|---|---|
| [`src/step1-status-pill/TECE1250_ServoCell_V6_2_SeqStatus.L5X`](src/step1-status-pill/TECE1250_ServoCell_V6_2_SeqStatus.L5X) | Full controller export. Adds 6 tags, the `HMI_Status` routine, and one JSR. |
| [`src/step1-status-pill/HMI_Status.txt`](src/step1-status-pill/HMI_Status.txt) | The same 9 rungs as neutral text — readable in a browser, pasteable into an existing project. |
| [`src/step1-status-pill/Seq_Status_tags.csv`](src/step1-status-pill/Seq_Status_tags.csv) | Logix tag import CSV for the 6 new tags. |
| [`docs/state-model.md`](docs/state-model.md) | Truth table, priority rules, fault sourcing, scan-order note. |
| [`docs/ftview-me-multistate-indicator.md`](docs/ftview-me-multistate-indicator.md) | FTView ME build sheet for the pill. |

### Step 2 — what the single manual screen needs

`V6_3` is cumulative: everything in `V6_2` plus three PLC changes. Almost all of the manual
screen is HMI work; this is only the part that cannot be done from the HMI.

| File | What it is |
|---|---|
| [`src/step2-manual-faceplate/TECE1250_ServoCell_V6_3_ManualFaceplate.L5X`](src/step2-manual-faceplate/TECE1250_ServoCell_V6_3_ManualFaceplate.L5X) | Full controller export. `V6_2` + 11 tags + the changed jog rungs. |
| [`src/step2-manual-faceplate/HMI_Status_v2.txt`](src/step2-manual-faceplate/HMI_Status_v2.txt) | Updated `HMI_Status`, plus the five changed `Manual_Conv` jog rungs. |
| [`src/step2-manual-faceplate/Manual_Faceplate_tags.csv`](src/step2-manual-faceplate/Manual_Faceplate_tags.csv) | Tag CSV for step 2's additions only. |
| [`src/step2-manual-faceplate/parameter-files/`](src/step2-manual-faceplate/parameter-files) | Five ME parameter files, `#1=141` … `#1=145`. |
| [`docs/ftview-me-manual-faceplate.md`](docs/ftview-me-manual-faceplate.md) | Build sheet for the one-screen manual layout. |

The three PLC changes, and why each exists:

- **`Axis_Fault_141..145`** — `V6_2` computed one cell-level `Axis_Faulted` in a single
  five-leg rung. The summary strip needs to light the row that is actually faulted, not tell
  the operator to go find the drive. Same logic, split per axis, then OR'd back into the
  summary the pill reads.
- **`Jog_Speed_Man_141..145`** — the manual jog speed was a literal `10.0` buried inside the
  `MAJ` instruction, so no screen could expose it. Now a tag per axis, defaulting to 10.0, so
  behaviour on import is identical until someone changes a value. Per-axis on purpose:
  `Jog_Accel` and `Jog_Decel` stay cell-wide because `AutoSeq_V5` shares them, including for
  its shutdown decel.
- **`Sel_Axis`** — so the faceplate can name the axis it is commanding. No ladder reads it.

## Drop it into an existing project

1. Import `src/step1-status-pill/Seq_Status_tags.csv` — `Tools > Import > Tags and Logic Comments`.
2. Create an RLL routine named `HMI_Status` in `MainProgram`.
3. Paste the block at the bottom of `src/step1-status-pill/HMI_Status.txt` into it.
4. Add `JSR(HMI_Status,0)` as the **last** rung of `MainRoutine`. Last, so the pill reports
   the state the scan ended in rather than lagging every transition by a scan.
5. Build the indicator per [docs/ftview-me-multistate-indicator.md](docs/ftview-me-multistate-indicator.md).

Or just import the full L5X and skip 1–4.

## Porting it to a different cell

The state model transfers; the tag names do not. Three things to change:

- **Axis names.** `Zippy_Axis_141..145` in rung 0.
- **Step ranges.** Rungs 6 and 7 hard-code this sequencer's steps (2–11 running, 1 and 99
  transitional). Any sequencer has an equivalent pair of ranges.
- **The fault word.** Rung 0 tests `AXIS_CIP_DRIVE.AxisFault ≠ 0`, which rolls up the
  physical-axis, module, config and guard faults in one comparison. If a firmware or drive
  family in your project does not expose that word, swap each leg for the specific bits —
  `XIC(Axis.PhysicalAxisFault)` and `XIC(Axis.ModuleFault)` — and leave the rest of the
  routine alone.

## Import order

A **full controller L5X import creates a new project** — it does not merge into an open one.
So import `V6_2`, verify the pill, then import `V6_3` as a separate project rather than
expecting it to layer on top. Any hand edits made to the `V6_2` project in between are not
carried across.

To apply step 2 on top of a project you have already been editing, use the partial artifacts
instead: import `Manual_Faceplate_tags.csv`, then hand-edit the rungs listed in
`HMI_Status_v2.txt`. Eleven tags, eleven rungs.

## Not done yet

- 90-second demo clip: START → amber → green, force a drive fault → red, MAFR → recover.
  Per [publishing rules](../../docs/publishing-rules.md) this folder stays private until
  that clip exists.
- The ISA-101 muted-palette variant is specified but not built. Both versions side by side
  is the interesting half of the demo.
- `Seq_Status` is the natural first entry in the `Cell.State` OPC UA contract in
  [docs/iiot-path.md](../../docs/iiot-path.md). Same DINT, same meaning, Ignition instead of ME.
