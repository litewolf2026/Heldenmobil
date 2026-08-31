(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.HeldenMobilHld=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  function createParser(deps={}){
    const {direct,directAll,attr,num,cleanName,talentCategory,buildMetaTalents,directSelections,isDisadvantage,sfEntryFromElement}=deps;
  const BASIC_BLESSING_NAMES=new Set(['Eidsegen','Feuersegen','Geburtssegen','Glückssegen','Grabsegen','Harmoniesegen','Heilungssegen','Märtyrersegen','Objektsegen','Schutzsegen','Speisesegen','Tranksegen','Weisheitssegen']);
  function parseLiturgySfName(raw,index=0){
    const full=String(raw||'').replace(/^Liturgie:\s*/,'').trim(),m=/^(.*?)\s+\(([IVX]+)\)$/.exec(full),name=(m?m[1]:full).trim(),grade=m?m[2]:'';
    return {raw:String(raw||''),name,grade,gradeLabel:grade?`Grad ${grade}`:'Grundgrad',blessing:BASIC_BLESSING_NAMES.has(name),key:`${String(raw||'')}␟${index}`};
  }
  function liturgyKnowledgeDeity(t){const m=/^Liturgiekenntnis\s*\((.*?)\)\s*$/.exec(String(t?.name||''));return m?m[1]:String(t?.name||'').replace(/^Liturgiekenntnis\s*/,'').trim()||'Geweiht';}
  function parseHero(hero){
    const held=hero.doc.querySelector('helden > held');
    const basis=direct(held,'basis');
    const rasse=direct(basis,'rasse'), kultur=direct(basis,'kultur');
    const ausb=direct(direct(basis,'ausbildungen'),'ausbildung');
    const variante=direct(ausb,'variante');
    const race=attr(rasse,'string',attr(rasse,'name'));
    const genderNode=direct(basis,'geschlecht')||direct(held,'geschlecht')||held.querySelector('geschlecht');
    const genderRaw=[attr(held,'geschlecht'),attr(basis,'geschlecht'),attr(genderNode,'name'),attr(genderNode,'value'),attr(genderNode,'string'),genderNode?.textContent||''].filter(Boolean).join(' ').toLocaleLowerCase('de');
    const gender=/weib|female|frau/.test(genderRaw)?'female':(/männ|maenn|male|mann/.test(genderRaw)?'male':'unknown');

    const eigRoot=direct(held,'eigenschaften');
    const props=directAll(eigRoot,'eigenschaft').map(e=>({name:attr(e,'name'),value:num(attr(e,'value')),mod:num(attr(e,'mod')),start:attr(e,'startwert',''),permanent:attr(e,'permanent','')}));

    const talentRoot=direct(held,'talentliste');
    let talents=directAll(talentRoot,'talent').map(t=>({name:attr(t,'name'),probe:attr(t,'probe').trim(),value:num(attr(t,'value')),se:attr(t,'se')==='true',method:attr(t,'lernmethode'),be:attr(t,'be'),k:attr(t,'k'),specs:[],mh:false,category:talentCategory(attr(t,'name')),meta:false}));
    talents=[...talents,...buildMetaTalents(talents)];

    const spellRoot=direct(held,'zauberliste');
    const spells=directAll(spellRoot,'zauber').map(z=>({name:attr(z,'name'),probe:attr(z,'probe').trim(),value:num(attr(z,'value')),rep:attr(z,'repraesentation'),column:attr(z,'k'),house:attr(z,'hauszauber')==='true',specs:[]}));

    const kampfRoot=direct(held,'kampf');
    const combat=directAll(kampfRoot,'kampfwerte').map(k=>({name:attr(k,'name'),at:num(attr(direct(k,'attacke'),'value')),pa:num(attr(direct(k,'parade'),'value'))}));
    const combatMap=new Map(combat.map(k=>[k.name,k]));

    const vtRoot=direct(held,'vt');
    const vorteile=directAll(vtRoot,'vorteil');
    const meisterhandwerke=new Set(vorteile.filter(v=>attr(v,'name')==='Meisterhandwerk').map(v=>cleanName(attr(v,'value'))).filter(Boolean));
    const vtEntries=vorteile.map(v=>{
      const name=attr(v,'name'),val=cleanName(attr(v,'value'));
      const choices=directAll(v,'auswahl').map((a,i)=>({position:num(attr(a,'position'),i),value:cleanName(attr(a,'value'))})).filter(x=>x.value).sort((a,b)=>a.position-b.position).map(x=>x.value);
      const details=[...choices,...directSelections(v).map(cleanName),val].filter(Boolean).filter((x,i,a)=>a.indexOf(x)===i);
      const level=choices.find(x=>/^[-+]?\d+(?:[.,]\d+)?$/.test(x));
      const targets=choices.filter(x=>x!==level);
      if(level&&targets.length&&(/^(?:Vorurteile gegen|Weltfremd bzgl\.|Angst vor)/i.test(name))){
        return {name,label:`${name} ${targets.join(' / ')}: ${level}`};
      }
      return {name,label:name+(details.length?`: ${details.join(' · ')}`:'')};
    });
    const vt=vtEntries.map(v=>v.label);
    const advantages=vtEntries.filter(v=>!isDisadvantage(v.name)).map(v=>v.label);
    const disadvantages=vtEntries.filter(v=>isDisadvantage(v.name)).map(v=>v.label);
    const vtNames=new Set(vorteile.map(v=>attr(v,'name')));
    const vtValues=new Map(vorteile.map(v=>[attr(v,'name'),attr(v,'value')]));

    const sfRoot=direct(held,'sf');
    const sfEls=directAll(sfRoot,'sonderfertigkeit');
    const sf=sfEls.map(s=>attr(s,'name')).filter(Boolean);
    const sfEntries=sfEls.map(sfEntryFromElement).filter(Boolean);
    const sfSet=new Set(sf);
    const liturgyKnowledges=talents.filter(t=>/^Liturgiekenntnis\s*\(/.test(t.name));
    const liturgies=sfEls.map((el,i)=>({el,name:attr(el,'name'),i})).filter(x=>/^Liturgie:\s*/.test(x.name)).map(x=>parseLiturgySfName(x.name,x.i));
    const karmal=liturgyKnowledges.length>0||liturgies.length>0||props.some(x=>x.name==='Karmaenergie'&&(Number(x.mod||0)!==0||Number(x.value||0)!==0))||sfSet.has('Karmalqueste');
    const magical=spells.length>0||props.some(x=>x.name==='Astralenergie'&&(Number(x.mod||0)!==0||Number(x.value||0)!==0));
    const talentSpecs=new Map(), spellSpecs=[];
    for(const s of sfEls){
      const name=attr(s,'name');
      if(name.startsWith('Talentspezialisierung ')){
        const tn=cleanName(attr(direct(s,'talent'),'name')), sn=cleanName(attr(direct(s,'spezialisierung'),'name'));
        if(tn&&sn){if(!talentSpecs.has(tn))talentSpecs.set(tn,[]);talentSpecs.get(tn).push(sn);}
      } else if(name.startsWith('Zauberspezialisierung ')){
        const z=direct(s,'zauber'),sp=direct(s,'spezialisierung');
        const zn=cleanName(attr(z,'name')),rep=cleanName(attr(z,'repraesentation')),sn=cleanName(attr(sp,'name'));
        if(zn&&sn)spellSpecs.push({name:zn,rep,spec:sn});
      }
    }
    for(const t of talents){t.specs=talentSpecs.get(t.name)||[];t.mh=meisterhandwerke.has(t.name);}
    for(const z of spells){z.specs=spellSpecs.filter(s=>s.name===z.name&&(!s.rep||s.rep===z.rep)).map(s=>s.spec);}

    const itemsRoot=direct(held,'gegenstände');
    const items=directAll(itemsRoot,'gegenstand').map(g=>parseItem(g));
    const equipRoot=direct(held,'ausrüstungen');
    const equip=directAll(equipRoot,'heldenausruestung');
    const setIds=[...new Set(equip.map(e=>num(attr(e,'set'))))].sort((a,b)=>a-b);
    const combatSets=setIds.map(id=>{
      const entries=equip.filter(e=>num(attr(e,'set'))===id).map(e=>parseEquipmentEntry(e,items));
      const shields=new Map(entries.filter(e=>e.type==='shield').map(e=>[e.index,e]));
      for(const e of entries.filter(e=>e.type==='melee'))e.linkedShield=e.shieldIndex?shields.get(e.shieldIndex)||null:null;
      return {id,entries};
    });

    const boniRoot=direct(held,'BoniWaffenlos');
    const unarmedBonuses=directAll(boniRoot,'boniSF').map(b=>({sf:attr(b,'sf'),talent:attr(b,'talent')}));

    const rg1=sfEls.filter(s=>attr(s,'name')==='Rüstungsgewöhnung I').map(s=>attr(direct(s,'gegenstand'),'name')).filter(Boolean);

    return {
      name:attr(held,'name'),key:attr(held,'key'),race,gender,
      culture:attr(kultur,'string',attr(kultur,'name')),
      profession:[attr(ausb,'string',attr(ausb,'name')),attr(variante,'name')].filter(Boolean).join(' · '),
      ap:num(attr(direct(basis,'abenteuerpunkte'),'value')),freeAp:num(attr(direct(basis,'freieabenteuerpunkte'),'value')),
      props,talents,spells,magical,liturgyKnowledges,liturgies,karmal,combat,combatMap,sf,sfEntries,sfSet,vt,advantages,disadvantages,vtNames,vtValues,meisterhandwerke,talentSpecs,combatSets,unarmedBonuses,rg1,items,
      staffItems:items.filter(i=>/magierstab/i.test(`${i.base} ${i.display}`))
    };
  }

  function parseItem(g){
    const base=attr(g,'name'),slot=attr(g,'slot');
    const mod=direct(g,'modallgemein'),display=attr(direct(mod,'name'),'value',base);
    const nk=direct(g,'Nahkampfwaffe'), sh=direct(g,'Schild'), ru=direct(g,'Rüstung');
    const tp=direct(nk,'trefferpunkte'),wm=direct(nk,'wm'),bf=direct(nk,'bf'),nki=direct(nk,'inimod'),tpkk=direct(nk,'tpkk');
    const swm=direct(sh,'wm'),sbf=direct(sh,'bf'),shi=direct(sh,'inimod');
    const armorZones={};
    for(const n of ['kopf','brust','ruecken','bauch','linkerarm','rechterarm','linkesbein','rechtesbein']){
      const e=direct(ru,n); if(e) armorZones[n]=num(attr(e,'value'));
    }
    return {
      base,slot,display,count:num(attr(g,'anzahl'),1),
      nk:nk?{tp:tp?[num(attr(tp,'mul'),1),num(attr(tp,'w'),6),num(attr(tp,'sum'),0)]:null,tpkk:tpkk?[num(attr(tpkk,'kk')),num(attr(tpkk,'schrittweite'))]:null,wm:wm?[num(attr(wm,'at')),num(attr(wm,'pa'))]:null,ini:nki?num(attr(nki,'ini')):null,bf:bf?num(attr(bf,'akt')):null}:null,
      fk:!!direct(g,'Fernkampfwaffe'),
      shield:sh?{wm:swm?[num(attr(swm,'at')),num(attr(swm,'pa'))]:null,ini:shi?num(attr(shi,'ini')):null,bf:sbf?num(attr(sbf,'akt')):null,bfmin:sbf?num(attr(sbf,'min')):null}:null,
      armor:ru?{
        rs:direct(ru,'rs')?num(attr(direct(ru,'rs'),'value')):null,
        gesRs:direct(ru,'geszors')?num(attr(direct(ru,'geszors'),'value')):null,
        gesBe:direct(ru,'gesbe')?num(attr(direct(ru,'gesbe'),'value')):null,
        stars:direct(ru,'sterne')?num(attr(direct(ru,'sterne'),'value')):null,
        parts:direct(ru,'teile')?num(attr(direct(ru,'teile'),'value')):null,
        zones:armorZones
      }:null
    };
  }

  function findItem(items,base,slot){ return items.find(i=>i.base===base&&String(i.slot)===String(slot))||items.find(i=>i.base===base)||null; }
  function parseEquipmentEntry(e,items){
    const n=attr(e,'name'); let type='other',base='',index=0;
    if(n.startsWith('nkwaffe')){type='melee';base=attr(e,'waffenname');index=num(n.replace(/\D/g,''));}
    else if(n.startsWith('fkwaffe')){type='ranged';base=attr(e,'waffenname');index=num(n.replace(/\D/g,''));}
    else if(n.startsWith('schild')){type='shield';base=attr(e,'schildname');index=num(n.replace(/\D/g,''));}
    else if(n.startsWith('ruestung')){type='armor';base=attr(e,'ruestungsname');index=num(n.replace(/\D/g,''));}
    else return {type:'other',record:n,index};
    const item=findItem(items,base,attr(e,'slot'));
    return {type,base,name:item?.display||base,slot:attr(e,'slot'),talent:attr(e,'talent'),item,record:n,index,hand:attr(e,'hand'),shieldIndex:num(attr(e,'schild')),usage:attr(e,'verwendungsArt'),descriptor:attr(e,'bezeichner'),bfakt:attr(e,'bfakt')===''?null:num(attr(e,'bfakt'))};
  }


    return {parseHero,parseItem,findItem,parseEquipmentEntry,parseLiturgySfName,liturgyKnowledgeDeity};
  }
  return {createParser};
});
