from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')


def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'marker missing: {label}')
    s = s.replace(old, new, 1)


if '<title>HeldenMobil – HLD PoC v19.0</title>' not in s:
    raise SystemExit('expected v19.0 base')

# Keep every visible/internal release marker aligned.
rep('<title>HeldenMobil – HLD PoC v19.0</title>',
    '<title>HeldenMobil – HLD PoC v19.0.1</title>', 'title version')
rep('<div class="sub">DSA 4.1 · HLD + Begleitdaten v17.3</div>',
    '<div class="sub">DSA 4.1 · HLD + Begleitdaten v19.0.1</div>', 'header sub version')
rep('<div class="badge">Beta v17.3</div>',
    '<div class="badge">Beta v19.0.1</div>', 'top right badge version')
rep('<footer>HeldenMobil Beta v17.3 · HLD read-only · Begleitdaten + OneDrive-Sync · Spieltisch</footer>',
    '<footer>HeldenMobil Beta v19.0.1 · HLD read-only · Begleitdaten + OneDrive-Sync · Spieltisch</footer>', 'footer version')
rep('HeldenMobil Qualitätsbericht v19.0',
    'HeldenMobil Qualitätsbericht v19.0.1', 'quality report text version')
rep("lastQualityAudit={version:'18.0.1'",
    "lastQualityAudit={version:'19.0.1'", 'quality report data version')

# Avoid flashing a spell tab before a hero is parsed, analogous to Liturgies.
rep('<button class="tab" data-tab="spells" disabled>Zauber</button>',
    '<button class="tab hidden" data-tab="spells" disabled>Zauber</button>', 'spell tab initial visibility')

karmal = "    const karmal=liturgyKnowledges.length>0||liturgies.length>0||props.some(x=>x.name==='Karmaenergie'&&(Number(x.mod||0)!==0||Number(x.value||0)!==0))||sfSet.has('Karmalqueste');\n    const talentSpecs=new Map(), spellSpecs=[];"
magical = "    const karmal=liturgyKnowledges.length>0||liturgies.length>0||props.some(x=>x.name==='Karmaenergie'&&(Number(x.mod||0)!==0||Number(x.value||0)!==0))||sfSet.has('Karmalqueste');\n    const magical=spells.length>0||props.some(x=>x.name==='Astralenergie'&&(Number(x.mod||0)!==0||Number(x.value||0)!==0));\n    const talentSpecs=new Map(), spellSpecs=[];"
rep(karmal, magical, 'magical hero detection')

rep('props,talents,spells,liturgyKnowledges,liturgies,karmal,combat,combatMap,sf,sfEntries,sfSet,vt,advantages,disadvantages,vtNames,vtValues,meisterhandwerke,talentSpecs,combatSets,unarmedBonuses,rg1,items,',
    'props,talents,spells,magical,liturgyKnowledges,liturgies,karmal,combat,combatMap,sf,sfEntries,sfSet,vt,advantages,disadvantages,vtNames,vtValues,meisterhandwerke,talentSpecs,combatSets,unarmedBonuses,rg1,items,',
    'hero return magical flag')

old_render = "    $('#workspace').classList.add('has-hero');$$('.tab[data-tab]').forEach(b=>{if(b.dataset.tab!=='data')b.disabled=false;});\n    const litTab=$('.tab[data-tab=\\\"liturgies\\\"]');if(litTab){litTab.classList.toggle('hidden',!h.karmal);litTab.disabled=!h.karmal;if(!h.karmal&&litTab.classList.contains('active'))$('.tab[data-tab=\\\"overview\\\"]')?.click();}"
new_render = "    $('#workspace').classList.add('has-hero');$$('.tab[data-tab]').forEach(b=>{if(b.dataset.tab!=='data')b.disabled=false;});\n    const spellTab=$('.tab[data-tab=\\\"spells\\\"]');if(spellTab){spellTab.classList.toggle('hidden',!h.magical);spellTab.disabled=!h.magical;if(!h.magical&&spellTab.classList.contains('active'))$('.tab[data-tab=\\\"overview\\\"]')?.click();}\n    const litTab=$('.tab[data-tab=\\\"liturgies\\\"]');if(litTab){litTab.classList.toggle('hidden',!h.karmal);litTab.disabled=!h.karmal;if(!h.karmal&&litTab.classList.contains('active'))$('.tab[data-tab=\\\"overview\\\"]')?.click();}"
rep(old_render, new_render, 'spell tab render visibility')

p.write_text(s, encoding='utf-8')

# Self-check the exact user-visible and functional contract.
checks = [
    '<title>HeldenMobil – HLD PoC v19.0.1</title>',
    '<div class="sub">DSA 4.1 · HLD + Begleitdaten v19.0.1</div>',
    '<div class="badge">Beta v19.0.1</div>',
    'HeldenMobil Beta v19.0.1',
    '<button class="tab hidden" data-tab="spells" disabled>Zauber</button>',
    "const magical=spells.length>0||props.some(x=>x.name==='Astralenergie'",
    "spellTab.classList.toggle('hidden',!h.magical)",
    "lastQualityAudit={version:'19.0.1'",
]
for marker in checks:
    if marker not in s:
        raise SystemExit(f'contract marker missing after patch: {marker}')
if 'Beta v17.3' in s or 'Begleitdaten v17.3' in s or 'HeldenMobil Beta v17.3' in s:
    raise SystemExit('stale visible v17.3 version remains')

print('v19.0.1 patch contract OK')
