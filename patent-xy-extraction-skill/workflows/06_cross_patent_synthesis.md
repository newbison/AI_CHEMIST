# Workflow 06 — Cross-Patent Synthesis

## Purpose

Combine extractions from multiple patents into a reusable technical intelligence map.

## Steps

1. Normalize X names across patents.
2. Normalize Y names across patents.
3. Group patents by material system and product architecture.
4. Separate tested evidence from claimed-only evidence.
5. Compare test methods before comparing values.
6. Identify repeated X-Y relationships.
7. Identify contradictions and possible explanations.
8. Rank critical Xs by frequency, evidence strength, and DOE usefulness.
9. Rank Ys by CTQ relevance and test-method readiness.

## Required Outputs

```markdown
# Cross-Patent X Dictionary

| Normalized X | Synonyms Found | Category | Patents Mentioned | Tested in Examples? | DOE Priority |
|---|---|---|---|---|---|

# Cross-Patent Y Dictionary

| Normalized Y | Synonyms Found | Units | Test Methods Found | Patents Mentioned | Comparability |
|---|---|---|---|---|---|

# Cross-Patent X-Y Matrix

| X | Y | Direction | Supporting Patents | Contradicting Patents | Evidence Strength | Context | DOE Implication |
|---|---|---|---|---|---|---|---|

# Contradiction Matrix

| X-Y Relationship | Patent A Evidence | Patent B Evidence | Possible Explanation | Follow-up Extraction / DOE |
|---|---|---|---|---|
```

## Critical X Prioritization Formula

Use qualitative scoring based on:

```text
frequency across patents
presence in examples
presence in comparative examples
strength of relationship to CTQs
controllability in lab
manufacturing feasibility
IP risk signal
portfolio transferability
```
