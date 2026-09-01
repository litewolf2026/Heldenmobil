from pathlib import Path


def read(path):
    return Path(path).read_text(encoding='utf-8')


def write(path, text):
    Path(path).write_text(text, encoding='utf-8')


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'missing marker: {label}')
    if text.count(old) != 1:
        raise SystemExit(f'non-unique marker: {label} ({text.count(old)})')
    return text.replace(old, new, 1)


# --- app.js: move backup history from localStorage to IndexedDB, keep current companion sync-compatible ---
app = read('js/app.js')
start_marker = "  const COMPANION_BACKUP_PREFIX='heldenmobil:backup:v1:',COMPANION_BACKUP_LIMIT=10;"
end_marker = "  function loadCompanionForHero(){"
start = app.find(start_marker)
end = app.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit('backup block markers not found')

backup_block = r'''  const COMPANION_BACKUP_LEGACY_PREFIX='heldenmobil:backup:v1:',COMPANION_BACKUP_LIMIT=5,COMPANION_BACKUP_DB='HeldenMobilBackups',COMPANION_BACKUP_STORE='snapshots';
  let backupDbPromise=null,backupWriteQueue=Promise.resolve(),backupStorageMode='IndexedDB';
  const backupMigrationByHero=new Map();
  function companionBackupLegacyKey(heroKey=state.current?.key){return COMPANION_BACKUP_LEGACY_PREFIX+String(heroKey||'unknown');}
  function openCompanionBackupDb(){
    if(backupDbPromise)return backupDbPromise;
    backupDbPromise=new Promise((resolve,reject)=>{
      if(!('indexedDB' in window)){reject(new Error('IndexedDB ist in diesem Browser nicht verfügbar.'));return;}
      const req=indexedDB.open(COMPANION_BACKUP_DB,1);
      req.onupgradeneeded=()=>{const db=req.result;if(!db.objectStoreNames.contains(COMPANION_BACKUP_STORE)){const store=db.createObjectStore(COMPANION_BACKUP_STORE,{keyPath:'id'});store.createIndex('heroKey','heroKey',{unique:false});}};
      req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error||new Error('IndexedDB konnte nicht geöffnet werden.'));req.onblocked=()=>reject(new Error('IndexedDB-Aktualisierung ist blockiert.'));
    });
    return backupDbPromise;
  }
  async function indexedBackupList(heroKey){
    const db=await openCompanionBackupDb(),key=String(heroKey||'unknown');
    return new Promise((resolve,reject)=>{const tx=db.transaction(COMPANION_BACKUP_STORE,'readonly'),req=tx.objectStore(COMPANION_BACKUP_STORE).index('heroKey').getAll(IDBKeyRange.only(key));req.onsuccess=()=>resolve(req.result||[]);req.onerror=()=>reject(req.error||new Error('Sicherungen konnten nicht gelesen werden.'));});
  }
  async function indexedBackupReplace(heroKey,list){
    const db=await openCompanionBackupDb(),key=String(heroKey||'unknown'),safe=HeldenMobilCompanion.normalizeSnapshotList(list,COMPANION_BACKUP_LIMIT).map(x=>({...x,heroKey:key}));
    return new Promise((resolve,reject)=>{const tx=db.transaction(COMPANION_BACKUP_STORE,'readwrite'),store=tx.objectStore(COMPANION_BACKUP_STORE),req=store.index('heroKey').getAllKeys(IDBKeyRange.only(key));req.onsuccess=()=>{for(const id of (req.result||[]))store.delete(id);for(const snap of safe)store.put(snap);};req.onerror=()=>tx.abort();tx.oncomplete=()=>resolve(safe);tx.onerror=()=>reject(tx.error||new Error('Sicherungen konnten nicht geschrieben werden.'));tx.onabort=()=>reject(tx.error||new Error('Sicherungsvorgang wurde abgebrochen.'));});
  }
  function legacyBackupList(heroKey=state.current?.key){try{return HeldenMobilCompanion.normalizeSnapshotList(JSON.parse(localStorage.getItem(companionBackupLegacyKey(heroKey))||'[]'),COMPANION_BACKUP_LIMIT);}catch(_){return [];}}
  function storeLegacyBackupList(list,heroKey=state.current?.key){const safe=HeldenMobilCompanion.normalizeSnapshotList(list,COMPANION_BACKUP_LIMIT),key=companionBackupLegacyKey(heroKey);try{if(safe.length)localStorage.setItem(key,JSON.stringify(safe));else localStorage.removeItem(key);return safe;}catch(e){console.warn('Fallback-Sicherungen konnten nicht gespeichert werden',e);return [];}}
  function ensureBackupMigration(heroKey=state.current?.key){
    const key=String(heroKey||'unknown');if(backupMigrationByHero.has(key))return backupMigrationByHero.get(key);
    const job=(async()=>{const legacy=legacyBackupList(key);if(!legacy.length)return;try{let merged=await indexedBackupList(key);for(const snap of legacy)merged=HeldenMobilCompanion.addSnapshot(merged,{...snap,heroKey:key},COMPANION_BACKUP_LIMIT);await indexedBackupReplace(key,merged);localStorage.removeItem(companionBackupLegacyKey(key));backupStorageMode='IndexedDB';}catch(e){backupStorageMode='localStorage-Fallback';console.warn('Alte Sicherungen bleiben im localStorage, weil IndexedDB nicht verfügbar ist',e);}})();
    backupMigrationByHero.set(key,job);return job;
  }
  async function loadCompanionBackups(heroKey=state.current?.key){
    const key=String(heroKey||'unknown');await ensureBackupMigration(key);try{const list=await indexedBackupList(key);backupStorageMode='IndexedDB';return HeldenMobilCompanion.normalizeSnapshotList(list,COMPANION_BACKUP_LIMIT);}catch(e){backupStorageMode='localStorage-Fallback';console.warn('IndexedDB-Sicherungen nicht verfügbar; nutze localStorage-Fallback',e);return legacyBackupList(key);}
  }
  async function storeCompanionBackups(list,heroKey=state.current?.key){
    const key=String(heroKey||'unknown'),safe=HeldenMobilCompanion.normalizeSnapshotList(list,COMPANION_BACKUP_LIMIT);try{const stored=await indexedBackupReplace(key,safe);localStorage.removeItem(companionBackupLegacyKey(key));backupStorageMode='IndexedDB';return stored;}catch(e){backupStorageMode='localStorage-Fallback';console.warn('IndexedDB-Sicherung fehlgeschlagen; nutze localStorage-Fallback',e);return storeLegacyBackupList(safe,key);}
  }
  function createCompanionSnapshot(data=companionState.data,reason='Automatisch',force=false){
    if(!data||!state.current?.key)return Promise.resolve(false);const heroKey=String(state.current.key);let copy;try{copy=JSON.parse(JSON.stringify(data));}catch(e){console.warn('Sicherung konnte nicht erstellt werden',e);return Promise.resolve(false);}
    backupWriteQueue=backupWriteQueue.catch(()=>false).then(async()=>{try{let list=await loadCompanionBackups(heroKey);if(!force&&list[0]){try{if(JSON.stringify(list[0].data)===JSON.stringify(copy))return false;}catch(_){}}
      const snap={id:uid('backup'),heroKey,at:new Date().toISOString(),reason:String(reason||'Automatisch'),updatedAt:copy.updatedAt||null,data:copy};list=await storeCompanionBackups(HeldenMobilCompanion.addSnapshot(list,snap,COMPANION_BACKUP_LIMIT),heroKey);if(state.current?.key===heroKey)void renderBackupControls();return list.some(x=>x.id===snap.id);}catch(e){console.warn('Sicherung konnte nicht gespeichert werden',e);return false;}});
    return backupWriteQueue;
  }
  function writeCompanionLocal(key,value){try{localStorage.setItem(key,value);return true;}catch(e){console.error('Begleitdaten konnten lokal nicht gespeichert werden',e);alert('Der lokale Browser-Speicher ist voll. Bitte Begleitdaten als JSON exportieren und Browser-Speicher prüfen.');return false;}}
  function saveCompanion(opts={}){
    if(!companionState.data)return;const key=companionStorageKey();let previous=null;try{const raw=localStorage.getItem(key);if(raw)previous=JSON.parse(raw);}catch(_){}
    if(opts.snapshot!==false&&previous){try{if(JSON.stringify(previous)!==JSON.stringify(companionState.data))void createCompanionSnapshot(previous,opts.snapshotReason||'Vor Änderung');}catch(_){}}
    if(opts.touch!==false)companionState.data.updatedAt=new Date().toISOString();if(!writeCompanionLocal(key,JSON.stringify(companionState.data)))return;companionState.localExists=true;renderDataMeta();renderDashboard();if(!opts.skipCloud)cloudScheduleSave();
  }
  async function selectedCompanionBackup(){const id=$('#backupSelect')?.value;if(!id)return null;return (await loadCompanionBackups()).find(x=>x.id===id)||null;}
  async function renderBackupControls(){
    const select=$('#backupSelect'),count=$('#backupCount'),heroKey=state.current?.key;if(!select||!count||!heroKey)return;const list=await loadCompanionBackups(heroKey);if(state.current?.key!==heroKey)return;count.textContent=`${list.length}/${COMPANION_BACKUP_LIMIT} Stände · ${backupStorageMode}`;select.innerHTML=list.length?list.map(x=>`<option value="${esc(x.id)}">${esc(new Date(x.at).toLocaleString('de-DE'))} · ${esc(x.reason||'Sicherung')} · ${Number(x.data?.adventures?.length||0)} Abenteuer</option>`).join(''):'<option value="">Noch keine Sicherung</option>';const disabled=!list.length;$('#backupRestore').disabled=disabled;$('#backupExport').disabled=disabled;
  }
  function backupMessage(text,type=''){const el=$('#backupMessage');if(!el)return;el.textContent=text||'';el.className=`cloud-message ${type}`;}
  async function backupNow(){const ok=await createCompanionSnapshot(companionState.data,'Manuell',true);backupMessage(ok?'Lokale Sicherung erstellt.':'Sicherung konnte nicht erstellt werden.',ok?'ok':'error');}
  async function restoreCompanionBackup(){const snap=await selectedCompanionBackup();if(!snap)return;if(!confirm(`Lokale Sicherung vom ${new Date(snap.at).toLocaleString('de-DE')} wiederherstellen? Der aktuelle Stand wird vorher ebenfalls gesichert.`))return;const protectedNow=await createCompanionSnapshot(companionState.data,'Vor Wiederherstellung',true);if(!protectedNow){backupMessage('Wiederherstellung abgebrochen: Der aktuelle Stand konnte vorher nicht gesichert werden.','error');return;}companionState.data=normalizeCompanion(snap.data);saveCompanion({snapshot:false});renderCompanionAll();backupMessage('Sicherung wiederhergestellt.','ok');}
  async function exportCompanionBackup(){const snap=await selectedCompanionBackup();if(!snap)return;const blob=new Blob([JSON.stringify(snap.data,null,2)],{type:'application/json'}),a=document.createElement('a'),stamp=String(snap.at||'').replace(/[:.]/g,'-');a.href=URL.createObjectURL(blob);a.download=`HeldenMobil-${(snap.data?.heroName||'Held').replace(/[^a-z0-9äöüß_-]+/gi,'_')}-Sicherung-${stamp}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
'''
app = app[:start] + backup_block + app[end:]

old_render_all = "  function renderCompanionAll(){renderStatus();renderAdventures();renderAdvancement();renderInventory();renderMoney();renderMagic();renderDataMeta();refreshAdventureSelectors();refreshWishTargets();if(state.current){renderCombat();renderLiturgies();}renderDashboard();}"
new_render_all = "  function renderCompanionAll(){renderStatus();renderAdventures();renderAdvancement();renderInventory();renderMoney();renderMagic();renderDataMeta();void renderBackupControls();refreshAdventureSelectors();refreshWishTargets();if(state.current){renderCombat();renderLiturgies();}renderDashboard();}"
app = replace_once(app, old_render_all, new_render_all, 'renderCompanionAll')

# Make destructive reset wait for a confirmed IndexedDB snapshot first.
lines = app.splitlines()
reset_found = False
for i, line in enumerate(lines):
    if "$('#resetCompanion').addEventListener('click',()=>{" in line:
        reset_found = True
        indent = line[:len(line)-len(line.lstrip())]
        lines[i] = indent + "$('#resetCompanion').addEventListener('click',async()=>{if(!confirm(`Begleitdaten für ${state.current?.name||'diesen Helden'} wirklich vollständig zurücksetzen?`))return;const protectedNow=await createCompanionSnapshot(companionState.data,'Vor Zurücksetzen',true);if(!protectedNow){backupMessage('Zurücksetzen abgebrochen: Der aktuelle Stand konnte nicht gesichert werden.','error');return;}localStorage.removeItem(companionStorageKey());localStorage.removeItem(companionStorageKey(6));localStorage.removeItem(companionStorageKey(5));localStorage.removeItem(companionStorageKey(4));localStorage.removeItem(companionStorageKey(3));localStorage.removeItem(companionStorageKey(2));localStorage.removeItem(companionStorageKey(1));companionState.data=emptyCompanion();saveCompanion({snapshot:false});renderCompanionAll();});"
        break
if not reset_found:
    raise SystemExit('reset listener marker not found')
app = '\n'.join(lines) + ('\n' if app.endswith('\n') else '')
app = app.replace("lastQualityAudit={version:'20.3.1'", "lastQualityAudit={version:'20.3.2'")
write('js/app.js', app)

# --- companion core: five snapshots is now the safe default ---
core = read('js/companion-core.js')
core = replace_once(core, 'function normalizeSnapshotList(raw,max=10){\n    const limit=Math.max(1,Math.floor(Number(max)||10));', 'function normalizeSnapshotList(raw,max=5){\n    const limit=Math.max(1,Math.floor(Number(max)||5));', 'snapshot default limit')
core = replace_once(core, 'function addSnapshot(raw,snapshot,max=10){', 'function addSnapshot(raw,snapshot,max=5){', 'addSnapshot default limit')
write('js/companion-core.js', core)

# --- index UI/version ---
index = read('index.html').replace('20.3.1', '20.3.2')
index = replace_once(index, 'id="backupCount" class="count">0/10 Stände</span>', 'id="backupCount" class="count">0/5 Stände</span>', 'backup count')
index = replace_once(index, 'HeldenMobil hält bis zu 10 ältere Stände dieses Helden im Browser. Sie schützen vor versehentlichen Änderungen, aber nicht vor dem Löschen der Browserdaten – dafür eine Sicherung zusätzlich als JSON exportieren.', 'HeldenMobil hält bis zu 5 ältere Stände dieses Helden in IndexedDB. Das entlastet den knappen localStorage und schützt vor versehentlichen Änderungen, aber nicht vor dem Löschen der Browserdaten – dafür eine Sicherung zusätzlich als JSON exportieren.', 'backup explanation')
write('index.html', index)

# --- tests ---
smoke = read('tests/smoke.mjs').replace('20.3.1', '20.3.2')
smoke = replace_once(smoke, "ok(app.includes(\"COMPANION_BACKUP_PREFIX='heldenmobil:backup:v1:'\"), 'local companion snapshot storage missing');", "ok(app.includes(\"COMPANION_BACKUP_DB='HeldenMobilBackups'\") && app.includes('indexedDB.open'), 'IndexedDB companion snapshot storage missing');\nok(app.includes('COMPANION_BACKUP_LIMIT=5'), 'backup history must be limited to five snapshots');", 'smoke backup storage check')
write('tests/smoke.mjs', smoke)

core_test = read('tests/core.mjs')
old_snapshot_test = "const snapshots=Array.from({length:12},(_,i)=>({id:`s${i}`,at:new Date(Date.parse('2026-08-31T08:00:00Z')+i*60000).toISOString(),data:{heroKey:'h',updatedAt:String(i)}}));const trimmed=companion.normalizeSnapshotList(snapshots,10);eq([trimmed.length,trimmed[0].id,trimmed.at(-1).id],[10,'s11','s2'],'snapshot history keeps newest ten');eq(companion.addSnapshot(trimmed,{id:'s12',at:'2026-08-31T08:12:00Z',data:{heroKey:'h'}},10)[0].id,'s12','new snapshot becomes newest');"
new_snapshot_test = "const snapshots=Array.from({length:12},(_,i)=>({id:`s${i}`,at:new Date(Date.parse('2026-08-31T08:00:00Z')+i*60000).toISOString(),data:{heroKey:'h',updatedAt:String(i)}}));const trimmed=companion.normalizeSnapshotList(snapshots,5);eq([trimmed.length,trimmed[0].id,trimmed.at(-1).id],[5,'s11','s7'],'snapshot history keeps newest five');eq(companion.addSnapshot(trimmed,{id:'s12',at:'2026-08-31T08:12:00Z',data:{heroKey:'h'}},5)[0].id,'s12','new snapshot becomes newest');eq(companion.normalizeSnapshotList(snapshots).length,5,'snapshot default limit is five');"
core_test = replace_once(core_test, old_snapshot_test, new_snapshot_test, 'core snapshot test')
core_test = core_test.replace('v20.1-v20.3.1 core regression tests passed', 'v20.1-v20.3.2 core regression tests passed')
write('tests/core.mjs', core_test)

# --- package/readme/changelog ---
package = read('package.json')
package = replace_once(package, '"version": "20.3.1"', '"version": "20.3.2"', 'package version')
write('package.json', package)

readme = read('README.md')
readme = readme.replace('## Quellstruktur ab v20.3.1', '## Quellstruktur ab v20.3.2').replace('## Stabilisierung v20.1 bis v20.3.1', '## Stabilisierung v20.1 bis v20.3.2')
anchor = '- **v20.3.1:** lokale Sicherungshistorie mit Wiederherstellung/Export ergänzt und letzten erfolgreichen OneDrive-Sync sichtbar gemacht.\n'
if anchor not in readme:
    raise SystemExit('README v20.3.1 anchor missing')
readme = readme.replace(anchor, anchor + '- **v20.3.2:** Backup-Historie auf fünf Stände begrenzt und aus `localStorage` in IndexedDB verschoben; bestehende v20.3.1-Sicherungen werden beim ersten Zugriff automatisch übernommen.\n', 1)
write('README.md', readme)

changelog = read('CHANGELOG.md')
entry = '''## v20.3.2\n\n- Lokale Sicherungshistorie pro Held von 10 auf 5 Stände reduziert.\n- Sicherungsstände in IndexedDB verschoben; der aktuelle Companion-Datensatz bleibt für die stabile v1-Endphase weiterhin im bewährten `localStorage`.\n- Bestehende v20.3.1-Sicherungen werden beim ersten Zugriff automatisch nach IndexedDB migriert und auf die fünf neuesten Stände begrenzt.\n- Falls IndexedDB nicht verfügbar ist, bleibt ein auf fünf Stände begrenzter `localStorage`-Fallback aktiv.\n- Wiederherstellen und vollständiges Zurücksetzen brechen ab, wenn der aktuelle Stand vorher nicht erfolgreich gesichert werden konnte.\n\n'''
if '## v20.3.2' in changelog:
    raise SystemExit('changelog already contains v20.3.2')
changelog = changelog.replace('# Changelog\n\n', '# Changelog\n\n' + entry, 1)
write('CHANGELOG.md', changelog)

print('v20.3.2 IndexedDB backup migration applied')
