# TwinCAT 3 PackML cell

**Status:** ⚪ planned — sequenced behind a working Logix cell on purpose
**Platform:** TwinCAT 3 XAE + 7-day trial runtime
**Hardware:** none required for v1 — simulated I/O

**Target machine:** 2-station inspect / reject cell.

## Why this exists

Half of this portfolio's argument is that a state model and a tag contract are portable and a
PLC brand is not. That claim is free until the same cell exists twice. This folder is the
second half of the proof.

## Scope for v1

- PackML state model
- `FB_Conveyor`, `FB_Station`, `FB_Divert`, `FB_FaultMgr`
- First-out fault stack — same concept as [logix-fault-handler](../logix-fault-handler),
  different language
- Recipe struct
- A sim I/O layer that can later map onto real EtherCAT terminals without touching the
  logic above it

## Done when

- [ ] Cell runs a full cycle in simulation
- [ ] It recovers from a forced fault cleanly, and will not re-enter Execute without
      Reset **and** Start
- [ ] The OPC UA contract in [docs/iiot-path.md](../../docs/iiot-path.md) is exposed and
      matches the Logix cell's field for field
- [ ] 90-second recover-from-fault clip

## Deliberately later

HMI and TwinSAFE simulation come **after** the PLC recovers from a fault cleanly. A screen
on top of a state machine that cannot recover is a screen that lies.
