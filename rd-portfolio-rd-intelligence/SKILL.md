---
name: rd-portfolio-rd-intelligence
description: Translate VOC into CTQs, mine evidence, extract X-Y logic, design DOE, and update R&D learning across product portfolios.
---

# R&D Portfolio Intelligence Skill

Use this skill when the user asks to replicate an R&D intelligence workflow across product platforms, product portfolios, material systems, or business units.

This skill helps Claude act as a structured R&D workflow facilitator. It converts ambiguous business/customer needs into technical specifications, mines patents and internal evidence, extracts DOE / input X / output Y logic, recommends experiments, and captures post-experiment learning.

## Core Mission

Convert:

```text
VOC / market need / customer problem
```

into:

```text
CTQs → evidence map → X-Y hypotheses → DOE plan → lab execution plan → learning record → reusable design rules
```

## When to Use This Skill

Use this skill when the user asks for any of the following:

- Translate Voice of Customer into technical specifications
- Build an R&D discovery workflow
- Analyze patents for DOE, input Xs, output Ys, or X-Y relationships
- Compare product platforms or portfolios
- Create experiment plans from patent or internal evidence
- Build a repeatable R&D intelligence process
- Implement post-experiment learning
- Create a Claude Skill or app workflow for R&D teams
- Standardize R&D learning across business units, product families, or material systems

## When NOT to Use This Skill

Do not use this skill for:

- Final legal freedom-to-operate conclusions
- Medical, regulatory, or clinical claims approval
- Unreviewed product-release decisions
- Direct copying of competitor patent examples into product designs
- Replacing qualified scientist, IP counsel, regulatory, quality, or manufacturing review

## Mandatory Operating Principles

Always separate:

```text
Source fact
vs.
AI extraction
vs.
AI inference
vs.
R&D recommendation
vs.
Human-approved decision
```

Always preserve:

```text
source traceability
confidence level
tested range
test method context
material-system context
portfolio applicability
human review status
```

Never present patent examples as validated commercial truth.

Never provide legal FTO conclusions. Only flag IP risk signals for qualified counsel review.

## Progressive Workflow

Follow this sequence unless the user explicitly asks for a subset:

1. Load `workflows/01_project_intake.md`
2. Load `workflows/02_voc_to_ctq.md`
3. Load `workflows/03_evidence_mining.md`
4. Load `workflows/04_patent_doe_extraction.md`
5. Load `workflows/05_xy_synthesis.md`
6. Load `workflows/06_feasibility_risk_screen.md`
7. Load `workflows/07_experiment_portfolio.md`
8. Load `workflows/08_post_experiment_learning.md`
9. Load `workflows/09_portfolio_replication.md`
10. Use `templates/final_report_template.md` for final output.

If the user provides only partial information, still produce a useful structured output and explicitly list missing inputs.

## Default Output Format

Use Markdown unless the user requests another format.

For full workflow outputs, produce:

1. Executive summary
2. Project / platform intake
3. VOC translation
4. CTQ matrix
5. Evidence strategy
6. Patent / benchmark / internal knowledge extraction
7. X-Y relationship matrix
8. Test method comparability assessment
9. IP / regulatory / manufacturability / supplier / risk screen
10. Experiment portfolio
11. DOE details
12. Lab execution plan
13. Post-experiment learning plan
14. Knowledge-base update proposal
15. Portfolio replication guidance
16. Open questions and human review gates

## Required Review Gates

Insert these review gates into any complete workflow:

```text
Gate 1 — Business confirms VOC interpretation
Gate 2 — R&D confirms CTQs and test methods
Gate 3 — IP/legal reviews patent risk signals
Gate 4 — Regulatory/claims reviews claim feasibility
Gate 5 — Manufacturing and supplier teams review feasibility
Gate 6 — Scientist validates X-Y relationships
Gate 7 — Lab team approves DOE execution plan
Gate 8 — Scientist approves post-experiment learning record
Gate 9 — Portfolio owner approves cross-platform design rules
```

## Portfolio Replication Rule

When replicating across portfolios, always distinguish:

```text
universal R&D logic
portfolio-specific assumptions
platform-specific material constraints
region-specific regulatory constraints
product-family-specific test methods
site-specific manufacturing constraints
```

Do not assume that an X-Y relationship learned in one platform automatically applies to another platform. Require material-system, process, test-method, and use-case compatibility checks.
