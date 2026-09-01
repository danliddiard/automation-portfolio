# Note: two motion instructions sharing one control tag

**Where this goes:** LinkedIn, or the five minutes of an interview where someone asks how you review code you did not write.

A gearing rung issued four `MAG` instructions — four followers geared to one master. The fourth read:

```
MAG(Zippy_Axis_145, Zippy_Axis_141, MAG_144, ...)
                                    ^^^^^^^ should be MAG_145
```

Classic copy-paste: the slave axis got updated, the motion control tag did not. Two motion instructions sharing one `MOTION_INSTRUCTION` tag fight over the same `.EN` / `.DN` / `.IP` / `.ER` bits, so axis 145's gearing faults would have been invisible, or blamed on 144.

**It was found before the feature was ever used**, by counting rather than by reading:

```
MAG_142   referenced 1 time
MAG_143   referenced 1 time
MAG_144   referenced 2 times   <-- one too many
MAG_145   declared, referenced 0 times
```

A `MOTION_INSTRUCTION` tag that is declared and never referenced is a reliable smell. Somebody created it intending to use it, and whatever was supposed to use it is pointing somewhere else.

Fix / practice:

- On any block of repeated motion instructions, census the control tags before trusting the block. Every instruction gets exactly one, and every declared tag gets used.
- The unused tag is the easier half to spot. Search for declared-but-unreferenced first; it points straight at the duplicate.
- This does not throw a verify error. Studio 5000 will not tell you.
- The same census catches the harder case: one control tag reached by two rungs that can be true at the same time. Reuse across mutually exclusive rungs is fine; reuse across concurrent ones is the same bug wearing a longer coat.
