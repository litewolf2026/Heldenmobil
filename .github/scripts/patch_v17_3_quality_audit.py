from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1: raise SystemExit(f'{label}: expected 1 match, found {n}')
    s=s.replace(old,new,1)

# Version labels
once('<title>HeldenMobil – HLD PoC v17.2.1</title>','<title>HeldenMobil – HLD PoC v17.3</title>','title')
if 'HLD + Begleitdaten v17.2</div>' in s:
    once('HLD + Begleitdaten v17.2</div>','HLD + Begleitdaten v17.3</div>','sub')
elif 'HLD + Begleitdaten v17.2.1</div>' in s:
    once('HLD + Begleitdaten v17.2.1</div>','HLD + Begleitdaten v17.3</div>','sub')
else: raise SystemExit('header sub version marker missing')
if 'Beta v17.2</div>' in s:
    once('Beta v17.2</div>','Beta v17.3</div>','badge')
elif 'Beta v17.2.1</div>' in s:
    once('Beta v17.2.1</div>','Beta v17.3</div>','badge')
else: raise SystemExit('badge version marker missing')
s=re.sub(r'HeldenMobil PoC v17\.1\.1', 'HeldenMobil Beta v17.3', s, count=1)

# Audit UI styles
css='''
/* v17.3 HLD quality audit */
.quality-audit-card{margin-top:12px}.quality-audit-head{display:flex;align-items:flex-start;justify-content:space-between;gap:14px}.quality-audit-head h4{margin-bottom:5px}.quality-summary{display:grid;grid-template-columns:repeat(4,minmax(100px,1fr));gap:8px;margin:10px 0}.quality-metric{border:1px solid var(--line);border-radius:9px;background:#111419;padding:9px 10px}.quality-metric span{display:block;color:var(--muted);font-size:.66rem;text-transform:uppercase;letter-spacing:.045em}.quality-metric strong{display:block;margin-top:2px;font-size:1.15rem}.quality-metric.error strong{color:#ef9c9c}.quality-metric.warn strong{color:#ebc17a}.quality-metric.ok strong{color:#8dd4a8}.quality-hero-list{display:flex;flex-direction:column;gap:7px;margin-top:9px}.quality-hero{border:1px solid #2f3540;border-radius:9px;background:#14181d}.quality-hero summary{cursor:pointer;padding:9px 10px;color:#e8d29c;font-weight:750}.quality-issues{padding:0 10px 8px}.quality-issue{display:grid;grid-template-columns:58px 150px 1fr;gap:8px;padding:6px 0;border-top:1px solid #292e36;font-size:.76rem;align-items:start}.quality-sev{font-weight:800;text-transform:uppercase;font-size:.64rem;letter-spacing:.04em}.quality-sev.error{color:#ef9c9c}.quality-sev.warn{color:#ebc17a}.quality-sev.info{color:#92b7df}.quality-code{color:#9da8b6;font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.68rem}.quality-catalog{margin-top:10px;padding:9px 10px;border:1px solid var(--line);border-radius:9px;background:#111419;color:#aeb7c5;font-size:.74rem;line-height:1.55}.quality-empty{padding:15px 4px;color:#8dd4a8}.quality-copy-state{font-size:.72rem;color:#8dd4a8}.quality-audit-actions button:disabled{opacity:.45;cursor:not-allowed}@media(max-width:700px){.quality-audit-head{flex-direction:column}.quality-summary{grid-template-columns:repeat(2,minmax(0,1fr))}.quality-issue{grid-template-columns:52px 1fr}.quality-code{grid-column:2}.quality-detail{grid-column:1/-1}}
'''
if s.count('</style>')!=1: raise SystemExit('style end marker not unique')
s=s.replace('</style>',css+'\n</style>',1)

# Insert audit panel at end of Data section.
m=re.search(r'<section id="data" class="section active">',s)
if not m: raise SystemExit('data section start missing')
data_end=s.find('    </section>',m.end())
if data_end<0: raise SystemExit('data section end missing')
audit_html='''
      <div class="comp-card quality-audit-card hero-data-only">
        <div class="quality-audit-head"><div><h4>HLD-Qualitätsprüfung</h4><div class="subtle">Prüft alle Helden der aktuell geladenen HLD mit demselben Parser wie die normale Anzeige. Gesucht werden vor allem nicht klassifizierte Talente, unvollständige Zauber, verdächtige Vor-/Nachteile, Spezialisierungsreste sowie fehlende Kampf- und Rüstungsreferenzen.</div></div><button type="button" class="action-btn primary" id="runQualityAudit">Alle Helden prüfen</button></div>
        <div class="toolbar-row quality-audit-actions"><button type="button" class="action-btn" id="copyQualityAudit" disabled>Prüfbericht kopieren</button><button type="button" class="action-btn" id="exportQualityAudit" disabled>Bericht als JSON</button><span id="qualityCopyState" class="quality-copy-state"></span></div>
        <div id="qualityAuditResult"><div class="empty-comp">Noch keine Prüfung ausgeführt.</div></div>
      </div>
'''
s=s[:data_end]+audit_html+s[data_end:]

# Audit logic before the dashboard code.
marker='  // ---- v17 Spieltisch -----------------------------------------------------\n'
if s.count(marker)!=1: raise SystemExit('dashboard marker missing')
js=r'''  // ---- v17.3 HLD-Qualitätsprüfung ----------------------------------------
  let lastQualityAudit=null;
  function qualityIssue(list,severity,code,detail,area=''){list.push({severity,code,area,detail:String(detail||'')});}
  function qualityDupes(values){const seen=new Set(),dup=new Set();for(const v of values){const k=String(v||'').trim();if(!k)continue;if(seen.has(k))dup.add(k);else seen.add(k);}return [...dup];}
  function qualityCounterAdd(map,key){key=String(key||'').trim()||'–';map.set(key,(map.get(key)||0)+1);}
  function qualityCounterObject(map){return Object.fromEntries([...map.entries()].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0],'de')));}
  function qualityAuditOne(raw,index,catalog){
    let h;try{h=parseHero(raw);}catch(e){return {name:raw?.name||`Held ${index+1}`,key:raw?.key||'',issues:[{severity:'error',code:'PARSER',area:'Parser',detail:e?.message||String(e)}]};}
    const issues=[],talents=(h.talents||[]).filter(t=>!t.meta),spells=h.spells||[],sets=h.combatSets||[];
    qualityCounterAdd(catalog.genders,h.gender);qualityCounterAdd(catalog.races,h.race);for(const z of spells)qualityCounterAdd(catalog.representations,z.rep);
    if(!h.name)qualityIssue(issues,'error','IDENTITY_NAME','Heldenname fehlt.','Basis');
    if(h.gender==='unknown')qualityIssue(issues,'info','GENDER_UNKNOWN','Geschlecht konnte nicht sicher als männlich/weiblich erkannt werden.','Basis');
    if(!h.race)qualityIssue(issues,'warn','RACE_MISSING','Rasse wurde nicht erkannt.','Basis');
    const pm=propMap(h.props||[]);for(const n of primaryNames)if(!pm.has(n))qualityIssue(issues,'error','ATTRIBUTE_MISSING',`${n} fehlt in den Eigenschaften.`,'Eigenschaften');
    const bm=new Map(deriveBasis(h.props||[]).map(x=>[x.name,x.value]));for(const n of ['LeP','AuP'])if(!bm.has(n))qualityIssue(issues,'warn','ENERGY_MISSING',`${n} konnte nicht abgeleitet werden.`,'Basiswerte');
    for(const t of talents){
      if(!t.name)qualityIssue(issues,'error','TALENT_NAME','Talent ohne Namen.','Talente');
      if(t.category==='Sonstige'){qualityIssue(issues,'warn','TALENT_CATEGORY',`${t.name} ist nicht klassifiziert und landet unter „Sonstige“.`,'Talente');catalog.unknownTalents.add(t.name);}
      if(!Number.isFinite(Number(t.value)))qualityIssue(issues,'error','TALENT_VALUE',`${t.name}: ungültiger TaW.`,'Talente');
    }
    for(const n of qualityDupes(talents.map(t=>t.name)))qualityIssue(issues,'warn','TALENT_DUPLICATE',`${n} kommt mehrfach in der Talentliste vor.`,'Talente');
    for(const [tn,specs] of (h.talentSpecs||new Map()).entries())if(!talents.some(t=>t.name===tn))qualityIssue(issues,'warn','TALENT_SPEC_ORPHAN',`${tn}: Spezialisierung ${specs.join(', ')} hat kein passendes Talent.`,'Talente');
    for(const tn of (h.meisterhandwerke||new Set()))if(!talents.some(t=>t.name===tn))qualityIssue(issues,'warn','MASTERCRAFT_ORPHAN',`${tn}: Meisterhandwerk hat kein passendes Talent.`,'Talente');
    for(const z of spells){
      if(!z.name)qualityIssue(issues,'error','SPELL_NAME','Zauber ohne Namen.','Zauber');
      if(!z.rep)qualityIssue(issues,'warn','SPELL_REP',`${z.name}: Repräsentation fehlt.`,'Zauber');
      if(!z.probe)qualityIssue(issues,'warn','SPELL_PROBE',`${z.name}${z.rep?` [${z.rep}]`:''}: Probe fehlt.`,'Zauber');
      if(!z.column)qualityIssue(issues,'info','SPELL_COLUMN',`${z.name}${z.rep?` [${z.rep}]`:''}: Steigerungsspalte fehlt.`,'Zauber');
      if(!Number.isFinite(Number(z.value)))qualityIssue(issues,'error','SPELL_VALUE',`${z.name}: ungültiger ZfW.`,'Zauber');
    }
    for(const n of qualityDupes(spells.map(z=>`${z.name} [${z.rep||'–'}]`)))qualityIssue(issues,'warn','SPELL_DUPLICATE',`${n} kommt mehrfach vor.`,'Zauber');
    for(const label of (h.vt||[])){
      if(/^Vorurteile gegen\s*(?::|$)/i.test(label))qualityIssue(issues,'warn','VT_TARGET',`${label}: Ziel der Vorurteile scheint zu fehlen.`,'Vor-/Nachteile');
      if(/^Vorurteile gegen .+:\s*$/i.test(label))qualityIssue(issues,'warn','VT_LEVEL',`${label}: Höhe der Vorurteile scheint zu fehlen.`,'Vor-/Nachteile');
      if(/:\s*·|·\s*·/.test(label))qualityIssue(issues,'info','VT_FORMAT',`${label}: ungewöhnliche Detailstruktur.`,'Vor-/Nachteile');
    }
    for(const n of qualityDupes(h.sf||[]))qualityIssue(issues,'info','SF_DUPLICATE',`${n} kommt mehrfach in den Sonderfertigkeiten vor.`,'Sonderfertigkeiten');
    for(const set of sets){for(const e of (set.entries||[])){
      const where=`Kampfset ${set.id}`;
      if(e.type==='other'){qualityIssue(issues,'info','EQUIP_UNKNOWN',`${e.record||'Unbekannter Eintrag'} konnte keinem Ausrüstungstyp zugeordnet werden.`,where);continue;}
      if(!e.base){qualityIssue(issues,'warn','EQUIP_NAME',`${e.type}: Gegenstandsname fehlt.`,where);continue;}
      if(e.type==='melee'){
        const ref=WEAPON_REF[e.base]||{},xml=e.item?.nk||{},tal=e.talent||ref.talent;
        if(!e.item&&!WEAPON_REF[e.base]){qualityIssue(issues,'warn','MELEE_REFERENCE',`${e.name||e.base}: weder HLD-Gegenstand noch Waffenreferenz gefunden.`,where);catalog.unknownCombat.add(e.base);}
        if(!(xml.tp||ref.tp))qualityIssue(issues,'warn','MELEE_DAMAGE',`${e.name||e.base}: Trefferpunkte fehlen.`,where);
        if(!tal)qualityIssue(issues,'warn','MELEE_TALENT',`${e.name||e.base}: Waffentalent fehlt.`,where);
        else if(!h.combatMap.has(tal)&&!talents.some(t=>t.name===tal))qualityIssue(issues,'warn','MELEE_TALENT_MATCH',`${e.name||e.base}: Talent „${tal}“ ist beim Helden nicht vorhanden.`,where);
      }else if(e.type==='ranged'){
        const ref=WEAPON_REF[e.base]||{},tal=e.talent||ref.talent;
        if(!WEAPON_REF[e.base]){qualityIssue(issues,'warn','RANGED_REFERENCE',`${e.name||e.base}: keine Fernkampf-Referenzdaten vorhanden.`,where);catalog.unknownCombat.add(e.base);}
        if(!tal)qualityIssue(issues,'warn','RANGED_TALENT',`${e.name||e.base}: Fernkampftalent fehlt.`,where);
        else if(!talents.some(t=>t.name===tal)&&!h.combatMap.has(tal))qualityIssue(issues,'warn','RANGED_TALENT_MATCH',`${e.name||e.base}: Talent „${tal}“ ist beim Helden nicht vorhanden.`,where);
      }else if(e.type==='armor'){
        const ref=ARMOR_REF[e.base]||{},zones=e.item?.armor?.zones||{};
        if(!ref.zones&&!Object.keys(zones).length){qualityIssue(issues,'warn','ARMOR_REFERENCE',`${e.name||e.base}: keine Trefferzonen-Rüstungsdaten vorhanden.`,where);catalog.unknownArmor.add(e.base);}
      }else if(e.type==='shield'){
        const parade=(e.usage||'').toLocaleLowerCase('de').includes('parade'),ref=(parade?PARRY_REF[e.base]:SHIELD_REF[e.base])||{},xml=e.item?.shield||{},mxml=e.item?.nk||{};
        if(!Object.keys(ref).length&&!xml.wm&&!mxml.wm&&xml.ini==null&&mxml.ini==null){qualityIssue(issues,'warn','SHIELD_REFERENCE',`${e.name||e.base}: keine Schild-/Parierwaffen-Referenzdaten vorhanden.`,where);catalog.unknownCombat.add(e.base);}
      }
    }}
    for(const rg of (h.rg1||[])){const ok=(h.items||[]).some(i=>i.armor&&(i.base===rg||i.display===rg||i.base.includes(rg)||rg.includes(i.base)||i.display.includes(rg)||rg.includes(i.display)));if(!ok)qualityIssue(issues,'info','RG1_REFERENCE',`Rüstungsgewöhnung I verweist auf „${rg}“, aber kein passendes Rüstungsstück wurde erkannt.`,'Rüstung');}
    return {name:h.name||raw?.name||`Held ${index+1}`,key:h.key||raw?.key||'',race:h.race,gender:h.gender,talentCount:talents.length,spellCount:spells.length,combatSetCount:sets.length,issues};
  }
  function qualityAuditText(report){
    const lines=[`HeldenMobil Qualitätsbericht v17.3`,`Erstellt: ${new Date(report.generatedAt).toLocaleString('de-DE')}`,`Helden: ${report.summary.heroes} · Fehler: ${report.summary.errors} · Warnungen: ${report.summary.warnings} · Hinweise: ${report.summary.infos}`,''];
    for(const h of report.heroes){if(!h.issues.length)continue;lines.push(`## ${h.name}`);for(const i of h.issues)lines.push(`${i.severity.toUpperCase()} [${i.code}]${i.area?` ${i.area}:`:''} ${i.detail}`);lines.push('');}
    const reps=Object.entries(report.catalog.representations||{}).map(([k,v])=>`${k} (${v})`).join(', ');if(reps)lines.push(`Repräsentationen: ${reps}`);
    if(report.catalog.unknownTalents.length)lines.push(`Nicht klassifizierte Talente: ${report.catalog.unknownTalents.join(', ')}`);
    if(report.catalog.unknownCombat.length)lines.push(`Kampfgegenstände ohne ausreichende Referenz: ${report.catalog.unknownCombat.join(', ')}`);
    if(report.catalog.unknownArmor.length)lines.push(`Rüstungen ohne Trefferzonenreferenz: ${report.catalog.unknownArmor.join(', ')}`);
    return lines.join('\n');
  }
  function renderQualityAudit(report){
    const host=$('#qualityAuditResult');if(!host)return;const s=report.summary,problemHeroes=report.heroes.filter(h=>h.issues.length),reps=Object.entries(report.catalog.representations).map(([k,v])=>`${esc(k)} <strong>${v}</strong>`).join(' · ')||'keine Zauber';
    const heroHtml=problemHeroes.map(h=>{const err=h.issues.filter(i=>i.severity==='error').length,warn=h.issues.filter(i=>i.severity==='warn').length,info=h.issues.filter(i=>i.severity==='info').length;return `<details class="quality-hero" ${err?'open':''}><summary>${esc(h.name)} · ${err?`${err} Fehler · `:''}${warn?`${warn} Warnungen · `:''}${info?`${info} Hinweise`:''}</summary><div class="quality-issues">${h.issues.map(i=>`<div class="quality-issue"><span class="quality-sev ${i.severity}">${esc(i.severity)}</span><span class="quality-code">${esc(i.code)}</span><span class="quality-detail">${i.area?`<strong>${esc(i.area)}:</strong> `:''}${esc(i.detail)}</span></div>`).join('')}</div></details>`;}).join('');
    host.innerHTML=`<div class="quality-summary"><div class="quality-metric ok"><span>Helden geprüft</span><strong>${s.heroes}</strong></div><div class="quality-metric error"><span>Fehler</span><strong>${s.errors}</strong></div><div class="quality-metric warn"><span>Warnungen</span><strong>${s.warnings}</strong></div><div class="quality-metric"><span>Hinweise</span><strong>${s.infos}</strong></div></div>${problemHeroes.length?`<div class="quality-hero-list">${heroHtml}</div>`:'<div class="quality-empty">Keine Auffälligkeiten nach den aktuellen Prüfregeln gefunden.</div>'}<div class="quality-catalog"><strong>Querschnitt:</strong> Repräsentationen: ${reps}${report.catalog.unknownTalents.length?`<br><strong>Sonstige Talente:</strong> ${esc(report.catalog.unknownTalents.join(', '))}`:''}${report.catalog.unknownCombat.length?`<br><strong>Kampf-Referenzen offen:</strong> ${esc(report.catalog.unknownCombat.join(', '))}`:''}${report.catalog.unknownArmor.length?`<br><strong>Rüstungs-Referenzen offen:</strong> ${esc(report.catalog.unknownArmor.join(', '))}`:''}</div>`;
  }
  function runQualityAudit(){
    const raws=Array.isArray(state.heroes)?state.heroes:[];if(!raws.length){$('#qualityAuditResult').innerHTML='<div class="empty-comp">Zuerst eine HLD laden.</div>';return;}
    const catalog={representations:new Map(),genders:new Map(),races:new Map(),unknownTalents:new Set(),unknownCombat:new Set(),unknownArmor:new Set()},heroes=raws.map((h,i)=>qualityAuditOne(h,i,catalog)),all=heroes.flatMap(h=>h.issues),summary={heroes:heroes.length,errors:all.filter(i=>i.severity==='error').length,warnings:all.filter(i=>i.severity==='warn').length,infos:all.filter(i=>i.severity==='info').length};
    lastQualityAudit={version:'17.3',generatedAt:new Date().toISOString(),sourceFile:state.fileName||'',summary,heroes,catalog:{representations:qualityCounterObject(catalog.representations),genders:qualityCounterObject(catalog.genders),races:qualityCounterObject(catalog.races),unknownTalents:[...catalog.unknownTalents].sort((a,b)=>a.localeCompare(b,'de')),unknownCombat:[...catalog.unknownCombat].sort((a,b)=>a.localeCompare(b,'de')),unknownArmor:[...catalog.unknownArmor].sort((a,b)=>a.localeCompare(b,'de'))}};
    renderQualityAudit(lastQualityAudit);$('#copyQualityAudit').disabled=false;$('#exportQualityAudit').disabled=false;$('#qualityCopyState').textContent='';
  }
  async function copyQualityAudit(){if(!lastQualityAudit)return;const text=qualityAuditText(lastQualityAudit);try{await navigator.clipboard.writeText(text);$('#qualityCopyState').textContent='Bericht kopiert.';}catch(_){const ta=document.createElement('textarea');ta.value=text;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();document.execCommand('copy');ta.remove();$('#qualityCopyState').textContent='Bericht kopiert.';}}
  function exportQualityAudit(){if(!lastQualityAudit)return;const blob=new Blob([JSON.stringify(lastQualityAudit,null,2)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`HeldenMobil-Qualitaetsbericht-${new Date().toISOString().slice(0,10)}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
  setTimeout(()=>{const r=$('#runQualityAudit'),c=$('#copyQualityAudit'),e=$('#exportQualityAudit');if(r)r.onclick=runQualityAudit;if(c)c.onclick=copyQualityAudit;if(e)e.onclick=exportQualityAudit;},0);

'''
s=s.replace(marker,js+marker,1)

# Static contract
required=['HeldenMobil – HLD PoC v17.3','HLD-Qualitätsprüfung','id="runQualityAudit"','function qualityAuditOne(','function runQualityAudit()','TALENT_CATEGORY','ARMOR_REFERENCE','Prüfbericht kopieren']
for token in required:
    if token not in s: raise SystemExit(f'missing token: {token}')

p.write_text(s,encoding='utf-8')
print('v17.3 quality audit patch contract OK')
