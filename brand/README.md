# Nest & Rest Cleaning — logo files

All text is converted to vector outlines, so these render identically for
everyone whether or not they have the fonts installed. Hand any of them to a
printer, a sign shop or an embroiderer as-is.

## Which file to use

| File | Use it for |
| --- | --- |
| `nest-rest-lockup.svg` | **Your default.** Website header, invoices and quotes, van doors, business cards, booking emails. |
| `nest-rest-lockup-black.svg` | One-colour printing, faxed or photocopied paperwork, newspaper ads. |
| `nest-rest-lockup-white.svg` | On navy or any dark photo. |
| `nest-rest-wordmark.svg` | Where the icon would crowd — email signature, letterhead, a sponsorship strip. Also the three `-black` / `-white` variants. |
| `nest-rest-icon.svg` | The folded corner on its own, where the name is already nearby. |
| `nest-rest-monogram.svg` | Small and square only: favicon, app icon, Instagram and Google profile circles, polo embroidery, invoice stamp. |
| `nest-rest-seal.svg` | Trust moments: door hanger left after a clean, rear van door, review cards. Never below 60 mm / 90 px. |
| `favicon-512.png` | Browser tab and app icon. Most hosts will resize this down for you. |

PNGs are provided at 1024–2048 px for anywhere that won't take an SVG
(Google Business, Instagram, some invoice software). They have transparent
backgrounds except `nest-rest-lockup-white-2048.png`, which is flattened onto
navy so the white marks are visible.

## Colours

| Name | Hex | Role |
| --- | --- | --- |
| Nest Navy | `#13293D` | Primary — wordmark, headings, van |
| Hearth Clay | `#C96F4A` | Accent — the ampersand, one button, one stripe. Roughly 5% of any surface |
| Linen | `#F4F1EA` | Ground — about 70% of any surface |
| Clay Deep | `#A4512C` | Text-safe clay. Plain `#C96F4A` on linen is 3.2:1 and fails accessibility; use this for clay type under 24 px |
| Slate | `#4A5A6B` | Body copy |
| Paper | `#FFFFFF` | Cards and forms floated on linen — never the page ground |

## Type

- **Fraunces** — wordmark and headings, weight 600. The ampersand is weight
  400 at 1.14× the cap size, which is what gives it the flourish.
- **Inter** — "CLEANING", body copy and all interface text. Weight 500 for the
  lockup, tracked to 0.70 em.

Both are SIL Open Font License, so they are free to use commercially,
including on products you sell. Download from Google Fonts.

## Rules

- **Clear space** on all four sides equals the height of the N. Nothing else
  enters that space.
- **Minimum size:** lockup 90 px on screen or 25 mm in print. Below that, use
  the monogram alone.
- **Never** re-space the icon against the wordmark by eye. The relationship is
  fixed: icon height = cap height × 1.8, gap = icon width × 0.4. It is already
  baked into `nest-rest-lockup.svg` — scale the whole file, don't rebuild it.
- **Never** add a drop shadow, bevel, gradient or outline.
- **Never** put "Scarborough & North York" inside the logo. It belongs on the
  seal only, and leaving it out keeps Markham and East York open to you later.
- Do not stretch. Scale proportionally.

### Before sending to an embroiderer

The monogram and the seal are drawn with strokes rather than filled shapes.
Most digitisers handle this, but if yours asks for outlined paths, open the
file in Illustrator, Inkscape or Figma and apply Object → Path → Outline
Stroke before sending. The lockup, wordmark and icon are already filled paths
and need nothing.

### Regenerating

`make_logos.py` built these from the Fraunces and Inter TTFs using fontTools
and HarfBuzz. If you ever need a different size relationship or a new variant,
that script is the source of truth rather than any one SVG.
