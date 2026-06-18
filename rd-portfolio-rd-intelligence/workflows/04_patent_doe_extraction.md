# Workflow 04 — Patent DOE / X / Y Extraction

## Purpose

Extract structured technical information from patents so they can inform experiment design.

## Mandatory Separation

Separate:

```text
Patent-disclosed fact
AI-extracted structure
AI-inferred relationship
R&D recommendation
```

## Per-Patent Extraction Steps

For each patent:

1. Identify patent metadata.
2. Summarize the technical problem.
3. Extract product/material structure.
4. Extract claims relevant to the project.
5. Extract experimental examples.
6. Identify input X variables.
7. Identify output Y responses.
8. Extract test methods and units.
9. Infer X-Y relationships only when evidence supports it.
10. Flag missing information and comparability issues.
11. Flag possible IP risk signals for legal review.

## Required Output

```markdown
# Patent Technical Extraction Card

## Patent Metadata
- Patent / publication number:
- Assignee:
- Publication date:
- Jurisdiction:
- Status, if known:

## Technical Purpose
[Summary]

## Product / Material Structure
| Component | Disclosed Detail | Source Location | Confidence |
|---|---|---|---|

## Relevant Claims
| Claim | Relevance | Risk Signal | Notes |
|---|---|---|---|

## Experimental Examples
| Example | X Variables | Y Responses | Test Method | Key Result | Source Location |
|---|---|---|---|---|---|

## Input X Variables
| X | Category | Range / Level | Evidence | Expected Effect |
|---|---|---|---|---|

## Output Y Responses
| Y | Unit | Test Method | Target Direction | Comparability Concern |
|---|---|---|---|---|

## X-Y Relationships
| X | Y | Direction | Evidence Type | Confidence | Limitation |
|---|---|---|---|---|---|

## Fact / Extraction / Inference / Recommendation
| Statement | Type | Source | Confidence |
|---|---|---|---|

## Open Questions
- ...
```

## Quality Check

Do not infer a trend from a single patent example unless clearly marked as low-confidence inference.
