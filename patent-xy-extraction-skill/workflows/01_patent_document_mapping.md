# Workflow 01 — Patent Document Mapping

## Purpose

Patents are not structured consistently. Before extracting Xs and Ys, create a map of the document.

## Steps

1. Identify bibliographic metadata.
2. Identify major sections.
3. Identify tables, examples, comparative examples, and test methods.
4. Identify where claims are located.
5. Identify figures and whether they describe product architecture.
6. Mark extraction priority zones.

## Extraction Priority Zones

```text
Highest priority:
- Examples
- Comparative examples
- Tables with numeric data
- Test methods
- Formulation tables
- Process condition tables

Medium priority:
- Detailed description
- Preferred embodiments
- Figure descriptions

Lower priority:
- Abstract
- Summary
- Broad claims
- Background
```

## Output Template

```markdown
# Patent Document Map

## Metadata
- Patent / publication number:
- Title:
- Assignee:
- Inventors:
- Publication date:
- Priority date:
- Jurisdiction:
- Status, if known:

## Section Map
| Section | Present? | Technical Value | Extraction Priority | Notes |
|---|---|---|---|---|
| Abstract | Yes/No | Intent | Low | |
| Background | Yes/No | Problem context | Low/Medium | |
| Summary | Yes/No | Solution logic | Medium | |
| Detailed description | Yes/No | Materials/ranges | High | |
| Claims | Yes/No | Legal scope | Medium | Not proof |
| Examples | Yes/No | Experimental evidence | Very high | |
| Comparative examples | Yes/No | Causal contrast | Very high | |
| Tables | Yes/No | Numeric evidence | Very high | |
| Test methods | Yes/No | Y comparability | Very high | |

## Extraction Hotspots
- Example numbers:
- Tables:
- Test methods:
- Claim numbers:
- Key paragraphs:

## Missing or Weak Areas
- 
```
