# Workflow 07 — Experiment Portfolio and DOE Design

## Purpose

Convert evidence-backed hypotheses into a **2-3 round DOE** (not just one round).
The goal is to systematically narrow from many candidate X variables to the optimal
formulation/process, with each round building on the previous.

## Multi-Round DOE Structure (MANDATORY)

```
Round 1 — Factor Screening
  Input: 5-10 candidate X variables from patent evidence
  Method: Fractional factorial (2^(k-p), Resolution ≥ IV)
  Output: 2-4 dominant levers that actually drive CTQs
  Decision: Which Xs have statistically significant main effects?

Round 2 — Response Surface Optimization
  Input: 2-4 dominant Xs from Round 1
  Method: Central Composite Design (CCD) or Box-Behnken
  Output: Optimal factor levels + desirability score
  Decision: Is the predicted optimum good enough to confirm?

Round 3 — Confirmation Run
  Input: Optimal formulation from Round 2
  Method: 3-5 replicate runs at the predicted optimum
  Output: Verified prediction accuracy + stability data
  Decision: Proceed to scale-up or iterate?
```

## Experiment Portfolio Logic

Rank experiments within each round by:

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
