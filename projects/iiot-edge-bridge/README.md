# IIoT edge bridge

**Status:** ⚪ planned — do not start until one PLC cell runs
**Stack:** OPC UA + MQTT + Ignition
**Source of tags:** [twincat-packml-cell](../twincat-packml-cell) and/or the Logix cell —
the same contract either way

## Why it is last

A broker with no PLC behind it is a screenshot. This folder is sequenced deliberately, and
the sequencing is part of the argument: the interesting claim is *the screen does not change
when the controller brand does*, and that claim is untestable until a controller exists.

## v1 = Pattern A from [docs/iiot-path.md](../../docs/iiot-path.md)

1. Curated OPC UA namespace — a contract, never a dump of the whole controller
2. Ignition: four views, historian on state and first-out
3. Optional MQTT event topic `plant/cell01/evt/fault`

## Done when

- [ ] Ignition browses the PLC's OPC UA namespace and drives all four views from it
- [ ] Alarms are detected in the PLC and displayed by Ignition — one alarm engine, not two
- [ ] Commands written from Ignition execute only if the PLC state machine allows them
- [ ] Point the same screens at the other PLC brand; nothing on the screen changes
- [ ] Historian shows the state change from the recover-from-fault clip

## Explicitly out of scope for v1

Sparkplug B, Kafka, UNS mega-trees, cloud IoT hubs. All of them are v2 decisions that get
easier once Pattern A works, and all of them are ways to avoid the part that is actually hard.
