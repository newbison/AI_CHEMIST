---
name: ppt-design-skill
description: Create beautiful PowerPoint presentations from R&D reports using PptxGenJS — FORGE AI brand design system, card-based layouts, process flow diagrams, and per-slide generation.
---

# PPT Design Skill

## Quick Reference

| Task | Guide |
|------|-------|
| Create from scratch | Read [pptxgenjs.md](pptxgenjs.md) |
| Design principles | This file |

---

## FORGE AI Brand Design System (Default)

**Always use this design system when creating FORGE AI report PPTs.** This produces a consistent, premium look across all project outputs.

### Color Palette (Slate + Teal)

```text
dark    "0F172A"   // Slate 900 — cover, closing, CTA slides
dark2   "1E293B"   // Slate 800 — cards on dark background
teal    "0D9488"   // Teal 600 — primary accent (dominant color)
tealL   "14B8A6"   // Teal 500 — lighter accent, taglines
tealBg  "CCFBF1"   // Teal 100 — icon circle fills, light card bg
light   "F1F5F9"   // Slate 100 — content slide background
cream   "F8FAFC"   // Slate 50 — footer bar background
white   "FFFFFF"   // card fills
muted   "64748B"   // secondary text, page numbers, captions
body    "334155"   // body text on light background
amber   "F59E0B"   // secondary accent (2nd DOE, variants)
emerald "10B981"   // success / evidence level indicators
red     "EF4444"   // problem callouts, warnings
slate3  "CBD5E1"   // borders, separators, dividers
```

### Typography

| Element | Font | Size | Weight | Color |
|---------|------|------|--------|-------|
| Slide title | Arial Black | 30-34pt | Bold | dark (or white on dark bg) |
| Tagline/subtitle | Calibri | 22pt | Normal | tealL |
| Section header | Arial Black | 14-15pt | Bold | dark |
| Body text | Calibri | 10-13pt | Normal | body |
| Caption/footer | Calibri | 7.5-9pt | Italic | muted |
| Big stat number | Arial Black | 48pt | Bold | white on teal bg |

### Slide Background Strategy ("Sandwich")

- **Dark background** (`0F172A`) for cover, section dividers, and closing slides
- **Light background** (`F1F5F9`) for content slides
- **Dark slides** — all text white or tealL for contrast
- **Light slides** — teal top accent bar (0.03" tall, full width) for visual continuity

### Visual Motifs (Use Consistently Across ALL Slides)

- **Cards** — white RECTANGLE with subtle drop shadow (`blur:3, offset:1, angle:135, opacity:0.07`), teal accent bar along top edge (0.04" tall)
- **Icon circles** — OVAL 0.5" diameter with tealBg fill, icon/emoji/letter centered inside
- **Feature grids** — 2x2 or 2x3 card grids for listing capabilities, with icon circle + bold title + description per card
- **Process flows** — horizontal card sequence with → arrows between steps, numbered circles
- **Big number callouts** — large teal card, 48pt Arial Black number, description in white smaller text
- **Bottom strips** — dark card (`0F172A`) spanning full content width for key takeaway or CTA
- **Shadow helper** — always create fresh shadow objects: `const mkSh = () => ({type:"outer", blur:3, offset:1, angle:135, color:"000000", opacity:0.07})`

### PptxGenJS Code Templates

**Card with shadow:**

```javascript
slide.addShape(pres.shapes.RECTANGLE, {
  x, y, w, h, fill: { color: "FFFFFF" },
  shadow: { type: "outer", blur: 3, offset: 1, angle: 135, color: "000000", opacity: 0.07 }
});
```

**Teal accent bar on card:**

```javascript
slide.addShape(pres.shapes.RECTANGLE, {
  x, y, w: cardWidth, h: 0.04, fill: { color: "0D9488" }
});
```

**Top bar for light slides:**

```javascript
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.03, fill: { color: "0D9488" }
});
```

**Dark bottom strip:**

```javascript
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.7, y, w: 8.6, h, fill: { color: "0F172A" }
});
```

**Slide title (light slide):**

```javascript
slide.addText("Title", { x: 0.7, y: 0.3, w: 8.6, h: 0.55,
  fontSize: 30, fontFace: "Arial Black", color: "0F172A", margin: 0, bold: true });
slide.addText("Subtitle", { x: 0.7, y: 0.85, w: 8.6, h: 0.35,
  fontSize: 13, fontFace: "Calibri", color: "64748B", margin: 0 });
```

**Big stat callout card:**

```javascript
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.7, y: 1.5, w: 3.8, h: 1.3, fill: { color: "0D9488" },
  shadow: makeShadow()
});
slide.addText("80%", { x: 0.7, y: 1.5, w: 3.8, h: 0.75,
  fontSize: 48, fontFace: "Arial Black", color: "FFFFFF", align: "center", margin: 0, bold: true });
slide.addText("description", { x: 0.7, y: 2.2, w: 3.8, h: 0.55,
  fontSize: 11, fontFace: "Calibri", color: "FFFFFF", align: "center", margin: 0 });
```

**Page number (bottom right):**
```javascript
slide.addText(`${n} / ${total}`, {
  x: 8.5, y: 5.18, w: 1, h: 0.3,
  fontSize: 8, color: "64748B", align: "right", fontFace: "Calibri", margin: 0
});
```

### Layout Recipes

**2-Column Comparison:**
Two cards side-by-side: left at x=0.7, w=4.1; right at x=5.2, w=4.1. Left gets teal accent bar, right gets amber accent bar for visual contrast. Each card: bold subtitle + bullet list below.

**Horizontal Process Flow (N steps):**
Each step card width = `(totalW - gaps) / N`, centered with `(10 - totalW) / 2` start. Cards have teal top accent bar (0.04"), number circle in top-left, bold label, 2-3 line description. Connected with `→` arrows at fontSize 20, tealL color.

**Card Grid (2x2 or 2x3):**
`col = i % cols`, `row = Math.floor(i / cols)`. Position: `x = startX + col * (cardW + gap)`, `y = startY + row * (cardH + gap)`. Each card: icon circle (0.5" OVAL, tealBg fill, icon centered), bold title right of circle, description below.

**Dark Cover Slide:**
Dark background (`0F172A`). Decorative semi-transparent teal rectangles at angles as background elements. Large bold title (52pt Arial Black, white). Tagline (22pt Calibri, tealL). Subtitle (15pt, muted). Small footer text at bottom.

---

## Alternate Design Palettes

If the report topic doesn't suit the slate/teal brand, choose from these alternatives:

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
