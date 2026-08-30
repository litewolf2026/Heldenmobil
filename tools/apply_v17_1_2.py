from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

if 'HLD PoC v17.1.1' not in text:
    raise SystemExit('Expected v17.1.1 title not found')
if 'v17.1.2 footer/abdomen alignment' in text:
    raise SystemExit('v17.1.2 patch already present')

text = text.replace('HLD PoC v17.1.1', 'HLD PoC v17.1.2', 1)

patch = r'''

/* v17.1.2 footer/abdomen alignment */
.dashboard-zone[data-zone="bauch"]{
  top:47.6% !important;
}
.dashboard-footer-overlay{
  left:7.5% !important;
  width:88% !important;
  grid-template-columns:24.32fr 22.16fr 23.07fr 30.45fr !important;
}
.dashboard-footer-overlay>div{
  justify-self:stretch;
  text-align:center;
}
'''

needle = '</style>'
if needle not in text:
    raise SystemExit('Closing style tag not found')
text = text.replace(needle, patch + '\n' + needle, 1)
path.write_text(text, encoding='utf-8')

print('Applied HeldenMobil v17.1.2 alignment patch')
