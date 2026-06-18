# Workflow 03 — Evidence Mining

## Purpose

Build a structured evidence base before designing experiments.

Evidence should include internal knowledge, patent literature, commercial benchmarks, and public literature where appropriate.

## Evidence Types

```text
1. Internal reports
2. Historical DOE data
3. Lab notebooks
4. Product complaint data
5. Manufacturing deviation data
6. Supplier documentation
7. Commercial benchmark products
8. Patent documents
9. Scientific literature
10. Regulatory or standards documents
```

## Search Strategy Requirements

Generate search strategies for:

- Technical keywords
- Material synonyms
- Product category terms
- Function terms
- Failure-mode terms
- Test-method terms
- IPC/CPC or classification terms, if relevant
- Competitor / assignee names
- Internal repository keywords

## Required Output

```markdown
# Evidence Mining Plan

## Evidence Questions
1. Have we tried this before?
2. What did competitors disclose?
3. What did competitors commercialize?
4. Which variables are repeatedly associated with target performance?
5. Which test methods are comparable?
6. Which constraints may block implementation?

## Internal Knowledge Search Plan
| Query Theme | Keywords | Target Repository | Expected Evidence |
|---|---|---|---|

## Commercial Benchmark Plan
| Product / Company | Claimed Benefit | Source to Review | CTQ Link |
|---|---|---|---|

## Patent Search Plan
| Search Block | Keywords / Classes / Assignees | Purpose |
|---|---|---|

## Inclusion Criteria
- ...

## Exclusion Criteria
- ...
```

## Evidence Reliability Labels

Use these labels:

```text
High — direct data, clear method, relevant material system
Medium — relevant but method or context differs
Low — indirect, incomplete, or inference-heavy
Unknown — insufficient detail
```
