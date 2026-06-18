# Design Spec — Wire R&D Portfolio Orchestrator to Patent-XY Extraction Skill

**Date:** 2026-06-19
**Status:** Approved
**Author:** brainstorming session, user-approved decisions below

## Problem

The project ships two Claude Agent Skills intended to compose:

- `patent-xy-extraction-skill` — a focused extractor that turns heterogeneous patents into a structured, evidence-backed technical intelligence layer (Xs, Ys, X-Y relationships, DOE hypotheses).
- `rd-portfolio-rd-intelligence` — an orchestrator that turns VOC into CTQs, mines evidence, designs DOE, and captures learning.

The decomposition intent is sound, but the **composition seam is broken**:

1. The orchestrator's `workflows/04_patent_doe_extraction.md` re-implements extraction inline (a weaker copy) instead of calling the dedicated extractor. It never references `patent-xy-extraction-skill`.
2. `templates/patent_extraction_template.md` is **not a template** — it is a verbatim copy of the old workflow prose. The templates folder is both missing a real patent template and holding a duplicate.
3. The "search top related patents" step (the user's most differentiated move, visible in the 6-patent reference `.docx`) exists only in the report output, not in the skill. `workflows/03_evidence_mining.md` produces a *search plan* but never executes it, and nothing tells the agent how to rank/select top-N.
4. The two per-skill `scripts/validate_skill_structure.py` files are near-duplicates that have drifted apart and validate almost nothing.

## Decisions (locked with user)

- **Coupling: HARD DEPENDENCY.** The orchestrator calls `patent-xy-extraction-skill` by name and expects its typed output bundle. Both skills ship as a pair. No degraded inline fallback.
- **Search step: MINIMAL SEARCH-AND-RANK NOW.** Add a lean `04a_patent_search_and_rank.md` so the seam has a real input (search plan → scored list → top-N → extractor). Full search-tooling is a later lane.
- **Top-N default:** 5–8 patents per VOC, configurable per portfolio (documented as a parameter in `04a`, not hardcoded in the contract). Chosen because the existing 6-patent reference output sits in that range.

## Out of scope (later lanes)

- Promoting the hand-sanitizer `.docx` cases to canonical in-skill examples.
- Mixture-DOE + design-selection guidance.
- Citation convention.
- `.docx` report generation.
- Portfolio-config scaffold (`config/` folder + example config).
- Light/full path routing.

## Architecture

```
rd-portfolio-rd-intelligence (orchestrator)
   01 intake → 02 VOC→CTQ → 03 evidence mining
   → 04a search & rank        (NEW: score with relevance rubric, select top-N >= 30)
   → 04 hand off ranked set   (REWRITE: package → invoke → ingest)
        → patent-xy-extraction-skill   (HARD DEPENDENCY)
             returns typed bundle (defined in HANDOFF.md)
   → 05 X-Y synthesis → 06 risk screen → 07 experiment portfolio → 08 learning → 09 replication
```

### The composition contract (`patent-xy-extraction-skill/HANDOFF.md`)

**Inputs the orchestrator MUST provide:**
1. Patent set — the ranked top-N list from `04a`.
2. Product / platform context.
3. Active CTQs.
4. Target test methods (for comparability).
5. The question being answered (one sentence).

**Selection rule (gate before extraction):**
- Score every candidate with `rubrics/patent_relevance_scoring.md` (0–50 across 10 dimensions).
- `>= 30` → pass to the extractor for full extraction.
- `< 30` → log as "background only"; do not extract.
- Default top-N: 5–8, portfolio-configurable; record the chosen N.

**Outputs the extractor returns (typed bundle, aligned to `schemas/patent_xy_extraction_schema.json`):**
1. Per-patent extraction cards.
2. Normalized X dictionary (cross-patent).
3. Normalized Y dictionary (cross-patent).
4. Test-method comparability matrix.
5. Cross-patent X-Y matrix.
6. Contradiction matrix.
7. DOE hypothesis library.
8. Relevance-priority list.

Every X, Y, and X-Y relationship in the bundle carries: source location, evidence level (0–5), confidence, tested range, material system, test method, confounders.

**Separation the extractor MUST preserve (5 layers, distinct in every statement):**
patent-disclosed fact / AI-normalized extraction / AI-inferred relationship / R&D hypothesis / DOE recommendation.

## Files

### Patent skill
| Action | Path |
|---|---|
| Create | `HANDOFF.md` |
| Modify | `SKILL.md` (add `## Used by`) |
| Modify | `README.md` (composition diagram) |
| Delete | `scripts/validate_skill_structure.py` |

### Orchestrator
| Action | Path |
|---|---|
| Modify | `SKILL.md` (add `## Skill Dependencies`; insert `04a`; reword `04`) |
| Create | `workflows/04a_patent_search_and_rank.md` |
| Rewrite | `workflows/04_patent_doe_extraction.md` |
| Replace | `templates/patent_extraction_template.md` → `templates/patent_summary_template.md` |
| Create | `templates/patent_priority_list_template.md` |
| Modify | `README.md` (composition diagram) |
| Delete | `scripts/validate_skill_structure.py` |

### Project root
| Action | Path |
|---|---|
| Create | `validate_skill_structure.py` (shared, stdlib only) |
| Create | `tests/test_validate_skill_structure.py` (`unittest` self-test) |
| Create | `.gitignore` |

## Verification

The shared validator must PASS for both skills and FAIL when:
- a `workflows/*.md` referenced in `SKILL.md` is missing,
- the patent JSON schema is malformed,
- `name` ≠ directory name,
- frontmatter is missing or description > 200 chars,
- `examples/` is empty.

The validator self-test (`tests/test_validate_skill_structure.py`) covers all of the above with temp-dir fixtures.
