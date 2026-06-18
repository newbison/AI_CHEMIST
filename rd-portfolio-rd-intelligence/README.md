# R&D Portfolio Intelligence Skill

This package contains a Claude Skill for replicating an AI-enabled R&D intelligence workflow across product portfolios and material platforms.

## Install

Copy the full folder `rd-portfolio-rd-intelligence/` into your Claude Skills directory, for example:

```bash
~/.claude/skills/rd-portfolio-rd-intelligence/
```

Or upload the zipped skill folder in Claude.ai if your environment supports custom skill upload.

## Validate

```bash
python scripts/validate_skill_structure.py
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
