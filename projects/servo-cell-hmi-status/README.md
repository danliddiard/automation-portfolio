# Servo cell — HMI status pill

**Status:** runs in auto on the cell, driven from a PanelView Plus 1000 · demo clip TBD
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

## What running it actually found

The pill was the deliverable. The more useful outcome was that commissioning it surfaced three
defects in logic that predates this work — none of them things a desk review would have caught,
all found by putting a real terminal on a real controller and pressing the button.

| What | How it showed up |
|---|---|
| The manual routine stopped every auto jog, one scan after it started | Each step took its full 1.8 s while the axis twitched an inch. [Note](../../notes/manual-routine-killed-the-auto-jog.md) |
| `Stop_PB` shipped latched at `1`, so no start press could ever hold | Start Auto did nothing at all, silently — the stop button was held down inside the export |
| Two `MAG` instructions shared one motion control tag | Found by census before the feature was ever used. [Note](../../notes/duplicate-motion-control-tag.md) |

A fourth is still open, and it is mine rather than inherited: `Seq_Step` between 1 and 11 with
`Auto_Running` false is an orphaned state that nothing detects, because `Servo_On_Timeout` — the
guard written to catch a stalled start — is itself gated by `Auto_Running`. The one case where
the sequencer is genuinely abandoned is the case the guard cannot see. One rung closes it. It is
listed here rather than quietly fixed because a guard with a blind spot is worth more as a
worked example than as a silent commit.

## Files

Staged in two imports on purpose. Step 1 is low risk and touches nothing that moves. Step 2
changes five live MAJ instructions, so it goes second.

### Step 1 — the status pill

| File | What it is |
|---|---|
| [`src/step1-status-pill/TECE1250_GreenMachine_V7_2_SeqStatus.L5X`](src/step1-status-pill/TECE1250_GreenMachine_V7_2_SeqStatus.L5X) | Full controller export. Adds 6 tags, the `HMI_Status` routine, and one JSR. |
| [`src/step1-status-pill/HMI_Status.txt`](src/step1-status-pill/HMI_Status.txt) | The same 9 rungs as neutral text — readable in a browser, pasteable into an existing project. |
| [`src/step1-status-pill/Seq_Status_tags.csv`](src/step1-status-pill/Seq_Status_tags.csv) | Logix tag import CSV for the 6 new tags. |
| [`docs/state-model.md`](docs/state-model.md) | Truth table, priority rules, fault sourcing, scan-order note. |
| [`docs/ftview-me-multistate-indicator.md`](docs/ftview-me-multistate-indicator.md) | FTView ME build sheet for the pill. |

### Step 2 — what the single manual screen needs

`V7_3` is cumulative: everything in `V7_2` plus three PLC changes. Almost all of the manual
screen is HMI work; this is only the part that cannot be done from the HMI.

| File | What it is |
|---|---|
| [`src/step2-manual-faceplate/TECE1250_GreenMachine_V7_3_ManualFaceplate.L5X`](src/step2-manual-faceplate/TECE1250_GreenMachine_V7_3_ManualFaceplate.L5X) | Full controller export. `V7_2` + 11 tags + the changed jog rungs. |
| [`src/step2-manual-faceplate/HMI_Status_v2.txt`](src/step2-manual-faceplate/HMI_Status_v2.txt) | Updated `HMI_Status`, plus the five changed `Manual_Conv` jog rungs. |
| [`src/step2-manual-faceplate/Manual_Faceplate_tags.csv`](src/step2-manual-faceplate/Manual_Faceplate_tags.csv) | Tag CSV for step 2's additions only. |
| [`src/step2-manual-faceplate/parameter-files/`](src/step2-manual-faceplate/parameter-files) | Five ME parameter files, `#1=141` … `#1=145`. |
| [`docs/ftview-me-manual-faceplate.md`](docs/ftview-me-manual-faceplate.md) | Build sheet for the one-screen manual layout. |

The three PLC changes, and why each exists:

- **`Axis_Fault_141..145`** — `V7_2` computed one cell-level `Axis_Faulted` in a single
  five-leg rung. The summary strip needs to light the row that is actually faulted, not tell
  the operator to go find the drive. Same logic, split per axis, then OR'd back into the
  summary the pill reads.
- **`Jog_Speed_Man_141..145`** — the manual jog speed was a literal `10.0` buried inside the
  `MAJ` instruction, so no screen could expose it. Now a tag per axis, defaulting to 10.0, so
  behaviour on import is identical until someone changes a value. Per-axis on purpose:
  `Jog_Accel` and `Jog_Decel` stay cell-wide because `AutoSeq_V5` shares them, including for
  its shutdown decel.
- **`Sel_Axis`** — so the faceplate can name the axis it is commanding. No ladder reads it.

### Step 3 — sequencer upgrade

`V7_5` is cumulative again. Four changes, all of them on a failure path, a guard, or a
read-only diagnostic — **the nominal cycle behaves exactly as it did before.**

| File | What it is |
|---|---|
| [`src/step3-sequencer-upgrade/TECE1250_GreenMachine_V7_5_SeqUpgrade.L5X`](src/step3-sequencer-upgrade/TECE1250_GreenMachine_V7_5_SeqUpgrade.L5X) | Full controller export. `V7_3` + 4 tags + the sequencer changes. |
| [`src/step3-sequencer-upgrade/AutoSeq_HMI_Status_v3.txt`](src/step3-sequencer-upgrade/AutoSeq_HMI_Status_v3.txt) | Both changed routines as neutral text. |
| [`src/step3-sequencer-upgrade/Sequencer_Upgrade_tags.csv`](src/step3-sequencer-upgrade/Sequencer_Upgrade_tags.csv) | Tag CSV for step 3's additions only. |
| [`docs/sequencer-upgrade.md`](docs/sequencer-upgrade.md) | What changed, why, and how to test the failure paths. |

The change worth having is the first one. Step 1 issued five MSOs, waited 800 ms, and
**advanced whether or not any axis actually enabled** — so an inhibited drive meant step 2
jogging an axis that was not on, the step timer counting merrily, and a conveyor sitting still
through all ten motion steps. The settle is now a timeout rather than a delay: advance on all
five reporting `ServoActionStatus`, or latch `Servo_On_Timeout` and stop at step 1.

Also: `Travel_Time` is clamped before it reaches the step timer (at 0 the TON is done on the
scan it starts, and all ten steps fire in milliseconds), `Start_Blocked_Reason` finally
explains why a start press in manual mode does nothing at all, and `Cycle_Count` gives the
`Cell.Production` OPC UA contract its first real entry.

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

### Step 4 — the manual routine was killing every auto jog

Found on the bench the first time the cell ran in auto. `Manual_Conv`'s per-axis "jog release"
rung — `XIO(Jog_14x)XIC(MAJ_14x.IP)MAS(...)` — had no `Mode_Manual` gate, so it read the auto
sequencer's jog as an abandoned manual one and stopped it about a scan after it started. Every
step, every axis. The jog *start* rung was gated; the *release* rung was not.

| File | What it is |
|---|---|
| [`src/step4-manual-jog-gate/TECE1250_GreenMachine_V7_6_JogGate.L5X`](src/step4-manual-jog-gate/TECE1250_GreenMachine_V7_6_JogGate.L5X) | Full controller export. `V7_5` + the gate + `Stop_PB` shipping as 0. |
| [`src/step4-manual-jog-gate/Manual_Conv_jog_release.txt`](src/step4-manual-jog-gate/Manual_Conv_jog_release.txt) | The five changed rungs as neutral text. |
| [`docs/manual-jog-gate.md`](docs/manual-jog-gate.md) | The interaction, the fix, and why axis 145 was the clue. |

One contact on five rungs. No new tags.

### Step 5 — gearing fix

| File | What it is |
|---|---|
| [`src/step5-gear-fix/TECE1250_GreenMachine_V7_7_GearFix.L5X`](src/step5-gear-fix/TECE1250_GreenMachine_V7_7_GearFix.L5X) | `V7_6` + one changed operand. No new tags, no new rungs. |
| [`src/step5-gear-fix/Manual_Conv_gear_rungs.txt`](src/step5-gear-fix/Manual_Conv_gear_rungs.txt) | The three gearing rungs as neutral text, with how to drive them. |

Axis 145's `MAG` used **`MAG_144`** as its motion control tag — the same tag as axis 144's
instruction. Two motion instructions sharing one `MOTION_INSTRUCTION` fight over
`.EN`/`.DN`/`.IP`/`.ER`, so 145's gearing faults would have been invisible or attributed to
144. `MAG_145` was declared and referenced zero times, which is what made it findable.

Pre-existing, like the jog gate. Found by auditing the gearing rungs before using them rather
than after.

## Version numbering

The machine is the **Green Machine** — the motion group in the controller is already called
`Mean_Green_Servos`, so the files are named for the machine rather than for a folder.

Numbering follows the ACD on Dan's bench, not this repo's history:

| File | Notes |
|---|---|
| `V7_2` | Status pill |
| `V7_3` | + manual faceplate groundwork |
| `V7_4` | **Not in this repo.** The first import, which carried a `LIM` instruction on the `Travel_Time` clamp rung |
| `V7_5` | `LIM` replaced with `GE`/`LE` |
| `V7_6` | `Mode_Manual` gate on the jog-release rungs; `Stop_PB` ships as 0 |
| `V7_7` | Axis 145's `MAG` given its own motion control tag. **Current** |

The gap at `V7_4` is deliberate — it is a real version that exists on disk and briefly had a
real defect. Renumbering to hide it would make the bench copy and the repo disagree, which is
the whole problem version numbers exist to prevent.

## Import order

A **full controller L5X import creates a new project** — it does not merge into an open one.
So import `V7_2`, verify the pill, then import `V7_3` as a separate project rather than
expecting it to layer on top. Any hand edits made to the `V7_2` project in between are not
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
