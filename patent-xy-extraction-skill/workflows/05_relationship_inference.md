# Workflow 05 — X-Y Relationship Inference

## Purpose

Infer relationships between input Xs and output Ys without overclaiming.

## Relationship Evidence Levels

```text
Level 5 — Controlled comparative examples isolate the X and show Y change
Level 4 — Multi-level table shows trend between X and Y
Level 3 — Example data supports relationship but confounding exists
Level 2 — Patent text states effect without supporting data
Level 1 — Claim implies relationship but no data
Level 0 — Speculation; do not include as relationship
```

## Relationship Direction Labels

```text
positive
negative
nonlinear
threshold
optimum_range
interaction
no_clear_effect
contradictory
unknown
```

## Inference Procedure

1. For each example, link X levels to Y results.
2. Identify whether only one X changed or multiple Xs changed.
3. If multiple Xs changed, mark confounding.
4. Compare examples and comparative examples.
5. Use tables to detect trends.
6. Check whether the detailed description supports the trend.
7. Check whether claims cover the same variable.
8. Assign evidence level and confidence.
9. Write relationship only within disclosed context.

## Output Template

```markdown
# X-Y Relationship Matrix

| Relationship ID | X | Y | Direction | Evidence Level | Source Examples / Tables | Tested Range | Material System | Test Method | Confounders | Confidence | Interpretation |
|---|---|---|---|---|---|---|---|---|---|---|---|
```

## Good Relationship Statement

```text
Within Examples 1-5, increasing adhesive coat weight from 25 to 55 gsm is associated with higher 180° peel adhesion on stainless steel under the disclosed dwell condition. Evidence level 4. Confidence medium-high. MVTR effect is unclear because backing film and adhesive chemistry also vary.
```

## Bad Relationship Statement

```text
Coat weight increases adhesion and decreases MVTR.
```

Why bad:

- no range
- no material system
- no test method
- no evidence level
- no confounder statement
