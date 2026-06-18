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
