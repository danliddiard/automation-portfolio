# Portfolio plan (working notes)

The job-search side of this repo. Moved out of the root README so that file reads as a
portfolio for a visitor rather than as a to-do list for me.

**Target:** non-rotating senior controls / automation roles, Utah.

**Positioning:** one machine story told across two PLC platforms, plus one modern data path.
Depth over breadth. A hiring manager should be able to name what I can do after ninety
seconds on the front page.

## Visibility

Default private. A folder flips public only when it passes all four items in the root
README's "What done means here". Flipping the *repo* public is a separate decision from
merging to `main` — merging is internal, and there is no reason to hold work on a branch
just because the demo clip is not filmed yet.

Publish order, once each has a clip:

1. `servo-cell-hmi-status` — closest to done, and the HMI-philosophy argument is the part
   most candidates cannot make
2. `logix-fault-handler` — first-out is the single most interview-legible pattern here
3. `l5x-from-spreadsheet` — the "I automate my own engineering" story
4. Everything else

## Resume / LinkedIn one-liner (when v1 exists)

> PackML-style cell in TwinCAT and Logix, first-out fault handling, OPC UA + MQTT into
> Ignition. Runnable in simulation.

Not usable until the fault-recovery loop works on camera. A one-liner that outruns the repo
is worse than no one-liner — it invites exactly the question the repo cannot answer yet.

## Talk track per project

Each folder should leave me able to answer three questions without notes:

1. What was the actual problem, in one sentence a non-controls manager understands?
2. What did I choose, and what did I reject?
3. How would this fail in a plant, and what did I do about it?

Question 3 is the one that separates a portfolio from a coursework dump. `servo-cell-hmi-status`
answers it with the Error-state section — a blank grey indicator that reads as a convincing
STOPPED pill while the HMI has actually lost the controller.
