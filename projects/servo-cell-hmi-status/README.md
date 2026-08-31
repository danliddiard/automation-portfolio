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

| File | What it is |
|---|---|
| [`src/TECE1250_ServoCell_V6_2_SeqStatus.L5X`](src/TECE1250_ServoCell_V6_2_SeqStatus.L5X) | Full controller export. Import and run. Adds 6 tags, the `HMI_Status` routine, and one JSR. |
| [`src/HMI_Status.txt`](src/HMI_Status.txt) | The same 9 rungs as neutral text — readable in a browser, pasteable into an existing project. |
| [`src/Seq_Status_tags.csv`](src/Seq_Status_tags.csv) | Logix tag import CSV for the 6 new tags. Use with the paste block. |
| [`docs/state-model.md`](docs/state-model.md) | Truth table, priority rules, fault sourcing, scan-order note. |
| [`docs/ftview-me-multistate-indicator.md`](docs/ftview-me-multistate-indicator.md) | FTView ME build sheet — states, exact RGB, connection string, and the test that actually proves it. |

## Drop it into an existing project

1. Import `src/Seq_Status_tags.csv` — `Tools > Import > Tags and Logic Comments`.
2. Create an RLL routine named `HMI_Status` in `MainProgram`.
3. Paste the block at the bottom of `src/HMI_Status.txt` into it.
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

## Not done yet

- 90-second demo clip: START → amber → green, force a drive fault → red, MAFR → recover.
  Per [publishing rules](../../docs/publishing-rules.md) this folder stays private until
  that clip exists.
- The ISA-101 muted-palette variant is specified but not built. Both versions side by side
  is the interesting half of the demo.
- `Seq_Status` is the natural first entry in the `Cell.State` OPC UA contract in
  [docs/iiot-path.md](../../docs/iiot-path.md). Same DINT, same meaning, Ignition instead of ME.
