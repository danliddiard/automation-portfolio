# Logix first-out fault handler

**Status:** 🟡 scoped — source pending
**Platform:** Studio 5000
**Why it is here:** the pattern, not the whole class project.

## The problem

A machine faults and the HMI lights up forty alarms. Thirty-nine of them are consequences.
An operator cannot tell which one stopped the machine, so they clear everything and press
start, and the machine stops again in the same place.

First-out means the PLC captures which condition went bad **first** and holds it, separate
from everything that fell over afterward. It is the difference between an alarm list and a
diagnosis.

## Scope for v1

- Fault UDT — code, source, timestamp, latch
- First-out capture, held distinctly from subsequent faults
- Reset rules: who is allowed to clear what, and from where
- RTO vs TON, chosen deliberately per fault and written down — retentive timing matters for
  the faults that must survive a power cycle, and is wrong for the ones that must not

## Done when

- [ ] Force two faults a few scans apart; the first-out register names the first one only
- [ ] Reset from the HMI does not let the machine re-enter Execute without Reset **and** Start
- [ ] Fault history survives a controller power cycle where it is supposed to
- [ ] 90-second clip of the recover-from-fault loop

## Notes

Sanitize any lab naming that points at a specific employer or plant before the first commit.

This is the pattern `servo-cell-hmi-status` stops short of: that project's pill reports
*that* the cell is faulted. This one answers *which fault, and was it the cause or a
symptom.* The two are meant to compose — `Seq_Status = 3` is the summary, the first-out
register is the detail behind it.
