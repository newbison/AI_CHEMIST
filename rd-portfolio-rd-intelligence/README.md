# R&D Portfolio Intelligence Skill

This package contains a Claude Skill for replicating an AI-enabled R&D intelligence workflow across product portfolios and material platforms.

## Install

Copy the full folder `rd-portfolio-rd-intelligence/` into your Claude Skills directory, for example:

```bash
~/.claude/skills/rd-portfolio-rd-intelligence/
```

Or upload the zipped skill folder in Claude.ai if your environment supports custom skill upload.

## How These Two Skills Compose

This skill is the **orchestrator**. It depends on `patent-xy-extraction-skill`:

```text
rd-portfolio-rd-intelligence (orchestrator)   ← THIS SKILL
   01 intake → 02 VOC→CTQ → 03 evidence mining
   → 04a search & rank (select top-N patents, score >= 30)
   → 04 hand off ranked set to patent-xy-extraction-skill
        extract: Xs, Ys, examples, test methods, X-Y matrix, contradictions, DOE hypotheses
        return typed bundle (see HANDOFF.md)
   → 05 X-Y synthesis → 06 risk screen → 07 experiment portfolio → 08 learning → 09 replication
```

Install both skills as a pair. The handoff contract is in `patent-xy-extraction-skill/HANDOFF.md`.

## Validate

Run the shared validator from the repo root:

```bash
python validate_skill_structure.py --all
```

## Use

Ask Claude something like:

```text
Use the R&D portfolio intelligence skill to translate this VOC into CTQs, mine patents, extract X-Y logic, propose DOE, and define post-experiment learning.
```

## Customization

For each portfolio, add or customize:

- competitor list
- approved test methods
- platform CTQs
- manufacturing constraints
- supplier constraints
- regulatory claim rules
- internal evidence sources
