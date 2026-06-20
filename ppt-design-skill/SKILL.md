---
name: ppt-design-skill
description: Design and beautify PowerPoint slides from R&D reports — color themes, layout selection, content density, visual hierarchy, and per-slide design instructions.
---

# PPT Design Skill

Use this skill when the user asks to convert an R&D report (Markdown) into a beautifully designed PowerPoint presentation.

This skill guides the LLM to act as a **presentation designer**. It reads a Markdown report and outputs a structured JSON design plan — one entry per slide — that a rendering engine (python-pptx) consumes to produce a polished .pptx file.

## Core Mission

Convert:

```text
R&D report (Markdown, ~3000-8000 words, with tables/lists/headings)
```

into:

```text
Per-slide design plan (JSON) → rendered .pptx with professional visual design
```

## Design Principles

1. **One idea per slide** — never cram multiple unrelated topics onto one page.
2. **Visual hierarchy** — title > key takeaway > supporting details. The eye should land on the most important element first.
3. **Content density ceiling** — max 6 bullets per slide, max 5 columns per table, max 8 data rows (overflow → truncate + indicator).
4. **Color with purpose** — use accent colors to highlight, not to decorate. Zebra stripes for tables, accent bars for section dividers.
5. **Consistency** — same font family throughout (Microsoft YaHei), consistent spacing, aligned baselines.
6. **Readability first** — minimum font size 9pt for table data, 11pt for body text, 18pt for slide titles.

## Color Theme System

The base theme is **Tech Blue** (deep blue primary). Each slide may pick an accent variant to create visual rhythm:

| Variant   | Primary (hex) | Accent (hex) | Use when                         |
|-----------|---------------|--------------|----------------------------------|
| `blue`    | #1A3C6E       | #2E5C8A      | Default, neutral content         |
| `teal`    | #1A3C6E       | #0D9488      | Positive results, opportunities  |
| `amber`   | #1A3C6E       | #D97706      | Warnings, risks, cautions        |
| `slate`   | #1A3C6E       | #475569      | Background info, methodology     |
| `indigo`  | #1A3C6E       | #4F46E5      | Key findings, highlights         |

## Layout Type Library

Each content slide must declare a `layout` type:

| Layout        | Description                                          | Best for                                    |
|---------------|------------------------------------------------------|---------------------------------------------|
| `bullets`     | Title + bullet list (supports 2 indent levels)       | Summaries, overviews, qualitative findings  |
| `table`       | Title + auto-scaled table (fills most of the slide)  | Patent lists, CTQ matrices, comparison data |
| `split`       | Title + left bullets + right table (50/50)           | Context + supporting data                   |
| `quote`       | Large centered callout text + attribution            | Key insights, customer voice, conclusions   |
| `comparison`  | Two-column side-by-side comparison                   | Trade-offs, before/after, pros/cons         |
| `metrics`     | 2-4 big-number cards in a row + caption              | KPIs, quantitative highlights               |

Non-content slides use `type` directly: `cover`, `toc`, `section`, `closing`.

## Content Density Rules

When designing each slide, the LLM must **condense** the source Markdown:

- **Bullets**: Rewrite verbose paragraphs into ≤15-word bullet points. Merge related points. Drop filler.
- **Tables**: Keep only essential columns (max 5). If a table has >8 rows, select the most important rows and note truncation. Rename columns to short labels (≤8 chars if possible).
- **Highlights**: Identify 1-3 key numbers, terms, or findings per slide and mark them in `highlights` for visual emphasis.
- **Callouts**: If a slide has a critical insight or risk, extract it into `callout` for a highlighted box.

## Output Format — JSON Design Plan

The LLM must output **only** a JSON object (no markdown fences, no explanation) with this schema:

```json
{
  "title": "Overall presentation title",
  "theme": "blue",
  "slides": [
    {
      "type": "cover",
      "title": "Presentation title",
      "subtitle": "R&D Portfolio Intelligence Report"
    },
    {
      "type": "toc",
      "items": ["Section 1 name", "Section 2 name", "..."]
    },
    {
      "type": "section",
      "title": "Section divider title",
      "accent": "teal"
    },
    {
      "type": "content",
      "title": "Slide title (concise, ≤20 chars if possible)",
      "layout": "bullets",
      "accent": "blue",
      "bullets": [
        {"text": "Key point (≤15 words)", "level": 0},
        {"text": "Supporting detail", "level": 1}
      ],
      "highlights": ["关键数据或术语"],
      "callout": "可选：重点提示框内容，无则省略此字段"
    },
    {
      "type": "content",
      "title": "Patent Priority List",
      "layout": "table",
      "accent": "indigo",
      "tables": [
        {
          "headers": ["专利号", "受让人", "评分", "理由"],
          "rows": [["US1234567", "3M", "85", "最相关"]],
          "note": "共12篇，展示Top 8"
        }
      ],
      "highlights": ["3M", "85"]
    },
    {
      "type": "content",
      "title": "Tradeoff Analysis",
      "layout": "split",
      "accent": "amber",
      "bullets": [
        {"text": "左侧要点", "level": 0}
      ],
      "tables": [
        {"headers": ["X", "Y"], "rows": [["值1", "值2"]]}
      ]
    },
    {
      "type": "content",
      "title": "Key Finding",
      "layout": "quote",
      "accent": "indigo",
      "callout": "核心发现的一句话总结，用于大字居中展示"
    },
    {
      "type": "closing"
    }
  ]
}
```

## Slide Count Guidelines

- Reports < 2000 words → 8-12 slides
- Reports 2000-5000 words → 12-20 slides
- Reports > 5000 words → 20-30 slides (never exceed 35)

Always include: 1 cover + 1 TOC + N section dividers + M content slides + 1 closing.

## Quality Checklist

Before outputting the JSON plan, the LLM should self-check:

- [ ] Every slide has a clear, concise title
- [ ] No slide exceeds 6 bullets
- [ ] No table exceeds 5 columns or 8 rows
- [ ] Accent colors vary to create visual rhythm (not all `blue`)
- [ ] Key findings are marked in `highlights`
- [ ] Critical risks/insights have `callout` boxes
- [ ] Section dividers exist between major topics
- [ ] Total slide count is within guidelines
