# Intersection / traffic controller

**Status:** 🟡 scoped — source pending
**Platform:** Studio 5000 · Factory I/O or SoftLogix
**Why it is here:** a state machine with conflicting-call interlocks is the same thinking as
a machine cell, with the safety case made obvious. Nobody needs convincing that green-vs-green
is unacceptable.

## The problem

Every direction wants the intersection. Some combinations are merely inefficient and some are
fatal, and the controller has to encode the difference in a way that cannot be defeated by
adding a feature later.

The interesting constraint is that the interlock must not live in the sequence logic. If
green-vs-green is prevented only because the sequence never happens to ask for it, the
protection disappears the first time someone adds a phase.

## Scope for v1

- States: through, left, pedestrian, all-red, flash
- A conflicting-call interlock that is structurally separate from phase sequencing
- Fault / flash fallback, and the rules for getting back out of it
- Minimum green and all-red clearance times, with the reasoning written down

## Done when

- [ ] No input sequence, including malicious ones, produces conflicting greens
- [ ] Loss of a detector degrades to a safe fixed-time mode, not a stall
- [ ] Recovery from flash requires a deliberate action, not just time passing
- [ ] 90-second clip: force a conflicting call, show it refused, then recover

## Publishing bar

A bare 4-way-stop lab worksheet does not belong in public form. This folder goes public only
if the write-up covers the interlock argument above — otherwise it is a traffic-light
animation, and there are ten thousand of those.
