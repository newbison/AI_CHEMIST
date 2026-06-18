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
  - if schemas/*.json exists, it parses

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
