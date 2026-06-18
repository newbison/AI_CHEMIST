# Workflow 04a — Patent Search and Rank

## Purpose

Turn the patent search plan from `workflows/03_evidence_mining.md` into a ranked, de-duplicated patent set ready to hand to `patent-xy-extraction-skill`.

This step owns the **search → score → select top-N** pipeline. It does NOT extract Xs/Ys — extraction is delegated to `patent-xy-extraction-skill` in `04_patent_doe_extraction.md`.

## Inputs

- The Patent Search Plan from `03_evidence_mining.md` (keyword blocks, IPC/CPC, assignees).
- The active CTQs (to anchor relevance scoring).
- The product/platform context.
- Top-N parameter (default **5–8** per VOC; configurable per portfolio — record the chosen value).

## Steps

1. Execute each search block from the search plan (keywords, classification codes, assignee names).
2. De-duplicate by patent family / publication number.
3. Score every candidate using `rubrics/patent_relevance_scoring.md` (0–50 across 10 dimensions).
4. Sort descending by total score.
5. Apply the selection rule:
   - score >= 30 → candidate for extraction
   - score < 30 → background only (record, do not extract)
6. Select the top-N candidates that score >= 30.
7. Emit the Patent Priority List using `templates/patent_priority_list_template.md`.

## Selection contract (mirrors HANDOFF.md)

```text
>= 30 : pass to patent-xy-extraction-skill
< 30  : background only
N     : 5–8 default, portfolio-configurable; record chosen N
```

## Output — Patent Priority List

Use `templates/patent_priority_list_template.md`.

This list is the **only** patent set handed to `04_patent_doe_extraction.md` and onward to the extractor.

## Quality Check

- Every selected patent must have a score and a one-line "why included".
- The chosen top-N value is recorded.
- Any patent dropped for score < 30 is listed as background only, not silently omitted.
- If fewer than N patents score >= 30, say so explicitly — do not pad with low-relevance patents.
