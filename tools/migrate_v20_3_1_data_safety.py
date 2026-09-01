from pathlib import Path

ROOT=Path('.')

def replace_once(text,old,new,label):
    if old not in text:
        raise SystemExit(f'missing anchor: {label}')
    if text.count(old)!=1:
        raise SystemExit(f'anchor not unique ({text.count(old)}): {label}')
    return text.replace(old,new,1)

# --- companion core -------------------------------------------------------
p=ROOT/'js/companion-core.js'
s=p.read_text(encoding='utf-8')
anchor="  function timeValue(x){const n=Date.parse(x||'');return Number.isFinite(n)?n:0;}\n"
insert="""  function normalizeSnapshotList(raw,max=10){
    const limit=Math.max(1,Math.floor(Number(max)||10));
    return (Array.isArray(raw)?raw:[]).filter(x=>x&&typeof x==='object'&&x.data&&typeof x.data==='object').sort((a,b)=>timeValue(b.at)-timeValue(a.at)).slice(0,limit);
  }
  function addSnapshot(raw,snapshot,max=10){
    if(!snapshot||typeof snapshot!=='object'||!snapshot.data||typeof snapshot.data!=='object')return normalizeSnapshotList(raw,max);
    const list=normalizeSnapshotList(raw,max),id=String(snapshot.id||'');if(id&&list.some(x=>String(x.id||'')===id))return list;
    return normalizeSnapshotList([snapshot,...list],max);
  }

  function timeValue(x){const n=Date.parse(x||'');return Number.isFinite(n)?n:0;}
"""
s=replace_once(s,anchor,insert,'companion snapshot helpers')
old="  return {WOUND_ZONE_KEYS,blankWoundZones,normalizeStatusWounds,magicOptionalInt,magicOptionalNumber,normalizeMagicEffect,normalizeInventoryMagic,energyEventText,parseLegacyEnergyEvent,normalizeAdventureEvents,mergeEnergyEvent,normalizeCompanionData,decideInitialSync,decideCloudWrite};"
new="  return {WOUND_ZONE_KEYS,blankWoundZones,normalizeStatusWounds,magicOptionalInt,magicOptionalNumber,normalizeMagicEffect,normalizeInventoryMagic,energyEventText,parseLegacyEnergyEvent,normalizeAdventureEvents,mergeEnergyEvent,normalizeCompanionData,normalizeSnapshotList,addSnapshot,decideInitialSync,decideCloudWrite};"
s=replace_once(s,old,new,'companion exports')
p.write_text(s,encoding='utf-8')

# --- app ------------------------------------------------------------------
p=ROOT/'js/app.js'
s=p.read_text(encoding='utf-8')
old="""  function normalizeCompanion(d){return HeldenMobilCompanion.normalizeCompanionData(d,{base:emptyCompanion(),heroKey:state.current.key,heroName:state.current.name,schemaVersion:COMP_SCHEMA,freshAdventureStatus,uid,energyWindowMs:ENERGY_EVENT_WINDOW_MS});}
  function saveCompanion(opts={}){if(!companionState.data)return;if(opts.touch!==false)companionState.data.updatedAt=new Date().toISOString();localStorage.setItem(companionStorageKey(),JSON.stringify(companionState.data));companionState.localExists=true;renderDataMeta();renderDashboard();if(!opts.skipCloud)cloudScheduleSave();}
"""
new="""  function normalizeCompanion(d){return HeldenMobilCompanion.normalizeCompanionData(d,{base:emptyCompanion(),heroKey:state.current.key,heroName:state.current.name,schemaVersion:COMP_SCHEMA,freshAdventureStatus,uid,energyWindowMs:ENERGY_EVENT_WINDOW_MS});}
  const COMPANION_BACKUP_PREFIX='heldenmobil:backup:v1:',COMPANION_BACKUP_LIMIT=10;
  function companionBackupKey(heroKey=state.current?.key){return COMPANION_BACKUP_PREFIX+String(heroKey||'unknown');}
  function loadCompanionBackups(heroKey=state.current?.key){try{return HeldenMobilCompanion.normalizeSnapshotList(JSON.parse(localStorage.getItem(companionBackupKey(heroKey))||'[]'),COMPANION_BACKUP_LIMIT);}catch(_){return [];}}
  function storeCompanionBackups(list,heroKey=state.current?.key){
    let safe=HeldenMobilCompanion.normalizeSnapshotList(list,COMPANION_BACKUP_LIMIT),key=companionBackupKey(heroKey);while(true){try{if(safe.length)localStorage.setItem(key,JSON.stringify(safe));else localStorage.removeItem(key);return safe;}catch(e){if(!safe.length){console.warn('Lokale Sicherungen konnten nicht gespeichert werden',e);return [];}safe=safe.slice(0,-1);}}
  }
  function createCompanionSnapshot(data=companionState.data,reason='Automatisch',force=false){
    if(!data||!state.current?.key)return false;let copy;try{copy=JSON.parse(JSON.stringify(data));}catch(e){console.warn('Sicherung konnte nicht erstellt werden',e);return false;}let list=loadCompanionBackups();if(!force&&list[0]){try{if(JSON.stringify(list[0].data)===JSON.stringify(copy))return false;}catch(_){}}
    const snap={id:uid('backup'),at:new Date().toISOString(),reason:String(reason||'Automatisch'),updatedAt:copy.updatedAt||null,data:copy};list=storeCompanionBackups(HeldenMobilCompanion.addSnapshot(list,snap,COMPANION_BACKUP_LIMIT));renderBackupControls();return list.some(x=>x.id===snap.id);
  }
  function writeCompanionLocal(key,value){
    try{localStorage.setItem(key,value);return true;}catch(first){let backups=loadCompanionBackups();while(backups.length){backups.pop();storeCompanionBackups(backups);try{localStorage.setItem(key,value);return true;}catch(_){}}console.error('Begleitdaten konnten lokal nicht gespeichert werden',first);alert('Der lokale Browser-Speicher ist voll. Bitte Begleitdaten als JSON exportieren und Browser-Speicher prüfen.');return false;}
  }
  function saveCompanion(opts={}){
    if(!companionState.data)return;const key=companionStorageKey();let previous=null;try{const raw=localStorage.getItem(key);if(raw)previous=JSON.parse(raw);}catch(_){}
    if(opts.snapshot!==false&&previous){try{if(JSON.stringify(previous)!==JSON.stringify(companionState.data))createCompanionSnapshot(previous,opts.snapshotReason||'Vor Änderung');}catch(_){}}
    if(opts.touch!==false)companionState.data.updatedAt=new Date().toISOString();if(!writeCompanionLocal(key,JSON.stringify(companionState.data)))return;companionState.localExists=true;renderDataMeta();renderDashboard();if(!opts.skipCloud)cloudScheduleSave();
  }
  function selectedCompanionBackup(){const id=$('#backupSelect')?.value;return loadCompanionBackups().find(x=>x.id===id)||null;}
  function renderBackupControls(){
    const select=$('#backupSelect'),count=$('#backupCount');if(!select||!count)return;const list=loadCompanionBackups();count.textContent=`${list.length}/${COMPANION_BACKUP_LIMIT} Stände`;select.innerHTML=list.length?list.map(x=>`<option value="${esc(x.id)}">${esc(new Date(x.at).toLocaleString('de-DE'))} · ${esc(x.reason||'Sicherung')} · ${Number(x.data?.adventures?.length||0)} Abenteuer</option>`).join(''):'<option value="">Noch keine Sicherung</option>';const disabled=!list.length;$('#backupRestore').disabled=disabled;$('#backupExport').disabled=disabled;
  }
  function backupMessage(text,type=''){const el=$('#backupMessage');if(!el)return;el.textContent=text||'';el.className=`cloud-message ${type}`;}
  function backupNow(){const ok=createCompanionSnapshot(companionState.data,'Manuell',true);backupMessage(ok?'Lokale Sicherung erstellt.':'Sicherung konnte nicht erstellt werden.',ok?'ok':'error');}
  function restoreCompanionBackup(){const snap=selectedCompanionBackup();if(!snap)return;if(!confirm(`Lokale Sicherung vom ${new Date(snap.at).toLocaleString('de-DE')} wiederherstellen? Der aktuelle Stand wird vorher ebenfalls gesichert.`))return;companionState.data=normalizeCompanion(snap.data);saveCompanion({snapshotReason:'Vor Wiederherstellung'});renderCompanionAll();backupMessage('Sicherung wiederhergestellt.','ok');}
  function exportCompanionBackup(){const snap=selectedCompanionBackup();if(!snap)return;const blob=new Blob([JSON.stringify(snap.data,null,2)],{type:'application/json'}),a=document.createElement('a'),stamp=String(snap.at||'').replace(/[:.]/g,'-');a.href=URL.createObjectURL(blob);a.download=`HeldenMobil-${(snap.data?.heroName||'Held').replace(/[^a-z0-9äöüß_-]+/gi,'_')}-Sicherung-${stamp}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
"""
s=replace_once(s,old,new,'app backup layer')

old="  function renderDataMeta(){const d=companionState.data;if(!d||!$('#dataMeta'))return;const imported=d.inventory.items.filter(x=>x.source==='Excel').length,remote=cloudState.remoteByHero.get(d.heroKey);$('#dataMeta').innerHTML=`<div><strong>Held:</strong> ${esc(d.heroName)}</div><div><strong>HLD-Key:</strong> ${esc(d.heroKey)}</div><div><strong>Schema:</strong> v${d.schemaVersion}</div><div><strong>Inventar:</strong> ${d.inventory.items.length} Einträge${imported?` · ${imported} aus Excel`:''}</div><div><strong>Geld:</strong> ${moneyTextFromTotal(moneyTotalK(),true)}</div><div><strong>Zauberspeicher:</strong> ${d.magic.staffSlots.length} Slots</div><div><strong>Magische Gegenstände:</strong> ${artifactItems().length} · ${artifactEffectCount()} Wirkungen</div><div><strong>Zuletzt lokal gespeichert:</strong> ${d.updatedAt?new Date(d.updatedAt).toLocaleString('de-DE'):'–'}</div><div><strong>OneDrive:</strong> ${remote?.id?`${esc(remote.name||cloudCompanionFileName(d.heroKey))}${remote.eTag?' · synchronisiert':''}`:'noch keine Cloud-Datei'}</div><div><strong>Speicherschlüssel:</strong> <span class=\"small-note\">${esc(companionStorageKey())}</span></div>`;}"
new="  function renderDataMeta(){const d=companionState.data;if(!d||!$('#dataMeta'))return;const imported=d.inventory.items.filter(x=>x.source==='Excel').length,remote=cloudState.remoteByHero.get(d.heroKey),baseline=cloudLoadBaseline(d.heroKey),lastSync=baseline?.syncedAt?new Date(baseline.syncedAt).toLocaleString('de-DE'):'–';$('#dataMeta').innerHTML=`<div><strong>Held:</strong> ${esc(d.heroName)}</div><div><strong>HLD-Key:</strong> ${esc(d.heroKey)}</div><div><strong>Schema:</strong> v${d.schemaVersion}</div><div><strong>Inventar:</strong> ${d.inventory.items.length} Einträge${imported?` · ${imported} aus Excel`:''}</div><div><strong>Geld:</strong> ${moneyTextFromTotal(moneyTotalK(),true)}</div><div><strong>Zauberspeicher:</strong> ${d.magic.staffSlots.length} Slots</div><div><strong>Magische Gegenstände:</strong> ${artifactItems().length} · ${artifactEffectCount()} Wirkungen</div><div><strong>Zuletzt lokal gespeichert:</strong> ${d.updatedAt?new Date(d.updatedAt).toLocaleString('de-DE'):'–'}</div><div><strong>Letzter erfolgreicher OneDrive-Sync:</strong> ${esc(lastSync)}</div><div><strong>OneDrive:</strong> ${remote?.id?`${esc(remote.name||cloudCompanionFileName(d.heroKey))}${remote.eTag?' · synchronisiert':''}`:'noch keine Cloud-Datei'}</div><div><strong>Speicherschlüssel:</strong> <span class=\"small-note\">${esc(companionStorageKey())}</span></div>`;renderBackupControls();}"
s=replace_once(s,old,new,'data metadata sync timestamp')

old="    const ds=$('#cloudDataState');if(ds){if(!connected)ds.innerHTML='<strong>Nicht mit Microsoft verbunden</strong><div class=\"small-note\" style=\"margin-top:4px\">Verbindung oben bei der HLD-Auswahl herstellen.</div>';else{const r=state.current?cloudState.remoteByHero.get(state.current.key):null;ds.innerHTML=`<strong>Microsoft verbunden</strong><div class=\"small-note\" style=\"margin-top:4px\">${state.current?(r?.id?`Cloud-Datei: ${esc(r.name)}`:'Für diesen Helden existiert noch keine Cloud-Datei.'):'Held laden, um Begleitdaten zu synchronisieren.'}</div>`;}}"
new="    const ds=$('#cloudDataState');if(ds){const baseline=state.current?cloudLoadBaseline(state.current.key):null,lastSync=baseline?.syncedAt?new Date(baseline.syncedAt).toLocaleString('de-DE'):'noch nie';if(!connected)ds.innerHTML=`<strong>Nicht mit Microsoft verbunden</strong><div class=\"small-note\" style=\"margin-top:4px\">Verbindung oben bei der HLD-Auswahl herstellen.</div><div class=\"small-note\" style=\"margin-top:4px\">Letzter erfolgreicher Sync: ${esc(lastSync)}</div>`;else{const r=state.current?cloudState.remoteByHero.get(state.current.key):null;ds.innerHTML=`<strong>Microsoft verbunden</strong><div class=\"small-note\" style=\"margin-top:4px\">${state.current?(r?.id?`Cloud-Datei: ${esc(r.name)}`:'Für diesen Helden existiert noch keine Cloud-Datei.'):'Held laden, um Begleitdaten zu synchronisieren.'}</div><div class=\"small-note\" style=\"margin-top:4px\">Letzter erfolgreicher Sync: ${esc(lastSync)}</div>`;}}"
s=replace_once(s,old,new,'cloud state last sync')

old="  $('#exportCompanion').addEventListener('click',exportCompanion);$('#importCompanion').addEventListener('change',e=>importCompanion(e.target.files[0]));\n"
new="  $('#exportCompanion').addEventListener('click',exportCompanion);$('#importCompanion').addEventListener('change',e=>importCompanion(e.target.files[0]));$('#backupNow').addEventListener('click',backupNow);$('#backupRestore').addEventListener('click',restoreCompanionBackup);$('#backupExport').addEventListener('click',exportCompanionBackup);\n"
s=replace_once(s,old,new,'backup event listeners')

old="  $('#resetCompanion').addEventListener('click',()=>{if(!confirm(`Begleitdaten für ${state.current?.name||'diesen Helden'} wirklich vollständig zurücksetzen?`))return;localStorage.removeItem(companionStorageKey());localStorage.removeItem(companionStorageKey(6));localStorage.removeItem(companionStorageKey(5));localStorage.removeItem(companionStorageKey(4));localStorage.removeItem(companionStorageKey(3));localStorage.removeItem(companionStorageKey(2));localStorage.removeItem(companionStorageKey(1));companionState.data=emptyCompanion();saveCompanion();renderCompanionAll();});"
new="  $('#resetCompanion').addEventListener('click',()=>{if(!confirm(`Begleitdaten für ${state.current?.name||'diesen Helden'} wirklich vollständig zurücksetzen?`))return;createCompanionSnapshot(companionState.data,'Vor Zurücksetzen',true);localStorage.removeItem(companionStorageKey());localStorage.removeItem(companionStorageKey(7));localStorage.removeItem(companionStorageKey(6));localStorage.removeItem(companionStorageKey(5));localStorage.removeItem(companionStorageKey(4));localStorage.removeItem(companionStorageKey(3));localStorage.removeItem(companionStorageKey(2));localStorage.removeItem(companionStorageKey(1));companionState.data=emptyCompanion();saveCompanion({snapshot:false});renderCompanionAll();backupMessage('Vorheriger Stand wurde als lokale Sicherung erhalten.','ok');});"
s=replace_once(s,old,new,'safe reset')

s=s.replace("lastQualityAudit={version:'20.3'","lastQualityAudit={version:'20.3.1'",1)
p.write_text(s,encoding='utf-8')

# --- index ----------------------------------------------------------------
p=ROOT/'index.html'
s=p.read_text(encoding='utf-8')
s=s.replace('v20.3','v20.3.1')
old='<div class="toolbar-row"><button class="action-btn primary" id="exportCompanion">JSON exportieren</button><label class="action-btn" for="importCompanion">JSON importieren</label><input id="importCompanion" type="file" accept="application/json,.json" hidden><button class="danger-btn" id="resetCompanion">Begleitdaten zurücksetzen</button></div><div id="dataMeta" class="data-box"></div>'
new='<div class="toolbar-row"><button class="action-btn primary" id="exportCompanion">JSON exportieren</button><label class="action-btn" for="importCompanion">JSON importieren</label><input id="importCompanion" type="file" accept="application/json,.json" hidden><button class="danger-btn" id="resetCompanion">Begleitdaten zurücksetzen</button></div><div class="data-box" style="margin-bottom:10px"><div style="display:flex;justify-content:space-between;gap:8px;align-items:baseline"><strong>Lokale Sicherungen</strong><span id="backupCount" class="count">0/10 Stände</span></div><div class="subtle" style="margin-top:5px">HeldenMobil hält bis zu 10 ältere Stände dieses Helden im Browser. Sie schützen vor versehentlichen Änderungen, aber nicht vor dem Löschen der Browserdaten – dafür eine Sicherung zusätzlich als JSON exportieren.</div><div class="toolbar-row"><select id="backupSelect" class="comp-input" style="min-width:260px;flex:1"><option value="">Noch keine Sicherung</option></select><button type="button" class="action-btn" id="backupNow">Jetzt sichern</button><button type="button" class="action-btn" id="backupRestore" disabled>Wiederherstellen</button><button type="button" class="action-btn" id="backupExport" disabled>Sicherung exportieren</button></div><div id="backupMessage" class="cloud-message"></div></div><div id="dataMeta" class="data-box"></div>'
s=replace_once(s,old,new,'backup UI')
p.write_text(s,encoding='utf-8')

# --- package --------------------------------------------------------------
p=ROOT/'package.json';s=p.read_text(encoding='utf-8');s=replace_once(s,'"version": "20.3.0"','"version": "20.3.1"','package version');p.write_text(s,encoding='utf-8')

# --- smoke tests ----------------------------------------------------------
p=ROOT/'tests/smoke.mjs';s=p.read_text(encoding='utf-8')
s=s.replace("ok(index.includes('Beta v20.3'), 'visible version badge must be v20.3');","ok(index.includes('Beta v20.3.1'), 'visible version badge must be v20.3.1');")
s=s.replace("ok(index.includes('Begleitdaten v20.3'), 'header version must be v20.3');","ok(index.includes('Begleitdaten v20.3.1'), 'header version must be v20.3.1');")
s=s.replace("ok(index.includes('HeldenMobil Beta v20.3'), 'footer version must be v20.3');","ok(index.includes('HeldenMobil Beta v20.3.1'), 'footer version must be v20.3.1');")
s=s.replace("ok(app.includes(\"lastQualityAudit={version:'20.3'\"), 'quality audit JSON version must be v20.3');","ok(app.includes(\"lastQualityAudit={version:'20.3.1'\"), 'quality audit JSON version must be v20.3.1');")
needle="ok(app.includes(\"cloudState.conflictHeroKey===key&&!force\"), 'unresolved OneDrive conflict must block automatic save');\n"
extra="ok(app.includes(\"cloudState.conflictHeroKey===key&&!force\"), 'unresolved OneDrive conflict must block automatic save');\nok(app.includes(\"COMPANION_BACKUP_PREFIX='heldenmobil:backup:v1:'\"), 'local companion snapshot storage missing');\nok(index.includes('id=\"backupRestore\"') && index.includes('id=\"backupExport\"'), 'backup restore/export UI missing');\nok(app.includes('Letzter erfolgreicher OneDrive-Sync:'), 'last successful sync timestamp missing');\n"
s=replace_once(s,needle,extra,'smoke backup assertions')
s=s.replace("console.log('HeldenMobil v20.3 smoke tests passed');","console.log('HeldenMobil v20.3.1 smoke tests passed');")
p.write_text(s,encoding='utf-8')

# --- core tests -----------------------------------------------------------
p=ROOT/'tests/core.mjs';s=p.read_text(encoding='utf-8')
needle="eq(companion.decideCloudWrite({force:true,remoteExists:true,currentEtag:'B',baselineEtag:'A'}),'write','explicit force overwrite');\n"
extra=needle+"const snapshots=Array.from({length:12},(_,i)=>({id:`s${i}`,at:new Date(Date.parse('2026-08-31T08:00:00Z')+i*60000).toISOString(),data:{heroKey:'h',updatedAt:String(i)}}));const trimmed=companion.normalizeSnapshotList(snapshots,10);eq([trimmed.length,trimmed[0].id,trimmed.at(-1).id],[10,'s11','s2'],'snapshot history keeps newest ten');eq(companion.addSnapshot(trimmed,{id:'s12',at:'2026-08-31T08:12:00Z',data:{heroKey:'h'}},10)[0].id,'s12','new snapshot becomes newest');\n"
s=replace_once(s,needle,extra,'core snapshot tests')
s=s.replace("console.log('HeldenMobil v20.1-v20.3 core regression tests passed');","console.log('HeldenMobil v20.1-v20.3.1 core regression tests passed');")
p.write_text(s,encoding='utf-8')

# --- changelog ------------------------------------------------------------
p=ROOT/'CHANGELOG.md';s=p.read_text(encoding='utf-8')
head="# Changelog\n\n"
entry="""# Changelog

## v20.3.1

- Bis zu 10 automatische lokale Sicherungsstände je Held ergänzt; vor Änderungen wird der vorherige persistierte Stand gesichert.
- Sicherungen können in der Oberfläche manuell erzeugt, wiederhergestellt und als JSON exportiert werden.
- Ein vollständiges Zurücksetzen legt vorher zwingend eine lokale Sicherung an.
- Bei knappem Browser-Speicher werden zuerst alte Sicherungen verworfen, bevor ein aktueller Spielstand verloren gehen kann.
- Zeitpunkt des letzten erfolgreichen OneDrive-Syncs ist in den Daten- und Sync-Informationen sichtbar.

"""
s=replace_once(s,head,entry,'changelog entry')
p.write_text(s,encoding='utf-8')

# --- readme ---------------------------------------------------------------
p=ROOT/'README.md';s=p.read_text(encoding='utf-8')
s=s.replace('## Quellstruktur ab v20.3','## Quellstruktur ab v20.3.1',1)
s=s.replace('## Stabilisierung v20.1 bis v20.3','## Stabilisierung v20.1 bis v20.3.1',1)
needle='- **v20.3:** bestehende Kampfberechnung in ein testbares Core-Modul verschoben; Wundereignisse bleiben manuell, passive magische Wirkungen sind nicht auslösbar, destruktive Magie-Aktionen sind bestätigt, Zauberliste nutzt die generische Einklapplogik.\n'
extra=needle+'- **v20.3.1:** lokale Sicherungshistorie mit Wiederherstellung/Export ergänzt und letzten erfolgreichen OneDrive-Sync sichtbar gemacht.\n'
s=replace_once(s,needle,extra,'readme v20.3.1')
p.write_text(s,encoding='utf-8')

print('v20.3.1 data safety migration applied')
