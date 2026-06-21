# Workflow 05 — Cross-Evidence X-Y Synthesis

## Purpose

Combine patent, internal, benchmark, and literature evidence into a structured X-Y hypothesis map.

## Steps

1. Consolidate all X variables.
2. Normalize naming and units.
3. Consolidate all Y metrics.
4. Group Xs by category:
   - material composition
   - structure / architecture
   - process condition
   - treatment / aging / post-processing
   - use-condition challenge
5. Group Ys by CTQ.
6. Identify recurring relationships.
7. Identify contradictions.
8. Rank confidence.
9. Convert relationships into DOE hypotheses.

## Required Output

```markdown
# Cross-Evidence X-Y Matrix

| X Variable | Category | Related Y | Direction | Evidence Sources | Confidence | Tested Range / Context | Recommended Action |
|---|---|---|---|---|---|---|---|

## Tradeoff Map
| Tradeoff | Evidence | Design Implication |
|---|---|---|

## Contradictions
| Relationship | Evidence A | Evidence B | Possible Explanation | Next Action |
|---|---|---|---|---|

## DOE Hypotheses
| Hypothesis | Basis | Confidence | Suggested Experiment |
|---|---|---|---|
```

## Confidence Scoring

Use `rubrics/learning_confidence_scoring.md`.

## Quality Check

Every relationship must include context:

```text
material system
tested range
test method
source evidence
confidence
```
