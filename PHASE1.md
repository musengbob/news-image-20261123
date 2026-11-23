# PHASE 1 — news-image-20261123

## Summary
- 36 stories, all researched 23 Nov 2026 (07:25–07:45 WIB) and dated
  Monday 23 November 2026: 3 heroes + 9 briefs + 24 numbered.
- Heroes: COP31 collapses with no deal (Reuters/AFP); NATO meets Monday
  over the Poland missiles (Reuters/eutoday); 24 body bags after the
  Indonesia factory fire, search resumes Monday (AP/BBC).
- Playbook reproduced from 20261122 (judge 977,797): dense front page +
  world map, masthead "THE WORLD TODAY", dateline Monday 23 November 2026.
  `compose.py` adapted from the 20261122 renderer (same layout, new
  NATO + factory-fire hero art, new stories, stats, markers, date check).
- No 20261122 stories or pixels reused; entry.png drawn fresh by compose.py.

## Files (~/workspace/makefun/entries/news-image-20261123/)
- STORIES.md — 36 stories with source + date each, plus DATE CHECK section
- compose.py — PIL renderer (deterministic)
- entry.png — 1024×1024, 152,786 bytes (≤1 MiB), sha256
  9cf2f1d35fe89e9c46e133a86b85517a230a983dc8052ee11ed4775b37aee3e6
- main.ts — Node 22 stdlib only, copies entry.png to $MAKEFUN_OUTPUT_DIR
- README.md — description + run instructions (no badges/About — Phase 2)

## Verification
- `python3 compose.py` → final y = 1015 (canvas 1024), no assertion
  failures (all 24 numbered headlines fit one line).
- Viewed entry.png at full size: masthead, ticker, stat strip, 3 heroes,
  9 briefs, world map with 12 red markers, DATE CHECK box, 24 numbered
  items, footer all legible; no overlapping or garbled text.
- Viewed downscaled to 300px: masthead, heroes and map still read;
  numbered list is small (same as the 20261121/22 playbook).
- Defect found and fixed: stat-strip labels overlapped neighbouring
  columns (e.g. "body bags in Indonesia factory fire" ran into the next
  label). Shortened all six labels; re-rendered and re-checked the strip
  crop — clean, no overlap.
- `mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts` → out/entry.png
  byte-identical to entry.png (sha256 match). Only a harmless Node
  MODULE_TYPELESS_PACKAGE_JSON warning (same as the 20261122 pattern).

## Notes / needs fixing
- Nothing outstanding. Dating caveat documented in STORIES.md: several
  items are Monday developments of Sunday events (COP31 collapse, NATO
  meeting, factory search resuming, Day 5 Test play); the DATE CHECK box
  in the image names the earlier events they follow. The Korea minister
  resignation was announced Sun 22 Nov and is carried as Monday's news
  per the 23 Nov assembly lists — flagged in STORIES.md.
- Phase 2 still to do: GitHub repo, badges/About, bundle, submit.
  (Not touched here per the task.)
