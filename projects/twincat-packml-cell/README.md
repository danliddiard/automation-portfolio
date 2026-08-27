# TwinCAT 3 PackML cell

**Status:** planned  
**Platform:** TwinCAT 3 XAE + 7-day trial runtime  
**Hardware:** none required for v1 (simulated I/O)

Target machine: 2-station inspect / reject cell.

- PackML states
- `FB_Conveyor`, `FB_Station`, `FB_Divert`, `FB_FaultMgr`
- first-out stack
- recipe struct
- sim I/O layer that can later map to EtherCAT terminals

HMI and TwinSAFE sim come after the PLC recovers from a fault cleanly.

See [docs/iiot-path.md](../../docs/iiot-path.md) for how this cell is exposed.
