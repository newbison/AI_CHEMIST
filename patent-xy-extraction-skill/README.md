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

## How These Two Skills Compose

This skill is a **focused extractor**. It pairs with the orchestrator `rd-portfolio-rd-intelligence`:

```text
rd-portfolio-rd-intelligence (orchestrator)
   01 intake → 02 VOC→CTQ → 03 evidence mining
   → 04a search & rank (select top-N patents, score >= 30)
   → 04 hand off ranked set to patent-xy-extraction-skill   ← THIS SKILL
        extract: Xs, Ys, examples, test methods, X-Y matrix, contradictions, DOE hypotheses
        return typed bundle (see HANDOFF.md)
   → 05 X-Y synthesis → 06 risk screen → 07 experiment portfolio → 08 learning → 09 replication
```

Install both skills as a pair. The handoff contract is in `HANDOFF.md`.

## Validate

Run the shared validator from the repo root:

```bash
python validate_skill_structure.py --all
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
