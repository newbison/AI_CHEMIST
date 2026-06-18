from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / 'SKILL.md',
    ROOT / 'workflows',
    ROOT / 'templates',
    ROOT / 'rubrics',
    ROOT / 'references',
    ROOT / 'examples',
]

missing = [str(p) for p in REQUIRED if not p.exists()]
if missing:
    raise SystemExit('Missing required paths:\n' + '\n'.join(missing))

skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
if not skill.startswith('---'):
    raise SystemExit('SKILL.md must start with YAML frontmatter')

m_name = re.search(r'^name:\s*(.+)$', skill, re.M)
m_desc = re.search(r'^description:\s*(.+)$', skill, re.M)
if not m_name or not m_desc:
    raise SystemExit('SKILL.md must include name and description')

name = m_name.group(1).strip()
if name != ROOT.name:
    raise SystemExit(f'name must match directory name: {name} != {ROOT.name}')

if not re.fullmatch(r'[a-z0-9-]{1,64}', name):
    raise SystemExit('name must use lowercase letters, numbers, hyphens only, max 64 chars')

print('Skill structure validation passed.')
