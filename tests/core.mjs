import {createRequire} from 'node:module';
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
const snapshots=Array.from({length:12},(_,i)=>({id:`s${i}`,at:new Date(Date.parse('2026-08-31T08:00:00Z')+i*60000).toISOString(),data:{heroKey:'h',updatedAt:String(i)}}));const trimmed=companion.normalizeSnapshotList(snapshots,5);eq([trimmed.length,trimmed[0].id,trimmed.at(-1).id],[5,'s11','s7'],'snapshot history keeps newest five');eq(companion.addSnapshot(trimmed,{id:'s12',at:'2026-08-31T08:12:00Z',data:{heroKey:'h'}},5)[0].id,'s12','new snapshot becomes newest');eq(companion.normalizeSnapshotList(snapshots).length,5,'snapshot default limit is five');

// v20.3 existing combat behavior frozen as regression tests
const meta={Schwerter:{offset:2},Hiebwaffen:{offset:4}};
eq(combat.combatEbe('Schwerter',4,meta),2,'Schwerter eBE');eq(combat.combatEbe('Hiebwaffen',3,meta),0,'eBE floor');
eq(combat.adjustCombatForBE(15,14,3),{at:14,pa:12},'odd eBE distribution');
eq(combat.finalDamage([1,6,2],[11,4],15),[1,6,3],'TP/KK bonus');eq(combat.finalDamage([1,6,2],[11,4],10),[1,6,1],'TP/KK penalty');
eq(combat.zoneFromD20(20).key,'kopf','zone head');eq(combat.zoneFromD20(15).key,'brust','zone chest');eq(combat.zoneFromD20(9).key,'linkerarm','zone left arm');eq(combat.zoneFromD20(10).key,'rechterarm','zone right arm');eq(combat.zoneFromD20(7).key,'bauch','zone abdomen');eq(combat.zoneFromD20(1).key,'linkesbein','zone left leg');eq(combat.zoneFromD20(2).key,'rechtesbein','zone right leg');

console.log('HeldenMobil v20.1-v20.3.2 core regression tests passed');
