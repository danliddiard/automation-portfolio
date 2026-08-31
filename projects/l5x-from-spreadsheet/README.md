# L5X generation from spreadsheets

**Status:** 🟡 scoped — source pending
**Platform:** Studio 5000 / Logix L5X
**Why it is here:** this is engineering automation, not a student timer lab. The story is
*I stopped hand-typing four hundred tags,* which is a story about judgement and time, not syntax.

## The problem

A cell's tag list, alarm list and faceplate instances all come from the same underlying
equipment list, and all three get typed by hand into Studio 5000. Every retype is a fresh
chance for `Cnv_03_Jam` and `CNV3_Jam` to end up in the same controller, and every scope
change means doing it again.

L5X is XML. The equipment list is already a table. There is no reason a human is the
transformation between them.

## Scope for v1

- Example input workbook — dummy tag names only, nothing that names a plant
- The script, or documented steps, that emit L5X
- A small sample `.L5X` fragment: tags, one UDT, one routine stub
- What Studio 5000 version it was tested against, and what it was **not** tested against

## Done when

- [ ] Spreadsheet row → imported tag and routine in Studio 5000, no hand-typed boilerplate
- [ ] Generated L5X imports clean on a real controller project
- [ ] Rerunning the generator on a changed row updates rather than duplicates
- [ ] 90-second clip: edit a row, regenerate, import, show the tag appear

## Not decided yet

Whether the generator emits a whole routine or only tags and UDTs. Generating ladder is the
flashier demo; generating the tag and UDT layer is the part that actually saves the day and
survives review. Probably both, with the ladder half clearly marked as scaffolding.
