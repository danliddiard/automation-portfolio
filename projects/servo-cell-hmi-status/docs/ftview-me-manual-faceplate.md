# Build sheet — one manual screen for all five servos, FactoryTalk View ME v16

**Prerequisite:** `TECE1250_GreenMachine_V7_3_ManualFaceplate.L5X` imported. See
[../src/step2-manual-faceplate](../src/step2-manual-faceplate).

Replaces five near-identical manual screens with one screen and one faceplate, using ME
parameter substitution. The PLC work is small; nearly all the risk is on this page.

## Why this is easy in this project

Every per-axis tag follows one suffix rule — 22 families × 5 axes, `Enable_141`, `Jog_142`,
`Act_Pos_143`. ME substitutes a **parameter placeholder** into a tag reference at runtime, so
the faceplate is written once as `{::[SHORTCUT]Enable_#1}` and opened with `#1 = 143`.

Had the tags been named `Enable_Infeed`, `EN_Axis3`, `DischargeEnable`, this document would
begin with "rename your tag database."

## Layout: two zones, one screen

**Zone 1 — summary strip, always visible, all five axes.** Direct tag references, no
parameters. This is the part five separate screens could never give you: one glance answers
*is the cell healthy.*

Five rows, one per axis, each with four objects:

| Column | Object | Tag |
|---|---|---|
| Axis | Text, static | `141` … `145` |
| Enabled | Multistate indicator, 2 states | `{::[SHORTCUT]Drive_Enabled_14x}` |
| Fault | Multistate indicator, 2 states | `{::[SHORTCUT]Axis_Fault_14x}` |
| Position | Numeric display | `{::[SHORTCUT]Act_Pos_14x}` |
| Velocity | Numeric display | `{::[SHORTCUT]Act_Vel_14x}` |

Build row 141, then copy-paste four times and edit the suffix. `Axis_Fault_14x` exists
because of this strip — before step 2, the only fault bit was cell-level `Axis_Faulted`,
which tells an operator something is wrong and not which drive.

**Zone 2 — one parameterized faceplate.** A *Goto Display* button on each summary row opens
it for that axis.

## Faceplate tag reference

Every reference uses `#1`. Build it once.

| Object | Type | Tag |
|---|---|---|
| Enable | Maintained push button | `{::[SHORTCUT]Enable_#1}` |
| Enabled lamp | Multistate indicator | `{::[SHORTCUT]Drive_Enabled_#1}` |
| Fault lamp | Multistate indicator | `{::[SHORTCUT]Axis_Fault_#1}` |
| Reset | Momentary push button | `{::[SHORTCUT]Reset_#1}` |
| **Jog** | **Momentary push button — see hazard below** | `{::[SHORTCUT]Jog_#1}` |
| Jog speed | Numeric input | `{::[SHORTCUT]Jog_Speed_Man_#1}` |
| Home | Momentary push button | `{::[SHORTCUT]Home_#1}` |
| Move start | Momentary push button | `{::[SHORTCUT]Start_#1}` |
| Move stop | Momentary push button | `{::[SHORTCUT]Stop_#1}` |
| Target position | Numeric input | `{::[SHORTCUT]Cmd_Pos_#1}` |
| Target velocity | Numeric input | `{::[SHORTCUT]Cmd_Vel_#1}` |
| Actual position | Numeric display | `{::[SHORTCUT]Act_Pos_#1}` |
| Actual velocity | Numeric display | `{::[SHORTCUT]Act_Vel_#1}` |

## Passing the parameter

Two ways; both work, pick one and be consistent.

**Parameter list** — on the Goto Display button, set *Parameter List* to `141`. Fastest, and
the value is visible on the button that uses it.

**Parameter file** — `../src/step2-manual-faceplate/parameter-files/Axis_141.par`, one line:

```
#1=141
```

Set the button's *Parameter File* to `Axis_141`. Better once a faceplate takes several
parameters, and the files are diffable, which is why they are committed here.

Five buttons, five values, one target display.

## The hazard: a momentary jog on a display that can close

`Manual_Conv` jogs while `Jog_14x` is true and stops on the falling edge:

```
XIC(Mode_Manual)XIC(Enable_141)XIC(Jog_141)MAJ(...)      // jog while held
XIO(Jog_141)XIC(MAJ_141.IP)MAS(...)                       // stop on release
```

So `Jog_#1` **must** be a momentary push button — a maintained one leaves the axis jogging
after the operator lets go.

The part to test rather than assume: **what happens if the faceplate closes while jog is
held.** Navigating away, a display timeout, or a shell change during a press can mean the
release write never happens, and the PLC never sees `Jog_14x` go false. Test it deliberately:
hold jog, close the faceplate, and confirm the axis stops. If it does not, that is a PLC fix
(drop the bit on a condition the HMI cannot skip), not an HMI setting to hunt for.

This is the single most important test on this page. Everything else fails loudly; this one
fails with an axis still moving.

## Three things that are cell-wide, not per-axis

Putting any of these on a per-axis faceplate makes the screen lie about its own scope.

| Tag | Scope | Where it belongs |
|---|---|---|
| `Jog_Accel`, `Jog_Decel` | All five axes **and** `AutoSeq_V5`, including its shutdown decel | Parent screen, labelled as cell setpoints |
| `Gear_Engage_PB`, `Gear_Ratio_SP`, `All_Geared` | Cell-level. `MAG`/`MASG` exist only for 142–145; 141 is the master | Parent screen |
| `Jog_Speed` | Auto sequencer only — **not** the manual jog | Leave off the manual screen entirely |

`Jog_Speed_Man_14x` is the per-axis manual jog speed added in step 2. Before it, the manual
jog speed was a literal `10.0` inside the MAJ instruction and could not be exposed at all.

Note `Stop_14x` is deliberately **not** gated by `Mode_Manual` in the ladder, so the
faceplate's stop button works in auto too. That is worth keeping.

## Titling the faceplate

The faceplate needs to name the axis it is commanding, or the operator is one misclick from
jogging the wrong conveyor.

Placeholders substitute reliably into tag references. Whether they substitute into a static
caption field in v16, I am not certain — try it first, it is thirty seconds. If it does not
work, the reliable route is `Sel_Axis`: make each summary-row button write the axis number to
`{::[SHORTCUT]Sel_Axis}` before navigating, and put a numeric display bound to it in the
faceplate header. `Sel_Axis` is in step 2's L5X for exactly this; no ladder reads it.

## Test plan

Parameter substitution fails **silently** at build time — a typo gives you a tag-not-found at
runtime, not an error at validate. So test all five, not just the first.

| Test | Expect |
|---|---|
| Open faceplate as 143, press Enable | 143 enables. **144 and 141 do not move.** |
| Repeat for all five axes | Each commands only itself |
| Hold jog, release | Axis jogs, then stops |
| **Hold jog, close the faceplate** | **Axis stops** |
| Set jog speed to 5 on 143, jog 141 | 141 still jogs at 10 — the speeds are per-axis |
| Fault one drive | That row's fault lamp lights, and only that row |
| Pull the Ethernet cable | Every object goes to its error state |

The wrong-axis test in row 1 is the one that catches a bad placeholder. Run it for every axis.

## Effort

| | |
|---|---|
| Summary strip | ~45 min — build one row, copy four times |
| Faceplate with `#1` | ~1 hr, built once |
| Five buttons + parameter files | ~15 min |
| Test all five, including the close-while-jogging test | ~45 min |

About half a day, against five screens maintained forever.

## If you were starting over

The clean version is a `UDT_Servo` with a `Servo[5]` array, so the HMI indexes rather than
string-substitutes. That is how to build it fresh, and it is exactly what
[l5x-from-spreadsheet](../../l5x-from-spreadsheet) is for — generating five UDT instances from
a table is that project's whole pitch.

But the flat names already parameterize perfectly. Restructuring working motion code for
elegance available free from a `#1` placeholder is a bad trade. Note it as v2 and move on.
