from pathlib import Path

p = Path('index.html')
t = p.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global t
    if old not in t:
        raise SystemExit(f'missing marker: {label}')
    t = t.replace(old, new, 1)

replace_once('HeldenMobil – HLD PoC v17.3.3', 'HeldenMobil – HLD PoC v18.0', 'title')
replace_once('const COMP_SCHEMA=6;', 'const COMP_SCHEMA=7;', 'schema')
replace_once("for(const v of [5,4,3,2,1])", "for(const v of [6,5,4,3,2,1])", 'migration versions')
replace_once("localStorage.removeItem(companionStorageKey(5));", "localStorage.removeItem(companionStorageKey(6));localStorage.removeItem(companionStorageKey(5));", 'reset v6')
replace_once('HeldenMobil Qualitätsbericht v17.3.3', 'HeldenMobil Qualitätsbericht v18.0', 'audit text version')
replace_once("lastQualityAudit={version:'17.3'", "lastQualityAudit={version:'18.0'", 'audit json version')

# Add a generic inventory type without forcing magical weapons/armour into it.
replace_once('<option>Handelsgut</option></select>', '<option>Handelsgut</option><option>Magischer Gegenstand</option></select>', 'inventory type')

# Schema-v7 normalization: magical data stays on the inventory item.
marker = """  function normalizeCompanion(d){
"""
helpers = r"""  function magicOptionalInt(v){if(v===null||v===undefined||v==='')return null;const n=Math.floor(Number(v));return Number.isFinite(n)?Math.max(0,n):null;}
  function magicOptionalNumber(v){if(v===null||v===undefined||v==='')return null;const n=Number(v);return Number.isFinite(n)?n:null;}
  function normalizeMagicEffect(raw,index=0){const r=raw&&typeof raw==='object'?raw:{},max=magicOptionalInt(r.maxCharges);let charges=magicOptionalInt(r.charges);if(max!=null){if(charges==null)charges=max;charges=Math.min(max,charges);}else charges=null;return {id:String(r.id||uid('effect')),name:String(r.name||`Wirkung ${index+1}`),type:String(r.type||'Zauber'),activation:String(r.activation||''),charges,maxCharges:max,zfp:magicOptionalNumber(r.zfp),asp:magicOptionalNumber(r.asp),recharge:String(r.recharge||''),note:String(r.note||'')};}
  function normalizeInventoryMagic(it){if(!it||typeof it!=='object')return it;const out={...it};if(out.magic&&typeof out.magic==='object'){const m=out.magic;out.magic={kind:String(m.kind||'Artefakt'),effects:(Array.isArray(m.effects)?m.effects:[]).map((x,i)=>normalizeMagicEffect(x,i))};}return out;}

  function normalizeCompanion(d){
"""
replace_once(marker, helpers, 'magic normalization helpers')
replace_once("x.inventory.items=Array.isArray(x.inventory.items)?x.inventory.items:[];", "x.inventory.items=Array.isArray(x.inventory.items)?x.inventory.items.map(normalizeInventoryMagic):[];", 'normalize inventory magic')

# Inventory UI card for magical properties.
old = """      </div>
      <div class=\"comp-card money-card\">
"""
new = """      </div>
      <div id=\"artifactCard\" class=\"comp-card artifact-card\">
        <div class=\"inv-head\"><div><h4>Magische Gegenstände</h4><div class=\"subtle\">Magische Eigenschaften gehören direkt zum Inventargegenstand. Waffen, Rüstungen, Ringe usw. bleiben deshalb ganz normal im Inventar; hier verwaltest du nur ihre Wirkungen.</div></div><span class=\"count\" id=\"artifactCount\"></span></div>
        <div class=\"form-grid artifact-form\">
          <div class=\"field wide\"><label>Inventargegenstand</label><select id=\"artifactItem\"></select></div>
          <div class=\"field\"><label>Art</label><select id=\"artifactKind\"><option>Artefakt</option><option>Matrixgeber</option><option>Gebundener Gegenstand</option><option>Magischer Gegenstand</option><option>Sonstiges</option></select></div>
          <div class=\"field wide\"><label>Wirkung / Zauber</label><input id=\"artifactEffectName\" placeholder=\"z. B. Balsam oder Schutz vor Feuer\"></div>
          <div class=\"field\"><label>Typ</label><select id=\"artifactEffectType\"><option>Zauber</option><option>Artefaktwirkung</option><option>Ritual</option><option>Passiv</option><option>Sonstiges</option></select></div>
          <div class=\"field wide\"><label>Auslöser</label><input id=\"artifactActivation\" placeholder=\"Wort, Berührung, Handlung …\"></div>
          <div class=\"field\"><label>Ladungen aktuell</label><input id=\"artifactCharges\" type=\"number\" min=\"0\" step=\"1\" placeholder=\"∞\"></div>
          <div class=\"field\"><label>Ladungen max.</label><input id=\"artifactMaxCharges\" type=\"number\" min=\"0\" step=\"1\" placeholder=\"∞\"></div>
          <div class=\"field\"><label>ZfP*</label><input id=\"artifactZfp\" type=\"number\" min=\"0\" placeholder=\"optional\"></div>
          <div class=\"field\"><label>AsP</label><input id=\"artifactAsp\" type=\"number\" min=\"0\" placeholder=\"optional\"></div>
          <div class=\"field wide\"><label>Aufladung</label><input id=\"artifactRecharge\" placeholder=\"z. B. einmal monatlich / nicht aufladbar\"></div>
          <div class=\"field full\"><label>Notiz</label><input id=\"artifactEffectNote\" placeholder=\"Varianten, Einschränkungen, bekannte Werte …\"></div>
        </div>
        <div class=\"toolbar-row\"><button class=\"action-btn primary\" id=\"addArtifactEffect\">Wirkung hinzufügen</button></div>
        <div id=\"artifactList\" class=\"artifact-list\"></div>
      </div>
      <div class=\"comp-card money-card\">
"""
replace_once(old, new, 'artifact inventory card')

# CSS for magical items.
css_marker = "\n\n/* v12 OneDrive / Microsoft Graph beta */"
css = r"""

/* v18 magical inventory items */
.artifact-card{margin-top:12px}.artifact-form{margin-top:10px}.artifact-list{display:flex;flex-direction:column;gap:10px;margin-top:12px}.artifact-item{border:1px solid #4c4432;background:linear-gradient(180deg,#1a1b20,#15171b);border-radius:11px;padding:11px}.artifact-item-head{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}.artifact-item-title{font-weight:800;color:#f0d58d}.artifact-item-meta{font-size:.69rem;color:var(--muted);margin-top:3px}.artifact-effects{display:flex;flex-direction:column;gap:7px;margin-top:9px}.artifact-effect{border:1px solid #303744;background:#12161b;border-radius:9px;padding:9px}.artifact-effect-head{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}.artifact-effect-name{font-weight:760}.artifact-effect-meta{font-size:.69rem;color:var(--muted);margin-top:3px;line-height:1.4}.artifact-effect-actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}.magic-pill{border-color:#675486!important;color:#d7c2ff!important;background:#211a2c!important}.charge-badge{display:inline-block;border:1px solid #536746;color:#bde2a7;background:#172116;border-radius:999px;padding:2px 7px;font-size:.64rem;white-space:nowrap}.charge-badge.empty{border-color:#6b4141;color:#eca7a7;background:#271717}.artifact-kind{display:inline-block;border:1px solid #625639;color:#e7cc86;background:#252117;border-radius:999px;padding:2px 7px;font-size:.64rem;margin-left:6px}.artifact-empty-effect{color:var(--muted);font-size:.76rem;padding:7px 0}.dashboard-magic-section-title{margin:9px 0 6px;color:#d9bd79;font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;font-weight:800}.dashboard-artifact-location{color:#8f99a7}.artifact-manage-row{margin-top:8px}
@media(max-width:650px){.artifact-item-head,.artifact-effect-head{flex-direction:column}.artifact-effect-actions .action-btn,.artifact-effect-actions .danger-btn{padding:6px 8px}}
"""
replace_once(css_marker, css + css_marker, 'artifact css')

# Add magical-item behavior directly after inventoryItemHtml.
old_func = r"""  function inventoryItemHtml(it){const consum=isConsumableItem(it),meta=[it.note||'',it.weight!=null&&it.weight!==''?`Gewicht ${it.weight}`:'',it.price?`Listenpreis ${it.price}`:''].filter(Boolean).join(' · ');return `<div class=\"inv-row\" data-item-id=\"${it.id}\"><div><div class=\"inv-name-line\"><span class=\"drag-handle\" draggable=\"true\" data-drag-kind=\"item\" data-drag-id=\"${it.id}\" data-drag-label=\"${esc(it.name)}\" title=\"Gegenstand verschieben\">⋮⋮</span><div><div class=\"inv-name ${/alchem/i.test(it.type||'')?'alchemy':''}\">${esc(it.name)}${it.quality?` <span class=\"tag spec\">${esc(it.quality)}</span>`:''}${it.source?` <span class=\"source-pill\">${esc(it.source)}</span>`:''}${consum?'<span class=\"source-pill consumable-pill\">Verbrauch</span>':''}</div><div class=\"inv-note\">${esc(meta)}</div></div></div></div><div class=\"inv-type\"><span class=\"badge-type\">${esc(it.type||'Gegenstand')}</span></div><div class=\"qty-controls\"><button class=\"mini-btn qty-minus\" title=\"${consum?'1 verbrauchen':'Anzahl -1'}\">−</button><strong>${it.qty}</strong><button class=\"mini-btn qty-plus\">+</button></div><div class=\"inv-location subtle\">${esc(it.locationId?locationPath(it.locationId):'')}</div><div class=\"inv-actions\"><button class=\"danger-btn delete-item\">Löschen</button></div></div>`;}
"""
new_func = r"""  function inventoryItemHtml(it){const consum=isConsumableItem(it),magical=!!it.magic||/magischer gegenstand/i.test(it.type||''),effectCount=it.magic?.effects?.length||0,meta=[it.note||'',it.weight!=null&&it.weight!==''?`Gewicht ${it.weight}`:'',it.price?`Listenpreis ${it.price}`:''].filter(Boolean).join(' · ');return `<div class=\"inv-row\" data-item-id=\"${it.id}\"><div><div class=\"inv-name-line\"><span class=\"drag-handle\" draggable=\"true\" data-drag-kind=\"item\" data-drag-id=\"${it.id}\" data-drag-label=\"${esc(it.name)}\" title=\"Gegenstand verschieben\">⋮⋮</span><div><div class=\"inv-name ${/alchem/i.test(it.type||'')?'alchemy':''}\">${esc(it.name)}${it.quality?` <span class=\"tag spec\">${esc(it.quality)}</span>`:''}${it.source?` <span class=\"source-pill\">${esc(it.source)}</span>`:''}${consum?'<span class=\"source-pill consumable-pill\">Verbrauch</span>':''}${magical?`<span class=\"source-pill magic-pill\">Magisch${effectCount?` · ${effectCount}`:''}</span>`:''}</div><div class=\"inv-note\">${esc(meta)}</div></div></div></div><div class=\"inv-type\"><span class=\"badge-type\">${esc(it.type||'Gegenstand')}</span></div><div class=\"qty-controls\"><button class=\"mini-btn qty-minus\" title=\"${consum?'1 verbrauchen':'Anzahl -1'}\">−</button><strong>${it.qty}</strong><button class=\"mini-btn qty-plus\">+</button></div><div class=\"inv-location subtle\">${esc(it.locationId?locationPath(it.locationId):'')}</div><div class=\"inv-actions\">${magical?'<button class=\"action-btn magic-item-open\">Magie</button>':''}<button class=\"danger-btn delete-item\">Löschen</button></div></div>`;}
  function artifactItems(){const items=companionState.data?.inventory?.items||[];return items.filter(it=>it.magic||/magischer gegenstand/i.test(it.type||''));}
  function artifactEffectCount(){return artifactItems().reduce((n,it)=>n+(it.magic?.effects?.length||0),0);}
  function refreshArtifactItemSelect(){const s=$('#artifactItem'),d=companionState.data;if(!s||!d)return;const old=s.value,items=d.inventory.items;s.innerHTML=items.map(it=>`<option value=\"${esc(it.id)}\">${esc(it.name)}${it.locationId?` · ${esc(locationPath(it.locationId))}`:''}</option>`).join('')||'<option value=\"\">Zuerst einen Gegenstand anlegen</option>';if(old&&items.some(x=>x.id===old))s.value=old;$('#addArtifactEffect').disabled=!items.length;}
  function artifactChargeText(effect){return effect.maxCharges==null?'∞':`${Math.max(0,Number(effect.charges||0))} / ${effect.maxCharges}`;}
  function artifactLookup(itemId,effectId){const item=companionState.data?.inventory?.items?.find(x=>x.id===itemId),effect=item?.magic?.effects?.find(x=>x.id===effectId);return {item,effect};}
  function clearArtifactForm(){for(const id of ['artifactEffectName','artifactActivation','artifactCharges','artifactMaxCharges','artifactZfp','artifactAsp','artifactRecharge','artifactEffectNote']){const el=$(`#${id}`);if(el)el.value='';}}
  function addArtifactEffect(){const d=companionState.data,item=d?.inventory?.items?.find(x=>x.id===$('#artifactItem').value),name=$('#artifactEffectName').value.trim();if(!item){alert('Bitte zuerst einen Inventargegenstand auswählen.');return;}if(!name){alert('Bitte eine Wirkung oder einen Zauber angeben.');return;}const max=magicOptionalInt($('#artifactMaxCharges').value);let charges=magicOptionalInt($('#artifactCharges').value);if(max!=null){if(charges==null)charges=max;charges=Math.min(max,charges);}else charges=null;item.magic=item.magic&&typeof item.magic==='object'?item.magic:{kind:'Artefakt',effects:[]};item.magic.kind=$('#artifactKind').value||item.magic.kind||'Artefakt';item.magic.effects=Array.isArray(item.magic.effects)?item.magic.effects:[];item.magic.effects.push(normalizeMagicEffect({id:uid('effect'),name,type:$('#artifactEffectType').value||'Zauber',activation:$('#artifactActivation').value.trim(),charges,maxCharges:max,zfp:magicOptionalNumber($('#artifactZfp').value),asp:magicOptionalNumber($('#artifactAsp').value),recharge:$('#artifactRecharge').value.trim(),note:$('#artifactEffectNote').value.trim()}));clearArtifactForm();saveCompanion();renderInventory();}
  function triggerArtifactEffect(itemId,effectId){const {item,effect}=artifactLookup(itemId,effectId);if(!item||!effect)return;if(effect.maxCharges!=null){const cur=Math.max(0,Number(effect.charges||0));if(cur<=0){alert(`${item.name} – ${effect.name}: keine Ladungen mehr.`);return;}effect.charges=cur-1;}const charge=effect.maxCharges!=null?` · ${artifactChargeText(effect)} Ladungen`:'';logEvent(`Magischer Gegenstand ${item.name}: ${effect.name} ausgelöst${charge}`,'magic');saveCompanion();renderInventory();renderAdventures();}
  function changeArtifactCharge(itemId,effectId,delta){const {effect}=artifactLookup(itemId,effectId);if(!effect||effect.maxCharges==null)return;effect.charges=Math.max(0,Math.min(effect.maxCharges,Number(effect.charges||0)+delta));saveCompanion();renderInventory();}
  function deleteArtifactEffect(itemId,effectId){const item=companionState.data?.inventory?.items?.find(x=>x.id===itemId);if(!item?.magic)return;item.magic.effects=(item.magic.effects||[]).filter(x=>x.id!==effectId);if(!item.magic.effects.length)delete item.magic;saveCompanion();renderInventory();}
  function removeArtifactMagic(itemId){const item=companionState.data?.inventory?.items?.find(x=>x.id===itemId);if(!item)return;delete item.magic;saveCompanion();renderInventory();}
  function renderArtifacts(){const d=companionState.data,host=$('#artifactList');if(!d||!host)return;refreshArtifactItemSelect();const items=artifactItems(),effects=artifactEffectCount();$('#artifactCount').textContent=`${items.length} Gegenstände · ${effects} Wirkungen`;host.innerHTML=items.map(it=>{const rows=(it.magic?.effects||[]).map(fx=>{const empty=fx.maxCharges!=null&&Number(fx.charges||0)<=0,meta=[fx.type||'',fx.activation?`Auslöser: ${fx.activation}`:'',fx.zfp!=null?`ZfP* ${fx.zfp}`:'',fx.asp!=null?`${fx.asp} AsP`:'',fx.recharge?`Aufladung: ${fx.recharge}`:'',fx.note||''].filter(Boolean).join(' · ');return `<div class=\"artifact-effect\" data-effect-id=\"${fx.id}\"><div class=\"artifact-effect-head\"><div><div class=\"artifact-effect-name\">${esc(fx.name)}</div><div class=\"artifact-effect-meta\">${esc(meta)}</div></div><span class=\"charge-badge ${empty?'empty':''}\">${artifactChargeText(fx)} Ladungen</span></div><div class=\"artifact-effect-actions\"><button class=\"action-btn artifact-trigger\" ${empty?'disabled':''}>Auslösen</button>${fx.maxCharges!=null?'<button class=\"mini-btn artifact-charge-minus\">−1</button><button class=\"mini-btn artifact-charge-plus\">+1</button>':''}<button class=\"danger-btn artifact-effect-delete\">Wirkung löschen</button></div></div>`;}).join('')||'<div class=\"artifact-empty-effect\">Noch keine magische Wirkung eingetragen.</div>';return `<div class=\"artifact-item\" data-artifact-item=\"${it.id}\"><div class=\"artifact-item-head\"><div><div class=\"artifact-item-title\">${esc(it.name)} <span class=\"artifact-kind\">${esc(it.magic?.kind||'Magischer Gegenstand')}</span></div><div class=\"artifact-item-meta\">${esc(it.type||'Gegenstand')}${it.locationId?` · ${esc(locationPath(it.locationId))}`:''}</div></div>${it.magic?'<button class=\"danger-btn artifact-remove-magic\">Magische Daten entfernen</button>':''}</div><div class=\"artifact-effects\">${rows}</div></div>`;}).join('')||'<div class=\"empty-comp\">Noch keine magischen Gegenstände erfasst. Wähle oben einen Inventargegenstand und füge seine erste Wirkung hinzu.</div>';host.querySelectorAll('[data-artifact-item]').forEach(row=>{const itemId=row.dataset.artifactItem;row.querySelector('.artifact-remove-magic')?.addEventListener('click',()=>removeArtifactMagic(itemId));row.querySelectorAll('.artifact-effect').forEach(er=>{const effectId=er.dataset.effectId;er.querySelector('.artifact-trigger')?.addEventListener('click',()=>triggerArtifactEffect(itemId,effectId));er.querySelector('.artifact-charge-minus')?.addEventListener('click',()=>changeArtifactCharge(itemId,effectId,-1));er.querySelector('.artifact-charge-plus')?.addEventListener('click',()=>changeArtifactCharge(itemId,effectId,1));er.querySelector('.artifact-effect-delete')?.addEventListener('click',()=>deleteArtifactEffect(itemId,effectId));});});}
"""
replace_once(old_func, new_func, 'inventory magic functions')

# Ensure inventory render updates artifact editor and offers a shortcut from magical rows.
old = """    $$('#inventoryGroups .inv-row').forEach(row=>{const id=row.dataset.itemId;row.querySelector('.qty-minus').onclick=()=>changeQty(id,-1);row.querySelector('.qty-plus').onclick=()=>changeQty(id,1);row.querySelector('.delete-item').onclick=()=>{d.inventory.items=d.inventory.items.filter(x=>x.id!==id);saveCompanion();renderInventory();};});
"""
new = """    $$('#inventoryGroups .inv-row').forEach(row=>{const id=row.dataset.itemId;row.querySelector('.qty-minus').onclick=()=>changeQty(id,-1);row.querySelector('.qty-plus').onclick=()=>changeQty(id,1);row.querySelector('.magic-item-open')?.addEventListener('click',()=>{if($('#artifactItem'))$('#artifactItem').value=id;$('#artifactCard')?.scrollIntoView({behavior:'smooth',block:'start'});});row.querySelector('.delete-item').onclick=()=>{d.inventory.items=d.inventory.items.filter(x=>x.id!==id);saveCompanion();renderInventory();};});
"""
replace_once(old, new, 'inventory magic shortcut')
replace_once("    $$('#inventoryGroups [data-delete-location]').forEach(btn=>btn.onclick=e=>{e.stopPropagation();requestDeleteLocation(btn.dataset.deleteLocation);});setupInventoryDragDrop();}", "    $$('#inventoryGroups [data-delete-location]').forEach(btn=>btn.onclick=e=>{e.stopPropagation();requestDeleteLocation(btn.dataset.deleteLocation);});setupInventoryDragDrop();renderArtifacts();}", 'render artifacts from inventory')

# Add form listener.
replace_once("$('#addLocation').addEventListener('click',addLocation);$('#addItem').addEventListener('click',addItem);$('#addMoney').addEventListener('click',addMoneyTransaction);", "$('#addLocation').addEventListener('click',addLocation);$('#addItem').addEventListener('click',addItem);$('#addArtifactEffect').addEventListener('click',addArtifactEffect);$('#addMoney').addEventListener('click',addMoneyTransaction);", 'artifact listener')

# Dashboard: Zauberspeicher and magical inventory items share one area without sharing data models.
start = t.find('  function renderDashboardMagic(){')
end = t.find('\n  function renderDashboard(){', start)
if start < 0 or end < 0:
    raise SystemExit('missing marker: renderDashboardMagic block')
new_dashboard = r"""  function renderDashboardMagic(){
    const host=$('#dashboardMagic'),d=companionState.data;if(!host||!d)return;const slots=[...(d.magic?.staffSlots||[])].sort((a,b)=>(a.slot||0)-(b.slot||0)),hasStorage=state.current?.sfSet?.has('Stabzauber: Zauberspeicher');
    const staffRows=slots.map(x=>`<div class=\"dashboard-magic-row ${x.loaded?'':'empty-slot'}\"><div class=\"dashboard-magic-title\"><span class=\"slot-badge\">Slot ${x.slot}</span>${esc(x.spell)} ${x.loaded?'<span class=\"loaded-badge\">geladen</span>':'<span class=\"empty-badge\">leer</span>'}</div><div class=\"dashboard-magic-meta\">${x.zfp!=null?`ZfP* ${x.zfp} · `:''}${x.asp!=null?`${x.asp} AsP · `:''}${esc(x.note||'')}</div><div class=\"dashboard-magic-actions\"><button type=\"button\" class=\"action-btn dashboard-toggle-slot\" data-slot-id=\"${x.id}\">${x.loaded?'Auslösen':'Wieder laden'}</button></div></div>`).join('');
    const artifactRows=artifactItems().flatMap(it=>(it.magic?.effects||[]).map(fx=>{const empty=fx.maxCharges!=null&&Number(fx.charges||0)<=0,meta=[it.magic?.kind||'Magischer Gegenstand',fx.type||'',fx.activation?`Auslöser: ${fx.activation}`:'',fx.maxCharges!=null?`${artifactChargeText(fx)} Ladungen`:'unbegrenzt',it.locationId?locationPath(it.locationId):''].filter(Boolean).join(' · ');return `<div class=\"dashboard-magic-row ${empty?'empty-slot':''}\"><div class=\"dashboard-magic-title\"><span class=\"source-pill magic-pill\">Magisch</span>${esc(it.name)} · ${esc(fx.name)}</div><div class=\"dashboard-magic-meta\">${esc(meta)}</div><div class=\"dashboard-magic-actions\"><button type=\"button\" class=\"action-btn dashboard-artifact-trigger\" data-artifact-item=\"${it.id}\" data-artifact-effect=\"${fx.id}\" ${empty?'disabled':''}>Auslösen</button></div></div>`;})).join('');
    const staffBlock=(hasStorage||slots.length)?`<div class=\"dashboard-magic-section-title\">Zauberspeicher</div><div class=\"dashboard-magic-list\">${staffRows||(hasStorage?'<div class=\"empty-comp\">Zauberspeicher vorhanden, aber noch nicht belegt.</div>':'')}</div>`:'';
    const artifactBlock=`<div class=\"dashboard-magic-section-title\">Magische Gegenstände</div><div class=\"dashboard-magic-list\">${artifactRows||'<div class=\"empty-comp\">Noch keine magischen Gegenstände erfasst.</div>'}</div><div class=\"artifact-manage-row\"><button type=\"button\" id=\"dashboardMagicManage\" class=\"action-btn\">Im Inventar verwalten</button></div>`;
    host.innerHTML=staffBlock+artifactBlock;host.querySelectorAll('.dashboard-toggle-slot').forEach(b=>b.onclick=()=>toggleStaffSlot(b.dataset.slotId));host.querySelectorAll('.dashboard-artifact-trigger').forEach(b=>b.onclick=()=>triggerArtifactEffect(b.dataset.artifactItem,b.dataset.artifactEffect));$('#dashboardMagicManage')?.addEventListener('click',()=>{const tab=$('.tab[data-tab=\"inventory\"]');tab?.click();setTimeout(()=>$('#artifactCard')?.scrollIntoView({behavior:'smooth',block:'start'}),30);});
  }
"""
t = t[:start] + new_dashboard + t[end:]

# Data metadata now shows magical inventory count.
old = """<div><strong>Zauberspeicher:</strong> ${d.magic.staffSlots.length} Slots</div><div><strong>Zuletzt lokal gespeichert:</strong>"""
new = """<div><strong>Zauberspeicher:</strong> ${d.magic.staffSlots.length} Slots</div><div><strong>Magische Gegenstände:</strong> ${artifactItems().length} · ${artifactEffectCount()} Wirkungen</div><div><strong>Zuletzt lokal gespeichert:</strong>"""
replace_once(old, new, 'data meta magical items')

p.write_text(t, encoding='utf-8')
print('v18.0 magical items patch applied')
