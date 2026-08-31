# Build sheet — STOPPED pill, FactoryTalk View ME v16

Everything below is a settings sheet, not code. An ME display is a binary `.med` inside
the `.apa`; there is no useful text artefact to commit for it, so the repo carries the
**PLC side as source** and the **HMI side as a reproducible build sheet**. Follow it
top to bottom and the object comes out identical every time.

![Seq_Status pill states](seq-status-pill.svg)

**Prerequisite:** the controller has `Seq_Status` and the `HMI_Status` routine. See
[../src](../src) and [state-model.md](state-model.md).

---

## 1. Create the object

`Objects > Indicator > Multistate Indicator`, then drag it on the display.

Size it so the longest caption — `COMM ERROR` — fits at the chosen font without the text
wrapping or clipping. ME truncates silently; it does not warn you.

## 2. States tab

Set **Number of states = 4**. States are indexed 0–3 and map 1:1 onto the tag value.

| State | Caption | Back color | Caption color | Blink |
|---|---|---|---|---|
| 0 | `STOPPED` | `#595959` — RGB 89, 89, 89 | `#FFFFFF` | off |
| 1 | `RUNNING` | `#00783C` — RGB 0, 120, 60 | `#FFFFFF` | off |
| 2 | `HOLDING` | `#FFC000` — RGB 255, 192, 0 | `#000000` | off |
| 3 | `FAULTED` | `#C00000` — RGB 192, 0, 0 | `#FFFFFF` | off |
| **Error** | `COMM ERROR` | `#000000` | `#FFFFFF` | **on** |

None of these are in ME's 48-swatch palette. Click the back-color swatch, choose
**Other / Custom**, and type the RGB triplet. Do it once, then copy-paste the finished
object for every other pill in the application so the colors cannot drift between screens.

Three things about this table are choices, not defaults:

- **Captions carry the state; color only reinforces it.** The pill still reads correctly
  in greyscale and to a red/green colour-blind operator. Never build a status object whose
  only difference between "running" and "faulted" is hue.
- **Amber takes black text.** White on `#FFC000` is roughly 1.9:1 contrast and is
  unreadable through a scratched panel window at an angle. Black on amber is ~11:1.
- **Only the Error state blinks.** Blink means "this number is not trustworthy". If
  FAULTED also blinks, blinking stops meaning anything.

### Set the Error state. It is not optional.

The Error state is what ME shows when it cannot read the tag — shortcut down, controller
in program mode, wrong path, tag renamed. **Left at its default it renders as a blank
grey box, which on a dark HMI is very nearly a convincing STOPPED pill.** A stopped
machine and an HMI that has lost the controller are not the same situation and must not
look the same.

Caption it `COMM ERROR`, black with white text, blink on. This is also your fastest field
diagnostic: if every pill on the screen goes black and blinks at once, stop looking at the
program and go look at the shortcut.

## 3. Connections tab

One connection. One tag.

| Connection | Value |
|---|---|
| `Indicator` | `{::[SHORTCUT]Seq_Status}` |

Replace `SHORTCUT` with the actual FactoryTalk Linx device shortcut name — this is the
name from `Communication Setup`, **not** the controller name and not the project name. The
leading `::` is what makes it an absolute reference; drop it and the reference resolves
against the display's own folder and fails at runtime, not at validate.

Because this is a direct controller reference, **nothing needs to be added to the HMI tag
database.** Do not create a duplicate ME tag pointing at the same address — it is a second
place to maintain and a second place to get it wrong.

## 4. Common / General tab

| Setting | Value | Why |
|---|---|---|
| Trigger type | **Value** | `Seq_Status` is a magnitude, 0–3 |
| Border style | Raised or none, consistent app-wide | — |
| Font | Whatever the app standard is, bold | Legible at panel distance |

**Value vs LSBit.** Use `Value` here. `LSBit` is for a tag whose *individual bits* are
driven independently — it selects the state from the position of the lowest set bit. Point
`LSBit` at a DINT holding 0/1/2/3 and value 3 (bits 0 *and* 1 set) selects state 1, so
FAULTED silently displays as RUNNING. This is the single most common way this object is
mis-wired. `HMI_Status` writes a magnitude, so the trigger is `Value`.

## 5. Test it before you call it done

Go online, put the controller in Run, and drive `Seq_Status` with the watch window:

| Set `Seq_Status` to | Expect |
|---|---|
| 0 | grey `STOPPED` |
| 1 | green `RUNNING` |
| 2 | amber `HOLDING` |
| 3 | red `FAULTED` |
| 4 (out of range) | the Error state |
| — pull the Ethernet cable | blinking black `COMM ERROR` within the shortcut timeout |

The last two rows are the test. Anyone can make a pill turn green.

Then run the machine for real and confirm the transitions: START gives you a brief amber
during the MSO settle before green, and STOP gives you amber for the shutdown decel before
grey. If STOP goes straight to grey, the JSR is in the wrong place in `MainRoutine` or the
step-99 leg got gated by `Auto_Running`.

---

## Variant — the ISA-101 / high-performance version

[docs/iiot-path.md](../../../docs/iiot-path.md) in this repo says: *gray background, color
only for abnormal.* Taken strictly, that rules out a green RUNNING pill — under
ISA-101 a normally-running machine is not supposed to spend its whole shift lit up, because
saturated color is a finite resource and spending it on "everything is fine" leaves you
nothing that pulls an operator's eye when something is not.

The build sheet above is the conventional-color version, which is what most plants and most
interviewers expect to see. If you want the strict one, change two rows and leave the rest
alone:

| State | Back color | Caption color |
|---|---|---|
| 0 STOPPED | `#D9D9D9` — RGB 217, 217, 217 | `#000000` |
| 1 RUNNING | `#F2F2F2` — RGB 242, 242, 242 | `#000000` |
| 2 HOLDING | `#FFC000` (unchanged) | `#000000` |
| 3 FAULTED | `#C00000` (unchanged) | `#FFFFFF` |

Normal states go quiet, abnormal states keep the color, and the captions still carry the
meaning. Worth building both and putting them side by side in the demo video — it is a
one-minute answer to "what is your HMI philosophy?" that most candidates cannot give.
