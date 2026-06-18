# Workflow 04 — Patent DOE / X / Y Extraction (via patent-xy-extraction-skill)

## Purpose

Hand the ranked patent set from `04a_patent_search_and_rank.md` to the dedicated extractor skill `patent-xy-extraction-skill`, then ingest its returned bundle into this orchestrator's downstream synthesis.

This workflow does **not** extract Xs/Ys inline. Extraction is delegated. See `patent-xy-extraction-skill/HANDOFF.md` for the contract.

## Hard Dependency

This step requires `patent-xy-extraction-skill` to be installed alongside this skill. Both ship as a pair. If it is not installed, this step cannot run.

## Step 1 — Package the extraction request

Assemble the inputs the contract requires:

```text
1. Patent set            -> the Patent Priority List from 04a (top-N, score >= 30)
2. Product/platform ctx  -> from 01_project_intake
3. Active CTQs           -> from 02_voc_to_ctq
4. Target test methods   -> internal/standard methods Ys must be comparable to
5. The question          -> one sentence: what must this extraction teach us?
```

## Step 2 — Invoke the extractor

Invoke `patent-xy-extraction-skill` by name, passing the packaged request.

The extractor returns the typed bundle defined in `HANDOFF.md`:

```text
1. Per-patent extraction cards
2. Normalized X dictionary
3. Normalized Y dictionary
4. Test-method comparability matrix
5. Cross-patent X-Y matrix
6. Contradiction matrix
7. DOE hypothesis library
8. Relevance-priority list
```

Every item in the bundle carries source location, evidence level (0–5), confidence, tested range, material system, test method, and confounders.

## Step 3 — Ingest the bundle

Map the returned bundle into this orchestrator's downstream inputs:

```text
normalized X dictionary + normalized Y dictionary   -> feed 05_xy_synthesis
cross-patent X-Y matrix + contradiction matrix      -> feed 05_xy_synthesis
test-method comparability matrix                    -> feed 05_xy_synthesis + 06_feasibility_risk_screen
DOE hypothesis library                              -> feed 07_experiment_portfolio
relevance-priority list                             -> cross-check vs 04a Patent Priority List
```

## Required Output — Portfolio-Side Patent Summary

Produce the orchestrator's portfolio-side view (one row per patent) using `templates/patent_summary_template.md`. This is the summary the rest of the workflow consumes; the deep per-patent cards remain in the extractor's bundle.

## Mandatory Separation

Preserve across the handoff:

```text
patent-disclosed fact
AI-normalized extraction
AI-inferred relationship
R&D recommendation
human-approved decision
```

## Quality Check

- The Patent Priority List from 04a and the relevance-priority list returned by the extractor must agree. Flag any divergence.
- Every ingested X-Y relationship must retain its evidence level and confidence — do not flatten them out.
- Do not present a patent claim as experimental proof. Do not produce legal freedom-to-operate conclusions.
