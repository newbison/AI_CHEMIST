---
name: ppt-design-skill
description: Create beautiful PowerPoint presentations from R&D reports using PptxGenJS — design principles, color palettes, layout variety, and per-slide generation.
---

# PPT Design Skill

## Quick Reference

| Task | Guide |
|------|-------|
| Create from scratch | Read [pptxgenjs.md](pptxgenjs.md) |
| Design principles | This file |

---

## Creating from Scratch

**Read [pptxgenjs.md](pptxgenjs.md) for the full PptxGenJS API reference.**

Use this approach when generating a new presentation from an R&D report. Write a complete Node.js script that uses `pptxgenjs` to create every slide programmatically.

---

## Design Ideas

**Don't create boring slides.** Plain bullets on a white background won't impress anyone. Apply these ideas for every slide.

### Before Starting

- **Pick a bold, content-informed color palette**: The palette should feel designed for THIS topic. If swapping your colors into a completely different presentation would still "work," you haven't made specific enough choices.
- **Dominance over equality**: One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp accent. Never give all colors equal weight.
- **Dark/light contrast**: Dark backgrounds for title + conclusion slides, light for content ("sandwich" structure). Or commit to dark throughout for a premium feel.
- **Commit to a visual motif**: Pick ONE distinctive element and repeat it — rounded image frames, icons in colored circles, thick single-side borders. Carry it across every slide.

### Color Palettes

Choose colors that match your topic — don't default to generic blue. Use these palettes as inspiration:

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| **Midnight Executive** | `1E2761` (navy) | `CADCFC` (ice blue) | `FFFFFF` (white) |
| **Forest & Moss** | `2C5F2D` (forest) | `97BC62` (moss) | `F5F5F5` (cream) |
| **Coral Energy** | `F96167` (coral) | `F9E795` (gold) | `2F3C7E` (navy) |
| **Warm Terracotta** | `B85042` (terracotta) | `E7E8D1` (sand) | `A7BEAE` (sage) |
| **Ocean Gradient** | `065A82` (deep blue) | `1C7293` (teal) | `21295C` (midnight) |
| **Charcoal Minimal** | `36454F` (charcoal) | `F2F2F2` (off-white) | `212121` (black) |
| **Teal Trust** | `028090` (teal) | `00A896` (seafoam) | `02C39A` (mint) |
| **Berry & Cream** | `6D2E46` (berry) | `A26769` (dusty rose) | `ECE2D0` (cream) |
| **Sage Calm** | `84B59F` (sage) | `69A297` (eucalyptus) | `50808E` (slate) |
| **Cherry Bold** | `990011` (cherry) | `FCF6F5` (off-white) | `2F3C7E` (navy) |

### For Each Slide

**Every slide needs a visual element** — image, chart, icon, or shape. Text-only slides are forgettable.

**Layout options:**
- Two-column (text left, illustration on right)
- Icon + text rows (icon in colored circle, bold header, description below)
- 2x2 or 2x3 grid (image on one side, grid of content blocks on other)
- Half-bleed image (full left or right side) with content overlay

**Data display:**
- Large stat callouts (big numbers 60-72pt with small labels below)
- Comparison columns (before/after, pros/cons, side-by-side options)
- Timeline or process flow (numbered steps, arrows)

**Visual polish:**
- Icons in small colored circles next to section headers
- Italic accent text for key stats or taglines

### Typography

**Choose an interesting font pairing** — don't default to Arial. Pick a header font with personality and pair it with a clean body font.

| Header Font | Body Font |
|-------------|-----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Calibri | Calibri Light |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Impact | Arial |
| Palatino | Garamond |
| Consolas | Calibri |

| Element | Size |
|---------|------|
| Slide title | 36-44pt bold |
| Section header | 20-24pt bold |
| Body text | 14-16pt |
| Captions | 10-12pt muted |

### Spacing

- 0.5" minimum margins
- 0.3-0.5" between content blocks
- Leave breathing room—don't fill every inch

### Avoid (Common Mistakes)

- **Don't repeat the same layout** — vary columns, cards, and callouts across slides
- **Don't center body text** — left-align paragraphs and lists; center only titles
- **Don't skimp on size contrast** — titles need 36pt+ to stand out from 14-16pt body
- **Don't default to blue** — pick colors that reflect the specific topic
- **Don't mix spacing randomly** — choose 0.3" or 0.5" gaps and use consistently
- **Don't style one slide and leave the rest plain** — commit fully or keep it simple throughout
- **Don't create text-only slides** — add images, icons, charts, or visual elements; avoid plain title + bullets
- **Don't forget text box padding** — when aligning lines or shapes with text edges, set `margin: 0` on the text box or offset the shape to account for padding
- **Don't use low-contrast elements** — icons AND text need strong contrast against the background; avoid light text on light backgrounds or dark text on dark backgrounds
- **NEVER use accent lines under titles** — these are a hallmark of AI-generated slides; use whitespace or background color instead

---

## R&D Report → PPT Conversion Rules

When converting an R&D report to slides:

1. **One idea per slide** — never cram multiple unrelated topics onto one page.
2. **Visual hierarchy** — title > key takeaway > supporting details.
3. **Content density ceiling** — max 6 bullets per slide, max 5 columns per table, max 8 data rows.
4. **Condense aggressively** — rewrite verbose paragraphs into ≤15-word bullet points. Merge related points. Drop filler.
5. **Vary accent colors** across sections to create visual rhythm (not all the same color).
6. **Always include**: 1 cover + 1 TOC + N section dividers + M content slides + 1 closing.

### Slide Count Guidelines

- Reports < 2000 words → 8-12 slides
- Reports 2000-5000 words → 12-20 slides
- Reports > 5000 words → 20-30 slides (never exceed 35)

---

## Output Format

You must output a **complete, runnable Node.js script** that uses `pptxgenjs` to generate the presentation. The script must:

1. `require("pptxgenjs")` at the top
2. Create a new `pptxgen()` instance
3. Set `pres.layout = 'LAYOUT_16x9'`
4. Define slide masters if needed
5. Add slides with `pres.addSlide()`
6. Add content to each slide (text, shapes, tables, etc.)
7. Call `pres.writeFile({ fileName: "output.pptx" })` at the end
8. Use `console.log("DONE: output.pptx")` when complete

**IMPORTANT: Output ONLY the JavaScript code. No markdown fences, no explanations.** The code will be saved to a `.js` file and executed with Node.js directly.

### Critical PptxGenJS Rules

- Colors: NEVER use `#` prefix — `"FF0000"` NOT `"#FF0000"`
- Bullets: Use `bullet: true` — NEVER Unicode bullet characters like "•"
- Multi-line text: Use `breakLine: true` between items
- Hex opacity: NEVER use 8-char hex like `"00000020"` — use the `opacity` property instead
- Object reuse: NEVER reuse option objects across calls — create fresh objects each time (or use factory functions)
- Each presentation needs a fresh `pptxgen()` instance
