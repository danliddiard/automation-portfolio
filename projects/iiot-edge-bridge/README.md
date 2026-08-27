# IIoT edge bridge

**Status:** planned — do not start until one PLC cell runs  
**Stack:** OPC UA + MQTT + Ignition  
**Source of tags:** `twincat-packml-cell` and/or the Logix cell, same contract

v1 = Pattern A in [docs/iiot-path.md](../../docs/iiot-path.md):

1. Curated OPC UA namespace
2. Ignition four views + historian on state and first-out
3. Optional MQTT event topic `plant/cell01/evt/fault`
