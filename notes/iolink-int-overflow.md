# Note: IO-Link beacon command looks negative after MOVE to INT

**Where this goes:** LinkedIn or a short talk track, not a standalone repo.

When a command word is calculated in a DINT (example: Pattern 8 × 4096 = 32768) and then MOVEd into a module INT tag, Studio 5000 displays the INT as **-32768**. The bit pattern is still correct. The device still responds. This is signed 16-bit wrap, not a broken beacon.

Fix / practice:

- Keep the math in DINT.
- If the module tag is INT, document that 0x8000 will display negative.
- Do not “fix” it by clamping to 32767 unless the device spec actually forbids bit 15.
- Verify on the wire / device, not by the watch window sign.
