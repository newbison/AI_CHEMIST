# Workflow 02 — Section-Aware Patent Extraction

## Purpose

Extract information differently depending on patent section, because each section has different reliability.

## Section Extraction Rules

### Abstract
Use for:
- invention intent
- high-level product type
- claimed benefit

Do not use for:
- quantitative X-Y relationships unless explicitly disclosed

### Background
Use for:
- problem statement
- prior-art limitations
- unmet need

Do not treat background statements as applicant-validated facts.

### Summary
Use for:
- broad solution concept
- proposed technical mechanism

Treat as medium-confidence unless supported by examples.

### Detailed Description
Use for:
- possible materials
- composition ranges
- process ranges
- architecture variations
- optional additives

Be careful: long lists may be generic coverage rather than preferred or tested materials.

### Claims
Use for:
- legal feature boundaries
- mandatory vs optional elements
- claim-overlap signals

Do not use claims as experimental proof.

### Examples and Comparative Examples
Use for:
- strongest X/Y extraction
- actual material combinations
- actual process conditions
- actual test results
- causal contrasts

### Test Methods
Use for:
- Y definition
- units
- comparability
- reproducibility

## Output Template

```markdown
# Section-Aware Extraction

| Extracted Item | Section | Source Location | Evidence Type | Reliability | Notes |
|---|---|---|---|---|---|
```

## Evidence Type Labels

```text
intent
problem statement
claim feature
embodiment range
tested example
comparative example
test method
numeric result
mechanistic assertion
```
