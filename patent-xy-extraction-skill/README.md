# Patent X-Y Extraction Skill

This Claude Skill is a focused extractor for heterogeneous patent documents.

It extracts:

- critical input Xs
- output Ys
- DOE / examples / test methods
- X-Y relationships
- evidence level
- confidence
- contradictions
- DOE-ready hypotheses

## Install

Copy the folder into your Claude skills directory:

```bash
~/.claude/skills/patent-xy-extraction-skill/
```

## Validate

```bash
cd ~/.claude/skills/patent-xy-extraction-skill
python scripts/validate_skill_structure.py
```

## Trigger Prompt

```text
Use patent-xy-extraction-skill to analyze these patents. Extract critical Xs, output Ys, examples, test methods, X-Y relationships, evidence levels, confidence, contradictions, and DOE-ready hypotheses.
```

## Recommended Inputs

- Product/platform context
- VOC or CTQs
- Patent PDFs or text
- Patent numbers or links
- Competitor/assignee context
- Internal target test methods, if available
