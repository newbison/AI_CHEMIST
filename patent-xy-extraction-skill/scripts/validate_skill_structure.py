from pathlib import Path
import re, json

ROOT = Path(__file__).resolve().parents[1]
required = [
    ROOT/'SKILL.md',
    ROOT/'workflows',
    ROOT/'templates',
    ROOT/'rubrics',
    ROOT/'schemas',
    ROOT/'references',
    ROOT/'examples'
]
missing = [str(p) for p in required if not p.exists()]
if missing:
    raise SystemExit('Missing required paths:\n' + '\n'.join(missing))

skill = (ROOT/'SKILL.md').read_text(encoding='utf-8')
if not skill.startswith('---'):
    raise SystemExit('SKILL.md must start with YAML frontmatter')

name_match = re.search(r'^name:\s*(.+)$', skill, re.M)
desc_match = re.search(r'^description:\s*(.+)$', skill, re.M)
if not name_match or not desc_match:
    raise SystemExit('SKILL.md must contain name and description')

name = name_match.group(1).strip()
if name != ROOT.name:
    raise SystemExit(f'name must match directory name: {name} != {ROOT.name}')

if not re.fullmatch(r'[a-z0-9-]{1,64}', name):
    raise SystemExit('name must be lowercase letters, numbers, hyphens only, max 64 chars')

if len(desc_match.group(1).strip()) > 200:
    raise SystemExit('description should be <= 200 characters for broad compatibility')

schema_path = ROOT/'schemas'/'patent_xy_extraction_schema.json'
json.loads(schema_path.read_text(encoding='utf-8'))

print('Patent X-Y extraction skill validation passed.')
