# Sequencer upgrade (V6_4) — the sequencer stops assuming

Four changes to `AutoSeq_V5` and `HMI_Status`. Each is independently justifiable, and in the
**nominal case the machine behaves exactly as it did before** — every change is on a failure
path, a guard, or a read-only diagnostic.

## 1. Step 1 advances on proof, not on elapsed time

This is the one worth having. Before:

```
rung 3   XIC(Auto_Running)EQ(Seq_Step,1) MSO ×5, TON 800 ms
rung 4   XIC(Auto_Running)EQ(Seq_Step,1)XIC(MSO_TMR.DN) MOVE(2,Seq_Step)
```

The sequence issued five MSOs, waited 800 ms, and **advanced regardless of whether any axis
actually enabled.** If a drive was inhibited, faulted, or simply absent, step 2 fired a `MAJ`
at an axis that was not on. The jog would be rejected, the step timer would keep counting, and
the conveyor would sit still while the sequencer worked happily through all ten motion steps.

Now the settle is a *timeout*, not a *delay*:

```
rung 4   XIC(...141.ServoActionStatus)…×5  OTE(All_Servos_On)
rung 5   …EQ(Seq_Step,1)XIC(MSO_TMR.DN)XIO(All_Servos_On)  OTL(Servo_On_Timeout)
rung 6   …EQ(Seq_Step,1)XIC(MSO_TMR.DN)XIC(All_Servos_On)XIO(Servo_On_Timeout)  MOVE(2,Seq_Step)
```

Five `XIC` in **series** — every axis, not any axis. If all five report servo action by the
time the settle expires, the sequence advances at exactly the same 800 ms it always did. If
one does not, it latches a fault and the sequence stays at step 1.

`XIO(Servo_On_Timeout)` on the advance rung makes a timeout a **failed start rather than a
slow one**. Without it, an axis enabling at 850 ms would let the sequence proceed while
`Servo_On_Timeout` stayed latched — and since FAULTED outranks RUNNING in the pill, the
operator would be looking at a red pill on a moving conveyor.

If a drive on this cell genuinely needs longer than 800 ms, raise `MSO_TMR.PRE` in rung 3.
Do not delete the contact.

The fault is latched and cleared by `OTU(Servo_On_Timeout)` on rung 0's start one-shot, so it
survives a stop and clears on the next start attempt — the same lifecycle as the `.ER` bits,
for the same reason.

## 2. `Travel_Time` is clamped before it reaches the step timer

`Travel_Time` is HMI-writable and feeds `Seq_TMR.PRE` directly. **At 0 the TON is done on the
scan it starts**, and all ten motion steps fire in a few milliseconds — five axes commanded
forward and reverse faster than anything can respond to.

```
MOVE(3500,Seq_TMR.PRE);                                    <- safe default, unconditional
LIM(500,Travel_Time,10000)MOVE(Travel_Time,Seq_TMR.PRE);   <- operator value, if sane
XIC(Auto_Running)GE(Seq_Step,2)LE(Seq_Step,11)TON(Seq_TMR,?,?);
```

Same priority-encoder shape as `Seq_Status`: write the safe value unconditionally, override it
only when the override is valid. An out-of-range entry falls back to 3.5 s rather than being
rejected with an error nobody reads.

`Travel_Time` is currently 1800, comfortably inside the band, so nothing changes today.

## 3. `Start_Blocked_Reason` — why the start button did nothing

`Manual_Conv` rung 0 is `XIC(Mode_Manual)OTU(Auto_Running)`, and `MainRoutine` calls
`AutoSeq_V5` before `Manual_Conv`. So in manual mode, a start press latches `Auto_Running` and
Manual_Conv unlatches it in the same scan. No motion, no message, no fault — nothing.

That interlock is correct and stays exactly as it is. What was missing is any way to *see* it:

| Value | Meaning |
|---|---|
| 0 | Clear to start |
| 3 | Already running |
| 2 | Cell is faulted |
| 1 | In manual mode |

Priority-encoded in `HMI_Status`, ascending, last write wins — 1 is highest because it is the
one that blocks silently and the one an operator hits first. No rung reads this tag; it exists
so a multistate indicator beside the start button can answer the question.

## 4. `Cycle_Count`

Incremented on the step 12 wrap, which is the actual cycle boundary. HMI may write 0 to clear.

One `ADD` on an existing rung, and it is the first real entry in the `Cell.Production` contract
in [../../../docs/iiot-path.md](../../../docs/iiot-path.md) — a counter that means something is
a better first OPC UA tag than a state enum nobody has trended yet.

## What this does not do

- **No safety logic.** This cell has no E-stop, guard, or safety input in the project, and
  inventing one in software would be worse than not having it. A real cell needs one; that is
  a hardware conversation, not a ladder edit.
- **No first-out fault register.** `Servo_On_Timeout` is one named fault, not a fault system.
  The general pattern belongs in [logix-fault-handler](../../logix-fault-handler).
- **No change to the motion steps.** Rungs 7–16 are untouched.

## Testing it

The failure path is the point, so test the failure path.

| Test | Expected |
|---|---|
| Normal start, all drives healthy | Identical to before — 800 ms amber, then green |
| Inhibit one drive in the I/O tree, then start | Pill red, `Seq_Step` stays 1, **conveyor does not move** |
| From that state, press Start again | Still red — the latch survives until a clean start |
| Stop, un-inhibit, Start | `Servo_On_Timeout` clears, cell runs |
| Write `Travel_Time` = 0, run a cycle | Steps advance at 3.5 s, not instantly |
| Write `Travel_Time` = 2000, run a cycle | Steps advance at 2 s |
| Press Start while in manual | `Start_Blocked_Reason` = 1 |
| Complete a full cycle | `Cycle_Count` increments once, on the wrap |

The second row is also the best shot in the demo video: a start attempt that is refused, with
the reason on screen, and a machine that stays still.
