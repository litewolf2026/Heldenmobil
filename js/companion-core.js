(function(root,factory){
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

  function normalizeSnapshotList(raw,max=10){
    const limit=Math.max(1,Math.floor(Number(max)||10));
    return (Array.isArray(raw)?raw:[]).filter(x=>x&&typeof x==='object'&&x.data&&typeof x.data==='object').sort((a,b)=>timeValue(b.at)-timeValue(a.at)).slice(0,limit);
  }
  function addSnapshot(raw,snapshot,max=10){
    if(!snapshot||typeof snapshot!=='object'||!snapshot.data||typeof snapshot.data!=='object')return normalizeSnapshotList(raw,max);
    const list=normalizeSnapshotList(raw,max),id=String(snapshot.id||'');if(id&&list.some(x=>String(x.id||'')===id))return list;
    return normalizeSnapshotList([snapshot,...list],max);
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

  return {WOUND_ZONE_KEYS,blankWoundZones,normalizeStatusWounds,magicOptionalInt,magicOptionalNumber,normalizeMagicEffect,normalizeInventoryMagic,energyEventText,parseLegacyEnergyEvent,normalizeAdventureEvents,mergeEnergyEvent,normalizeCompanionData,normalizeSnapshotList,addSnapshot,decideInitialSync,decideCloudWrite};
});
