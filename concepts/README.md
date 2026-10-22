# Round 1 — concept directions

Four directions for the NEST & REST CLEANING redesign. Pick one and it gets
built out properly in round 3.

| File | What it is |
| --- | --- |
| `round1-board.png` | **Start here.** All four side by side, each with a 64 px icon, a 32 px favicon test and a one-colour navy version. |
| `concept-a-the-woven-nest.svg` | A — nest seen from above, two woven rings of twigs around a home |
| `concept-b-the-rest-crescent.svg` | B — crescent that doubles as a moon and a cradle |
| `concept-c-the-fresh-ampersand.svg` | C — the ampersand itself carries a leaf and a glint |
| `concept-d-the-nandr-house-badge.svg` | D — N&R monogram in a house-shaped badge |
| `build_concepts.py` | Source of truth. All four are drawn in code; text is outlined, so no font is required to open the SVGs. |
| `ideogram/` | (empty) Ideogram's CDN is blocked by this session's network policy — see the permalinks in the chat instead. |
| `ai-explorations/` | Earlier AI concept sketches used as reference for the four directions above. |

Colours here are a **working palette only** — the three real palette options
come at round 2, along with Adobe Fonts type pairings. Nothing below is final:

- Navy `#0F2F43` · Teal `#1A9E96` · Deep teal `#12776F`
- Sky `#7FCBE3` · Leaf `#6ED3A8` · Cream `#F6F1E8` · Gold `#E4A951`

Type is Inter throughout, standing in until the Adobe Fonts pairings are chosen.

---

# Round 2 — colour + type

`round2-board.png` — three combinations applied to concept A, each with the real
name and the real tagline, a reversed version on the primary, the palette with
hex codes and roles, and **computed** WCAG contrast figures.

All six fonts are available in Adobe Fonts (checked with `find_fonts`, all
entitled). The TTFs in `fonts/` come from Google Fonts, where the same families
are published — that is what lets these boards render the pairings rather than
describe them.

| # | Palette | Type pairing |
| --- | --- | --- |
| 1 | Linen & Teal — warm, homely | Quicksand Bold + Nunito Sans |
| 2 | Harbour — cool, trustworthy | Poppins SemiBold + Fira Sans |
| 3 | Morning — soft, airy | Montserrat Bold + Playwrite IE (script tagline) |

Every primary was darkened from its first draft until white-on-primary and
primary-on-background both cleared WCAG AA (4.5:1). The first drafts failed:
#0E8C86 gave 4.1:1 and #1FA39B gave 3.1:1 for white on primary, which would
have broken buttons and small teal text.
