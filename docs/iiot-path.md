# One modern IIoT path: OPC UA + MQTT + Ignition

This is not three hobbies. It is **one pipe** from the PLC to a usable screen and a historian.

## Why these three

| Piece | Job | What it is not |
|---|---|---|
| **OPC UA** | Structured, browsable, secure read/write of PLC tags. The industrial API. | Not a dashboard. |
| **MQTT** | Cheap event pipe: cycle complete, fault raised, OEE tick. Good for edge → broker → many consumers. | Not a replacement for a PLC. Do not put interlocks in MQTT. |
| **Ignition** | The place humans and history live: HMI, alarms, trends, transactions. Already respected in Utah plants. | Not the controller. |

Together they answer the interview question: *how does the cell talk to the rest of the plant without a custom driver mess?*

Logix and TwinCAT both speak OPC UA. That is the point of picking this path instead of a brand-only SCADA.

## Architecture (build this, nothing fancier)

```
  [ TwinCAT cell ]                    [ CompactLogix / SoftLogix cell ]
           \                                  /
            \         OPC UA                  /
             +-------- curated namespace ----+
                        |
                        |
              [ Ignition OPC UA connection ]
                        |
                        +-- Perspective / Vision screens
                        +-- Alarm journal
                        +-- Tag historian
                        |
                        +-- MQTT Engine  <--- broker (Mosquitto / HiveMQ)
                                  ^
                                  |
                     PLC or edge client publishes
                     plant/cell01/evt/fault
                     plant/cell01/oee
```

Two valid wiring patterns. Pick **one** for v1.

### Pattern A — Ignition as the hub (simpler, preferred first)

1. PLC exposes a small OPC UA namespace.
2. Ignition browses that server and becomes the system of record for display/history.
3. If you want MQTT, Ignition MQTT Engine / Transmission can publish selected tags. You do not need a second custom publisher yet.

Use this if the goal is “I can show a plant screen and a trend in 30 minutes.”

### Pattern B — PLC / TwinCAT publishes MQTT itself

1. Same OPC UA for Ignition (still do this).
2. TwinCAT TF6701 / a small Python or Node-RED client publishes **events only** to MQTT.
3. Ignition subscribes for those events.

Use this when you want to prove the controller can be an edge node, not just a tag source.

Do **not** start with Sparkplug B, Kafka, UNS mega-trees, or cloud IoT hubs. Those are v2 after Pattern A works.

## What to expose (curated namespace)

Never dump the whole controller. Expose a contract.

```
Cell
  Identity
    Name            STRING
    Version         STRING
  State
    PackML          DINT / ENUM
    Mode            DINT        // Auto / Manual / Maint
    InCycle         BOOL
  Production
    CycleCount      DINT
    GoodCount       DINT
    RejectCount     DINT
    CycleTime_ms    DINT
  Recipe
    Name            STRING
    StationTime_ms  DINT
    InspectLimit    REAL
  Alarms
    Active          BOOL
    FirstOutCode    DINT
    FirstOutText    STRING
    ResetReq        BOOL
  Cmd               // writes from SCADA, interlocked in PLC
    Start           BOOL
    Stop            BOOL
    Hold            BOOL
    Reset           BOOL
```

Rules:

- Commands are written from Ignition, **executed only if** the PLC state machine allows it.
- Alarms are detected in the PLC. Ignition displays them. Do not invent a second alarm engine.
- Analog noise stays in the PLC. MQTT gets events and counters, not 50 ms waveforms.

## TwinCAT-specific notes

- Engineering is free. TF6100 OPC UA and TF6701 MQTT run on 7-day trial licenses while you learn.
- Mark only the contract structs with the OPC UA publish pragma. Do not expose internal FB guts.
- Keep ADS for engineering. Use OPC UA for Ignition. Do not make Ignition talk raw ADS if you can avoid it — OPC UA is the portable story.

## Logix-specific notes

- SoftLogix or a CompactLogix with the OPC UA server module / FactoryTalk Linx OPC UA is enough.
- Same tag contract as TwinCAT so Ignition screens are reusable.
- L5X-from-spreadsheet work can generate this UDT once and stamp it on both a real and a lab controller.

## Ignition v1 screen list (four views, stop)

1. Overview — PackML state, counts, last first-out
2. Alarms — active + history
3. Recipe — load three recipes, write only in Idle / Held
4. I/O / sim faceplate — raw bits for demo forcing

No navigation maze. No 40-template ISA-101 thesis. High-performance HMI: gray background, color only for abnormal.

## Minimum demo script (this is the interview)

1. Cell running in Auto. Ignition overview live.
2. Force a station timeout in the PLC / sim.
3. First-out code appears on the HMI and in the alarm journal.
4. MQTT client (MQTT Explorer) shows `plant/cell01/evt/fault` if Pattern B is on.
5. Reset from Ignition. Cell does **not** sneak back into Execute until Reset + Start.
6. Historian shows the state change.

If that loop works, the IIoT path is done enough to put on LinkedIn.

## What “done” is not

- A broker with no PLC behind it
- Node-RED blinking a dashboard with no alarm philosophy
- Sparkplug certificates before a single curated tag list
- Cloud dashboards while the cell cannot recover from a fault

## Suggested build order

1. PackML + first-out on one PLC (TwinCAT sim **or** SoftLogix / Factory I/O).
2. OPC UA contract tags only.
3. Ignition connected, four views, historian on `PackML` + `FirstOutCode`.
4. Optional MQTT event publish.
5. Then repeat the same contract on the other PLC brand so the screen does not change.
