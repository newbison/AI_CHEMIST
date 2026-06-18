# Workflow 07 — Experiment Portfolio and DOE Design

## Purpose

Convert evidence-backed hypotheses into a prioritized experiment portfolio.

## Experiment Portfolio Logic

Rank experiments by:

```text
learning value
business impact
technical feasibility
cost / speed
IP risk signal
regulatory burden
manufacturing relevance
supplier readiness
portfolio transferability
```

## Required Output

```markdown
# Recommended Experiment Portfolio

## Portfolio Summary
| Rank | Experiment | Learning Goal | Key Xs | Key Ys | Priority Rationale | Review Gates |
|---:|---|---|---|---|---|---|

## Experiment Details

### Experiment [Number] — [Name]

#### Hypothesis
[Hypothesis]

#### Evidence Basis
- Patent evidence:
- Internal evidence:
- Benchmark evidence:
- AI inference:

#### Factors
| Factor | Type | Levels / Range | Rationale |
|---|---|---|---|

#### Responses
| Response | Unit | Test Method | Target / Decision Rule |
|---|---|---|---|

#### Controls
- Baseline:
- Benchmark:
- Negative / positive control, if relevant:

#### Statistical Design
- DOE type:
- Replicates:
- Randomization:
- Blocking:
- Interaction risks:

#### Lab Execution Notes
- Materials:
- Process conditions:
- Conditioning:
- Safety / handling:

#### Decision Rule
[Go / no-go / iterate rule]

#### Risks
- Technical:
- IP:
- Regulatory:
- Manufacturing:
- Supplier:
```

## Quality Check

Every experiment must have:

- hypothesis
- input Xs
- output Ys
- controls
- decision rule
- review gates
