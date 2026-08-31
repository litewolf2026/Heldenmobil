from pathlib import Path
import re

ROOT = Path('.')
app_path = ROOT / 'js' / 'app.js'
index_path = ROOT / 'index.html'
package_path = ROOT / 'package.json'
readme_path = ROOT / 'README.md'
tests_path = ROOT / 'tests' / 'smoke.mjs'

app = app_path.read_text(encoding='utf-8')
index = index_path.read_text(encoding='utf-8')
package = package_path.read_text(encoding='utf-8')


def require_once(text, needle, label):
    count = text.count(needle)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one occurrence, got {count}')


def replace_once(text, old, new, label):
    require_once(text, old, label)
    return text.replace(old, new, 1)

# ---------------------------------------------------------------------------
# v20.1 - HLD parser module
# ---------------------------------------------------------------------------
start = app.index('  const BASIC_BLESSING_NAMES=')
primary_start = app.index('  function primaryLiturgyKnowledge()', start)
parse_start = app.index('  function parseHero(hero)', primary_start)
prop_start = app.index('  function propMap(props)', parse_start)

hld_head = app[start:primary_start]
primary_fn = app[primary_start:parse_start]
hld_parser_block = app[parse_start:prop_start]

hld_module = """(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.HeldenMobilHld=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  function createParser(deps={}){
    const {direct,directAll,attr,num,cleanName,talentCategory,buildMetaTalents,directSelections,isDisadvantage,sfEntryFromElement}=deps;
""" + hld_head + hld_parser_block + """
    return {parseHero,parseItem,findItem,parseEquipmentEntry,parseLiturgySfName,liturgyKnowledgeDeity};
  }
  return {createParser};
});
"""

hld_delegate = """  const hldParser=HeldenMobilHld.createParser({direct,directAll,attr,num,cleanName,talentCategory,buildMetaTalents,directSelections,isDisadvantage,sfEntryFromElement});
  const parseLiturgySfName=hldParser.parseLiturgySfName;
  const liturgyKnowledgeDeity=hldParser.liturgyKnowledgeDeity;
""" + primary_fn + """  const parseHero=hldParser.parseHero;
  const parseItem=hldParser.parseItem;
  const findItem=hldParser.findItem;
  const parseEquipmentEntry=hldParser.parseEquipmentEntry;

"""
app = app[:start] + hld_delegate + app[prop_start:]
(ROOT / 'js' / 'hld-parser.js').write_text(hld_module, encoding='utf-8')

# ---------------------------------------------------------------------------
# v20.2 - Companion/adventure core + sync decision layer
# ---------------------------------------------------------------------------
companion_module = r"""(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.HeldenMobilCompanion=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const WOUND_ZONE_KEYS=['kopf','brust','ruecken','bauch','linkerarm','rechterarm','linkesbein','rechtesbein'];

  function blankWoundZones(){return {kopf:0,brust:0,ruecken:0,bauch:0,linkerarm:0,rechterarm:0,linkesbein:0,rechtesbein:0,unassigned:0};}
  function normalizeStatusWounds(status){
    if(!status||typeof status!=='object')return status;
    const raw=(status.woundZones&&typeof status.woundZones==='object')?status.woundZones:{};
    const zones=blankWoundZones();for(const k of WOUND_ZONE_KEYS)zones[k]=Math.max(0,Math.min(3,Math.floor(Number(raw[k]||0))));
    const zoned=WOUND_ZONE_KEYS.reduce((a,k)=>a+zones[k],0),oldTotal=Math.max(0,Math.floor(Number(status.wounds||0)));
    zones.unassigned=Math.max(0,Math.floor(Number(raw.unassigned??Math.max(0,oldTotal-zoned))||0));
    if(zoned+zones.unassigned<oldTotal)zones.unassigned+=oldTotal-(zoned+zones.unassigned);
    status.woundZones=zones;status.wounds=zoned+zones.unassigned;return status;
  }
  function magicOptionalInt(v){if(v===null||v===undefined||v==='')return null;const n=Math.floor(Number(v));return Number.isFinite(n)?Math.max(0,n):null;}
  function magicOptionalNumber(v){if(v===null||v===undefined||v==='')return null;const n=Number(v);return Number.isFinite(n)?n:null;}
  function fallbackUid(prefix='id'){return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,8)}`;}
  function normalizeMagicEffect(raw,index=0,uid=fallbackUid){const r=raw&&typeof raw==='object'?raw:{},max=magicOptionalInt(r.maxCharges);let charges=magicOptionalInt(r.charges);if(max!=null){if(charges==null)charges=max;charges=Math.min(max,charges);}else charges=null;return {id:String(r.id||uid('effect')),name:String(r.name||`Wirkung ${index+1}`),type:String(r.type||'Zauber'),activation:String(r.activation||''),charges,maxCharges:max,zfp:magicOptionalNumber(r.zfp),asp:magicOptionalNumber(r.asp),recharge:String(r.recharge||''),note:String(r.note||'')};}
  function normalizeInventoryMagic(it,uid=fallbackUid){if(!it||typeof it!=='object')return it;const out={...it};if(out.magic&&typeof out.magic==='object'){const m=out.magic;out.magic={kind:String(m.kind||'Artefakt'),effects:(Array.isArray(m.effects)?m.effects:[]).map((x,i)=>normalizeMagicEffect(x,i,uid))};}return out;}

  function energyEventText(label,from,to){const delta=Number(to)-Number(from),signed=delta>0?`+${delta}`:`${delta}`;return `${label} ${signed} · ${from} → ${to}`;}
  function parseLegacyEnergyEvent(raw){
    if(!raw||typeof raw!=='object')return null;
    if(raw.type==='energy'&&raw.energy&&Number.isFinite(Number(raw.from))&&Number.isFinite(Number(raw.to))){const e={...raw,from:Number(raw.from),to:Number(raw.to)};e.delta=e.to-e.from;e.startedAt=e.startedAt||e.at||e.lastAt||null;e.lastAt=e.lastAt||e.at||e.startedAt||null;e.text=energyEventText(e.energy,e.from,e.to);return e;}
    if(raw.type!=='status')return null;
    const m=/^(LeP|AuP|AsP|KaP)\s+[+-]?\d+:\s*(-?\d+)\s*→\s*(-?\d+)\s*$/.exec(String(raw.text||''));if(!m)return null;
    const e={...raw,type:'energy',energy:m[1],from:Number(m[2]),to:Number(m[3])};e.delta=e.to-e.from;e.startedAt=e.at||null;e.lastAt=e.at||null;e.text=energyEventText(e.energy,e.from,e.to);return e;
  }
  function normalizeAdventureEvents(events,windowMs=25000){
    const out=[],lastByEnergy=new Map();
    for(const raw of (Array.isArray(events)?events:[])){
      const e=parseLegacyEnergyEvent(raw);if(!e){out.push(raw);continue;}
      const nowMs=Date.parse(e.lastAt||e.at||'')||0,prev=lastByEnergy.get(e.energy),prevMs=prev?(Date.parse(prev.lastAt||prev.at||'')||0):0;
      if(prev&&nowMs&&prevMs&&nowMs>=prevMs&&nowMs-prevMs<=windowMs&&Number(prev.to)===Number(e.from)){
        prev.to=e.to;prev.delta=prev.to-prev.from;prev.lastAt=e.lastAt||e.at||prev.lastAt;prev.at=e.at||prev.at;prev.text=energyEventText(prev.energy,prev.from,prev.to);
        const idx=out.indexOf(prev);if(idx>=0)out.splice(idx,1);if(prev.delta!==0){out.push(prev);lastByEnergy.set(prev.energy,prev);}else lastByEnergy.delete(prev.energy);continue;
      }
      if(e.delta!==0){out.push(e);lastByEnergy.set(e.energy,e);}
    }
    return out;
  }
  function mergeEnergyEvent(events,label,before,after,{nowMs=Date.now(),uid=fallbackUid,windowMs=25000}={}){
    before=Number(before);after=Number(after);const out=Array.isArray(events)?events.slice():[];if(before===after)return out;const now=new Date(nowMs).toISOString();let found=-1,event=null;
    for(let i=out.length-1;i>=0;i--){const parsed=parseLegacyEnergyEvent(out[i]);if(!parsed||parsed.energy!==label)continue;const lastMs=Date.parse(parsed.lastAt||parsed.at||'')||0;if(lastMs&&nowMs>=lastMs&&nowMs-lastMs<=windowMs&&Number(parsed.to)===before){found=i;event=parsed;}break;}
    if(found>=0&&event){out.splice(found,1);event.to=after;event.delta=event.to-event.from;event.lastAt=now;event.at=now;event.text=energyEventText(label,event.from,event.to);if(event.delta!==0)out.push(event);return out;}
    out.push({id:uid('evt'),at:now,lastAt:now,startedAt:now,type:'energy',energy:label,from:before,to:after,delta:after-before,text:energyEventText(label,before,after)});return out;
  }

  function normalizeCompanionData(d,{base,heroKey,heroName,schemaVersion=8,freshAdventureStatus,uid=fallbackUid,energyWindowMs=25000}){
    if(!d||typeof d!=='object')return base;
    const legacyStatus=d.status&&typeof d.status==='object'?d.status:null;
    const x={...base,...d,favorites:{...base.favorites,...(d.favorites||{})},inventory:{...base.inventory,...(d.inventory||{})},money:{...base.money,...(d.money||{})},magic:{...base.magic,...(d.magic||{})}};
    x.heroKey=heroKey;x.heroName=heroName;x.schemaVersion=schemaVersion;
    x.adventures=Array.isArray(x.adventures)?x.adventures:[];x.advancement=Array.isArray(x.advancement)?x.advancement:[];
    x.adventures=x.adventures.map(a=>{const status={...freshAdventureStatus(),...(a.status||{})};normalizeStatusWounds(status);return {...a,events:normalizeAdventureEvents(a.events,energyWindowMs),learning:Array.isArray(a.learning)?a.learning:[],combatBySet:(a.combatBySet&&typeof a.combatBySet==='object')?a.combatBySet:{},status};});
    if(legacyStatus&&x.adventures.length){const target=x.adventures.find(a=>a.id===x.activeAdventureId)||x.adventures[0];target.status={...target.status,...legacyStatus};normalizeStatusWounds(target.status);if(!x.activeAdventureId)x.activeAdventureId=target.id;}
    delete x.status;
    x.inventory.locations=Array.isArray(x.inventory.locations)&&x.inventory.locations.length?x.inventory.locations:base.inventory.locations;
    x.inventory.items=Array.isArray(x.inventory.items)?x.inventory.items.map(it=>normalizeInventoryMagic(it,uid)):[];
    x.money.transactions=Array.isArray(x.money.transactions)?x.money.transactions:[];x.magic.staffSlots=Array.isArray(x.magic.staffSlots)?x.magic.staffSlots:[];
    x.favorites.talents=Array.isArray(x.favorites.talents)?[...new Set(x.favorites.talents.map(String).filter(Boolean))]:[];
    x.favorites.spells=Array.isArray(x.favorites.spells)?[...new Set(x.favorites.spells.map(String).filter(Boolean))]:[];
    x.favorites.liturgies=Array.isArray(x.favorites.liturgies)?[...new Set(x.favorites.liturgies.map(String).filter(Boolean))]:[];
    delete x.magic.artifacts;return x;
  }

  function timeValue(x){const n=Date.parse(x||'');return Number.isFinite(n)?n:0;}
  function decideInitialSync({localExists=false,localUpdatedAt=null,remoteUpdatedAt=null,remoteEtag=null,baseline=null}={}){
    if(!localExists)return 'remote';
    if(baseline&&baseline.eTag){
      const remoteChanged=!!remoteEtag&&remoteEtag!==baseline.eTag;
      const baseLocal=timeValue(baseline.localUpdatedAt),local=timeValue(localUpdatedAt),localChanged=baseLocal?local!==baseLocal:false;
      if(remoteChanged&&localChanged)return 'conflict';
      if(remoteChanged)return 'remote';
      if(localChanged)return 'local';
      return 'equal';
    }
    const rt=timeValue(remoteUpdatedAt),lt=timeValue(localUpdatedAt);if(rt>lt)return 'remote';if(lt>rt)return 'local';return 'equal';
  }
  function decideCloudWrite({force=false,remoteExists=false,currentEtag=null,knownEtag=null,baselineEtag=null}={}){
    if(force)return 'write';const reference=knownEtag||baselineEtag||null;
    if(remoteExists&&reference&&currentEtag&&currentEtag!==reference)return 'conflict';
    if(remoteExists&&!reference)return 'unknown-remote';return 'write';
  }

  return {WOUND_ZONE_KEYS,blankWoundZones,normalizeStatusWounds,magicOptionalInt,magicOptionalNumber,normalizeMagicEffect,normalizeInventoryMagic,energyEventText,parseLegacyEnergyEvent,normalizeAdventureEvents,mergeEnergyEvent,normalizeCompanionData,decideInitialSync,decideCloudWrite};
});
"""
(ROOT / 'js' / 'companion-core.js').write_text(companion_module, encoding='utf-8')

# Delegate wound helpers.
wound_start = app.index('  function blankWoundZones()')
storage_start = app.index('  function companionStorageKey', wound_start)
app = app[:wound_start] + """  const blankWoundZones=()=>HeldenMobilCompanion.blankWoundZones();
  function normalizeStatusWounds(status){return HeldenMobilCompanion.normalizeStatusWounds(status);}
""" + app[storage_start:]

# Delegate magic + full companion normalization.
magic_start = app.index('  function magicOptionalInt')
save_start = app.index('  function saveCompanion', magic_start)
app = app[:magic_start] + """  function magicOptionalInt(v){return HeldenMobilCompanion.magicOptionalInt(v);}
  function magicOptionalNumber(v){return HeldenMobilCompanion.magicOptionalNumber(v);}
  function normalizeMagicEffect(raw,index=0){return HeldenMobilCompanion.normalizeMagicEffect(raw,index,uid);}
  function normalizeInventoryMagic(it){return HeldenMobilCompanion.normalizeInventoryMagic(it,uid);}
  function normalizeCompanion(d){return HeldenMobilCompanion.normalizeCompanionData(d,{base:emptyCompanion(),heroKey:state.current.key,heroName:state.current.name,schemaVersion:COMP_SCHEMA,freshAdventureStatus,uid,energyWindowMs:ENERGY_EVENT_WINDOW_MS});}
""" + app[save_start:]

# Persist normalized/migrated legacy payloads immediately without touching updatedAt.
load_start = app.index('  function loadCompanionForHero()')
render_all_start = app.index('  function renderCompanionAll()', load_start)
load_fn = """  function loadCompanionForHero(){
    let d=null,migrated=false,raw=null;try{raw=localStorage.getItem(companionStorageKey());if(!raw){for(const v of [7,6,5,4,3,2,1]){raw=localStorage.getItem(companionStorageKey(v));if(raw){migrated=true;break;}}}if(raw)d=JSON.parse(raw);}catch(e){console.warn('Begleitdaten unlesbar',e);}
    companionState.localExists=!!raw;const normalized=normalizeCompanion(d);companionState.data=normalized;let normalizedChanged=false;if(raw){try{normalizedChanged=JSON.stringify(d)!==JSON.stringify(normalized);}catch(_){normalizedChanged=true;}}if(raw&&(migrated||normalizedChanged))saveCompanion({touch:false,skipCloud:true});renderTalents();renderCompanionAll();cloudOnHeroChanged();
  }
"""
app = app[:load_start] + load_fn + app[render_all_start:]

# Delegate energy event normalization/aggregation.
energy_start = app.index('  function energyEventText')
active_start = app.index('  function activeAdventure()', energy_start)
app = app[:energy_start] + """  function energyEventText(label,from,to){return HeldenMobilCompanion.energyEventText(label,from,to);}
  function parseLegacyEnergyEvent(raw){return HeldenMobilCompanion.parseLegacyEnergyEvent(raw);}
  function normalizeAdventureEvents(events){return HeldenMobilCompanion.normalizeAdventureEvents(events,ENERGY_EVENT_WINDOW_MS);}
""" + app[active_start:]
log_energy_start = app.index('  function logEnergyEvent(')
adjust_start = app.index('  function adjustStatus(', log_energy_start)
app = app[:log_energy_start] + """  function logEnergyEvent(label,before,after){const a=activeAdventure();if(!a||Number(before)===Number(after))return;a.events=HeldenMobilCompanion.mergeEnergyEvent(a.events,label,before,after,{nowMs:Date.now(),uid,windowMs:ENERGY_EVENT_WINDOW_MS});}
""" + app[adjust_start:]

# Wounds/status are user-managed events; only energy bundles are automatic.
app = replace_once(app, "  function automaticEvent(e){return e?.type==='energy'||e?.type==='status';}", "  function automaticEvent(e){return e?.type==='energy';}", 'automaticEvent')

# Persistent OneDrive baseline, so cross-device offline divergence fails closed.
baseline_marker = "  function cloudCompanionFileName(heroKey){"
baseline_insert = """  const CLOUD_SYNC_BASELINE_PREFIX='heldenmobil:onedrive:baseline:v1:';
  function cloudBaselineKey(heroKey){return CLOUD_SYNC_BASELINE_PREFIX+String(heroKey||'unknown');}
  function cloudLoadBaseline(heroKey){try{const x=JSON.parse(localStorage.getItem(cloudBaselineKey(heroKey))||'null');return x&&typeof x==='object'?x:null;}catch(_){return null;}}
  function cloudStoreBaseline(heroKey,meta,localUpdatedAt){if(!heroKey||!meta?.eTag)return;localStorage.setItem(cloudBaselineKey(heroKey),JSON.stringify({eTag:meta.eTag,localUpdatedAt:localUpdatedAt||null,syncedAt:new Date().toISOString()}));}

""" + baseline_marker
app = replace_once(app, baseline_marker, baseline_insert, 'cloud baseline insertion')

cloud_changed_start = app.index('  async function cloudOnHeroChanged()')
cloud_auto_start = app.index('  function cloudAutoSyncEnabled()', cloud_changed_start)
cloud_changed_fn = """  async function cloudOnHeroChanged(){
    const key=state.current?.key;if(!key||!cloudIsConnected()){cloudState.heroReadyKey=null;cloudRenderState();return;}const seq=key;cloudState.heroReadyKey=null;cloudMessage('Begleitdaten werden mit OneDrive abgeglichen …','','#cloudSyncMessage');
    try{const meta=await cloudCompanionMeta(key);if(state.current?.key!==seq)return;cloudSetRemote(key,meta);if(!meta){cloudState.heroReadyKey=key;cloudMessage(companionState.localExists?'Noch keine Cloud-Datei. Die nächste Änderung wird hochgeladen.':'Noch keine Cloud-Datei für diesen Helden.','ok','#cloudSyncMessage');if(cloudState.dirtyHeroes.has(key))cloudScheduleSave(true);return;}
      const remote=await cloudReadCompanion(key,meta);if(state.current?.key!==seq)return;const rd=normalizeCompanion(remote.data),rt=isoTime(rd.updatedAt),lt=isoTime(companionState.data?.updatedAt),baseline=cloudLoadBaseline(key),decision=HeldenMobilCompanion.decideInitialSync({localExists:companionState.localExists,localUpdatedAt:companionState.data?.updatedAt,remoteUpdatedAt:rd.updatedAt,remoteEtag:remote.meta?.eTag,baseline});cloudSetRemote(key,remote.meta);
      if(decision==='conflict'){cloudState.conflictHeroKey=key;cloudState.heroReadyKey=key;cloudRenderState();cloudMessage('Konflikt: Lokale Daten und OneDrive wurden seit dem letzten gemeinsamen Stand beide geändert. Keine Seite wurde überschrieben.','warn','#cloudSyncMessage');return;}
      if(decision==='remote'){companionState.data=rd;saveCompanion({touch:false,skipCloud:true});renderCompanionAll();cloudStoreBaseline(key,remote.meta,rd.updatedAt);cloudMessage('Neuere OneDrive-Version geladen.','ok','#cloudSyncMessage');}
      else if(decision==='local'){cloudMessage('Lokale Version ist neuer und wird nach OneDrive gespeichert.','warn','#cloudSyncMessage');cloudState.dirtyHeroes.add(key);}
      else{cloudStoreBaseline(key,remote.meta,companionState.data?.updatedAt);cloudMessage('Lokale Daten und OneDrive sind auf demselben Stand.','ok','#cloudSyncMessage');}
      cloudState.heroReadyKey=key;if(cloudState.dirtyHeroes.has(key))cloudScheduleSave(true);
    }catch(e){cloudState.heroReadyKey=key;cloudMessage(`OneDrive-Abgleich fehlgeschlagen: ${e.message}`,'error','#cloudSyncMessage');}
  }
"""
app = app[:cloud_changed_start] + cloud_changed_fn + app[cloud_auto_start:]

cloud_save_start = app.index('  async function cloudSaveCurrent(')
cloud_manual_start = app.index('  async function cloudLoadCurrentManual()', cloud_save_start)
cloud_save_fn = """  async function cloudSaveCurrent(force=false){
    const key=state.current?.key,d=companionState.data;if(!key||!d){return;}if(!cloudIsConnected()){cloudMessage('Nicht mit Microsoft verbunden.','warn','#cloudSyncMessage');return;}if(cloudState.saving)return;cloudState.saving=true;cloudMessage('Speichere Begleitdaten nach OneDrive …','','#cloudSyncMessage');
    try{const known=cloudState.remoteByHero.get(key)||null,baseline=cloudLoadBaseline(key),meta=await cloudCompanionMeta(key),decision=HeldenMobilCompanion.decideCloudWrite({force,remoteExists:!!meta,currentEtag:meta?.eTag||null,knownEtag:known?.eTag||null,baselineEtag:baseline?.eTag||null});if(decision==='conflict'){cloudSetRemote(key,meta);cloudState.conflictHeroKey=key;cloudRenderState();cloudMessage('Konflikt: Die OneDrive-Datei wurde auf einem anderen Gerät geändert.','warn','#cloudSyncMessage');return;}if(decision==='unknown-remote'){cloudSetRemote(key,meta);cloudState.conflictHeroKey=key;cloudRenderState();cloudMessage('Cloud-Datei existiert bereits. Bitte zuerst laden oder bewusst überschreiben.','warn','#cloudSyncMessage');return;}
      const body=JSON.stringify(d,null,2),path=meta?`/me/drive/items/${encodeURIComponent(meta.id)}/content`:`/me/drive/special/approot:/${encodeURIComponent(cloudCompanionFileName(key))}:/content`,r=await graphFetch(path,{method:'PUT',headers:{'Content-Type':'application/json; charset=utf-8'},body});if(!r.ok){let m=`Speichern fehlgeschlagen (${r.status})`;try{m=(await r.json()).error?.message||m;}catch(_){}throw new Error(m);}const saved=await r.json();cloudSetRemote(key,saved);cloudStoreBaseline(key,saved,d.updatedAt);cloudState.conflictHeroKey=null;cloudState.dirtyHeroes.delete(key);cloudState.heroReadyKey=key;cloudRenderState();cloudMessage(`In OneDrive gespeichert · ${new Date().toLocaleTimeString('de-DE',{hour:'2-digit',minute:'2-digit'})}`,'ok','#cloudSyncMessage');
    }catch(e){cloudMessage(e.message,'error','#cloudSyncMessage');}finally{cloudState.saving=false;}
  }
"""
app = app[:cloud_save_start] + cloud_save_fn + app[cloud_manual_start:]

# Manual remote load establishes a new common baseline.
old_manual = "  async function cloudLoadCurrentManual(){const key=state.current?.key;if(!key)return;try{const remote=await cloudReadCompanion(key);if(!remote){cloudMessage('Für diesen Helden gibt es noch keine OneDrive-Datei.','warn','#cloudSyncMessage');return;}companionState.data=normalizeCompanion(remote.data);saveCompanion({touch:false,skipCloud:true});cloudSetRemote(key,remote.meta);cloudState.conflictHeroKey=null;cloudState.heroReadyKey=key;cloudState.dirtyHeroes.delete(key);renderCompanionAll();cloudRenderState();cloudMessage('OneDrive-Version geladen.','ok','#cloudSyncMessage');}catch(e){cloudMessage(e.message,'error','#cloudSyncMessage');}}"
new_manual = "  async function cloudLoadCurrentManual(){const key=state.current?.key;if(!key)return;try{const remote=await cloudReadCompanion(key);if(!remote){cloudMessage('Für diesen Helden gibt es noch keine OneDrive-Datei.','warn','#cloudSyncMessage');return;}companionState.data=normalizeCompanion(remote.data);saveCompanion({touch:false,skipCloud:true});cloudSetRemote(key,remote.meta);cloudStoreBaseline(key,remote.meta,companionState.data?.updatedAt);cloudState.conflictHeroKey=null;cloudState.heroReadyKey=key;cloudState.dirtyHeroes.delete(key);renderCompanionAll();cloudRenderState();cloudMessage('OneDrive-Version geladen.','ok','#cloudSyncMessage');}catch(e){cloudMessage(e.message,'error','#cloudSyncMessage');}}"
app = replace_once(app, old_manual, new_manual, 'manual cloud baseline')

# ---------------------------------------------------------------------------
# v20.3 - Combat core + small safety/UI fixes
# ---------------------------------------------------------------------------
combat_module = r"""(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.HeldenMobilCombat=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  function combatEbe(talent,be,combatMeta={}){const m=combatMeta[talent];return m?Math.max(0,Number(be||0)-Number(m.offset||0)):Number(be||0);}
  function adjustCombatForBE(at,pa,ebe){const e=Number(ebe||0);return {at:Number(at)-Math.floor(e/2),pa:Number(pa)-Math.ceil(e/2)};}
  function finalDamage(tp,tpkk,kk){if(!tp)return null;const out=[...tp];if(tpkk){const [thr,step]=tpkk,delta=Number(kk||0)-Number(thr||0),s=Math.max(1,Number(step||1)),bonus=delta>=0?Math.floor(delta/s):-Math.ceil(Math.abs(delta)/s);out[2]=Number(out[2]||0)+bonus;}return out;}
  function clamp(n,min,max){return Math.max(min,Math.min(max,n));}
  function zoneFromD20(r){r=clamp(Math.round(Number(r)||1),1,20);if(r>=19)return {label:'Kopf',key:'kopf'};if(r>=15)return {label:'Brust',key:'brust'};if(r>=9)return r%2?{label:'Schildarm (links)',key:'linkerarm'}:{label:'Schwertarm (rechts)',key:'rechterarm'};if(r>=7)return {label:'Bauch',key:'bauch'};return r%2?{label:'linkes Bein',key:'linkesbein'}:{label:'rechtes Bein',key:'rechtesbein'};}
  return {combatEbe,adjustCombatForBE,finalDamage,zoneFromD20};
});
"""
(ROOT / 'js' / 'combat-core.js').write_text(combat_module, encoding='utf-8')

# Replace existing combat helpers with delegates, preserving behavior.
old_ebe = "  function combatEbe(talent,be){const m=COMBAT_META[talent];return m?Math.max(0,be-m.offset):be;}\n  function adjustCombatForBE(at,pa,ebe){return {at:at-Math.floor(ebe/2),pa:pa-Math.ceil(ebe/2)};}"
new_ebe = "  function combatEbe(talent,be){return HeldenMobilCombat.combatEbe(talent,be,COMBAT_META);}\n  function adjustCombatForBE(at,pa,ebe){return HeldenMobilCombat.adjustCombatForBE(at,pa,ebe);}"
app = replace_once(app, old_ebe, new_ebe, 'combat BE delegates')

fd_start = app.index('  function finalDamage(')
melee_start = app.index('  function meleeValues(', fd_start)
app = app[:fd_start] + "  function finalDamage(tp,tpkk){const kk=currentAttr(propMap(state.current.props),'Körperkraft');return HeldenMobilCombat.finalDamage(tp,tpkk,kk);}\n" + app[melee_start:]

zone_start = app.index('  function zoneFromD20(')
zone_next = app.index('  function currentZoneArmor(', zone_start)
app = app[:zone_start] + "  function zoneFromD20(r){return HeldenMobilCombat.zoneFromD20(r);}\n" + app[zone_next:]

# Passive effects cannot be triggered or consume charges.
app = replace_once(app, "  function triggerArtifactEffect(itemId,effectId){const {item,effect}=artifactLookup(itemId,effectId);if(!item||!effect)return;if(effect.maxCharges!=null){", "  function triggerArtifactEffect(itemId,effectId){const {item,effect}=artifactLookup(itemId,effectId);if(!item||!effect||/^passiv$/i.test(String(effect.type||'').trim()))return;if(effect.maxCharges!=null){", 'passive trigger guard')
app = replace_once(app, "const empty=fx.maxCharges!=null&&Number(fx.charges||0)<=0,meta=[fx.type||''", "const empty=fx.maxCharges!=null&&Number(fx.charges||0)<=0,passive=/^passiv$/i.test(String(fx.type||'').trim()),meta=[fx.type||''", 'artifact passive state')
app = app.replace("<button class=\"action-btn artifact-trigger\" ${empty?'disabled':''}>Auslösen</button>", "<button class=\"action-btn artifact-trigger\" ${empty||passive?'disabled':''}>${passive?'Passiv':'Auslösen'}</button>", 1)
# Dashboard has a second artifact renderer.
dash_passive_old = "const empty=fx.maxCharges!=null&&Number(fx.charges||0)<=0,meta=[it.magic?.kind||'Magischer Gegenstand'"
dash_passive_new = "const empty=fx.maxCharges!=null&&Number(fx.charges||0)<=0,passive=/^passiv$/i.test(String(fx.type||'').trim()),meta=[it.magic?.kind||'Magischer Gegenstand'"
app = replace_once(app, dash_passive_old, dash_passive_new, 'dashboard passive state')
app = app.replace("data-artifact-effect=\"${fx.id}\" ${empty?'disabled':''}>Auslösen</button>", "data-artifact-effect=\"${fx.id}\" ${empty||passive?'disabled':''}>${passive?'Passiv':'Auslösen'}</button>", 1)

# Destructive magical-data actions now require confirmation.
del_start = app.index('  function deleteArtifactEffect(')
remove_start = app.index('  function removeArtifactMagic(', del_start)
render_art_start = app.index('  function renderArtifacts()', remove_start)
new_delete = """  function deleteArtifactEffect(itemId,effectId){const item=companionState.data?.inventory?.items?.find(x=>x.id===itemId),effect=item?.magic?.effects?.find(x=>x.id===effectId);if(!item?.magic||!effect)return;if(!confirm(`Wirkung „${effect.name}“ von „${item.name}“ wirklich löschen?`))return;item.magic.effects=(item.magic.effects||[]).filter(x=>x.id!==effectId);if(!item.magic.effects.length)delete item.magic;saveCompanion();renderInventory();}
  function removeArtifactMagic(itemId){const item=companionState.data?.inventory?.items?.find(x=>x.id===itemId);if(!item?.magic)return;if(!confirm(`Alle magischen Daten von „${item.name}“ wirklich entfernen?`))return;delete item.magic;saveCompanion();renderInventory();}
"""
app = app[:del_start] + new_delete + app[render_art_start:]

# The spell card participates in the generic persisted collapse mechanism.
selector_old = "document.querySelectorAll('.combat-block,.combat-card,.comp-card,.sf-group')"
if selector_old in app:
    app = app.replace(selector_old, "document.querySelectorAll('.combat-block,.combat-card,.comp-card,.sf-group,.spell-list-card')", 1)

# ---------------------------------------------------------------------------
# Versioning, scripts, tests and docs
# ---------------------------------------------------------------------------
index = index.replace('v20.0', 'v20.3')
app = app.replace('v20.0', 'v20.3')
app = app.replace("lastQualityAudit={version:'19.0.2'", "lastQualityAudit={version:'20.3'")
package = package.replace('"version": "20.0.0"', '"version": "20.3.0"')
package = package.replace('"test": "node tests/smoke.mjs"', '"test": "node tests/smoke.mjs && node tests/core.mjs"')

scripts_old = '<script src="vendor/jszip-3.10.1.min.js"></script>\n<script src="js/app.js"></script>'
scripts_new = '<script src="vendor/jszip-3.10.1.min.js"></script>\n<script src="js/hld-parser.js"></script>\n<script src="js/companion-core.js"></script>\n<script src="js/combat-core.js"></script>\n<script src="js/app.js"></script>'
index = replace_once(index, scripts_old, scripts_new, 'module script order')

smoke = r"""import fs from 'node:fs';
import vm from 'node:vm';

const index = fs.readFileSync('index.html', 'utf8');
const app = fs.readFileSync('js/app.js', 'utf8');
const hld = fs.readFileSync('js/hld-parser.js', 'utf8');
const companion = fs.readFileSync('js/companion-core.js', 'utf8');
const combat = fs.readFileSync('js/combat-core.js', 'utf8');
const vendor = fs.readFileSync('vendor/jszip-3.10.1.min.js', 'utf8');

function ok(condition, message) { if (!condition) throw new Error(message); }

const order = ['vendor/jszip-3.10.1.min.js','js/hld-parser.js','js/companion-core.js','js/combat-core.js','js/app.js'].map(x=>index.indexOf(`<script src="${x}"></script>`));
ok(order.every(x=>x>=0) && order.every((x,i)=>i===0||x>order[i-1]), 'core scripts must load before app.js');
ok(!index.includes('JSZip v3.10.1 - A JavaScript class'), 'JSZip must stay external');
ok(index.includes('Beta v20.3'), 'visible version badge must be v20.3');
ok(index.includes('Begleitdaten v20.3'), 'header version must be v20.3');
ok(index.includes('HeldenMobil Beta v20.3'), 'footer version must be v20.3');
ok(hld.includes('function parseHero'), 'HLD parser must live in hld-parser.js');
ok(!app.includes('function parseHero(hero)'), 'HLD parser must no longer live in app.js');
ok(app.includes('HeldenMobilCompanion.normalizeCompanionData'), 'companion core delegate missing');
ok(app.includes('HeldenMobilCombat.combatEbe'), 'combat core delegate missing');
ok(app.includes("function automaticEvent(e){return e?.type==='energy';}"), 'wound/status events must remain manually managed');
ok(app.includes("lastQualityAudit={version:'20.3'"), 'quality audit JSON version must be v20.3');
ok(vendor.includes('JSZip v3.10.1'), 'wrong JSZip vendor payload');
for (const [name,src] of [['app',app],['hld',hld],['companion',companion],['combat',combat],['vendor',vendor]]) new vm.Script(src,{filename:`${name}.js`});
console.log('HeldenMobil v20.3 smoke tests passed');
"""
tests_path.write_text(smoke, encoding='utf-8')

core_tests = r"""import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const hld=require('../js/hld-parser.js');
const companion=require('../js/companion-core.js');
const combat=require('../js/combat-core.js');

function eq(actual,expected,label){const a=JSON.stringify(actual),e=JSON.stringify(expected);if(a!==e)throw new Error(`${label}: expected ${e}, got ${a}`);}
function ok(value,label){if(!value)throw new Error(label);}

// v20.1 HLD semantics
const parser=hld.createParser({});
const grad4=parser.parseLiturgySfName('Liturgie: Objektsegen (IV)',3);
eq([grad4.name,grad4.grade,grad4.gradeLabel,grad4.blessing],['Objektsegen','IV','Grad IV',true],'liturgy grade IV');
const basic=parser.parseLiturgySfName('Liturgie: Eidsegen',1);
eq([basic.gradeLabel,basic.blessing],['Grundgrad',true],'basic blessing');
ok(!parser.parseLiturgySfName('Liturgie: Segnung der Stählernen Stirn',2).blessing,'non-basic liturgy must stay in liturgies');
eq(parser.liturgyKnowledgeDeity({name:'Liturgiekenntnis (Rondra)'}),'Rondra','deity extraction');

// v20.2 companion migration/event behavior
const wounds={wounds:4,woundZones:{kopf:1,brust:1}};companion.normalizeStatusWounds(wounds);
eq(wounds.wounds,4,'wound total preserved');eq(wounds.woundZones.unassigned,2,'legacy wounds become unassigned');
const finite=companion.normalizeMagicEffect({name:'Ladung',maxCharges:3,charges:9},0,()=> 'fx');eq([finite.charges,finite.maxCharges],[3,3],'finite charges clamp');
const unlimited=companion.normalizeMagicEffect({name:'Passiv',charges:5},0,()=> 'fx2');eq([unlimited.charges,unlimited.maxCharges],[null,null],'unlimited charges');
const t0=Date.parse('2026-08-31T08:00:00Z');
let events=[];events=companion.mergeEnergyEvent(events,'LeP',30,25,{nowMs:t0,uid:()=> 'e1'});events=companion.mergeEnergyEvent(events,'LeP',25,20,{nowMs:t0+20000,uid:()=> 'e2'});eq([events.length,events[0].from,events[0].to,events[0].delta],[1,30,20,-10],'25 second energy aggregation');
events=companion.mergeEnergyEvent(events,'AuP',40,39,{nowMs:t0+21000,uid:()=> 'e3'});eq(events.length,2,'energy types remain separate');
let zero=[];zero=companion.mergeEnergyEvent(zero,'LeP',10,9,{nowMs:t0,uid:()=> 'z1'});zero=companion.mergeEnergyEvent(zero,'LeP',9,10,{nowMs:t0+1000,uid:()=> 'z2'});eq(zero.length,0,'net zero energy burst removed');
const base={schemaVersion:8,heroKey:'x',heroName:'X',activeAdventureId:null,adventures:[],advancement:[],favorites:{talents:[],spells:[],liturgies:[]},inventory:{locations:[],items:[]},money:{transactions:[]},magic:{staffSlots:[]}};
const migrated=companion.normalizeCompanionData({schemaVersion:7,favorites:{talents:['Klettern','Klettern']},magic:{artifacts:[1]}},{base,heroKey:'h',heroName:'Held',schemaVersion:8,freshAdventureStatus:()=>({wounds:0,woundZones:companion.blankWoundZones()}),uid:()=> 'id'});
eq([migrated.schemaVersion,migrated.heroKey,migrated.favorites.talents.length,migrated.favorites.liturgies.length],[8,'h',1,0],'schema migration');ok(!('artifacts' in migrated.magic),'legacy global artifacts removed');
const baseline={eTag:'A',localUpdatedAt:'2026-08-31T08:00:00Z'};
eq(companion.decideInitialSync({localExists:true,localUpdatedAt:'2026-08-31T08:05:00Z',remoteUpdatedAt:'2026-08-31T08:04:00Z',remoteEtag:'B',baseline}),'conflict','offline divergence must conflict');
eq(companion.decideInitialSync({localExists:true,localUpdatedAt:'2026-08-31T08:00:00Z',remoteUpdatedAt:'2026-08-31T08:04:00Z',remoteEtag:'B',baseline}),'remote','remote-only change');
eq(companion.decideInitialSync({localExists:true,localUpdatedAt:'2026-08-31T08:05:00Z',remoteUpdatedAt:'2026-08-31T08:00:00Z',remoteEtag:'A',baseline}),'local','local-only change');
eq(companion.decideCloudWrite({remoteExists:true,currentEtag:'B',baselineEtag:'A'}),'conflict','write must fail closed on changed etag');
eq(companion.decideCloudWrite({force:true,remoteExists:true,currentEtag:'B',baselineEtag:'A'}),'write','explicit force overwrite');

// v20.3 existing combat behavior frozen as regression tests
const meta={Schwerter:{offset:2},Hiebwaffen:{offset:4}};
eq(combat.combatEbe('Schwerter',4,meta),2,'Schwerter eBE');eq(combat.combatEbe('Hiebwaffen',3,meta),0,'eBE floor');
eq(combat.adjustCombatForBE(15,14,3),{at:14,pa:12},'odd eBE distribution');
eq(combat.finalDamage([1,6,2],[11,4],15),[1,6,3],'TP/KK bonus');eq(combat.finalDamage([1,6,2],[11,4],10),[1,6,1],'TP/KK penalty');
eq(combat.zoneFromD20(20).key,'kopf','zone head');eq(combat.zoneFromD20(15).key,'brust','zone chest');eq(combat.zoneFromD20(9).key,'linkerarm','zone left arm');eq(combat.zoneFromD20(10).key,'rechterarm','zone right arm');eq(combat.zoneFromD20(7).key,'bauch','zone abdomen');eq(combat.zoneFromD20(1).key,'linkesbein','zone left leg');eq(combat.zoneFromD20(2).key,'rechtesbein','zone right leg');

console.log('HeldenMobil v20.1-v20.3 core regression tests passed');
"""
(ROOT / 'tests' / 'core.mjs').write_text(core_tests, encoding='utf-8')

readme = """# HeldenMobil

DSA 4.1 Heldentool für HLD-Dateien mit lokalen Begleitdaten und optionalem OneDrive-Sync.

## Quellstruktur ab v20.3

- `index.html` – HTML/CSS und statische Oberfläche
- `vendor/jszip-3.10.1.min.js` – vendorte ZIP-Bibliothek für HLD-Dateien
- `js/hld-parser.js` – HLD-Parsing und HLD-spezifische Semantik
- `js/companion-core.js` – Begleitdaten-Normalisierung, Ereignisaggregation und Sync-Entscheidungslogik
- `js/combat-core.js` – kleine, bereits produktiv genutzte Kampfberechnungen
- `js/app.js` – UI, Orchestrierung, OneDrive/Graph und verbleibende Anwendungslogik
- `tests/smoke.mjs` – Struktur-, Lade- und Syntaxprüfungen
- `tests/core.mjs` – Regressionstests für Parser-, Companion-, Sync- und Kampfverhalten

## Stabilisierung v20.1 bis v20.3

- **v20.1:** HLD-Parser aus dem UI-Monolithen gelöst und HLD-Semantik testbar gemacht.
- **v20.2:** Companion-/Abenteuer-Normalisierung ausgelagert; Energieereignisse werden dauerhaft normalisiert; OneDrive erkennt mit persistenter Sync-Baseline parallele Offline-/Remote-Änderungen und blockiert fail-closed statt still zu überschreiben.
- **v20.3:** bestehende Kampfberechnung in ein testbares Core-Modul verschoben; Wundereignisse bleiben manuell, passive magische Wirkungen sind nicht auslösbar, destruktive Magie-Aktionen sind bestätigt, Zauberliste nutzt die generische Einklapplogik.

Die Module bilden nur Verhalten ab, das HeldenMobil tatsächlich verwendet. Es wird kein vollständiges DSA-4.1-Regelwerk nachgebaut.

## Tests

```bash
npm test
```

Die CI führt die Tests bei jedem Push und Pull Request aus.
"""
readme_path.write_text(readme, encoding='utf-8')

changelog = """# Changelog

## v20.3

- Kampf-Kernberechnungen aus `app.js` entkoppelt und als Regressionstests eingefroren.
- Passive magische Wirkungen können keine Ladungen mehr verbrauchen und werden als passiv dargestellt.
- Löschen von Wirkungen bzw. allen magischen Daten erfordert Bestätigung.
- Wunden/Statusereignisse sind wieder manuell bearbeitbar und werden nicht wie automatische Energieereignisse behandelt.
- Zauberliste in die generische, persistente Einklapplogik aufgenommen.

## v20.2

- Companion-Normalisierung und Energieereignis-Aggregation in `js/companion-core.js` ausgelagert.
- Normalisierte Altbestände werden ohne Änderung des Zeitstempels zurückgespeichert.
- Persistente OneDrive-Sync-Baseline ergänzt: parallele lokale und entfernte Änderungen führen zu einem Konflikt statt zu stillem Überschreiben.

## v20.1

- HLD-Parser und HLD-spezifische Liturgie-/Ausrüstungssemantik in `js/hld-parser.js` ausgelagert.
- Erste gezielte HLD-Regressionstests ergänzt.

## v20.0

- Monolithische `index.html` in HTML, `js/app.js` und vendorte JSZip-Datei aufgeteilt.
- Dauerhafte CI und Smoke-Tests eingeführt.
"""
(ROOT / 'CHANGELOG.md').write_text(changelog, encoding='utf-8')

app_path.write_text(app, encoding='utf-8')
index_path.write_text(index, encoding='utf-8')
package_path.write_text(package, encoding='utf-8')

print('prepared HeldenMobil v20.1-v20.3 stabilization pass')
