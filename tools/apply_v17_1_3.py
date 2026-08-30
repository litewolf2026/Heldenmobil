from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

if 'HeldenMobil – HLD PoC v17.1.2' not in text:
    raise SystemExit('Expected v17.1.2 title not found')

text = text.replace('HeldenMobil – HLD PoC v17.1.2', 'HeldenMobil – HLD PoC v17.1.3', 1)

override = r'''

/* v17.1.3 final optical alignment */
/* Bauch: minimal nach oben und links; vorhandener v17.1.1-Y-Offset bleibt erhalten. */
.dashboard-zone[data-zone="bauch"]{
  left:4.5% !important;
  top:47.2% !important;
}
/* Die gezeichneten Footer-Felder sind optisch nicht exakt gleich breit.
   gRS und gBE passen bereits; nur WS und GS werden gezielt nach links gerueckt. */
.dashboard-footer-item:nth-child(3){position:relative;left:-1cqw;}
.dashboard-footer-item:nth-child(4){position:relative;left:-1.5cqw;}
'''

if '/* v17.1.3 final optical alignment */' in text:
    raise SystemExit('v17.1.3 override already present')
if '</style>' not in text:
    raise SystemExit('Closing style tag not found')

text = text.replace('</style>', override + '\n</style>', 1)
path.write_text(text, encoding='utf-8')

checks = [
    'HeldenMobil – HLD PoC v17.1.3',
    'left:4.5% !important;',
    'top:47.2% !important;',
    '.dashboard-footer-item:nth-child(3){position:relative;left:-1cqw;}',
    '.dashboard-footer-item:nth-child(4){position:relative;left:-1.5cqw;}',
]
for check in checks:
    if check not in text:
        raise SystemExit(f'Verification failed: {check}')
print('v17.1.3 alignment patch verified')
