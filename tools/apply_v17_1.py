from pathlib import Path

PATH = Path('index.html')
s = PATH.read_text(encoding='utf-8')

if '/* v17.1 Spieltisch layout polish */' in s:
    print('v17.1 already applied')
    raise SystemExit(0)

def one(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise RuntimeError(f'{label}: expected 1 occurrence, found {n}')
    s = s.replace(old, new, 1)

# Visible version markers.
for old, new, label in [
    ('HeldenMobil – HLD PoC v17', 'HeldenMobil – HLD PoC v17.1', 'title'),
    ('DSA 4.1 · HLD + Begleitdaten v17', 'DSA 4.1 · HLD + Begleitdaten v17.1', 'header'),
    ('Proof of Concept v17', 'Proof of Concept v17.1', 'badge'),
    ('HeldenMobil PoC v17 · HLD read-only · Begleitdaten + OneDrive-Sync · Spieltisch',
     'HeldenMobil PoC v17.1 · HLD read-only · Begleitdaten + OneDrive-Sync · Spieltisch', 'footer'),
]:
    one(old, new, label)

# Keep all three energy columns vertically aligned by always reserving the threshold row.
one(
"""    const thresholds=e.label==='LeP'&&e.max>0?`<div class=\"dashboard-energy-thresholds\">½ ${Math.floor(e.max/2)} · ⅓ ${Math.floor(e.max/3)} · ¼ ${Math.floor(e.max/4)}</div>`:'';
    return `<div class=\"dashboard-energy ${severity}\"><div class=\"dashboard-energy-main\"><span class=\"dashboard-energy-name\">${e.label}</span><span class=\"dashboard-energy-value\">${e.value}${e.max!=null?`/${e.max}`:''}</span></div><div class=\"dashboard-energy-buttons\">${[-5,-1,1,5].map(n=>`<button type=\"button\" data-dashboard-energy=\"${e.label}\" data-delta=\"${n}\" ${e.active?'':'disabled'}>${n>0?'+':''}${n}</button>`).join('')}</div>${compact?'':thresholds}</div>`;""",
"""    const thresholds=e.label==='LeP'&&e.max>0?`<div class=\"dashboard-energy-thresholds\">½ ${Math.floor(e.max/2)} · ⅓ ${Math.floor(e.max/3)} · ¼ ${Math.floor(e.max/4)}</div>`:'<div class=\"dashboard-energy-thresholds dashboard-energy-empty\">&nbsp;</div>';
    return `<div class=\"dashboard-energy ${severity}\"><div class=\"dashboard-energy-main\"><span class=\"dashboard-energy-name\">${e.label}</span><span class=\"dashboard-energy-value\">${e.value}${e.max!=null?`/${e.max}`:''}</span></div><div class=\"dashboard-energy-buttons\">${[-5,-1,1,5].map(n=>`<button type=\"button\" data-dashboard-energy=\"${e.label}\" data-delta=\"${n}\" ${e.active?'':'disabled'}>${n>0?'+':''}${n}</button>`).join('')}</div>${compact?'':thresholds}</div>`;""",
'energy threshold placeholder')

# Footer: label and value share one line; an effective-BE note may still sit underneath.
one(
"""    $('#dashboardFooterOverlay').innerHTML=`<div title=\"Gewichteter Rüstungsschutz\"><span class=\"dashboard-foot-label\">gRS</span><strong class=\"dashboard-foot-value\">${armor.rs}</strong></div><div title=\"Gesamtbehinderung${gbe!==eff?` · effektiv nach Rüstungsgewöhnung: ${eff}`:''}\"><span class=\"dashboard-foot-label\">gBE</span><strong class=\"dashboard-foot-value\">${gbe}</strong>${gbe!==eff?`<small class=\"dashboard-foot-sub\">eff. ${eff}</small>`:''}</div><div title=\"Wundschwelle\"><span class=\"dashboard-foot-label\">WS</span><strong class=\"dashboard-foot-value\">${wd.threshold}</strong></div><div title=\"Aktuelle Geschwindigkeit: ${esc(speed.parts.join(' · '))}\"><span class=\"dashboard-foot-label\">GS</span><strong class=\"dashboard-foot-value\">${speed.value}</strong></div>`;""",
"""    $('#dashboardFooterOverlay').innerHTML=`<div class=\"dashboard-footer-item\" title=\"Gewichteter Rüstungsschutz\"><span class=\"dashboard-foot-label\">gRS</span><strong class=\"dashboard-foot-value\">${armor.rs}</strong></div><div class=\"dashboard-footer-item\" title=\"Gesamtbehinderung${gbe!==eff?` · effektiv nach Rüstungsgewöhnung: ${eff}`:''}\"><span class=\"dashboard-foot-label\">gBE</span><strong class=\"dashboard-foot-value\">${gbe}</strong>${gbe!==eff?`<small class=\"dashboard-foot-sub\">eff. ${eff}</small>`:''}</div><div class=\"dashboard-footer-item\" title=\"Wundschwelle\"><span class=\"dashboard-foot-label\">WS</span><strong class=\"dashboard-foot-value\">${wd.threshold}</strong></div><div class=\"dashboard-footer-item\" title=\"Aktuelle Geschwindigkeit: ${esc(speed.parts.join(' · '))}\"><span class=\"dashboard-foot-label\">GS</span><strong class=\"dashboard-foot-value\">${speed.value}</strong></div>`;""",
'footer inline layout')

css = r'''
/* v17.1 Spieltisch layout polish */
.dashboard-energy-slot:not(.special-stack){display:grid;grid-template-rows:auto auto auto;align-content:start;justify-items:center;padding:.2cqw .8cqw}
.dashboard-energy-slot:not(.special-stack) .dashboard-energy{display:grid;grid-template-rows:minmax(2.9cqw,auto) minmax(2.35cqw,auto) minmax(1.15cqw,auto);align-content:start}
.dashboard-energy-slot:not(.special-stack) .dashboard-energy-main{min-height:2.9cqw}
.dashboard-energy-slot:not(.special-stack) .dashboard-energy-buttons{min-height:2.35cqw;margin-top:.35cqw}
.dashboard-energy-slot:not(.special-stack) .dashboard-energy-thresholds{min-height:1.15cqw;margin-top:.18cqw}
.dashboard-energy-empty{visibility:hidden}
.dashboard-zone[data-zone="bauch"]{left:4.9%;top:43.9%;width:21%;height:10%}
.dashboard-zone[data-zone="rechterarm"]{left:75.1%;top:42.9%;width:20.9%;height:10%}
.dashboard-footer-overlay{align-items:stretch}
.dashboard-footer-item{display:flex;flex-wrap:wrap;align-content:center;align-items:baseline;justify-content:center;gap:.7cqw;height:100%;padding:.2cqw .45cqw;text-align:center}
.dashboard-foot-label{display:inline;color:#d9bd79;font-size:2.05cqw;font-weight:900;line-height:1}
.dashboard-foot-value{display:inline;color:#fff0c9;font-size:3.2cqw;font-weight:900;line-height:1}
.dashboard-foot-sub{display:block;flex-basis:100%;margin-top:-.15cqw;color:#aeb7c4;font-size:1.0cqw;line-height:1}
@media(max-width:430px){.dashboard-foot-label{font-size:2.25cqw}.dashboard-foot-value{font-size:3.45cqw}.dashboard-foot-sub{font-size:1.1cqw}}
'''
one('</style>', css + '\n</style>', 'insert v17.1 CSS')

required = [
    'HeldenMobil – HLD PoC v17.1',
    '/* v17.1 Spieltisch layout polish */',
    'dashboard-energy-empty',
    'dashboard-footer-item',
    'data-zone="bauch"',
    'data-zone="rechterarm"',
]
for token in required:
    if token not in s:
        raise RuntimeError(f'missing token after patch: {token}')

PATH.write_text(s, encoding='utf-8')
print('Applied HeldenMobil v17.1 Spieltisch layout polish.')
