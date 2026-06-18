# Composition Contract — patent-xy-extraction-skill ↔ rd-portfolio-rd-intelligence

This file is the **handoff contract** between the orchestrator skill (`rd-portfolio-rd-intelligence`) and this extractor skill (`patent-xy-extraction-skill`).

The orchestrator depends on this skill as a **hard dependency**. Both skills ship as a pair. If this skill is not installed, the orchestrator's patent-extraction step cannot run.

## Skill name the orchestrator must invoke

```text
patent-xy-extraction-skill
```

## Inputs the orchestrator MUST provide

The orchestrator packages and passes these to the extractor. Missing items must still be passed as empty/None and surfaced by the extractor in its "missing information" section.

```text
1. Patent set
   - A ranked list of patents (PDFs, text excerpts, patent numbers, or URLs).
   - Sourced from the orchestrator's 04a_patent_search_and_rank step.
2. Product / platform context
   - Product family, platform, material system, target region.
3. Active CTQs
   - The CTQ matrix row(s) this extraction must serve.
4. Target test methods
   - Internal/standard methods the extracted Ys must be comparable to (e.g. EN 1500, ASTM E2755).
   - Used to populate the test-method comparability matrix.
5. The question being answered
   - A one-sentence statement of what the orchestrator needs to learn,
     e.g. "Which Xs most likely drive 'hand-feel comfort' under repeated use?"
```

## Selection rule (gate before extraction)

The orchestrator scores every candidate patent with `rd-portfolio-rd-intelligence/rubrics/patent_relevance_scoring.md` (0–50 across 10 dimensions).

```text
>= 30 : pass to the extractor for full extraction
< 30  : log as "background only"; do NOT extract (out of scope for this VOC)
```

Default top-N cutoff per VOC: **5–8 patents**. This is a portfolio parameter, not a contract constant — the orchestrator may raise or lower N per portfolio and must record the chosen N in its Patent Priority List.

## Outputs the extractor returns (the typed bundle)

All outputs align with `schemas/patent_xy_extraction_schema.json`. The orchestrator consumes this bundle directly into `workflows/05_xy_synthesis.md`.

```text
1. Per-patent extraction cards      (templates/patent_extraction_card.md)
2. Normalized X dictionary          (cross-patent)
3. Normalized Y dictionary          (cross-patent)
4. Test-method comparability matrix
5. Cross-patent X-Y matrix          (templates/xy_relationship_matrix.md)
6. Contradiction matrix
7. DOE hypothesis library           (workflows/07_doe_hypothesis_generation.md)
8. Relevance-priority list          (mirrors the orchestrator's Patent Priority List)
```

Every X, Y, and X-Y relationship in the bundle MUST carry: source location, evidence level (0–5), confidence, tested range, material system, test method, and confounders — as required by the skill's Quality Rules.

## Separation the extractor MUST preserve

The bundle must keep these five layers distinct in every statement:

```text
patent-disclosed fact
AI-normalized extraction
AI-inferred relationship
R&D hypothesis
DOE recommendation
```

Never present a patent claim as experimental proof. Never give legal freedom-to-operate conclusions.

## What the extractor does NOT do

```text
- run the patent search          (that is 04a in the orchestrator)
- rank/select top-N              (that is 04a in the orchestrator)
- feasibility/IP/regulatory risk screen  (that is 06 in the orchestrator)
- design the final DOE portfolio         (that is 07 in the orchestrator)
```
