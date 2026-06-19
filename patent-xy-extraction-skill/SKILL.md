---
name: patent-xy-extraction-skill
description: Extract critical Xs, output Ys, DOE structure, and X-Y relationships from heterogeneous patents with evidence traceability.
---

# Patent X-Y Extraction Skill

Use this skill when the user needs to fully utilize patents that are structured differently and extract:

```text
critical input Xs
output Y metrics
DOE / examples / test methods
X-Y relationships
technical tradeoffs
confidence and traceability
```

This skill is optimized for R&D teams analyzing patents across materials, medical devices, chemicals, adhesives, films, coatings, formulations, manufacturing processes, and product constructions.

## Core Mission

Convert messy, differently structured patent documents into a structured, evidence-backed technical intelligence layer:

```text
Patent text → document map → extracted facts → normalized Xs/Ys → evidence table → inferred relationships → X-Y matrix → DOE-ready hypotheses
```

## When to Use This Skill

Use this skill when the user provides or references:

- patent PDFs, patent text, publication numbers, or patent excerpts
- a patent set from competitors or top assignees
- a request to extract input variables, output metrics, examples, test methods, or claims
- a request to build X-Y correlation maps from patents
- a request to compare patents with inconsistent formats
- a request to turn patent examples into DOE hypotheses

## Core Principle: Multi-Pass Extraction

Patent structures vary. Do not rely on a single linear reading.

Always use a multi-pass method:

```text
Pass 1 — Document map
Pass 2 — Problem / invention intent extraction
Pass 3 — Claim scope extraction
Pass 4 — Example / experiment extraction
Pass 5 — X variable extraction
Pass 6 — Y metric extraction
Pass 7 — Test method and unit extraction
Pass 8 — X-Y relationship inference
Pass 9 — Confidence scoring and contradiction check
Pass 10 — DOE-ready synthesis
```

## Mandatory Separation

Always separate:

```text
patent-disclosed fact
AI-normalized extraction
AI-inferred relationship
R&D hypothesis
DOE recommendation
IP/legal risk signal
```

Never treat a patent claim as experimental proof.

Never treat a patent example as commercial validation.

Never give legal freedom-to-operate conclusions. Only flag claim-overlap signals for IP counsel review.

## Patent Section Awareness

When reading a patent, classify evidence by section:

```text
Title / abstract — invention intent, but shallow evidence
Background — problem framing, may contain competitor or prior art context
Summary — broad solution logic, often generic
Brief description / figures — structure and architecture clues
Detailed description — material lists, ranges, embodiments
Claims — legal scope, not necessarily tested examples
Examples — strongest technical evidence for X/Y extraction
Tables — strongest source for X-Y numerical relationships
Test methods — required for Y comparability
Comparative examples — especially valuable for causal contrast
```

## Evidence Hierarchy

Use this hierarchy when extracting X-Y relationships:

```text
Level 5 — Comparative examples with same method and controlled variable
Level 4 — Experimental table with multiple levels and output data
Level 3 — Single example plus disclosed test result
Level 2 — Detailed description states expected effect without data
Level 1 — Claim language only
Level 0 — AI speculation; do not use as relationship evidence
```

## Required Output for Each Patent

For every patent, produce:

1. Patent identity card
2. Document structure map
3. Invention intent
4. Product / material / process architecture
5. Claims-to-technical-feature map
6. Example / experiment extraction table
7. Critical X inventory
8. Output Y inventory
9. Test method inventory
10. X-Y relationship matrix
11. Fact / extraction / inference / hypothesis separation table
12. Missing information and ambiguity list
13. Transferability assessment
14. DOE-ready hypotheses

## Default Final Output

When analyzing multiple patents, produce:

1. Patent-by-patent extraction cards
2. Normalized X dictionary
3. Normalized Y dictionary
4. Test method comparability matrix
5. Cross-patent X-Y matrix
6. Contradiction matrix
7. Critical X prioritization
8. Output Y prioritization
9. DOE hypothesis library
10. Recommended next extraction or experiment actions

## Quality Rules

- Every extracted X must include source location when available.
- Every extracted Y must include unit and test method if available.
- Every X-Y relationship must include evidence level and confidence.
- If unit, test method, or range is missing, mark it explicitly.
- If a relationship is inferred from claims only, label it as low-confidence claim-based inference.
- If examples use different substrates, conditioning, aging, or methods, mark comparability as limited.
- Do not overgeneralize beyond disclosed material system and tested range.

## Used by

This skill is a **focused extractor**. It is invoked by the orchestrator skill `rd-portfolio-rd-intelligence` at its patent-extraction step.

- The composition contract is in `HANDOFF.md`.
- The orchestrator passes a ranked patent set + product/platform context + active CTQs + target test methods + the question to answer.
- This skill returns the typed bundle defined in `HANDOFF.md`.
- Both skills ship as a pair. This skill can also be used standalone on any patent set.

## Useful Supporting Files

Load these as needed:

- `workflows/01_patent_document_mapping.md`
- `workflows/02_section_aware_extraction.md`
- `workflows/03_x_variable_extraction.md`
- `workflows/04_y_output_extraction.md`
- `workflows/05_relationship_inference.md`
- `workflows/06_cross_patent_synthesis.md`
- `workflows/07_doe_hypothesis_generation.md`
- `templates/patent_extraction_card.md`
- `templates/xy_relationship_matrix.md`
- `rubrics/evidence_level_rubric.md`
- `rubrics/extraction_confidence_rubric.md`
- `schemas/patent_xy_extraction_schema.json`
