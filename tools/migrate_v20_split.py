from pathlib import Path
import re

root = Path('.')
index_path = root / 'index.html'
s = index_path.read_text(encoding='utf-8')

if 'v19.0.2' not in s:
    raise SystemExit('expected v19.0.2 source')

# Extract the two existing inline script blocks: vendored JSZip first, app second.
blocks = list(re.finditer(r'<script>(.*?)</script>', s, flags=re.S))
if len(blocks) != 2:
    raise SystemExit(f'expected exactly 2 inline script blocks, found {len(blocks)}')

vendor = blocks[0].group(1).strip() + '\n'
app = blocks[1].group(1).strip() + '\n'
if 'JSZip v3.10.1' not in vendor:
    raise SystemExit('first script is not JSZip 3.10.1')
if "const state = { heroes:" not in app or 'function parseHero' not in app:
    raise SystemExit('second script is not HeldenMobil app code')

(root / 'vendor').mkdir(exist_ok=True)
(root / 'js').mkdir(exist_ok=True)
(root / 'tests').mkdir(exist_ok=True)
(root / '.github' / 'workflows').mkdir(parents=True, exist_ok=True)

(root / 'vendor' / 'jszip-3.10.1.min.js').write_text(vendor, encoding='utf-8')
(root / 'js' / 'app.js').write_text(app.replace('v19.0.2', 'v20.0'), encoding='utf-8')

# Replace from the end so match offsets stay valid.
for match, replacement in [
    (blocks[1], '<script src="js/app.js"></script>'),
    (blocks[0], '<script src="vendor/jszip-3.10.1.min.js"></script>'),
]:
    s = s[:match.start()] + replacement + s[match.end():]

s = s.replace('v19.0.2', 'v20.0')
index_path.write_text(s, encoding='utf-8')

(root / 'package.json').write_text('''{\n  "name": "heldenmobil",\n  "private": true,\n  "version": "20.0.0",\n  "scripts": {\n    "test": "node tests/smoke.mjs"\n  }\n}\n''', encoding='utf-8')

(root / 'tests' / 'smoke.mjs').write_text(r'''import fs from 'node:fs';
import vm from 'node:vm';

const index = fs.readFileSync('index.html', 'utf8');
const app = fs.readFileSync('js/app.js', 'utf8');
const vendor = fs.readFileSync('vendor/jszip-3.10.1.min.js', 'utf8');

function ok(condition, message) {
  if (!condition) throw new Error(message);
}

ok(index.includes('<script src="vendor/jszip-3.10.1.min.js"></script>'), 'index must load vendored JSZip');
ok(index.includes('<script src="js/app.js"></script>'), 'index must load app.js');
ok(!index.includes('JSZip v3.10.1 - A JavaScript class'), 'JSZip must no longer be inline');
ok(!index.includes("const state = { heroes:"), 'application code must no longer be inline');
ok(index.includes('Beta v20.0'), 'visible version badge must be v20.0');
ok(index.includes('Begleitdaten v20.0'), 'header version must be v20.0');
ok(index.includes('HeldenMobil Beta v20.0'), 'footer version must be v20.0');
ok(app.includes('function parseHero'), 'HLD parser contract missing');
ok(app.includes('function setArmor'), 'armor rule contract missing');
ok(app.includes('function combatEbe'), 'effective-BE rule contract missing');
ok(app.includes('function parseLiturgySfName'), 'liturgy parser contract missing');
ok(app.includes('function normalizeCompanion'), 'companion migration contract missing');
ok(app.includes("const wd=woundData(),gbe=armor.be"), 'gBE semantic fix must remain');
ok(vendor.includes('JSZip v3.10.1'), 'wrong JSZip vendor payload');

new vm.Script(app, { filename: 'js/app.js' });
new vm.Script(vendor, { filename: 'vendor/jszip-3.10.1.min.js' });
console.log('HeldenMobil v20.0 smoke tests passed');
''', encoding='utf-8')

(root / '.github' / 'workflows' / 'ci.yml').write_text('''name: HeldenMobil CI\n\non:\n  push:\n    branches: [main]\n  pull_request:\n\npermissions:\n  contents: read\n\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-node@v4\n        with:\n          node-version: 22\n      - run: npm test\n''', encoding='utf-8')

(root / 'README.md').write_text('''# HeldenMobil\n\nDSA 4.1 Heldentool fuer HLD-Dateien mit lokalen Begleitdaten und optionalem OneDrive-Sync.\n\n## Quellstruktur ab v20\n\n- `index.html` - HTML/CSS und statische Oberflaeche\n- `vendor/jszip-3.10.1.min.js` - vendorte ZIP-Bibliothek fuer HLD-Dateien\n- `js/app.js` - HeldenMobil-Anwendungslogik (wird in den folgenden v20-Schritten weiter modularisiert)\n- `tests/smoke.mjs` - regressionskritische Struktur- und Syntaxpruefungen\n\n## Tests\n\n```bash\nnpm test\n```\n\nDie CI fuehrt diese Tests bei jedem Push und Pull Request aus.\n''', encoding='utf-8')

print('prepared v20.0 source split')
