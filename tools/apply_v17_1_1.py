from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')
marker = '/* v17.1.1 Spieltisch alignment */'
if marker in s:
    print('v17.1.1 already applied')
    raise SystemExit(0)

for old, new in [
    ('HeldenMobil – HLD PoC v17.1', 'HeldenMobil – HLD PoC v17.1.1'),
    ('DSA 4.1 · HLD + Begleitdaten v17.1', 'DSA 4.1 · HLD + Begleitdaten v17.1.1'),
    ('Proof of Concept v17.1', 'Proof of Concept v17.1.1'),
    ('HeldenMobil PoC v17.1', 'HeldenMobil PoC v17.1.1'),
]:
    if old in s:
        s = s.replace(old, new)

css = r'''

/* v17.1.1 Spieltisch alignment */
.dashboard-energy-overlay{transform:translateY(1.35cqw)}
.dashboard-zone[data-zone="bauch"]{transform:translateY(2.1cqw)}
.dashboard-zone[data-zone="rechterarm"]{transform:translateY(1.8cqw)}
'''

if '</style>' not in s:
    raise RuntimeError('style end tag not found')
s = s.replace('</style>', css + '\n</style>', 1)
path.write_text(s, encoding='utf-8')
print('v17.1.1 alignment applied')
