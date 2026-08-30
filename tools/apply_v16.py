from pathlib import Path
import re
import subprocess
import tempfile

PATH = Path('index.html')
text = PATH.read_text(encoding='utf-8')
original = text

if '/* v16 Regel- und UI-Fixes */' in text:
    print('v16 patch already applied')
    raise SystemExit(0)

def replace_exact(old, new, expected=1, label='replacement'):
    global text
    count = text.count(old)
    if count != expected:
        raise RuntimeError(f'{label}: expected {expected} occurrence(s), found {count}')
    text = text.replace(old, new)

def replace_regex(pattern, replacement, expected=1, label='regex replacement', flags=re.S):
    global text
    text, count = re.subn(pattern, replacement, text, flags=flags)
    if count != expected:
        raise RuntimeError(f'{label}: expected {expected} occurrence(s), found {count}')

# Visible version labels.
replace_exact('HeldenMobil – HLD PoC v15', 'HeldenMobil – HLD PoC v16', 1, 'document title')
replace_exact('DSA 4.1 · HLD + Begleitdaten v15', 'DSA 4.1 · HLD + Begleitdaten v16', 1, 'header version')
replace_exact('Proof of Concept v15', 'Proof of Concept v16', 1, 'badge version')
replace_exact('HeldenMobil PoC v15 · HLD read-only · Begleitdaten + OneDrive-Sync · Würfeltisch',
              'HeldenMobil PoC v16 · HLD read-only · Begleitdaten + OneDrive-Sync · Würfeltisch', 1, 'footer version')

# Correct/robust DSA 4.1 talent grouping. Keep display names untouched; only classification is normalized.
new_talent_groups = r'''  const TALENT_GROUPS = [
    ['Kampf', new Set([...Object.keys(COMBAT_META),'Blasrohr','Kettenstäbe','Peitsche','Zweihandflegel'])],
    ['Körperlich', new Set(['Akrobatik','Athletik','Fliegen','Gaukeleien','Klettern','Körperbeherrschung','Reiten','Schleichen','Schwimmen','Selbstbeherrschung','Sich verstecken','Singen','Sinnenschärfe','Skifahren','Stimmen imitieren','Tanzen','Taschendiebstahl','Zechen'])],
    ['Gesellschaftlich', new Set(['Betören','Etikette','Gassenwissen','Lehren','Menschenkenntnis','Schauspielerei','Schriftlicher Ausdruck','Sich verkleiden','Überreden','Überzeugen'])],
    ['Natur', new Set(['Fallenstellen','Fallen stellen','Fesseln/Entfesseln','Fischen/Angeln','Fährtensuchen','Orientierung','Wettervorhersage','Wildnisleben'])],
    ['Wissen', new Set(['Anatomie','Baukunst','Brett-/Kartenspiel','Geographie','Geografie','Geschichtswissen','Gesteinskunde','Götter/Kulte','Götter und Kulte','Heraldik','Hüttenkunde','Kriegskunst','Kryptographie','Magiekunde','Mechanik','Pflanzenkunde','Philosophie','Rechnen','Rechtskunde','Sagen/Legenden','Sagen und Legenden','Schätzen','Sprachenkunde','Staatskunst','Sternkunde','Tierkunde'])],
    ['Handwerk', new Set(['Abrichten','Ackerbau','Alchimie','Bergbau','Bogenbau','Boote fahren','Boote Fahren','Brauer','Drucker','Eissegler Fahren','Fahrzeug lenken','Fahrzeug Lenken','Falschspiel','Feinmechanik','Feuersteinbearbeitung','Fleischer','Gerber/Kürschner','Glaskunst','Grobschmied','Handel','Hauswirtschaft','Heilkunde: Gift','Heilkunde Gift','Heilkunde: Krankheiten','Heilkunde Krankheiten','Heilkunde: Seele','Heilkunde Seele','Heilkunde: Wunden','Heilkunde Wunden','Holzbearbeitung','Hundeschlitten Fahren','Instrumentenbauer','Kapellmeister','Kartographie','Kartografie','Kochen','Kristallzucht','Kristallzüchter','Lederarbeiten','Malen/Zeichnen','Maurer','Metallguss','Musizieren','Schlösser knacken','Schlösser Knacken','Schnaps brennen','Schnaps Brennen','Schneidern','Seefahrt','Seiler','Steinmetz','Steinschneider/Juwelier','Stellmacher','Steuermann','Stoffe färben','Stoffe Färben','Tätowieren','Töpfern','Viehzucht','Webkunst','Winzer','Zimmermann'])]
  ];
  const GROUP_ORDER = ['Gaben','Kampf','Körperlich','Gesellschaftlich','Natur','Wissen','Sprachen','Schriften','Handwerk','Ritual-/Liturgiekenntnis','Sonstige'];
'''
replace_regex(r"  const TALENT_GROUPS = \[\n.*?\n  \];\n  const GROUP_ORDER = \['Gaben'.*?\n",
              new_talent_groups, 1, 'talent group table')

new_talent_category = r'''  function talentKey(name){
    let key=String(name||'').normalize('NFC').toLocaleLowerCase('de').replace(/\bund\b/g,'').replace(/[^a-z0-9äöüß]+/g,'');
    const aliases={kartografie:'kartographie',geografie:'geographie',kristallzüchter:'kristallzucht'};
    return aliases[key]||key;
  }
  const TALENT_GROUP_BY_KEY=(()=>{const out=new Map();for(const [group,set] of TALENT_GROUPS)for(const name of set)out.set(talentKey(name),group);return out;})();
  function talentCategory(name){
    const raw=String(name||'').trim(),lower=raw.toLocaleLowerCase('de');
    if(lower.startsWith('sprachen kennen ')) return 'Sprachen';
    if(lower.startsWith('lesen/schreiben ')) return 'Schriften';
    if(lower.startsWith('ritualkenntnis:') || lower.startsWith('liturgiekenntnis ')) return 'Ritual-/Liturgiekenntnis';
    const key=talentKey(raw);
    const gifts=new Set(['empathie','gefahreninstinkt','geräuschhexerei','magiegespür','prophezeien','tierempathie','zwergennase']);
    if(gifts.has(key) || lower.startsWith('talentschub ') || lower.startsWith('talentschub:') || lower.startsWith('kräfteschub ') || lower.startsWith('kräfteschub:')) return 'Gaben';
    return TALENT_GROUP_BY_KEY.get(key)||'Sonstige';
  }

  // Die HLD enthält'''
replace_regex(r"  function talentCategory\(name\)\{\n.*?\n  \}\n\n  // Die HLD enthält",
              new_talent_category, 1, 'talent category function')

# Preserve selections/levels of parameterized advantages and disadvantages.
old_vt = """    const vtRoot=direct(held,'vt');
    const vorteile=directAll(vtRoot,'vorteil');
    const meisterhandwerke=new Set(vorteile.filter(v=>attr(v,'name')==='Meisterhandwerk').map(v=>cleanName(attr(v,'value'))).filter(Boolean));
    const vtEntries=vorteile.map(v=>{const name=attr(v,'name'),val=attr(v,'value');return {name,label:name+(val?`: ${val}`:'')};});
    const vt=vtEntries.map(v=>v.label);
    const advantages=vtEntries.filter(v=>!isDisadvantage(v.name)).map(v=>v.label);
    const disadvantages=vtEntries.filter(v=>isDisadvantage(v.name)).map(v=>v.label);
    const vtNames=new Set(vorteile.map(v=>attr(v,'name')));
    const vtValues=new Map(vorteile.map(v=>[attr(v,'name'),attr(v,'value')]));
"""
new_vt = """    const vtRoot=direct(held,'vt');
    const vorteile=directAll(vtRoot,'vorteil');
    const meisterhandwerke=new Set(vorteile.filter(v=>attr(v,'name')==='Meisterhandwerk').map(v=>cleanName(attr(v,'value'))).filter(Boolean));
    const vtEntries=vorteile.map(v=>{
      const name=attr(v,'name'),val=cleanName(attr(v,'value'));
      const details=[...directSelections(v).map(cleanName),val].filter(Boolean).filter((x,i,a)=>a.indexOf(x)===i);
      if(/^Vorurteile(?: gegen)?$/i.test(name)&&details.length){
        const numbers=details.filter(x=>/^[-+]?\\d+(?:[.,]\\d+)?$/.test(x)),targets=details.filter(x=>!/^[-+]?\\d+(?:[.,]\\d+)?$/.test(x));
        return {name,label:`${name==='Vorurteile'?'Vorurteile gegen':name}${targets.length?` ${targets.join(' / ')}`:''}${numbers.length?` ${numbers.join(' / ')}`:''}`};
      }
      return {name,label:name+(details.length?`: ${details.join(' · ')}`:'')};
    });
    const vt=vtEntries.map(v=>v.label);
    const advantages=vtEntries.filter(v=>!isDisadvantage(v.name)).map(v=>v.label);
    const disadvantages=vtEntries.filter(v=>isDisadvantage(v.name)).map(v=>v.label);
    const vtNames=new Set(vorteile.map(v=>attr(v,'name')));
    const vtValues=new Map(vorteile.map(v=>[attr(v,'name'),attr(v,'value')]));
"""
replace_exact(old_vt, new_vt, 1, 'parameterized advantages/disadvantages')

# Klingentänzer grants one additional W6, not two.
replace_exact("const dice=dancer?'3W6':'1W6';", "const dice=dancer?'2W6':'1W6';", 1, 'single-loadout Klingentänzer')
replace_exact("dice:dancer?'3W6':'1W6'", "dice:dancer?'2W6':'1W6'", 1, 'dual-loadout Klingentänzer')

# Shared UI-collapse storage and collapsible talent groups.
new_render_talents = r'''  const TALENT_COLLAPSE_KEY='heldenmobil:ui:collapsed-talents:v1',INVENTORY_COLLAPSE_KEY='heldenmobil:ui:collapsed-inventory:v1',MONEY_HISTORY_COLLAPSE_KEY='heldenmobil:ui:money-history-collapsed:v1';
  function uiSetFromStorage(key){try{const value=JSON.parse(localStorage.getItem(key)||'[]');return new Set(Array.isArray(value)?value:[]);}catch(_){return new Set();}}
  function saveUiSet(key,set){localStorage.setItem(key,JSON.stringify([...set]));}
  const collapsedTalentGroups=uiSetFromStorage(TALENT_COLLAPSE_KEY),collapsedInventoryLocations=uiSetFromStorage(INVENTORY_COLLAPSE_KEY);
  function renderTalents(){
    const q=$('#talentSearch').value.trim().toLocaleLowerCase('de');
    const arr=state.current.talents.filter(t=>!q||(`${t.name} ${t.probe} ${t.specs.join(' ')} ${t.mh?'meisterhandwerk':''} ${t.meta?'metatalent':''} ${t.metaDetail||''} ${t.category}`).toLocaleLowerCase('de').includes(q));
    const grouped=new Map();for(const g of GROUP_ORDER)grouped.set(g,[]);for(const t of arr){if(!grouped.has(t.category))grouped.set(t.category,[]);grouped.get(t.category).push(t);}
    let html='';for(const g of GROUP_ORDER){const rows=grouped.get(g)||[];if(!rows.length)continue;const collapsed=!q&&collapsedTalentGroups.has(g);html+=`<tr class="group-row"><td colspan="4"><button type="button" class="group-toggle" data-talent-group="${esc(g)}" aria-expanded="${collapsed?'false':'true'}"><span class="collapse-chevron">${collapsed?'▸':'▾'}</span><span class="group-label">${esc(g)}</span><span class="group-count">${rows.length}</span></button></td></tr>`;if(!collapsed)html+=rows.map(t=>{const idx=state.current.talents.indexOf(t),ref=registerRoll(`talent:${idx}`,rollPayloadForThreePart(t.name,t.probe,t.value,'talent'));return `<tr class="rollable-row" tabindex="0" data-roll-ref="${ref}" title="${esc(t.name)} würfeln"><td>${esc(t.name)} <span class="roll-mark">◆</span>${t.metaDetail?`<div class="cell-sub">${esc(t.metaDetail)}</div>`:''}</td><td>${esc(t.probe)}</td><td class="num hot">${t.value}</td><td><div class="tagrow">${tagsForTalent(t)}</div></td></tr>`;}).join('');}
    $('#talentBody').innerHTML=html||'<tr><td colspan="4" class="empty">Keine Treffer</td></tr>';
    if(!q)$$('#talentBody .group-toggle').forEach(btn=>btn.addEventListener('click',()=>{const g=btn.dataset.talentGroup;if(collapsedTalentGroups.has(g))collapsedTalentGroups.delete(g);else collapsedTalentGroups.add(g);saveUiSet(TALENT_COLLAPSE_KEY,collapsedTalentGroups);renderTalents();}));
  }
  function renderSpells(){'''
replace_regex(r"  function renderTalents\(\)\{\n.*?\n  \}\n  function renderSpells\(\)\{",
              new_render_talents, 1, 'collapsible talent groups')

# Add collapsible money history while leaving current balance and booking controls visible.
replace_exact('        <div id="moneyTransactions" class="money-list"></div>',
              '        <div class="money-history"><button type="button" id="moneyHistoryToggle" class="money-history-toggle" aria-expanded="true"><span class="collapse-chevron" id="moneyHistoryChevron">▾</span><span>Ein- und Ausgaben</span><span class="count" id="moneyHistoryCount"></span></button><div id="moneyTransactions" class="money-list"></div></div>',
              1, 'money history markup')

new_render_money = r'''  function renderMoney(){const d=companionState.data;if(!d||!$('#moneySummary'))return;const total=moneyTotalK(),m=splitMoney(total);$('#moneySummary').innerHTML=`<div class="money-coin"><span>Dukaten</span><strong>${m.sign<0?'−':''}${m.d}</strong></div><div class="money-coin"><span>Silber</span><strong>${m.s}</strong></div><div class="money-coin"><span>Heller</span><strong>${m.h}</strong></div><div class="money-coin"><span>Kreuzer</span><strong>${m.k}</strong></div>`;const tx=d.money.transactions||[];$('#moneyCount').textContent=`${tx.length} Buchungen`;const shown=tx.slice(-20).reverse(),collapsed=localStorage.getItem(MONEY_HISTORY_COLLAPSE_KEY)==='1',list=$('#moneyTransactions'),toggle=$('#moneyHistoryToggle');if($('#moneyHistoryCount'))$('#moneyHistoryCount').textContent=`${tx.length}`;if(toggle){toggle.setAttribute('aria-expanded',collapsed?'false':'true');const c=$('#moneyHistoryChevron');if(c)c.textContent=collapsed?'▸':'▾';toggle.onclick=()=>{localStorage.setItem(MONEY_HISTORY_COLLAPSE_KEY,collapsed?'0':'1');renderMoney();};}list.hidden=collapsed;list.innerHTML=(tx.length>20?`<div class="small-note" style="padding:7px 0">Letzte 20 von ${tx.length} Buchungen.</div>`:'')+shown.map(t=>{const v=transactionTotalK(t);return `<div class="money-row" data-money-id="${t.id}"><div class="money-amount ${v<0?'negative':''}">${esc(moneyTextFromTotal(v))}</div><div><div class="money-note">${esc(t.note||'ohne Notiz')}${t.source?` <span class="source-pill">${esc(t.source)}</span>`:''}</div><div class="money-meta">${t.at?new Date(t.at).toLocaleString('de-DE'):'importiert'}</div></div><div class="money-actions"><button class="danger-btn delete-money">Löschen</button></div></div>`;}).join('')||'<div class="empty-comp">Noch keine Geldbuchungen.</div>';
    $$('#moneyTransactions .money-row').forEach(row=>row.querySelector('.delete-money').onclick=()=>{d.money.transactions=d.money.transactions.filter(x=>x.id!==row.dataset.moneyId);saveCompanion();renderMoney();});}
'''
replace_regex(r"  function renderMoney\(\)\{.*?\n    \$\$\('#moneyTransactions \.money-row'\).*?\}\n",
              new_render_money, 1, 'collapsible money history')

# Inventory container collapse + safe deletion semantics.
new_inventory = r'''  function locationMap(){return new Map((companionState.data?.inventory?.locations||[]).map(x=>[x.id,x]));}
  function locationHasCollapsedAncestor(id){const by=locationMap();let cur=by.get(id),guard=0;while(cur?.parentId&&guard++<50){if(collapsedInventoryLocations.has(cur.parentId))return true;cur=by.get(cur.parentId);}return false;}
  function descendantLocationIds(id){const locs=companionState.data?.inventory?.locations||[],out=new Set(),stack=[id];while(stack.length){const cur=stack.pop();for(const loc of locs)if(loc.parentId===cur&&!out.has(loc.id)){out.add(loc.id);stack.push(loc.id);}}return out;}
  function locationHasContent(id){const d=companionState.data;return d.inventory.items.some(x=>x.locationId===id)||d.inventory.locations.some(x=>x.parentId===id);}
  function ensureLocationDeleteDialog(){let dlg=$('#locationDeleteDialog');if(dlg)return dlg;dlg=document.createElement('dialog');dlg.id='locationDeleteDialog';dlg.className='location-delete-dialog';dlg.innerHTML='<form method="dialog" class="location-delete-card"><h3>Behälter löschen?</h3><p id="locationDeleteText" class="subtle"></p><div class="location-delete-actions"><button type="button" class="action-btn primary" data-choice="move">Inhalt verschieben</button><button type="button" class="danger-btn" data-choice="delete">Alles löschen</button><button type="button" class="action-btn" data-choice="cancel">Abbrechen</button></div></form>';document.body.appendChild(dlg);return dlg;}
  function chooseFilledLocationDelete(loc){return new Promise(resolve=>{const dlg=ensureLocationDeleteDialog();$('#locationDeleteText').textContent=`„${loc.name}“ enthält Gegenstände oder Unterbehälter. Was soll damit passieren?`;let done=false;const finish=choice=>{if(done)return;done=true;try{dlg.close();}catch(_){}resolve(choice);};dlg.querySelectorAll('[data-choice]').forEach(b=>b.onclick=()=>finish(b.dataset.choice));dlg.oncancel=e=>{e.preventDefault();finish('cancel');};if(typeof dlg.showModal==='function')dlg.showModal();else{const a=prompt('Behälter ist gefüllt: 1 = Inhalt verschieben, 2 = alles löschen, sonst = abbrechen','1');finish(a==='1'?'move':a==='2'?'delete':'cancel');}});}
  async function requestDeleteLocation(id){const d=companionState.data,loc=d?.inventory?.locations?.find(x=>x.id===id);if(!loc)return;if(!locationHasContent(id)){if(!confirm(`Leeren Behälter „${loc.name}“ löschen?`))return;d.inventory.locations=d.inventory.locations.filter(x=>x.id!==id);collapsedInventoryLocations.delete(id);saveUiSet(INVENTORY_COLLAPSE_KEY,collapsedInventoryLocations);saveCompanion();renderInventory();return;}const choice=await chooseFilledLocationDelete(loc);if(choice==='cancel')return;if(choice==='move'){const parent=loc.parentId||null;for(const it of d.inventory.items)if(it.locationId===id)it.locationId=parent;for(const child of d.inventory.locations)if(child.parentId===id)child.parentId=parent;d.inventory.locations=d.inventory.locations.filter(x=>x.id!==id);collapsedInventoryLocations.delete(id);}else if(choice==='delete'){const ids=descendantLocationIds(id);ids.add(id);d.inventory.items=d.inventory.items.filter(x=>!ids.has(x.locationId));d.inventory.locations=d.inventory.locations.filter(x=>!ids.has(x.id));for(const x of ids)collapsedInventoryLocations.delete(x);}saveUiSet(INVENTORY_COLLAPSE_KEY,collapsedInventoryLocations);saveCompanion();renderInventory();}
  function renderInventory(){const d=companionState.data;if(!d)return;refreshLocationSelects();renderPriceCatalogCount();const items=d.inventory.items,groups=new Map(),cons=items.filter(isConsumableItem).length;for(const it of items){const k=it.locationId||'';if(!groups.has(k))groups.set(k,[]);groups.get(k).push(it);}$('#inventoryCount').textContent=`${items.length} Gegenstände · ${cons} Verbrauch · ${d.inventory.locations.length} Orte`;
    const rowsFor=id=>groups.get(id)||[],rootRows=rowsFor('');
    const rootHtml=rootRows.length?`<div class="inv-group inv-drop-zone" data-location-id="" style="--inv-depth:0"><div class="inv-head"><div><h4>Ohne Ort</h4><div class="subtle">Nicht zugeordnet</div></div><span class="count">${rootRows.length}</span></div>${rootRows.map(inventoryItemHtml).join('')}</div>`:'';
    const locHtml=locationOrder().map(({loc,depth})=>{if(locationHasCollapsedAncestor(loc.id))return '';const rows=rowsFor(loc.id),path=locationPath(loc.id),collapsed=collapsedInventoryLocations.has(loc.id),childCount=d.inventory.locations.filter(x=>x.parentId===loc.id).length,contentCount=rows.length+childCount;return `<div class="inv-group inv-drop-zone${collapsed?' collapsed':''}" data-location-id="${loc.id}" style="--inv-depth:${Math.min(depth,5)}"><div class="inv-head"><div class="inv-location-title"><span class="drag-handle" draggable="true" data-drag-kind="location" data-drag-id="${loc.id}" data-drag-label="${esc(loc.name)}" title="Behälter verschieben">⋮⋮</span><button type="button" class="inv-collapse-toggle" data-location-toggle="${loc.id}" aria-expanded="${collapsed?'false':'true'}"><span class="collapse-chevron">${collapsed?'▸':'▾'}</span><span class="inv-location-copy"><strong>${esc(loc.name)}</strong>${depth?`<small>${esc(path)}</small>`:''}</span></button></div><div class="inv-head-actions"><span class="count">${contentCount}</span><button type="button" class="danger-btn delete-location" data-delete-location="${loc.id}">Löschen</button></div></div>${collapsed?'':rows.map(inventoryItemHtml).join('')}${collapsed?'':(rows.length||childCount?'':'<div class="empty-comp">Leer – Gegenstände oder Behälter hierher ziehen.</div>')}</div>`;}).join('');
    $('#inventoryGroups').innerHTML=rootHtml+locHtml||'<div class="empty-comp">Noch kein eigenes Inventar angelegt.</div>';
    $$('#inventoryGroups .inv-row').forEach(row=>{const id=row.dataset.itemId;row.querySelector('.qty-minus').onclick=()=>changeQty(id,-1);row.querySelector('.qty-plus').onclick=()=>changeQty(id,1);row.querySelector('.delete-item').onclick=()=>{d.inventory.items=d.inventory.items.filter(x=>x.id!==id);saveCompanion();renderInventory();};});
    $$('#inventoryGroups [data-location-toggle]').forEach(btn=>btn.onclick=()=>{const id=btn.dataset.locationToggle;if(collapsedInventoryLocations.has(id))collapsedInventoryLocations.delete(id);else collapsedInventoryLocations.add(id);saveUiSet(INVENTORY_COLLAPSE_KEY,collapsedInventoryLocations);renderInventory();});
    $$('#inventoryGroups [data-delete-location]').forEach(btn=>btn.onclick=e=>{e.stopPropagation();requestDeleteLocation(btn.dataset.deleteLocation);});setupInventoryDragDrop();}
  function inventoryItemHtml(it){'''
replace_regex(r"  function renderInventory\(\)\{.*?\n  function inventoryItemHtml\(it\)\{",
              new_inventory, 1, 'inventory collapse/delete')

# Trefferzonen are raw W20 rolls: remove all zone modifiers, including TP+Zone.
replace_exact("    if(r.type==='zone')return {label:'Zonenmodifikator (+/−)',mode:'zone'};\n", '', 1, 'zone modifier label')
replace_exact("  function diceZoneModifier(){return Number($('#diceZoneModifier')?.value||0);}\n", '', 1, 'zone modifier helper')
replace_exact("    if(r.type==='damage'||r.type==='initiative'){const d=r.dice||[1,6,0],base=diceText(d);return `${base}${mod?` · zusätzlicher Modifikator ${signedNum(mod)}`:''}${r.withZone&&diceZoneModifier()?` · Zone ${signedNum(diceZoneModifier())}`:''}`;}\n",
              "    if(r.type==='damage'||r.type==='initiative'){const d=r.dice||[1,6,0],base=diceText(d);return `${base}${mod?` · zusätzlicher Modifikator ${signedNum(mod)}`:''}`;}\n", 1, 'zone modifier preview')
replace_exact("    if(r.type==='zone')return `Trefferzone per W20${mod?` · Zonenwurf ${signedNum(mod)}`:''}`;\n",
              "    if(r.type==='zone')return 'Trefferzone per W20';\n", 1, 'pure zone preview')
replace_exact("  function openDice(req){diceRequest={modifier:0,zoneModifier:0,...req};diceHasRolled=false;$('#diceTitle').textContent=req.title||'Würfeltisch';$('#diceSubtitle').textContent=req.subtitle||'';$('#diceOverlay').classList.remove('hidden');renderDiceControls();resetDiceStage();setTimeout(()=>$('#diceModifier')?.focus(),40);}\n",
              "  function openDice(req){diceRequest={modifier:0,...req};diceHasRolled=false;$('#diceTitle').textContent=req.title||'Würfeltisch';$('#diceSubtitle').textContent=req.subtitle||'';$('#diceOverlay').classList.remove('hidden');renderDiceControls();resetDiceStage();setTimeout(()=>$('#diceModifier')?.focus(),40);}\n", 1, 'openDice zone state')

new_controls = r'''  function renderDiceControls(){
    const r=diceRequest,spec=modifierSpec(r);let html='';
    if(r.type!=='zone')html=`<div class="dice-control"><label>${esc(spec.label)}</label><input id="diceModifier" type="number" step="1" inputmode="numeric" value="${Number(r.modifier||0)}"></div>`;
    if(r.type==='pool')html+=`<div class="dice-control"><label>Anzahl W6</label><input id="diceCount" type="number" min="1" max="30" step="1" inputmode="numeric" value="${Math.max(1,Number(r.count||2))}"></div>`;
    html+='<button type="button" id="diceReroll" class="dice-roll-btn">Würfeln</button><div id="dicePreview" class="dice-preview"></div>';
    $('#diceControls').innerHTML=html;$('#diceReroll').onclick=()=>performDiceRoll();['#diceModifier','#diceCount'].forEach(sel=>{$(sel)?.addEventListener('input',updateDicePreview);$(sel)?.addEventListener('keydown',e=>{if(e.key==='Enter')performDiceRoll();});});updateDicePreview();
  }
  function performDiceRoll(){'''
replace_regex(r"  function renderDiceControls\(\)\{.*?\n  \}\n  function performDiceRoll\(\)\{",
              new_controls, 1, 'dice controls without zone modifier')
replace_exact("      if(r.withZone){const raw=secureDie(20),zmod=diceZoneModifier(),adjusted=clamp(raw+zmod,1,20),zone=zoneFromD20(adjusted),rs=currentZoneArmor(zone);add(raw,20,'Trefferzone','zone',zone);result.zone={...zone,rs,roll:raw,adjusted,modifier:zmod};}\n",
              "      if(r.withZone){const raw=secureDie(20),zone=zoneFromD20(raw),rs=currentZoneArmor(zone);add(raw,20,'Trefferzone','zone',zone);result.zone={...zone,rs,roll:raw};}\n", 1, 'damage+zone raw roll')
replace_exact("    else if(r.type==='zone'){\n      const raw=secureDie(20),adjusted=clamp(raw+mod,1,20),zone=zoneFromD20(adjusted),rs=currentZoneArmor(zone);add(raw,20,'Trefferzone','zone',zone);result={title:zone.label,detail:`Trefferzonenwurf ${raw}${mod?` ${mod>0?'+':'−'} ${Math.abs(mod)} → ${adjusted}`:''}${rs!=null?` · RS in diesem Kampfset: ${rs}`:''}`,className:'',zone:{...zone,rs,roll:raw,adjusted,modifier:mod}};\n    }\n",
              "    else if(r.type==='zone'){\n      const raw=secureDie(20),zone=zoneFromD20(raw),rs=currentZoneArmor(zone);add(raw,20,'Trefferzone','zone',zone);result={title:zone.label,detail:`Trefferzonenwurf ${raw}${rs!=null?` · RS in diesem Kampfset: ${rs}`:''}`,className:'',zone:{...zone,rs,roll:raw}};\n    }\n", 1, 'pure zone raw roll')

# Context-aware prep text for pure zone roll (there is no modifier anymore).
replace_exact("    $('#diceStage').innerHTML='<div class=\"dice-ready\"><strong>Wurf vorbereiten</strong><span>Modifikator setzen und dann auf „Würfeln“ tippen.</span></div>';\n",
              "    $('#diceStage').innerHTML=`<div class=\"dice-ready\"><strong>Wurf vorbereiten</strong><span>${diceRequest?.type==='zone'?'Trefferzone direkt würfeln.':'Modifikator setzen und dann auf „Würfeln“ tippen.'}</span></div>`;\n", 1, 'dice prep copy')

# v16 styles.
v16_css = r'''
/* v16 Regel- und UI-Fixes */
.group-row td{padding:0}.group-toggle{display:flex;align-items:center;gap:7px;width:100%;min-height:42px;padding:9px 12px;border:0;background:transparent;color:inherit;text-align:left;cursor:pointer;font:inherit;text-transform:inherit;letter-spacing:inherit}.group-toggle:hover{background:#2b3038}.group-toggle:focus-visible,.inv-collapse-toggle:focus-visible,.money-history-toggle:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}.group-toggle .collapse-chevron,.group-toggle .group-label,.group-toggle .group-count{margin-left:0}.collapse-chevron{display:inline-block;width:1em;color:#b9a26b;font-weight:900}.group-toggle .group-count{color:#8e99a8;font-weight:600;margin-left:2px}.inv-head-actions{display:flex;align-items:center;gap:8px;flex-wrap:wrap;justify-content:flex-end}.inv-collapse-toggle{display:flex;align-items:flex-start;gap:7px;min-width:0;border:0;background:transparent;color:inherit;text-align:left;padding:0;cursor:pointer}.inv-location-copy{display:flex;flex-direction:column;min-width:0}.inv-location-copy strong{color:#e8d29c;font-size:.94rem}.inv-location-copy small{margin-top:2px;color:var(--muted);font-size:.68rem}.inv-group.collapsed{padding-bottom:9px}.money-history{margin-top:10px;border-top:1px solid #2b3038;padding-top:8px}.money-history-toggle{display:flex;align-items:center;gap:7px;width:100%;min-height:40px;border:0;background:transparent;color:#e8d29c;text-align:left;padding:5px 2px;cursor:pointer;font-weight:760}.money-history-toggle .count{margin-left:auto}.location-delete-dialog{max-width:min(520px,calc(100% - 28px));border:1px solid #4a515d;border-radius:12px;background:#171a1f;color:var(--text);padding:0;box-shadow:0 24px 70px rgba(0,0,0,.6)}.location-delete-dialog::backdrop{background:rgba(0,0,0,.68)}.location-delete-card{padding:18px}.location-delete-card h3{margin:0 0 8px;color:#f0c979}.location-delete-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}
@media(max-width:650px){.inv-head{align-items:flex-start}.inv-head-actions{gap:5px}.delete-location{padding:6px 7px;font-size:.7rem}.group-toggle{min-height:44px}.location-delete-actions>*{flex:1 1 100%}}
'''
replace_exact('</style>', v16_css + '\n</style>', 1, 'v16 CSS')

# Final sanity checks.
if 'diceZoneModifier' in text or 'zoneModifier' in text:
    raise RuntimeError('zone modifier code remains after patch')
if "dancer?'3W6':'1W6'" in text:
    raise RuntimeError('Klingentänzer 3W6 code remains after patch')
if "['Gesellschaftlich', new Set(['Betören','Etikette','Falschspiel'" in text:
    raise RuntimeError('Falschspiel still classified as Gesellschaftlich')
if '/* v16 Regel- und UI-Fixes */' not in text:
    raise RuntimeError('v16 style marker missing')

PATH.write_text(text, encoding='utf-8')

# Syntax-check every inline script with Node.js.
scripts = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', text, flags=re.S|re.I)
if not scripts:
    raise RuntimeError('no inline scripts found')
for i, script in enumerate(scripts):
    with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as fh:
        fh.write(script)
        tmp = fh.name
    proc = subprocess.run(['node','--check',tmp], text=True, capture_output=True)
    Path(tmp).unlink(missing_ok=True)
    if proc.returncode:
        raise RuntimeError(f'JavaScript syntax check failed for inline script {i}:\n{proc.stderr}')

print(f'Applied HeldenMobil v16 patch: {len(original)} -> {len(text)} bytes; {len(scripts)} inline script(s) syntax-checked.')
