# Workflow 03 — Critical X Variable Extraction

## Purpose

Identify controllable input factors that may affect output performance.

## X Categories

Classify every X into one or more categories:

```text
Material composition X
- polymer type
- monomer ratio
- additive type
- filler type
- crosslinker level
- solvent type
- catalyst / initiator
- active ingredient loading

Structure / architecture X
- layer sequence
- film thickness
- adhesive coat weight
- pore size
- pattern coating
- backing type
- liner type
- geometry

Process X
- coating method
- drying temperature
- curing time
- mixing order
- pressure
- line speed
- post-processing method
- aging condition

Use-condition X
- humidity
- temperature
- dwell time
- substrate
- load
- movement / flexing
- fluid exposure
```

## Extraction Rules

For each X, capture:

- original term used in patent
- normalized term
- category
- disclosed value or range
- whether tested or only described
- source section
- source location
- related examples
- likely related Ys
- extraction confidence

## Criticality Assessment

Mark X criticality as:

```text
High — varied in examples or appears in independent claims and linked to performance
Medium — disclosed as preferred range or appears repeatedly
Low — optional additive/list item with no performance linkage
Unknown — insufficient evidence
```

## Output Template

```markdown
# Critical X Inventory

| X ID | Original Patent Term | Normalized X | Category | Value / Range | Tested? | Source | Related Examples | Related Ys | Criticality | Confidence |
|---|---|---|---|---|---|---|---|---|---|---|
```

## Normalization Examples

```text
"basis weight of adhesive", "coating amount", "adhesive mass per unit area" → adhesive coat weight
"water vapor permeability", "moisture vapor transmission rate" → MVTR
"peeling force", "adhesion to steel", "180-degree peel" → peel adhesion, but preserve substrate/method
```
