# Workflow 08 — Post-Experiment Learning

## Purpose

Turn experiment results into structured, reusable organizational knowledge.

## Core Principle

Do not ask only whether the experiment passed or failed.

Ask:

```text
What did we expect?
What happened?
What did we learn?
Where does the learning apply?
How confident are we?
What should we do next?
```

## Required Inputs

- Original experiment plan
- Hypotheses
- Factor matrix
- Output response data
- Test methods
- Acceptance criteria
- Raw data file or table
- Deviations from protocol
- Analyst notes

## Workflow Steps

1. Validate result completeness.
2. Check method consistency.
3. Summarize raw results.
4. Perform or request statistical analysis.
5. Compare actual results to expected X-Y relationships.
6. Classify each hypothesis.
7. Update X-Y matrix.
8. Identify contradictions.
9. Create learning record.
10. Propose knowledge-base update.
11. Recommend next experiment.

## Hypothesis Status Labels

```text
Confirmed
Partially confirmed
Contradicted
Inconclusive
Not tested
Not comparable due to method deviation
```

## Required Output

```markdown
# Post-Experiment Learning Report

## Experiment Summary
- Experiment ID:
- Project:
- Platform:
- Material system:
- Date:
- Test methods:

## Planned Hypotheses
| Hypothesis | Expected X-Y Direction | Evidence Basis | Pre-Test Confidence |
|---|---|---|---|

## Data Completeness Check
| Check | Status | Notes |
|---|---|---|

## Key Results
| X | Y | Observed Direction | Effect Size | Statistical Confidence | Notes |
|---|---|---|---|---|---|

## Hypothesis Evaluation
| Hypothesis | Expected | Observed | Status | Explanation |
|---|---|---|---|---|

## Updated X-Y Matrix
| X | Y | Prior Belief | New Evidence | Updated Confidence | Valid Range / Context |
|---|---|---|---|---|---|

## Contradictions and Explanations
| Contradiction | Possible Explanation | Recommended Follow-up |
|---|---|---|

## Technical Interpretation
[Scientist-readable interpretation]

## Knowledge-Base Update Proposal
| Proposed Learning | Evidence | Confidence | Scope of Applicability | Reviewer Decision |
|---|---|---|---|---|

## Next Experiment Recommendation
- Option A:
- Option B:
- Recommended next step:
```

## Range Awareness Rule

Always write learnings with range and context.

Bad:

```text
Coat weight does not affect MVTR.
```

Good:

```text
Within 25-55 gsm for this adhesive/backing system, coat weight did not show a statistically significant effect on MVTR using the current MVTR method.
```
