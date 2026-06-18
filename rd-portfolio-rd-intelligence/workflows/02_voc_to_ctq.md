# Workflow 02 — VOC to CTQ Translation

## Purpose

Translate business/customer language into measurable technical attributes and testable hypotheses.

## Steps

1. Preserve the original VOC.
2. Extract implied customer needs.
3. Identify ambiguous terms.
4. Generate clarification questions.
5. Translate each need into CTQs.
6. Identify candidate output Ys.
7. Identify possible input Xs.
8. Identify technical contradictions and tradeoffs.
9. Flag claims that may require regulatory or clinical evidence.

## Required Output

```markdown
# VOC Translation Brief

## Original VOC
> [Original VOC]

## Interpreted Customer Needs
1. ...

## Ambiguous Terms
| Term | Possible Meanings | Clarifying Question |
|---|---|---|

## VOC-to-CTQ Matrix
| Customer Need | CTQ | Candidate Y Metric | Possible Test Method | Initial Target Logic | Risk / Tradeoff |
|---|---|---|---|---|---|

## Candidate Input X Variables
| X Variable | Category | Why It May Matter | Expected Related Y |
|---|---|---|---|

## Technical Tradeoff Map
- ...

## Claim Feasibility Flags
| Potential Claim | Evidence Needed | Risk Level | Review Needed |
|---|---|---|---|
```

## Quality Check

Ensure every CTQ has at least one measurable Y response and one possible test method or a clearly stated test-method gap.
