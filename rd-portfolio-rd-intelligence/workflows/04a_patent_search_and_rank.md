# Workflow 04a — Patent Search and Rank

## Purpose

Turn the patent search plan from `workflows/03_evidence_mining.md` into a ranked, de-duplicated, **provenance-backed** patent set ready to hand to `patent-xy-extraction-skill`.

This step owns the **search → verify → score → select top-N** pipeline. It does NOT extract Xs/Ys — extraction is delegated to `patent-xy-extraction-skill` in `04_patent_doe_extraction.md`.

## Inputs

- The Patent Search Plan from `03_evidence_mining.md` (keyword blocks, IPC/CPC, assignees).
- The active CTQs (to anchor relevance scoring).
- The product/platform context.
- Top-N parameter (default **5–8** per VOC; configurable per portfolio — record the chosen value).

## Retrieval & Anti-Fabrication Rules (MANDATORY)

This step is the single point where patents enter the pipeline. Hallucinated patents corrupt every downstream step, so these rules are hard requirements, not guidance.

1. **Real retrieval only.** Step 1 MUST be executed through an actual retrieval channel:
   - the webapp backend (`patent_search.py` — Google Patents / freepatentonline / CN filter), or
   - a live web search / patent-database fetch (Google Patents, Espacenet, CNIPA, 企查查, xjishu, jigao616, etc.), or
   - user-supplied patent PDFs/text with a stated source.
2. **Never generate from memory.** You may NOT invent, recall, or "fill in" patent numbers, assignees, titles, abstracts, or technical content. A plausible-sounding patent number that you cannot point to a fetched source for is a fabrication and is forbidden.
3. **Every patent carries provenance.** Each candidate must record: the source URL (or "user-supplied PDF/text"), the retrieval date, and the kind code (A/B/U etc.). A patent with no source URL is rejected before scoring.
4. **Empty is valid; padding is not.** If a search block returns no retrievable patents, record "0 results" for that block. Do not invent patents to reach top-N. Report a short set honestly rather than a padded long one.
5. **No retrieval capability → stop, do not improvise.** If the runtime has no web access and no patent API and the user supplied no documents, this step MUST report "cannot retrieve — provide patents or enable retrieval" and halt. It must NOT fall back to memory-based generation.

## Steps

1. **Retrieve.** Execute each search block from the search plan (keywords, classification codes, assignee names) via a real retrieval channel per the rules above. Capture, for every hit: publication number (with kind code), assignee, title, source URL, retrieval date.
2. **De-duplicate** by patent family / publication number.
3. **Verify (gate before scoring).** For each candidate, open the source URL and confirm the assignee and title on the page match what you recorded. Mark `Verified = Y` only on a match. If the number is real but the assignee/title/subject you intended does not match the fetched page (e.g. the number belongs to an unrelated patent), mark `Verified = N`, correct the record or drop it, and note the mismatch. A patent whose number exists but whose subject was misread is treated as unverified and may not enter extraction.
4. **Score** every verified candidate using `rubrics/patent_relevance_scoring.md` (0–50 across 10 dimensions).
5. **Sort** descending by total score.
6. **Apply the selection rule:**
   - score >= 30 → candidate for extraction
   - score < 30 → background only (record, do not extract)
7. **Select** the top-N candidates that score >= 30 AND `Verified = Y`.
8. **Emit** the Patent Priority List using `templates/patent_priority_list_template.md`, including the source URL, retrieval date, kind code, and verified status for every row.

## Selection contract (mirrors HANDOFF.md)

```text
>= 30 AND Verified = Y : pass to patent-xy-extraction-skill
< 30  : background only
N     : 5–8 default, portfolio-configurable; record chosen N
```

## Output — Patent Priority List

Use `templates/patent_priority_list_template.md`.

This list is the **only** patent set handed to `04_patent_doe_extraction.md` and onward to the extractor. The extractor's handoff contract (`patent-xy-extraction-skill/HANDOFF.md`) accepts patent numbers, URLs, or documents — but a bare patent number with no source URL is no longer acceptable from this step; always pair it with provenance.

## Quality Check

- Every selected patent has a score, a one-line "why included", a source URL, a retrieval date, a kind code, and `Verified = Y`.
- No selected patent was generated from memory — each traces to a fetched source.
- Any mismatch found in the verify gate is recorded (number kept or dropped, with reason).
- The chosen top-N value is recorded.
- Any patent dropped for score < 30 is listed as background only, not silently omitted.
- If fewer than N patents score >= 30, say so explicitly — do not pad with low-relevance or unverified patents.
- If retrieval was unavailable, the report states this and halts rather than producing an unverified list.
