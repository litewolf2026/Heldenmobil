from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Release version everywhere visible/reporting.
s = s.replace('19.0.1', '19.0.2')

# Combat summary: the displayed value already is the RG-adjusted gBE.
old_summary = "{l:'BE',v:armor.be,n:`gBE ${armor.baseBE}${armor.beReduction?` · Rüstungsgewöhnung −${armor.beReduction}`:''}`}"
new_summary = "{l:'gBE',v:armor.be,n:`Roh-gBE ${armor.baseBE}${armor.beReduction?` · Rüstungsgewöhnung −${armor.beReduction}`:''}`}"
if old_summary not in s:
    raise SystemExit('combat summary marker not found')
s = s.replace(old_summary, new_summary, 1)

# The dashboard footer needs access to the current combat set so eBE can be
# derived from the selected main weapon/talent after RG has reduced gBE.
old_head = "function renderDashboardBody(){\n    if(!state.current||!$('#dashboardBodyImage'))return;const {armor,speed}=dashboardArmor(),s=activeAdventureStatus();"
new_head = "function renderDashboardBody(){\n    if(!state.current||!$('#dashboardBodyImage'))return;const {set,armor,speed}=dashboardArmor(),s=activeAdventureStatus();"
if old_head not in s:
    raise SystemExit('dashboard body head marker not found')
s = s.replace(old_head, new_head, 1)

# Insert a small helper immediately before renderDashboardBody.
marker = "  function renderDashboardBody(){\n"
helper = """  function dashboardEffectiveBE(set,armor){
    if(!set)return {value:armor.be,talent:'',offset:0};
    const meleeRows=set.entries.filter(e=>e.type==='melee').map(e=>({e,v:meleeValues(e,armor.be)})),loadouts=buildCombatLoadouts(set,armor.be,meleeRows),active=activeLoadout(set,loadouts);
    const talent=active?.main?(active.main.talent||itemMeleeData(active.main).talent||''):'';
    return {value:talent?combatEbe(talent,armor.be):armor.be,talent,offset:COMBAT_META[talent]?.offset||0};
  }
"""
if marker not in s:
    raise SystemExit('dashboard helper insertion marker not found')
s = s.replace(marker, helper + marker, 1)

old_footer = """    const wd=woundData(),gbe=armor.baseBE,eff=armor.be;
    $('#dashboardFooterOverlay').innerHTML=`<div class=\"dashboard-footer-item\" title=\"Gewichteter Rüstungsschutz\"><span class=\"dashboard-foot-label\">gRS</span><strong class=\"dashboard-foot-value\">${armor.rs}</strong></div><div class=\"dashboard-footer-item\" title=\"Gesamtbehinderung${gbe!==eff?` · effektiv nach Rüstungsgewöhnung: ${eff}`:''}\"><span class=\"dashboard-foot-label\">gBE</span><strong class=\"dashboard-foot-value\">${gbe}</strong>${gbe!==eff?`<small class=\"dashboard-foot-sub\">eff. ${eff}</small>`:''}</div><div class=\"dashboard-footer-item\" title=\"Wundschwelle\"><span class=\"dashboard-foot-label\">WS</span><strong class=\"dashboard-foot-value\">${wd.threshold}</strong></div><div class=\"dashboard-footer-item\" title=\"Aktuelle Geschwindigkeit: ${esc(speed.parts.join(' · '))}\"><span class=\"dashboard-foot-label\">GS</span><strong class=\"dashboard-foot-value\">${speed.value}</strong></div>`;
"""
new_footer = """    const wd=woundData(),gbe=armor.be,ebe=dashboardEffectiveBE(set,armor),eff=ebe.value,rawGbe=armor.baseBE;
    const gbeTitle=`Gesamtbehinderung nach Rüstungsgewöhnung${armor.beReduction?` · Roh-gBE ${rawGbe} − RG ${armor.beReduction} = gBE ${gbe}`:''}${ebe.talent?` · eff. BE Hauptwaffe (${ebe.talent}): ${eff}`:''}`;
    $('#dashboardFooterOverlay').innerHTML=`<div class=\"dashboard-footer-item\" title=\"Gewichteter Rüstungsschutz\"><span class=\"dashboard-foot-label\">gRS</span><strong class=\"dashboard-foot-value\">${armor.rs}</strong></div><div class=\"dashboard-footer-item\" title=\"${esc(gbeTitle)}\"><span class=\"dashboard-foot-label\">gBE</span><strong class=\"dashboard-foot-value\">${gbe}</strong>${ebe.talent&&eff!==gbe?`<small class=\"dashboard-foot-sub\">eff. ${eff}</small>`:''}</div><div class=\"dashboard-footer-item\" title=\"Wundschwelle\"><span class=\"dashboard-foot-label\">WS</span><strong class=\"dashboard-foot-value\">${wd.threshold}</strong></div><div class=\"dashboard-footer-item\" title=\"Aktuelle Geschwindigkeit: ${esc(speed.parts.join(' · '))}\"><span class=\"dashboard-foot-label\">GS</span><strong class=\"dashboard-foot-value\">${speed.value}</strong></div>`;
"""
if old_footer not in s:
    raise SystemExit('dashboard footer marker not found')
s = s.replace(old_footer, new_footer, 1)

# Contract guardrails.
required = [
    'HLD PoC v19.0.2',
    'Beta v19.0.2',
    'Begleitdaten v19.0.2',
    'dashboardEffectiveBE(set,armor)',
    "const wd=woundData(),gbe=armor.be",
    "l:'gBE',v:armor.be",
    'Roh-gBE',
    'eff. BE Hauptwaffe',
]
for token in required:
    if token not in s:
        raise SystemExit(f'missing contract token: {token}')
if "gbe=armor.baseBE,eff=armor.be" in s:
    raise SystemExit('old dashboard BE semantics still present')
if '19.0.1' in s:
    raise SystemExit('stale 19.0.1 version marker remains')

p.write_text(s, encoding='utf-8')
print('patched v19.0.2 BE semantics')
