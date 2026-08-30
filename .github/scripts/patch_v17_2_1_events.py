from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    s = s.replace(old, new, 1)


def replace_block(start: str, end: str, new_block: str, label: str) -> None:
    global s
    a = s.find(start)
    if a < 0:
        raise SystemExit(f'{label}: start marker missing')
    b = s.find(end, a)
    if b < 0:
        raise SystemExit(f'{label}: end marker missing')
    if s.find(start, a + 1) >= 0:
        raise SystemExit(f'{label}: start marker not unique')
    s = s[:a] + new_block + s[b:]


# Version.
replace_once('<title>HeldenMobil – HLD PoC v17.2</title>', '<title>HeldenMobil – HLD PoC v17.2.1</title>', 'title')
replace_once('<div class="sub">DSA 4.1 · HLD + Begleitdaten v17.2</div>', '<div class="sub">DSA 4.1 · HLD + Begleitdaten v17.2.1</div>', 'header sub')
replace_once('<div class="badge">Beta v17.2</div>', '<div class="badge">Beta v17.2.1</div>', 'header badge')

# Compact event presentation.
css_anchor = '/* v17.1.3 final optical alignment */'
css_add = '''/* v17.2.1 compact adventure event log */
.event-energy-label{color:#f0c979;font-weight:850}
.event-energy-range{color:#d4dae3}
.event-list-more{display:flex;justify-content:center;padding:8px 0 2px;border-top:1px solid #272d35;margin-top:4px}
.event-list-more .mini-btn{min-width:150px}

'''
if s.count(css_anchor) != 1:
    raise SystemExit('CSS anchor missing or duplicated')
s = s.replace(css_anchor, css_add + css_anchor, 1)

# Event state + 25-second aggregation window.
replace_once(
    "  const companionState={data:null,localExists:false};\n  const COMP_SCHEMA=6;",
    "  const companionState={data:null,localExists:false};\n  const ENERGY_EVENT_WINDOW_MS=25000,expandedEventAdventures=new Set();\n  const COMP_SCHEMA=6;",
    'event constants',
)

# Normalize old click-by-click energy events on load as well.
replace_once(
    "    x.adventures=x.adventures.map(a=>{const status={...freshAdventureStatus(),...(a.status||{})};normalizeStatusWounds(status);return {...a,events:Array.isArray(a.events)?a.events:[],learning:Array.isArray(a.learning)?a.learning:[],combatBySet:(a.combatBySet&&typeof a.combatBySet==='object')?a.combatBySet:{},status};});",
    "    x.adventures=x.adventures.map(a=>{const status={...freshAdventureStatus(),...(a.status||{})};normalizeStatusWounds(status);return {...a,events:normalizeAdventureEvents(a.events),learning:Array.isArray(a.learning)?a.learning:[],combatBySet:(a.combatBySet&&typeof a.combatBySet==='object')?a.combatBySet:{},status};});",
    'event normalization hook',
)

# Replace status/event helpers with structured energy aggregation.
helper_start = "  function energyMaxMap(){return new Map(deriveBasis(state.current.props).map(x=>[x.name,x.value]));}\n"
helper_end = "  function renderStatus(){\n"
new_helpers = '''  function energyMaxMap(){return new Map(deriveBasis(state.current.props).map(x=>[x.name,x.value]));}
  function statusKeyFor(label){return {LeP:'lep',AuP:'aup',AsP:'asp',KaP:'kap'}[label];}
  function energyEventText(label,from,to){const delta=Number(to)-Number(from),signed=delta>0?`+${delta}`:`${delta}`;return `${label} ${signed} · ${from} → ${to}`;}
  function parseLegacyEnergyEvent(raw){
    if(!raw||typeof raw!=='object')return null;
    if(raw.type==='energy'&&raw.energy&&Number.isFinite(Number(raw.from))&&Number.isFinite(Number(raw.to))){const e={...raw,from:Number(raw.from),to:Number(raw.to)};e.delta=e.to-e.from;e.startedAt=e.startedAt||e.at||e.lastAt||null;e.lastAt=e.lastAt||e.at||e.startedAt||null;e.text=energyEventText(e.energy,e.from,e.to);return e;}
    if(raw.type!=='status')return null;
    const m=/^(LeP|AuP|AsP|KaP)\s+[+-]?\d+:\s*(-?\d+)\s*→\s*(-?\d+)\s*$/.exec(String(raw.text||''));if(!m)return null;
    const e={...raw,type:'energy',energy:m[1],from:Number(m[2]),to:Number(m[3])};e.delta=e.to-e.from;e.startedAt=e.at||null;e.lastAt=e.at||null;e.text=energyEventText(e.energy,e.from,e.to);return e;
  }
  function normalizeAdventureEvents(events){
    const out=[],lastByEnergy=new Map();
    for(const raw of (Array.isArray(events)?events:[])){
      const e=parseLegacyEnergyEvent(raw);if(!e){out.push(raw);continue;}
      const nowMs=Date.parse(e.lastAt||e.at||'')||0,prev=lastByEnergy.get(e.energy),prevMs=prev?(Date.parse(prev.lastAt||prev.at||'')||0):0;
      if(prev&&nowMs&&prevMs&&nowMs>=prevMs&&nowMs-prevMs<=ENERGY_EVENT_WINDOW_MS&&Number(prev.to)===Number(e.from)){
        prev.to=e.to;prev.delta=prev.to-prev.from;prev.lastAt=e.lastAt||e.at||prev.lastAt;prev.at=e.at||prev.at;prev.text=energyEventText(prev.energy,prev.from,prev.to);
        const idx=out.indexOf(prev);if(idx>=0)out.splice(idx,1);if(prev.delta!==0){out.push(prev);lastByEnergy.set(prev.energy,prev);}else lastByEnergy.delete(prev.energy);continue;
      }
      if(e.delta!==0){out.push(e);lastByEnergy.set(e.energy,e);}
    }
    return out;
  }
  function activeAdventure(){const d=companionState.data;return d?.adventures.find(a=>a.id===d.activeAdventureId)||null;}
  function activeAdventureStatus(){return activeAdventure()?.status||null;}
  function logEvent(text,type='note'){
    const a=activeAdventure();if(!a)return;a.events=Array.isArray(a.events)?a.events:[];a.events.push({id:uid('evt'),at:new Date().toISOString(),type,text});
  }
  function logEnergyEvent(label,before,after){
    const a=activeAdventure();before=Number(before);after=Number(after);if(!a||before===after)return;a.events=Array.isArray(a.events)?a.events:[];const nowMs=Date.now(),now=new Date(nowMs).toISOString();let found=-1,event=null;
    for(let i=a.events.length-1;i>=0;i--){const parsed=parseLegacyEnergyEvent(a.events[i]);if(!parsed||parsed.energy!==label)continue;const lastMs=Date.parse(parsed.lastAt||parsed.at||'')||0;if(lastMs&&nowMs>=lastMs&&nowMs-lastMs<=ENERGY_EVENT_WINDOW_MS&&Number(parsed.to)===before){found=i;event=parsed;}break;}
    if(found>=0&&event){a.events.splice(found,1);event.to=after;event.delta=event.to-event.from;event.lastAt=now;event.at=now;event.text=energyEventText(label,event.from,event.to);if(event.delta!==0)a.events.push(event);return;}
    a.events.push({id:uid('evt'),at:now,lastAt:now,startedAt:now,type:'energy',energy:label,from:before,to:after,delta:after-before,text:energyEventText(label,before,after)});
  }
  function adjustStatus(label,delta){const a=activeAdventure(),s=a?.status,k=statusKeyFor(label);if(!s||!k)return;const max=energyMaxMap().get(label);const before=Number(s[k]??max??0);let after=before+delta;if(max!=null)after=Math.min(max,after);if(after===before)return;s[k]=after;logEnergyEvent(label,before,after);saveCompanion();renderStatus();renderAdventures();}
'''
replace_block(helper_start, helper_end, new_helpers, 'status/event helpers')

# Event editing/deleting/display helpers. Automatic status/energy events delete immediately;
# manual notes keep the safety confirmation.
old_event_ops = '''  function editEvent(advId,eventId){const a=companionState.data.adventures.find(x=>x.id===advId),e=a?.events?.find(x=>x.id===eventId);if(!e)return;const txt=prompt('Ereignis bearbeiten',e.text||'');if(txt===null)return;const clean=txt.trim();if(!clean)return;e.text=clean;e.editedAt=new Date().toISOString();saveCompanion();renderAdventures();}
  function deleteEvent(advId,eventId){const a=companionState.data.adventures.find(x=>x.id===advId);if(!a||!confirm('Ereignis wirklich löschen?'))return;a.events=(a.events||[]).filter(x=>x.id!==eventId);saveCompanion();renderAdventures();}
'''
new_event_ops = '''  function editEvent(advId,eventId){const a=companionState.data.adventures.find(x=>x.id===advId),e=a?.events?.find(x=>x.id===eventId);if(!e)return;const txt=prompt('Ereignis bearbeiten',e.text||'');if(txt===null)return;const clean=txt.trim();if(!clean)return;e.text=clean;e.editedAt=new Date().toISOString();saveCompanion();renderAdventures();}
  function automaticEvent(e){return e?.type==='energy'||e?.type==='status';}
  function eventDisplayHtml(e){if(e?.type==='energy'&&e.energy){const delta=Number(e.delta??(Number(e.to)-Number(e.from))),signed=(delta>0?`+${delta}`:`${delta}`).replace('-', '−');return `<strong class="event-energy-label">${esc(e.energy)} ${esc(signed)}</strong><span class="event-energy-range"> · ${esc(String(e.from))} → ${esc(String(e.to))}</span>`;}return esc(e?.text||'');}
  function deleteEvent(advId,eventId){const a=companionState.data.adventures.find(x=>x.id===advId),e=a?.events?.find(x=>x.id===eventId);if(!a||!e)return;if(!automaticEvent(e)&&!confirm('Ereignis wirklich löschen?'))return;a.events=(a.events||[]).filter(x=>x.id!==eventId);saveCompanion();renderAdventures();}
'''
replace_once(old_event_ops, new_event_ops, 'event operations')

# Rebuild adventure rendering with last-10 default and per-adventure expand toggle.
new_render_adventures = '''  function renderAdventures(){
    const d=companionState.data;if(!d)return;$('#adventureCount').textContent=`${d.adventures.length} Abenteuer`;
    $('#adventureList').innerHTML=d.adventures.map(a=>{
      const active=a.id===d.activeAdventureId,events=[...(a.events||[])].reverse(),expanded=expandedEventAdventures.has(a.id),shown=expanded?events:events.slice(0,10),learning=a.learning||[];
      const eventRows=shown.map(e=>{const auto=automaticEvent(e);return `<div class="event event-managed" data-event-id="${e.id}"><div class="event-main"><div>${eventDisplayHtml(e)}</div><div class="event-meta">${e.at?new Date(e.at).toLocaleString('de-DE'):''}${e.editedAt?' · bearbeitet':''}</div></div><div class="event-actions">${auto?'':`<button class="mini-btn edit-event">Bearbeiten</button>`}<button class="danger-btn delete-event">Löschen</button></div></div>`;}).join('')||'<div class="empty-comp">Noch keine Ereignisse.</div>';
      const more=events.length>10?`<div class="event-list-more"><button type="button" class="mini-btn toggle-events">${expanded?'Nur letzte 10 anzeigen':`Alle ${events.length} anzeigen`}</button></div>`:'';
      return `<div class="adv-card" data-adv-id="${a.id}"><div class="adv-head"><div><h4>${esc(a.title)}</h4><div class="adv-meta">${esc(a.date||'ohne Datum')} · AP ${Number(a.ap||0).toLocaleString('de-DE')}</div><div class="adv-energy-summary">${adventureEnergyHtml(a)}</div></div><div>${active?'<span class="active-pill">aktiv</span>':`<button class="mini-btn set-active-adv">Aktivieren</button>`} <button class="danger-btn delete-adv">Löschen</button></div></div>${a.notes?`<div class="subtle" style="margin-top:7px">${esc(a.notes)}</div>`:''}<details class="event-details" ${active?'open':''}><summary>Ereignisse (${events.length})</summary><div class="event-list">${eventRows}${more}<div class="toolbar-row"><input class="comp-input" data-role="event-text" placeholder="Ereignis hinzufügen"><button class="mini-btn add-event">+</button></div></div></details><div class="learning-list"><strong class="small-note">Lerngelegenheiten</strong>${learning.map(l=>`<div class="learning"><span class="learn-type">${esc(l.type)}</span><span><strong>${esc(l.target||'')}</strong>${l.detail?` · ${esc(l.detail)}`:''}</span></div>`).join('')||'<div class="empty-comp">Keine SE, Lehrmeister oder Quellen erfasst.</div>'}<div class="form-grid" style="margin-top:7px"><div class="field"><label>Art</label><select data-role="learn-type"><option>Spezielle Erfahrung</option><option>Lehrmeister</option><option>Buch/Thesis</option><option>Andere Lernchance</option></select></div><div class="field wide"><label>Talent / Zauber / SF</label><input data-role="learn-target" list="wishTargets"></div><div class="field wide"><label>Details</label><input data-role="learn-detail" placeholder="z. B. bis TaW 15, Ort, Bedingung"></div><div class="field"><button class="action-btn add-learning">Hinzufügen</button></div></div></div></div>`;
    }).join('')||'<div class="empty-comp">Noch keine Abenteuer angelegt.</div>';
    $$('#adventureList .adv-card').forEach(card=>{const id=card.dataset.advId;card.querySelector('.set-active-adv')?.addEventListener('click',()=>setActiveAdventure(id));card.querySelector('.delete-adv')?.addEventListener('click',()=>{if(!confirm('Abenteuer wirklich löschen?'))return;d.adventures=d.adventures.filter(a=>a.id!==id);expandedEventAdventures.delete(id);if(d.activeAdventureId===id)d.activeAdventureId=d.adventures[0]?.id||null;saveCompanion();renderStatus();renderAdventures();refreshAdventureSelectors();renderAdvancement();});card.querySelector('.add-learning')?.addEventListener('click',()=>addLearning(id,card));card.querySelector('.add-event')?.addEventListener('click',()=>addManualEvent(id,card.querySelector('[data-role="event-text"]')));card.querySelector('.toggle-events')?.addEventListener('click',()=>{if(expandedEventAdventures.has(id))expandedEventAdventures.delete(id);else expandedEventAdventures.add(id);renderAdventures();});card.querySelectorAll('.event-managed').forEach(er=>{const eid=er.dataset.eventId;er.querySelector('.edit-event')?.addEventListener('click',()=>editEvent(id,eid));er.querySelector('.delete-event')?.addEventListener('click',()=>deleteEvent(id,eid));});});
  }
'''
replace_block('  function renderAdventures(){\n', '  function refreshWishTargets(){', new_render_adventures, 'renderAdventures')

p.write_text(s, encoding='utf-8')

# Static contract checks.
required = [
    'HeldenMobil – HLD PoC v17.2.1',
    'ENERGY_EVENT_WINDOW_MS=25000',
    'function normalizeAdventureEvents(events)',
    'function logEnergyEvent(label,before,after)',
    'logEnergyEvent(label,before,after)',
    'events.slice(0,10)',
    'Alle ${events.length} anzeigen',
    'function automaticEvent(e)',
    "!automaticEvent(e)&&!confirm('Ereignis wirklich löschen?')",
    'event-energy-label',
]
for token in required:
    if token not in s:
        raise SystemExit(f'missing post-patch token: {token}')

if 'logEvent(`${label} ${delta>=0?' in s:
    raise SystemExit('old click-by-click energy logging still present')

print('v17.2.1 compact event log contract OK')
