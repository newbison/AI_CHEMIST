# Workflow 04 — Output Y Extraction

## Purpose

Identify measured or claimed output responses and normalize them into comparable technical metrics.

## Y Categories

Classify Ys into categories:

```text
Performance Y
- adhesion
- peel force
- tack
- shear
- MVTR
- tensile strength
- elongation
- barrier performance
- release force
- wear time

Safety / biological Y
- irritation
- sensitization
- cytotoxicity
- antimicrobial performance
- biocompatibility

Usability Y
- pain on removal
- residue
- conformability
- comfort
- handling
- removability

Reliability / durability Y
- aging stability
- sterilization stability
- edge lift
- leakage
- delamination
- cohesive failure

Manufacturing Y
- coating quality
- defect rate
- drying time
- yield
- processability
```

## Extraction Rules

For each Y, capture:

- original patent term
- normalized metric
- unit
- test method
- substrate
- conditioning
- time point
- directionality
- target / threshold if disclosed
- source example or table
- comparability concerns

## Output Template

```markdown
# Output Y Inventory

| Y ID | Original Patent Term | Normalized Y | Category | Unit | Test Method | Substrate / Condition | Source | Direction | Comparability Concern | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|
```

## Direction Labels

```text
higher_better
lower_better
within_range
binary_pass_fail
qualitative_score
unknown
```

## Quality Rule

If the patent discloses a Y without a test method, mark the metric as weak for cross-patent comparison.
