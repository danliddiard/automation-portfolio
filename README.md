# Automation Portfolio

Private working repo for controls / automation portfolio pieces.
Public later, project by project, after a demo exists.

**Owner:** Daniel Liddiard  
**Focus:** non-rotating senior controls / automation roles (Utah)  
**Rule:** one machine story, two platforms, one IIoT path. Not a junk drawer of labs.

## What belongs here

| Folder | Status | Why it exists |
|---|---|---|
| [projects/servo-cell-hmi-status](projects/servo-cell-hmi-status) | **source in repo** | Operator state pill: one DINT in Logix, one multistate indicator in FTView ME |
| [projects/l5x-from-spreadsheet](projects/l5x-from-spreadsheet) | files TBD | Engineering automation — generate Logix tags/routines from data |
| [projects/intersection-controller](projects/intersection-controller) | files TBD | State machine + interlocks (Studio 5000 / Factory I/O) |
| [projects/logix-fault-handler](projects/logix-fault-handler) | files TBD | First-out fault pattern, not a whole class project |
| [projects/twincat-packml-cell](projects/twincat-packml-cell) | planned | TwinCAT 3 PackML cell (sim first, hardware later) |
| [projects/iiot-edge-bridge](projects/iiot-edge-bridge) | planned | Same cell → OPC UA + MQTT → Ignition |

Short technical notes (LinkedIn-sized) live in [notes/](notes/).

`servo-cell-hmi-status` is the format the rest of these folders get held to: a README
that argues for the design, source that imports and runs, a diagram, and a build sheet
for anything that lives in a binary the repo cannot carry.

## IIoT path (the one to finish)

PLC (Logix **or** TwinCAT) → curated tags over **OPC UA** → optional **MQTT** publish → **Ignition** for HMI/history/alarms.

Full write-up: [docs/iiot-path.md](docs/iiot-path.md)

## How to use this repo

0. `python3 tools/validate.py` before pushing. It parses every committed L5X and resolves every relative link in every README; CI runs the same script.
1. Drop real source into the matching `projects/` folder when it runs.
2. Keep employer / plant / customer material out. Sanitize names and IPs.
3. Demo video stays **unlisted** (YouTube) or a Drive link. Do not commit large `.mp4` files.
4. Flip a project public only after: README, diagram, and a 90-second recover-from-fault clip.

## LinkedIn / resume one-liner (when v1 exists)

> PackML-style cell in TwinCAT and Logix, first-out fault handling, OPC UA + MQTT into Ignition. Runnable in simulation.
