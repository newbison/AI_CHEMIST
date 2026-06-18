# Wire R&D Portfolio Orchestrator to Patent-XY Extraction Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `rd-portfolio-rd-intelligence` (orchestrator) call `patent-xy-extraction-skill` (extractor) as a hard dependency through a documented contract, add a minimal search→rank step so the seam has a real input, fix the misplaced template, and unify the validator.

**Architecture:** The two skills already exist and are well-formed individually. The seam is missing. We add one contract file (`HANDOFF.md`) in the patent skill, one new workflow (`04a_patent_search_and_rank.md`) + two real templates in the orchestrator, rewrite the orchestrator's `04` workflow from "extract inline" to "package → invoke → ingest", declare the dependency in both `SKILL.md` files, and replace the two drifted validators with one shared validator that has a real self-test. No degraded fallback — both skills ship as a pair.

**Tech Stack:** Markdown skill content (Claude Agent Skills), Python 3 (stdlib only — `unittest`, `json`, `re`, `pathlib`), Git.

**Scope decisions locked with user:**
- **Hard dependency**: orchestrator invokes `patent-xy-extraction-skill` by name, expects its typed bundle, ships as a pair. No inline fallback.
- **Minimal search→rank now**: add lean `04a` so the seam has a real input. Full search-tooling is a later lane.
- **Out of scope this round**: hand-sanitizer example promotion, mixture-DOE/citations, `.docx` generation, portfolio-config scaffold.

**Top-N default:** `~5–8` patents per VOC, configurable per portfolio (documented as a parameter in `04a`, not hardcoded in the contract). Chosen because the existing 6-patent reference output sits in that range.

---

## File Structure

Map of every file created or modified. Decomposition locked here.

### Patent skill (`patent-xy-extraction-skill/`)
| Action | Path | Responsibility |
|---|---|---|
| Create | `HANDOFF.md` | The composition contract: inputs/outputs the orchestrator must obey. |
| Modify | `SKILL.md` | Add `## Used by` section pointing to orchestrator + `HANDOFF.md`. |
| Modify | `README.md` | Add "how these two compose" diagram + install-as-a-pair note. |
| Delete | `scripts/validate_skill_structure.py` | Replaced by shared validator. |

### Orchestrator (`rd-portfolio-rd-intelligence/`)
| Action | Path | Responsibility |
|---|---|---|
| Modify | `SKILL.md` | Add `## Skill Dependencies` (hard dep); insert `04a` into workflow list; reword `04`. |
| Create | `workflows/04a_patent_search_and_rank.md` | Run search plan, score with relevance rubric, select top-N, emit Patent Priority List. |
| Rewrite | `workflows/04_patent_doe_extraction.md` | From inline extraction → package request, invoke extractor, ingest bundle. |
| Replace | `templates/patent_extraction_template.md` | Currently workflow prose (misplaced). → real portfolio-side `patent_summary_template.md`. |
| Create | `templates/patent_priority_list_template.md` | Thin one-table template for `04a` output. |
| Rename/Replace | `templates/patent_extraction_template.md` → `patent_summary_template.md` | Same file, corrected name + corrected content. |
| Modify | `README.md` | Add composition diagram + install-as-a-pair note. |
| Delete | `scripts/validate_skill_structure.py` | Replaced by shared validator. |

### Project root
| Action | Path | Responsibility |
|---|---|---|
| Create | `validate_skill_structure.py` | One shared validator run from each skill root. Stdlib only. |
| Create | `tests/test_validate_skill_structure.py` | `unittest` self-test for the validator (TDD). |
| Create | `docs/superpowers/specs/2026-06-19-wire-skills-together-design.md` | The approved design (this plan's spec). |
| Create | `.gitignore` | Ignore OS/editor noise; commit skill files. |
| Delete | `_tmp_read_docx.py` | Already removed; listed for completeness. |

---

## Task 0: Initialize Git repository and capture the design spec

**Files:**
- Create: `D:\coding_is_fun\AI_CHEMIST_SKILL_2\.gitignore`
- Create: `D:\coding_is_fun\AI_CHEMIST_SKILL_2\docs\superpowers\specs\2026-06-19-wire-skills-together-design.md`

- [ ] **Step 1: Initialize git repo**

Run:
```bash
cd /d "D:\coding_is_fun\AI_CHEMIST_SKILL_2"
git init
git config user.name "AI Chemist Skill"
git config user.email "skill@local"
```
Expected: `Initialized empty Git repository` message.

- [ ] **Step 2: Write `.gitignore`**

Create `D:\coding_is_fun\AI_CHEMIST_SKILL_2\.gitignore`:
```gitignore
# OS / editor
Thumbs.db
desktop.ini
.DS_Store
*.swp
.vscode/
.idea/

# Python
__pycache__/
*.pyc
.pytest_cache/

# Temp
_tmp_*
```

- [ ] **Step 3: Write the design spec**

Create `docs/superpowers/specs/2026-06-19-wire-skills-together-design.md` with the full approved design — copy the "Design spec" content agreed in the conversation (decisions: hard dependency, minimal search→rank now, top-N 5–8 configurable). This is the source of truth for the plan.

- [ ] **Step 4: Commit the baseline**

```bash
git add -A
git commit -m "chore: init repo + capture wire-skills-together design spec"
```
Expected: commit created with all existing skill files + spec + gitignore.

---

## Task 1: Write the validator self-test (RED)

This is the only piece of real executable code, so it gets genuine TDD. The validator's contract is fixed before we write the validator.

**Files:**
- Create: `D:\coding_is_fun\AI_CHEMIST_SKILL_2\tests\test_validate_skill_structure.py`

- [ ] **Step 1: Write the failing test**

Create `tests\test_validate_skill_structure.py`:
```python
"""Self-test for the shared skill-structure validator.

Builds throwaway well-formed and malformed skill trees in temp dirs,
runs the validator on each, and asserts pass/fail behavior. Stdlib only.
"""
import sys
import textwrap
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from validate_skill_structure import validate_skill, ValidationError  # noqa: E402


VALID_FRONTMATTER = textwrap.dedent("""\
    ---
    name: demo-skill
    description: A demo skill for testing.
    ---
    # Demo Skill

    body
""")


def _write_skill(root: Path, name: str, *, frontmatter: str = VALID_FRONTMATTER,
                 workflow_refs=(), examples_present=True, schema_present=False,
                 schema_valid=True):
    root.mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text(frontmatter, encoding="utf-8")
    wf = root / "workflows"
    wf.mkdir(exist_ok=True)
    for ref in workflow_refs:
        (wf / ref).write_text("# " + ref + "\n", encoding="utf-8")
    tpl = root / "templates"; tpl.mkdir(exist_ok=True); (tpl / "x.md").write_text("t\n", encoding="utf-8")
    rub = root / "rubrics"; rub.mkdir(exist_ok=True); (rub / "y.md").write_text("t\n", encoding="utf-8")
    ref2 = root / "references"; ref2.mkdir(exist_ok=True); (ref2 / "z.md").write_text("t\n", encoding="utf-8")
    ex = root / "examples"
    if examples_present:
        ex.mkdir(exist_ok=True); (ex / "e.md").write_text("e\n", encoding="utf-8")
    else:
        ex.mkdir(exist_ok=True)
    if schema_present:
        sc = root / "schemas"; sc.mkdir(exist_ok=True)
        body = "{}" if schema_valid else "{not json"
        (sc / "schema.json").write_text(body, encoding="utf-8")


class ValidatorTests(unittest.TestCase):
    def test_valid_skill_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "demo-skill"
            _write_skill(root, "demo-skill")
            validate_skill(root)  # must not raise

    def test_name_must_match_dir_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "demo-skill"
            bad = VALID_FRONTMATTER.replace("name: demo-skill", "name: wrong-name")
            _write_skill(root, "demo-skill", frontmatter=bad)
            with self.assertRaises(ValidationError):
                validate_skill(root)

    def test_name_regex_enforced(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "Bad_Name"
            bad = VALID_FRONTMATTER.replace("name: demo-skill", "name: Bad_Name")
            _write_skill(root, "Bad_Name", frontmatter=bad)
            with self.assertRaises(ValidationError):
                validate_skill(root)

    def test_missing_frontmatter_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "demo-skill"
            _write_skill(root, "demo-skill", frontmatter="# no frontmatter\n\nbody\n")
            with self.assertRaises(ValidationError):
                validate_skill(root)

    def test_description_too_long_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "demo-skill"
            long_desc = "description: " + ("x" * 201)
            bad = VALID_FRONTMATTER.replace("description: A demo skill for testing.", long_desc)
            _write_skill(root, "demo-skill", frontmatter=bad)
            with self.assertRaises(ValidationError):
                validate_skill(root)

    def test_empty_examples_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "demo-skill"
            _write_skill(root, "demo-skill", examples_present=False)
            with self.assertRaises(ValidationError):
                validate_skill(root)

    def test_missing_referenced_workflow_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "demo-skill"
            fm = VALID_FRONTMATTER + "\n- `workflows/01_missing.md`\n"
            _write_skill(root, "demo-skill", frontmatter=fm, workflow_refs=["02_present.md"])
            with self.assertRaises(ValidationError):
                validate_skill(root)

    def test_present_referenced_workflow_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "demo-skill"
            fm = VALID_FRONTMATTER + "\n- `workflows/01_present.md`\n"
            _write_skill(root, "demo-skill", frontmatter=fm, workflow_refs=["01_present.md"])
            validate_skill(root)

    def test_malformed_schema_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "demo-skill"
            _write_skill(root, "demo-skill", schema_present=True, schema_valid=False)
            with self.assertRaises(ValidationError):
                validate_skill(root)

    def test_valid_schema_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "demo-skill"
            _write_skill(root, "demo-skill", schema_present=True, schema_valid=True)
            validate_skill(root)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test to verify it fails**

Run:
```bash
cd /d "D:\coding_is_fun\AI_CHEMIST_SKILL_2"
python -m unittest tests.test_validate_skill_structure -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'validate_skill_structure'`. This is the desired RED state.

- [ ] **Step 3: Commit the failing test**

```bash
git add tests/test_validate_skill_structure.py
git commit -m "test: add validator self-test (red)"
```

---

## Task 2: Implement the shared validator (GREEN)

**Files:**
- Create: `D:\coding_is_fun\AI_CHEMIST_SKILL_2\validate_skill_structure.py`

- [ ] **Step 1: Write the validator implementation**

Create `D:\coding_is_fun\AI_CHEMIST_SKILL_2\validate_skill_structure.py`:
```python
"""Shared skill-structure validator.

Run from a skill root:
    python ../validate_skill_structure.py           # validates the current skill
    python ../validate_skill_structure.py --all      # validates both skills in the pair

Checks, per skill root:
  - YAML frontmatter present and starts with '---'
  - name field present, matches the directory name, matches [a-z0-9-]{1,64}
  - description field present and <= 200 chars
  - required folders present: workflows, templates, rubrics, references, examples
  - examples/ is non-empty
  - every `workflows/<file>` referenced in SKILL.md exists on disk
  - (schemas/ present only expected for patent skill) if schemas/*.json exists, it parses

Stdlib only.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
WORKFLOW_REF_RE = re.compile(r"`workflows/([A-Za-z0-9_\-]+\.md)`")
MAX_DESC_LEN = 200

REQUIRED_FOLDERS = ("workflows", "templates", "rubrics", "references", "examples")


class ValidationError(Exception):
    """Raised when a skill fails structural validation."""


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        raise ValidationError("SKILL.md must start with YAML frontmatter ('---').")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValidationError("SKILL.md frontmatter is not closed with a second '---'.")
    block = text[3:end]
    out = {}
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return out


def validate_skill(root: Path) -> None:
    """Validate a single skill root. Raises ValidationError on failure."""
    if not root.is_dir():
        raise ValidationError(f"Not a directory: {root}")

    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        raise ValidationError(f"Missing SKILL.md: {skill_md}")
    text = skill_md.read_text(encoding="utf-8")

    fm = _parse_frontmatter(text)

    if "name" not in fm or not fm["name"]:
        raise ValidationError("SKILL.md frontmatter must include a 'name' field.")
    name = fm["name"]
    if name != root.name:
        raise ValidationError(f"name ({name!r}) must match directory name ({root.name!r}).")
    if not NAME_RE.fullmatch(name):
        raise ValidationError(
            f"name must be lowercase letters, numbers, hyphens only, max 64 chars: {name!r}"
        )

    if "description" not in fm or not fm["description"]:
        raise ValidationError("SKILL.md frontmatter must include a 'description' field.")
    if len(fm["description"]) > MAX_DESC_LEN:
        raise ValidationError(
            f"description must be <= {MAX_DESC_LEN} chars (is {len(fm['description'])})."
        )

    for folder in REQUIRED_FOLDERS:
        if not (root / folder).is_dir():
            raise ValidationError(f"Missing required folder: {folder}/")

    examples = root / "examples"
    if not any(examples.iterdir()):
        raise ValidationError("examples/ folder is empty.")

    referenced = set(WORKFLOW_REF_RE.findall(text))
    for ref in sorted(referenced):
        if not (root / "workflows" / ref).is_file():
            raise ValidationError(f"SKILL.md references workflows/{ref} but it does not exist.")

    schemas_dir = root / "schemas"
    if schemas_dir.is_dir():
        for jf in schemas_dir.glob("*.json"):
            try:
                json.loads(jf.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                raise ValidationError(f"Malformed JSON schema {jf.name}: {e}")


def _discover_skill_roots(start: Path) -> list:
    """Find skill roots to validate from a starting directory."""
    # Heuristic: a directory containing SKILL.md at the level below `start`.
    roots = []
    for child in sorted(start.iterdir()):
        if child.is_dir() and (child / "SKILL.md").is_file():
            roots.append(child)
    return roots


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    here = Path(__file__).resolve().parent

    if "--all" in argv:
        roots = _discover_skill_roots(here)
        if not roots:
            print("No skill roots found next to the validator.", file=sys.stderr)
            return 2
    else:
        # Default: validate the skill whose folder we are run from.
        cwd = Path.cwd()
        if (cwd / "SKILL.md").is_file():
            roots = [cwd]
        else:
            # Fallback: assume validator is one level above a skill root and was invoked from there.
            roots = _discover_skill_roots(cwd)
            if not roots:
                print(
                    "Usage: run from inside a skill folder, or use --all from the repo root.",
                    file=sys.stderr,
                )
                return 2

    failures = []
    for root in roots:
        try:
            validate_skill(root)
            print(f"PASS: {root.name}")
        except ValidationError as e:
            failures.append((root.name, str(e)))
            print(f"FAIL: {root.name} — {e}", file=sys.stderr)

    if failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run the self-test to verify it passes (GREEN)**

Run:
```bash
cd /d "D:\coding_is_fun\AI_CHEMIST_SKILL_2"
python -m unittest tests.test_validate_skill_structure -v
```
Expected: PASS — 10 tests, 0 failures.

- [ ] **Step 3: Run the validator against the current (pre-rewrite) skills**

```bash
python validate_skill_structure.py --all
```
Expected at this stage: **PASS for both** (they are well-formed today). Note: `04a` does not yet exist, and `SKILL.md` does not yet reference it, so the workflow-reference check passes. We expect this to flip later when we add the `04a` reference before creating the file — the task order below avoids that gap.

- [ ] **Step 4: Commit**

```bash
git add validate_skill_structure.py
git commit -m "feat: add shared skill-structure validator with self-test"
```

---

## Task 3: Write the composition contract — `HANDOFF.md`

This is the keystone file. Everything else references it.

**Files:**
- Create: `D:\coding_is_fun\AI_CHEMIST_SKILL_2\patent-xy-extraction-skill\HANDOFF.md`

- [ ] **Step 1: Write `HANDOFF.md`**

Create `patent-xy-extraction-skill\HANDOFF.md`:
````markdown
# Composition Contract — patent-xy-extraction-skill ↔ rd-portfolio-rd-intelligence

This file is the **handoff contract** between the orchestrator skill (`rd-portfolio-rd-intelligence`) and this extractor skill (`patent-xy-extraction-skill`).

The orchestrator depends on this skill as a **hard dependency**. Both skills ship as a pair. If this skill is not installed, the orchestrator's patent-extraction step cannot run.

## Skill name the orchestrator must invoke

```text
patent-xy-extraction-skill
```

## Inputs the orchestrator MUST provide

The orchestrator packages and passes these to the extractor. Missing items must still be passed as empty/None and surfaced by the extractor in its "missing information" section.

```text
1. Patent set
   - A ranked list of patents (PDFs, text excerpts, patent numbers, or URLs).
   - Sourced from the orchestrator's 04a_patent_search_and_rank step.
2. Product / platform context
   - Product family, platform, material system, target region.
3. Active CTQs
   - The CTQ matrix row(s) this extraction must serve.
4. Target test methods
   - Internal/standard methods the extracted Ys must be comparable to (e.g. EN 1500, ASTM E2755).
   - Used to populate the test-method comparability matrix.
5. The question being answered
   - A one-sentence statement of what the orchestrator needs to learn,
     e.g. "Which Xs most likely drive 'hand-feel comfort' under repeated use?"
```

## Selection rule (gate before extraction)

The orchestrator scores every candidate patent with `rd-portfolio-rd-intelligence/rubrics/patent_relevance_scoring.md` (0–50 across 10 dimensions).

```text
>= 30 : pass to the extractor for full extraction
< 30  : log as "background only"; do NOT extract (out of scope for this VOC)
```

Default top-N cutoff per VOC: **5–8 patents**. This is a portfolio parameter, not a contract constant — the orchestrator may raise or lower N per portfolio and must record the chosen N in its Patent Priority List.

## Outputs the extractor returns (the typed bundle)

All outputs align with `schemas/patent_xy_extraction_schema.json`. The orchestrator consumes this bundle directly into `workflows/05_xy_synthesis.md`.

```text
1. Per-patent extraction cards      (templates/patent_extraction_card.md)
2. Normalized X dictionary          (cross-patent)
3. Normalized Y dictionary          (cross-patent)
4. Test-method comparability matrix
5. Cross-patent X-Y matrix          (templates/xy_relationship_matrix.md)
6. Contradiction matrix
7. DOE hypothesis library           (workflows/07_doe_hypothesis_generation.md)
8. Relevance-priority list          (mirrors the orchestrator's Patent Priority List)
```

Every X, Y, and X-Y relationship in the bundle MUST carry: source location, evidence level (0–5), confidence, tested range, material system, test method, and confounders — as required by the skill's Quality Rules.

## Separation the extractor MUST preserve

The bundle must keep these five layers distinct in every statement:

```text
patent-disclosed fact
AI-normalized extraction
AI-inferred relationship
R&D hypothesis
DOE recommendation
```

Never present a patent claim as experimental proof. Never give legal freedom-to-operate conclusions.

## What the extractor does NOT do

```text
- run the patent search          (that is 04a in the orchestrator)
- rank/select top-N              (that is 04a in the orchestrator)
- feasibility/IP/regulatory risk screen  (that is 06 in the orchestrator)
- design the final DOE portfolio         (that is 07 in the orchestrator)
```
````

- [ ] **Step 2: Verify the file parses as expected (sanity)**

```bash
cd /d "D:\coding_is_fun\AI_CHEMIST_SKILL_2\patent-xy-extraction-skill"
python ../validate_skill_structure.py
```
Expected: `PASS: patent-xy-extraction-skill` (HANDOFF.md is not checked by the validator, but confirms nothing else broke).

- [ ] **Step 3: Commit**

```bash
git add patent-xy-extraction-skill/HANDOFF.md
git commit -m "feat: add composition contract HANDOFF.md for the skill seam"
```

---

## Task 4: Add the minimal search→rank workflow (`04a`) + its template

**Files:**
- Create: `D:\coding_is_fun\AI_CHEMIST_SKILL_2\rd-portfolio-rd-intelligence\workflows\04a_patent_search_and_rank.md`
- Create: `D:\coding_is_fun\AI_CHEMIST_SKILL_2\rd-portfolio-rd-intelligence\templates\patent_priority_list_template.md`

- [ ] **Step 1: Write `04a_patent_search_and_rank.md`**

Create `rd-portfolio-rd-intelligence\workflows\04a_patent_search_and_rank.md`:
```markdown
# Workflow 04a — Patent Search and Rank

## Purpose

Turn the patent search plan from `workflows/03_evidence_mining.md` into a ranked, de-duplicated patent set ready to hand to `patent-xy-extraction-skill`.

This step owns the **search → score → select top-N** pipeline. It does NOT extract Xs/Ys — extraction is delegated to `patent-xy-extraction-skill` in `04_patent_doe_extraction.md`.

## Inputs

- The Patent Search Plan from `03_evidence_mining.md` (keyword blocks, IPC/CPC, assignees).
- The active CTQs (to anchor relevance scoring).
- The product/platform context.
- Top-N parameter (default **5–8** per VOC; configurable per portfolio — record the chosen value).

## Steps

1. Execute each search block from the search plan (keywords, classification codes, assignee names).
2. De-duplicate by patent family / publication number.
3. Score every candidate using `rubrics/patent_relevance_scoring.md` (0–50 across 10 dimensions).
4. Sort descending by total score.
5. Apply the selection rule:
   - score >= 30 → candidate for extraction
   - score < 30 → background only (record, do not extract)
6. Select the top-N candidates that score >= 30.
7. Emit the Patent Priority List using `templates/patent_priority_list_template.md`.

## Selection contract (mirrors HANDOFF.md)

```text
>= 30 : pass to patent-xy-extraction-skill
< 30  : background only
N     : 5–8 default, portfolio-configurable; record chosen N
```

## Output — Patent Priority List

Use `templates/patent_priority_list_template.md`.

This list is the **only** patent set handed to `04_patent_doe_extraction.md` and onward to the extractor.

## Quality Check

- Every selected patent must have a score and a one-line "why included".
- The chosen top-N value is recorded.
- Any patent dropped for score < 30 is listed as background only, not silently omitted.
- If fewer than N patents score >= 30, say so explicitly — do not pad with low-relevance patents.
```

- [ ] **Step 2: Write `patent_priority_list_template.md`**

Create `rd-portfolio-rd-intelligence\templates\patent_priority_list_template.md`:
```markdown
# Patent Priority List

> Output of workflow 04a_patent_search_and_rank. This is the ranked set handed to patent-xy-extraction-skill.

## Parameters
- Top-N applied: [value]
- Relevance cutoff: score >= 30
- Total candidates scored: [value]
- Candidates >= 30: [value]
- Selected for extraction: [value]

## Selected for Extraction (top-N, score >= 30)
| Rank | Patent / Publication | Assignee | Title (short) | Score | Why Included | Extraction Priority |
|---:|---|---|---|---:|---|---|

## Background Only (score < 30)
| Patent / Publication | Assignee | Score | Reason Not Extracted |
|---|---|---:|---|

## Notes
- 
```

- [ ] **Step 3: Commit**

```bash
git add rd-portfolio-rd-intelligence/workflows/04a_patent_search_and_rank.md rd-portfolio-rd-intelligence/templates/patent_priority_list_template.md
git commit -m "feat: add 04a patent search-and-rank workflow + priority list template"
```

---

## Task 5: Rewrite orchestrator `04` from "extract inline" to "package → invoke → ingest"

**Files:**
- Modify: `D:\coding_is_fun\AI_CHEMIST_SKILL_2\rd-portfolio-rd-intelligence\workflows\04_patent_doe_extraction.md` (full rewrite)

- [ ] **Step 1: Rewrite the file**

Replace the entire contents of `rd-portfolio-rd-intelligence\workflows\04_patent_doe_extraction.md` with:
```markdown
# Workflow 04 — Patent DOE / X / Y Extraction (via patent-xy-extraction-skill)

## Purpose

Hand the ranked patent set from `04a_patent_search_and_rank.md` to the dedicated extractor skill `patent-xy-extraction-skill`, then ingest its returned bundle into this orchestrator's downstream synthesis.

This workflow does **not** extract Xs/Ys inline. Extraction is delegated. See `patent-xy-extraction-skill/HANDOFF.md` for the contract.

## Hard Dependency

This step requires `patent-xy-extraction-skill` to be installed alongside this skill. Both ship as a pair. If it is not installed, this step cannot run.

## Step 1 — Package the extraction request

Assemble the inputs the contract requires:

```text
1. Patent set            -> the Patent Priority List from 04a (top-N, score >= 30)
2. Product/platform ctx  -> from 01_project_intake
3. Active CTQs           -> from 02_voc_to_ctq
4. Target test methods   -> internal/standard methods Ys must be comparable to
5. The question          -> one sentence: what must this extraction teach us?
```

## Step 2 — Invoke the extractor

Invoke `patent-xy-extraction-skill` by name, passing the packaged request.

The extractor returns the typed bundle defined in `HANDOFF.md`:

```text
1. Per-patent extraction cards
2. Normalized X dictionary
3. Normalized Y dictionary
4. Test-method comparability matrix
5. Cross-patent X-Y matrix
6. Contradiction matrix
7. DOE hypothesis library
8. Relevance-priority list
```

Every item in the bundle carries source location, evidence level (0–5), confidence, tested range, material system, test method, and confounders.

## Step 3 — Ingest the bundle

Map the returned bundle into this orchestrator's downstream inputs:

```text
normalized X dictionary + normalized Y dictionary   -> feed 05_xy_synthesis
cross-patent X-Y matrix + contradiction matrix      -> feed 05_xy_synthesis
test-method comparability matrix                    -> feed 05_xy_synthesis + 06_feasibility_risk_screen
DOE hypothesis library                              -> feed 07_experiment_portfolio
relevance-priority list                             -> cross-check vs 04a Patent Priority List
```

## Required Output — Portfolio-Side Patent Summary

Produce the orchestrator's portfolio-side view (one row per patent) using `templates/patent_summary_template.md`. This is the summary the rest of the workflow consumes; the deep per-patent cards remain in the extractor's bundle.

## Mandatory Separation

Preserve across the handoff:

```text
patent-disclosed fact
AI-normalized extraction
AI-inferred relationship
R&D recommendation
human-approved decision
```

## Quality Check

- The Patent Priority List from 04a and the relevance-priority list returned by the extractor must agree. Flag any divergence.
- Every ingested X-Y relationship must retain its evidence level and confidence — do not flatten them out.
- Do not present a patent claim as experimental proof. Do not produce legal freedom-to-operate conclusions.
```

- [ ] **Step 2: Commit**

```bash
git add rd-portfolio-rd-intelligence/workflows/04_patent_doe_extraction.md
git commit -m "refactor: orchestrator 04 delegates extraction to patent-xy-extraction-skill"
```

---

## Task 6: Replace the misplaced template

`templates/patent_extraction_template.md` currently contains workflow prose (a copy of old `04`). Replace it with a real portfolio-side summary template under the correct name.

**Files:**
- Delete: `rd-portfolio-rd-intelligence\templates\patent_extraction_template.md`
- Create: `rd-portfolio-rd-intelligence\templates\patent_summary_template.md`

- [ ] **Step 1: Create the real template**

Create `rd-portfolio-rd-intelligence\templates\patent_summary_template.md`:
```markdown
# Patent Summary (Portfolio-Side View)

> One row per patent. This is the orchestrator's summary view derived from the extractor's bundle. Deep per-patent cards live in patent-xy-extraction-skill's bundle.

| Patent / Publication | Assignee | Key Xs | Key Ys | Key X-Y Relationships (direction, evidence level) | DOE Usefulness | Relevance Score | Main Limitation | Source |
|---|---|---|---|---|---|---:|---|---|

## Notes on comparability
- 

## Contradictions across patents
| X-Y Relationship | Patent A | Patent B | Possible Explanation | Follow-up |
|---|---|---|---|---|
```

- [ ] **Step 2: Delete the misplaced file**

```bash
git rm rd-portfolio-rd-intelligence/templates/patent_extraction_template.md
```
Expected: file staged for deletion.

- [ ] **Step 3: Commit**

```bash
git add rd-portfolio-rd-intelligence/templates/patent_summary_template.md
git commit -m "fix: replace misplaced patent_extraction_template with real patent_summary_template"
```

---

## Task 7: Declare the dependency in the orchestrator `SKILL.md`

**Files:**
- Modify: `D:\coding_is_fun\AI_CHEMIST_SKILL_2\rd-portfolio-rd-intelligence\SKILL.md`

- [ ] **Step 1: Add the `## Skill Dependencies` section**

In `rd-portfolio-rd-intelligence\SKILL.md`, insert this section immediately after the `## Core Mission` block (before `## When to Use This Skill`):

```markdown
## Skill Dependencies

This skill is an **orchestrator**. It depends on `patent-xy-extraction-skill` as a **hard dependency** for patent X-Y extraction.

- Install both skills together as a pair.
- The handoff contract is defined in `patent-xy-extraction-skill/HANDOFF.md`.
- Step 04 (`workflows/04_patent_doe_extraction.md`) invokes `patent-xy-extraction-skill` by name and ingests its typed output bundle.
- If `patent-xy-extraction-skill` is not installed, the patent-extraction step cannot run.
```

- [ ] **Step 2: Update the Progressive Workflow list**

In the same `SKILL.md`, replace the current workflow list block (the `1. Load ... 10. Use templates/final_report_template.md` block under `## Progressive Workflow`) with:

```markdown
Follow this sequence unless the user explicitly asks for a subset:

1. Load `workflows/01_project_intake.md`
2. Load `workflows/02_voc_to_ctq.md`
3. Load `workflows/03_evidence_mining.md`
4. Load `workflows/04a_patent_search_and_rank.md` — search, score, and select top-N patents
5. Load `workflows/04_patent_doe_extraction.md` — hand off the ranked set to `patent-xy-extraction-skill`; ingest its bundle
6. Load `workflows/05_xy_synthesis.md`
7. Load `workflows/06_feasibility_risk_screen.md`
8. Load `workflows/07_experiment_portfolio.md`
9. Load `workflows/08_post_experiment_learning.md`
10. Load `workflows/09_portfolio_replication.md`
11. Use `templates/final_report_template.md` for final output.
```

- [ ] **Step 3: Run the validator to confirm SKILL.md stays well-formed**

```bash
cd /d "D:\coding_is_fun\AI_CHEMIST_SKILL_2\rd-portfolio-rd-intelligence"
python ../validate_skill_structure.py
```
Expected: `PASS: rd-portfolio-rd-intelligence`. (The validator checks that every `workflows/*.md` referenced in SKILL.md exists. `04a_patent_search_and_rank.md` and `04_patent_doe_extraction.md` both exist at this point, so this passes. This ordering is deliberate.)

- [ ] **Step 4: Commit**

```bash
git add rd-portfolio-rd-intelligence/SKILL.md
git commit -m "feat: declare hard dependency on patent-xy-extraction-skill in orchestrator SKILL.md"
```

---

## Task 8: Add `## Used by` to the patent skill `SKILL.md`

**Files:**
- Modify: `D:\coding_is_fun\AI_CHEMIST_SKILL_2\patent-xy-extraction-skill\SKILL.md`

- [ ] **Step 1: Insert the `## Used by` section**

In `patent-xy-extraction-skill\SKILL.md`, insert immediately before `## Useful Supporting Files`:

```markdown
## Used by

This skill is a **focused extractor**. It is invoked by the orchestrator skill `rd-portfolio-rd-intelligence` at its patent-extraction step.

- The composition contract is in `HANDOFF.md`.
- The orchestrator passes a ranked patent set + product/platform context + active CTQs + target test methods + the question to answer.
- This skill returns the typed bundle defined in `HANDOFF.md`.
- Both skills ship as a pair. This skill can also be used standalone on any patent set.
```

- [ ] **Step 2: Run the validator**

```bash
cd /d "D:\coding_is_fun\AI_CHEMIST_SKILL_2\patent-xy-extraction-skill"
python ../validate_skill_structure.py
```
Expected: `PASS: patent-xy-extraction-skill`.

- [ ] **Step 3: Commit**

```bash
git add patent-xy-extraction-skill/SKILL.md
git commit -m "feat: add Used by section pointing patent skill at the orchestrator"
```

---

## Task 9: Delete the two drifted per-skill validators

**Files:**
- Delete: `D:\coding_is_fun\AI_CHEMIST_SKILL_2\patent-xy-extraction-skill\scripts\validate_skill_structure.py`
- Delete: `D:\coding_is_fun\AI_CHEMIST_SKILL_2\rd-portfolio-rd-intelligence\scripts\validate_skill_structure.py`

- [ ] **Step 1: Delete both**

```bash
git rm patent-xy-extraction-skill/scripts/validate_skill_structure.py
git rm rd-portfolio-rd-intelligence/scripts/validate_skill_structure.py
```
Expected: both staged for deletion.

- [ ] **Step 2: Confirm scripts/ folders may be left empty (acceptable) or note it**

The validator no longer lives in scripts/. Leave the empty `scripts/` folders; they are still valid structure and may host future tooling. (Validator requires folders `workflows/templates/rubrics/references/examples`, not `scripts/`, so empty scripts/ is fine.)

- [ ] **Step 3: Commit**

```bash
git commit -m "chore: remove drifted per-skill validators in favor of shared one"
```

---

## Task 10: Update both READMEs with the composition diagram + install-as-a-pair

**Files:**
- Modify: `D:\coding_is_fun\AI_CHEMIST_SKILL_2\patent-xy-extraction-skill\README.md`
- Modify: `D:\coding_is_fun\AI_CHEMIST_SKILL_2\rd-portfolio-rd-intelligence\README.md`

- [ ] **Step 1: Add composition section to the patent skill README**

In `patent-xy-extraction-skill\README.md`, after the `## Install` section, insert:

```markdown
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
```

- [ ] **Step 2: Add composition section to the orchestrator README**

In `rd-portfolio-rd-intelligence\README.md`, after the `## Install` section, insert the same diagram block but with the orchestrator's annotation. Replace the existing `## Validate` block to point at the shared validator:

```markdown
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
```

And replace the existing `## Validate` section with:

```markdown
## Validate

Run the shared validator from the repo root:

```bash
python validate_skill_structure.py --all
```
```

- [ ] **Step 3: Commit**

```bash
git add patent-xy-extraction-skill/README.md rd-portfolio-rd-intelligence/README.md
git commit -m "docs: add composition diagram + shared-validator usage to both READMEs"
```

---

## Task 11: Final end-to-end verification

**Files:** none modified.

- [ ] **Step 1: Run the validator self-test**

```bash
cd /d "D:\coding_is_fun\AI_CHEMIST_SKILL_2"
python -m unittest tests.test_validate_skill_structure -v
```
Expected: PASS, 10 tests.

- [ ] **Step 2: Run the shared validator across both skills**

```bash
python validate_skill_structure.py --all
```
Expected:
```text
PASS: patent-xy-extraction-skill
PASS: rd-portfolio-rd-intelligence
```

- [ ] **Step 3: Manual consistency cross-check**

Verify by reading the final state (these are assertions; if any is false, fix before finishing):
1. `rd-portfolio-rd-intelligence/SKILL.md` references `workflows/04a_patent_search_and_rank.md` and `workflows/04_patent_doe_extraction.md`, and both files exist.
2. `rd-portfolio-rd-intelligence/workflows/04_patent_doe_extraction.md` names `patent-xy-extraction-skill` and references `HANDOFF.md`.
3. `patent-xy-extraction-skill/HANDOFF.md` exists and lists the 5 inputs, the selection rule (>=30 / top-N 5–8 configurable), and the 8 bundle outputs.
4. `rd-portfolio-rd-intelligence/templates/patent_extraction_template.md` no longer exists; `patent_summary_template.md` does.
5. Neither `scripts/validate_skill_structure.py` exists; the repo-root `validate_skill_structure.py` does.

- [ ] **Step 4: Commit verification note (optional)**

If any fix was needed in Step 3, commit it. Otherwise no commit.

---

## Self-Review (run after writing this plan)

**1. Spec coverage** — mapped against the agreed design:
- Composition contract HANDOFF.md → Task 3 ✓
- New 04a search→rank workflow → Task 4 ✓
- Misplaced template fixed → Task 6 ✓
- Orchestrator 04 rewritten to delegate → Task 5 ✓
- Both SKILL.md declare the relationship → Tasks 7, 8 ✓
- Unified validator → Tasks 1, 2, 9 ✓
- READMEs updated → Task 10 ✓
- patent_priority_list_template + patent_summary_template → Tasks 4, 6 ✓

**2. Placeholder scan** — none. Every code/markdown block is complete. No "TODO/TBD/similar to".

**3. Type/name consistency** — checked:
- Skill name string `patent-xy-extraction-skill` used identically in HANDOFF.md (Task 3), orchestrator SKILL.md (Task 7), orchestrator workflow 04 (Task 5), patent SKILL.md (Task 8), both READMEs (Task 10).
- File name `04a_patent_search_and_rank.md` identical in Task 4 (create), Task 7 (reference), Task 11 (assertion).
- Template name `patent_summary_template.md` identical in Task 6 (create), Task 5 (reference).
- Workflow-ref ordering note: Task 7 is sequenced *after* Tasks 4–6 so that `04a` exists before SKILL.md references it — validator stays green throughout.

**4. Dependency ordering** — validator self-test (Task 1) before validator impl (Task 2); HANDOFF (Task 3) before anything that references it (Tasks 5, 7, 8); `04a` file (Task 4) before SKILL.md references it (Task 7). No forward references.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-06-19-wire-skills-together.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
