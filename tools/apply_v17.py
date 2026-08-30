from pathlib import Path
import re

PATH = Path('index.html')
s = PATH.read_text(encoding='utf-8')
original = s

if '/* v17 Spieltisch */' in s:
    print('v17 already applied')
    raise SystemExit(0)

def one(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise RuntimeError(f'{label}: expected 1 occurrence, found {n}')
    s = s.replace(old, new, 1)

def rx(pattern, repl, label, flags=re.S):
    global s
    s, n = re.subn(pattern, repl, s, count=1, flags=flags)
    if n != 1:
        raise RuntimeError(f'{label}: expected 1 regex match, found {n}')

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------
for old, new, label in [
    ('HeldenMobil – HLD PoC v16.1', 'HeldenMobil – HLD PoC v17', 'title'),
    ('DSA 4.1 · HLD + Begleitdaten v16.1', 'DSA 4.1 · HLD + Begleitdaten v17', 'header version'),
    ('Proof of Concept v16.1', 'Proof of Concept v17', 'badge version'),
    ('HeldenMobil PoC v16.1 · HLD read-only · Begleitdaten + OneDrive-Sync · Würfeltisch',
     'HeldenMobil PoC v17 · HLD read-only · Begleitdaten + OneDrive-Sync · Spieltisch', 'footer version'),
]:
    one(old, new, label)

# ---------------------------------------------------------------------------
# New Spieltisch tab + static dashboard shell
# ---------------------------------------------------------------------------
one(
'''    <button class="tab active" data-tab="data">Daten</button>
    <button class="tab" data-tab="overview" disabled>Übersicht</button>''',
'''    <button class="tab active" data-tab="data">Daten</button>
    <button class="tab" data-tab="dashboard" disabled>Spieltisch</button>
    <button class="tab" data-tab="overview" disabled>Übersicht</button>''',
'add dashboard tab')

dashboard_html = r'''    <section id="dashboard" class="section">
      <div class="section-title dashboard-title"><h3>Spieltisch</h3><span class="count" id="dashboardAdventureState"></span></div>
      <div class="dashboard-attr-card">
        <div class="dashboard-card-label">Eigenschaften · MR · SO</div>
        <div id="dashboardAttributes" class="dashboard-attributes"></div>
      </div>
      <div class="dashboard-layout">
        <div class="dashboard-body-shell">
          <div id="dashboardBodyMap" class="dashboard-body-map">
            <img id="dashboardBodyImage" alt="Trefferzonen und Rüstung" draggable="false">
            <div id="dashboardEnergyOverlay" class="dashboard-energy-overlay"></div>
            <div id="dashboardZoneOverlay"></div>
            <div id="dashboardFooterOverlay" class="dashboard-footer-overlay"></div>
          </div>
          <div id="dashboardWoundHint" class="dashboard-wound-hint"></div>
        </div>
        <div class="dashboard-side">
          <div class="comp-card dashboard-combat-card"><h4>Aktuelle Kampfkombination</h4><div id="dashboardCombat"></div></div>
          <div class="comp-card"><h4>Lieblingstalente</h4><div id="dashboardFavorites"></div></div>
          <div class="comp-card"><h4>Geld</h4><div id="dashboardMoney"></div></div>
          <div class="comp-card"><h4>Magische Speicher</h4><div id="dashboardMagic"></div></div>
        </div>
      </div>
    </section>

'''
one('''  <main class="content">
    <section id="overview" class="section">''',
    '''  <main class="content">
''' + dashboard_html + '''    <section id="overview" class="section">''',
    'insert dashboard section')

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
css = r'''
/* v17 Spieltisch */
.dashboard-title{margin-bottom:10px}.dashboard-attr-card{border:1px solid var(--line);border-radius:11px;background:var(--panel);padding:9px 11px;margin-bottom:12px}.dashboard-card-label{font-size:.68rem;color:var(--accent2);text-transform:uppercase;letter-spacing:.055em;font-weight:800;margin-bottom:7px}.dashboard-attributes{display:grid;grid-template-columns:repeat(10,minmax(55px,1fr));gap:6px}.dashboard-attr{border:1px solid #343b46;border-radius:8px;background:#15191f;min-height:45px;padding:6px 7px;text-align:center;display:flex;flex-direction:column;justify-content:center;gap:1px}.dashboard-attr.rollable{cursor:pointer}.dashboard-attr.rollable:hover{border-color:#76643a;background:#211e17}.dashboard-attr span{font-size:.62rem;text-transform:uppercase;color:#9ea8b5;letter-spacing:.04em}.dashboard-attr strong{font-size:1.05rem;color:#f2d586}.dashboard-layout{display:grid;grid-template-columns:minmax(390px,1.32fr) minmax(290px,.68fr);gap:12px;align-items:start}.dashboard-side{display:flex;flex-direction:column;gap:12px}.dashboard-body-shell{min-width:0}.dashboard-body-map{position:relative;width:min(100%,620px);aspect-ratio:2/3;margin:0 auto;overflow:hidden;border-radius:11px;box-shadow:0 12px 34px rgba(0,0,0,.26);container-type:inline-size}.dashboard-body-map>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;user-select:none;pointer-events:none}.dashboard-energy-overlay{position:absolute;left:7.7%;top:3.15%;width:84.7%;height:7.15%;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));align-items:stretch;color:#f5e7c2}.dashboard-energy-slot{min-width:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:.2cqw .8cqw;text-shadow:0 1px 2px #000}.dashboard-energy-slot.special-stack{gap:.2cqw}.dashboard-energy{width:100%;text-align:center;min-width:0}.dashboard-energy-main{display:flex;align-items:baseline;justify-content:center;gap:.6cqw;line-height:1}.dashboard-energy-name{font-size:2.35cqw;color:#e7c577;font-weight:800}.dashboard-energy-value{font-size:2.9cqw;font-weight:850;color:#fff5d8}.dashboard-energy-buttons{display:flex;justify-content:center;gap:.45cqw;margin-top:.55cqw}.dashboard-energy-buttons button{min-width:3.25cqw;height:2.35cqw;padding:0 .4cqw;border:1px solid rgba(220,187,112,.55);border-radius:.55cqw;background:rgba(12,15,19,.82);color:#f0dfb5;font-size:1.42cqw;font-weight:800;cursor:pointer;line-height:1}.dashboard-energy-buttons button:hover:not(:disabled){background:#342a19;border-color:#d2ac56}.dashboard-energy-buttons button:disabled{opacity:.3;cursor:default}.dashboard-energy-thresholds{font-size:1.03cqw;color:#b9c1cb;margin-top:.3cqw;white-space:nowrap}.dashboard-energy.critical-half .dashboard-energy-value{color:#ffd477}.dashboard-energy.critical-third .dashboard-energy-value{color:#ffad78}.dashboard-energy.critical-quarter .dashboard-energy-value{color:#ff7f7f}.dashboard-energy-slot.special-stack .dashboard-energy-main{line-height:.9}.dashboard-energy-slot.special-stack .dashboard-energy-name{font-size:1.7cqw}.dashboard-energy-slot.special-stack .dashboard-energy-value{font-size:2.05cqw}.dashboard-energy-slot.special-stack .dashboard-energy-buttons{margin-top:.25cqw}.dashboard-energy-slot.special-stack .dashboard-energy-buttons button{height:1.8cqw;font-size:1.05cqw;min-width:2.8cqw}.dashboard-zone{position:absolute;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;color:#fff4d8;text-shadow:0 1px 3px #000;padding:.5cqw;box-sizing:border-box}.dashboard-zone-name{font-size:2.05cqw;line-height:1.05;font-weight:900;color:#e8c77c;text-transform:uppercase;letter-spacing:.03em}.dashboard-zone-rs{font-size:1.75cqw;line-height:1.1;margin-top:.5cqw}.dashboard-wounds{display:flex;gap:.7cqw;justify-content:center;margin-top:.7cqw}.dashboard-wound-dot{width:2.65cqw;height:2.65cqw;min-width:13px;min-height:13px;max-width:22px;max-height:22px;border-radius:50%;border:1.4px solid #ead49d;background:rgba(7,9,12,.68);box-shadow:0 1px 3px #000;cursor:pointer;padding:0}.dashboard-wound-dot.active{background:#b73b38;border-color:#ffd0b0;box-shadow:0 0 0 1px rgba(110,20,20,.8),0 0 7px rgba(213,65,53,.55)}.dashboard-wound-dot:disabled{cursor:default;opacity:.55}.dashboard-zone[data-zone="ruecken"]{left:5.2%;top:16.65%;width:25.7%;height:9.75%}.dashboard-zone[data-zone="kopf"]{left:69.4%;top:15.55%;width:24.0%;height:9.7%}.dashboard-zone[data-zone="linkerarm"]{left:5.35%;top:31.0%;width:20.2%;height:9.35%}.dashboard-zone[data-zone="brust"]{left:73.2%;top:30.55%;width:21.3%;height:9.45%}.dashboard-zone[data-zone="bauch"]{left:4.25%;top:43.25%;width:20.3%;height:9.35%}.dashboard-zone[data-zone="rechterarm"]{left:75.65%;top:42.9%;width:20.25%;height:9.35%}.dashboard-zone[data-zone="linkesbein"]{left:4.25%;top:64.95%;width:22.0%;height:9.4%}.dashboard-zone[data-zone="rechtesbein"]{left:72.9%;top:64.95%;width:23.0%;height:9.4%}.dashboard-footer-overlay{position:absolute;left:6.7%;top:89.05%;width:86.3%;height:6.55%;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));align-items:center;text-align:center;text-shadow:0 1px 3px #000}.dashboard-foot-label{display:block;color:#d9bd79;font-size:1.65cqw;font-weight:800}.dashboard-foot-value{display:block;color:#fff0c9;font-size:3cqw;font-weight:900;line-height:1.05}.dashboard-foot-sub{display:block;color:#aeb7c4;font-size:.9cqw;line-height:1}.dashboard-wound-hint{min-height:1.25em;margin:6px auto 0;max-width:620px;text-align:center;color:#9ba5b2;font-size:.7rem}.dashboard-combat-select{margin-bottom:9px}.dashboard-combat-weapon{border-top:1px solid #2b3038;padding:8px 0}.dashboard-combat-weapon:first-of-type{border-top:0}.dashboard-combat-hand{font-size:.62rem;color:#8e99a8;text-transform:uppercase;letter-spacing:.04em}.dashboard-combat-name{font-weight:800;margin:2px 0 6px}.dashboard-combat-rolls{display:flex;gap:6px;flex-wrap:wrap}.dashboard-combat-roll{border:1px solid #5f5134;background:#292319;color:#ebcf88;border-radius:8px;padding:6px 8px;cursor:pointer;font-size:.72rem;font-weight:800}.dashboard-combat-roll strong{margin-left:4px;color:#fff0c3}.dashboard-combat-roll:hover{background:#352d1d}.dashboard-ini{display:flex;align-items:center;justify-content:space-between;gap:8px;border-top:1px solid #2b3038;margin-top:6px;padding-top:9px}.dashboard-ini .ini-main{font-size:1.22rem;color:#f3d58a;font-weight:900}.dashboard-dodge{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:8px;padding-top:8px;border-top:1px solid #2b3038}.dashboard-dodge strong{font-size:1.15rem;color:#f3d58a}.favorite-star{border:0;background:transparent;color:#8e99a8;cursor:pointer;padding:0 5px 0 0;font-size:1.05rem;vertical-align:middle}.favorite-star.active{color:#e6c46f}.favorite-star:hover{color:#f2d78e}.dashboard-fav-list{display:flex;flex-direction:column;gap:5px}.dashboard-fav-row{display:grid;grid-template-columns:auto 1fr auto;gap:6px;align-items:center;border:1px solid #303743;background:#15191f;border-radius:8px;padding:7px 8px}.dashboard-fav-roll{min-width:0;cursor:pointer}.dashboard-fav-roll:hover .dashboard-fav-name{color:#f3d58a}.dashboard-fav-name{font-size:.8rem;font-weight:750}.dashboard-fav-probe{font-size:.64rem;color:#818c99;margin-top:1px}.dashboard-fav-value{color:#f3d58a;font-weight:850}.dashboard-money-total{font-size:1.3rem;color:#f3d58a;font-weight:850;margin-bottom:8px}.dashboard-magic-list{display:flex;flex-direction:column;gap:6px}.dashboard-magic-row{border:1px solid #303743;background:#15191f;border-radius:8px;padding:7px 8px}.dashboard-magic-row.empty-slot{opacity:.55}.dashboard-magic-title{font-size:.78rem;font-weight:800}.dashboard-magic-meta{font-size:.65rem;color:#8994a2;margin-top:2px}.dashboard-magic-actions{margin-top:5px}.dashboard-magic-actions button{padding:4px 7px;font-size:.66rem}.dashboard-artifact-note{border-top:1px solid #2b3038;margin-top:8px;padding-top:7px;color:#8d98a5;font-size:.68rem}
@media(max-width:900px){.dashboard-layout{grid-template-columns:minmax(340px,1fr) minmax(250px,.65fr)}.dashboard-attributes{grid-template-columns:repeat(5,minmax(55px,1fr))}}
@media(max-width:720px){.dashboard-layout{grid-template-columns:1fr}.dashboard-body-shell{order:0}.dashboard-side{order:1}.dashboard-body-map{width:min(100%,560px)}.dashboard-attributes{grid-template-columns:repeat(5,minmax(0,1fr))}}
@media(max-width:430px){.dashboard-attr-card{padding:7px}.dashboard-attributes{gap:4px}.dashboard-attr{min-height:39px;padding:4px}.dashboard-attr strong{font-size:.95rem}.dashboard-energy-name{font-size:2.65cqw}.dashboard-energy-value{font-size:3.1cqw}.dashboard-energy-buttons button{min-width:3.7cqw;height:2.8cqw;font-size:1.65cqw}.dashboard-zone-name{font-size:2.25cqw}.dashboard-zone-rs{font-size:1.9cqw}.dashboard-foot-label{font-size:1.8cqw}.dashboard-foot-value{font-size:3.25cqw}}
'''
one('</style>', css + '\n</style>', 'insert dashboard CSS')

# ---------------------------------------------------------------------------
# Parse gender from the HLD, robustly across likely Helden-Software forms.
# ---------------------------------------------------------------------------
one(
"""    const race=attr(rasse,'string',attr(rasse,'name'));

    const eigRoot=direct(held,'eigenschaften');""",
"""    const race=attr(rasse,'string',attr(rasse,'name'));
    const genderNode=direct(basis,'geschlecht')||direct(held,'geschlecht')||held.querySelector('geschlecht');
    const genderRaw=[attr(held,'geschlecht'),attr(basis,'geschlecht'),attr(genderNode,'name'),attr(genderNode,'value'),attr(genderNode,'string'),genderNode?.textContent||''].filter(Boolean).join(' ').toLocaleLowerCase('de');
    const gender=/weib|female|frau/.test(genderRaw)?'female':(/männ|maenn|male|mann/.test(genderRaw)?'male':'unknown');

    const eigRoot=direct(held,'eigenschaften');""",
'gender parser')
one("name:attr(held,'name'),key:attr(held,'key'),race,", "name:attr(held,'name'),key:attr(held,'key'),race,gender,", 'return gender')

# ---------------------------------------------------------------------------
# Companion schema v6: favorite talents + zonal wounds, backward compatible.
# ---------------------------------------------------------------------------
one('  const COMP_SCHEMA=5;', '  const COMP_SCHEMA=6;', 'schema v6')
one(
"""  const uid=(p='id')=>`${p}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,8)}`;
  function companionStorageKey(ver=COMP_SCHEMA){return state.current?`heldenmobil:v${ver}:${state.current.key}`:null;}
  function freshAdventureStatus(){""",
"""  const uid=(p='id')=>`${p}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2,8)}`;
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
  function companionStorageKey(ver=COMP_SCHEMA){return state.current?`heldenmobil:v${ver}:${state.current.key}`:null;}
  function freshAdventureStatus(){""",
'wound helpers')
one(
"return {lep:b.get('LeP')??null,aup:b.get('AuP')??null,asp:b.get('AsP')??null,kap:b.get('KaP')??null,wounds:0,notes:''};",
"return {lep:b.get('LeP')??null,aup:b.get('AuP')??null,asp:b.get('AsP')??null,kap:b.get('KaP')??null,wounds:0,woundZones:blankWoundZones(),notes:''};",
'fresh status zones')
one(
"adventures:[],advancement:[],inventory:{locations:[{id:'loc_person',name:'Am Mann',parentId:null},{id:'loc_pack',name:'Rucksack',parentId:'loc_person'},{id:'loc_wagon',name:'Wagen',parentId:null},{id:'loc_home',name:'Zuhause',parentId:null}],items:[]},money:{transactions:[]},magic:{staffSlots:[]}};",
"adventures:[],advancement:[],favorites:{talents:[]},inventory:{locations:[{id:'loc_person',name:'Am Mann',parentId:null},{id:'loc_pack',name:'Rucksack',parentId:'loc_person'},{id:'loc_wagon',name:'Wagen',parentId:null},{id:'loc_home',name:'Zuhause',parentId:null}],items:[]},money:{transactions:[]},magic:{staffSlots:[]}};",
'empty favorites')
one(
"const x={...base,...d,inventory:{...base.inventory,...(d.inventory||{})},money:{...base.money,...(d.money||{})},magic:{...base.magic,...(d.magic||{})}};",
"const x={...base,...d,favorites:{...base.favorites,...(d.favorites||{})},inventory:{...base.inventory,...(d.inventory||{})},money:{...base.money,...(d.money||{})},magic:{...base.magic,...(d.magic||{})}};",
'normalize favorites merge')
one(
"x.adventures=x.adventures.map(a=>({...a,events:Array.isArray(a.events)?a.events:[],learning:Array.isArray(a.learning)?a.learning:[],combatBySet:(a.combatBySet&&typeof a.combatBySet==='object')?a.combatBySet:{},status:{...freshAdventureStatus(),...(a.status||{})}}));",
"x.adventures=x.adventures.map(a=>{const status={...freshAdventureStatus(),...(a.status||{})};normalizeStatusWounds(status);return {...a,events:Array.isArray(a.events)?a.events:[],learning:Array.isArray(a.learning)?a.learning:[],combatBySet:(a.combatBySet&&typeof a.combatBySet==='object')?a.combatBySet:{},status};});",
'normalize adventure wounds')
one(
"if(legacyStatus&&x.adventures.length){const target=x.adventures.find(a=>a.id===x.activeAdventureId)||x.adventures[0];target.status={...target.status,...legacyStatus};if(!x.activeAdventureId)x.activeAdventureId=target.id;}",
"if(legacyStatus&&x.adventures.length){const target=x.adventures.find(a=>a.id===x.activeAdventureId)||x.adventures[0];target.status={...target.status,...legacyStatus};normalizeStatusWounds(target.status);if(!x.activeAdventureId)x.activeAdventureId=target.id;}",
'legacy status wounds')
one(
"x.money.transactions=Array.isArray(x.money.transactions)?x.money.transactions:[];x.magic.staffSlots=Array.isArray(x.magic.staffSlots)?x.magic.staffSlots:[];delete x.magic.artifacts;",
"x.money.transactions=Array.isArray(x.money.transactions)?x.money.transactions:[];x.magic.staffSlots=Array.isArray(x.magic.staffSlots)?x.magic.staffSlots:[];x.favorites.talents=Array.isArray(x.favorites.talents)?[...new Set(x.favorites.talents.map(String).filter(Boolean))]:[];delete x.magic.artifacts;",
'normalize favorite talents')
one("for(const v of [4,3,2,1])", "for(const v of [5,4,3,2,1])", 'schema migration chain')
one("localStorage.removeItem(companionStorageKey(4));", "localStorage.removeItem(companionStorageKey(5));localStorage.removeItem(companionStorageKey(4));", 'reset v5')

# Central dashboard refresh whenever companion data changes.
one(
"function saveCompanion(opts={}){if(!companionState.data)return;if(opts.touch!==false)companionState.data.updatedAt=new Date().toISOString();localStorage.setItem(companionStorageKey(),JSON.stringify(companionState.data));companionState.localExists=true;renderDataMeta();if(!opts.skipCloud)cloudScheduleSave();}",
"function saveCompanion(opts={}){if(!companionState.data)return;if(opts.touch!==false)companionState.data.updatedAt=new Date().toISOString();localStorage.setItem(companionStorageKey(),JSON.stringify(companionState.data));companionState.localExists=true;renderDataMeta();renderDashboard();if(!opts.skipCloud)cloudScheduleSave();}",
'save refresh dashboard')
one(
"companionState.localExists=!!raw;companionState.data=normalizeCompanion(d);if(migrated)saveCompanion({skipCloud:true});renderCompanionAll();cloudOnHeroChanged();",
"companionState.localExists=!!raw;companionState.data=normalizeCompanion(d);if(migrated)saveCompanion({skipCloud:true});renderTalents();renderCompanionAll();cloudOnHeroChanged();",
'favorites after hero load')
one(
"function renderCompanionAll(){renderStatus();renderAdventures();renderAdvancement();renderInventory();renderMoney();renderMagic();renderDataMeta();refreshAdventureSelectors();refreshWishTargets();if(state.current)renderCombat();}",
"function renderCompanionAll(){renderStatus();renderAdventures();renderAdvancement();renderInventory();renderMoney();renderMagic();renderDataMeta();refreshAdventureSelectors();refreshWishTargets();if(state.current)renderCombat();renderDashboard();}",
'render dashboard all')

# ---------------------------------------------------------------------------
# Favorite talents
# ---------------------------------------------------------------------------
favorite_helpers = r'''  function favoriteTalentNames(){const d=companionState.data;return new Set(d&&d.heroKey===state.current?.key?(d.favorites?.talents||[]):[]);}
  function toggleFavoriteTalent(name){const d=companionState.data;if(!d||d.heroKey!==state.current?.key)return;d.favorites=d.favorites||{talents:[]};const set=new Set(d.favorites.talents||[]);if(set.has(name))set.delete(name);else set.add(name);d.favorites.talents=[...set];saveCompanion();renderTalents();}
'''
one("  function renderTalents(){", favorite_helpers + "  function renderTalents(){", 'favorite helpers')
one(
'''return `<tr class="rollable-row" tabindex="0" data-roll-ref="${ref}" title="${esc(t.name)} würfeln"><td>${esc(t.name)} <span class="roll-mark">◆</span>${t.metaDetail?`<div class="cell-sub">${esc(t.metaDetail)}</div>`:''}</td>''',
'''const fav=favoriteTalentNames().has(t.name);return `<tr class="rollable-row" tabindex="0" data-roll-ref="${ref}" title="${esc(t.name)} würfeln"><td><button type="button" class="favorite-star ${fav?'active':''}" data-favorite-talent="${esc(t.name)}" title="${fav?'Von Lieblingstalenten entfernen':'Zu Lieblingstalenten hinzufügen'}">${fav?'★':'☆'}</button>${esc(t.name)} <span class="roll-mark">◆</span>${t.metaDetail?`<div class="cell-sub">${esc(t.metaDetail)}</div>`:''}</td>''',
'favorite star in talents')
one(
"    $('#talentBody').innerHTML=html||'<tr><td colspan=\"4\" class=\"empty\">Keine Treffer</td></tr>';\n    if(!q)",
"    $('#talentBody').innerHTML=html||'<tr><td colspan=\"4\" class=\"empty\">Keine Treffer</td></tr>';\n    $$('#talentBody .favorite-star').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();toggleFavoriteTalent(b.dataset.favoriteTalent);}));\n    if(!q)",
'favorite bindings')

# ---------------------------------------------------------------------------
# Wound total editing remains compatible with zonal wound tracking.
# ---------------------------------------------------------------------------
wound_functions = r'''  function zonedWoundTotal(s){normalizeStatusWounds(s);return WOUND_ZONE_KEYS.reduce((a,k)=>a+Number(s.woundZones[k]||0),0);}
  function setTotalWounds(total){const s=activeAdventureStatus();if(!s)return;normalizeStatusWounds(s);total=Math.max(0,Math.floor(Number(total||0)));let zoned=zonedWoundTotal(s);if(total>=zoned)s.woundZones.unassigned=total-zoned;else{let remove=zoned-total;for(const k of [...WOUND_ZONE_KEYS].reverse()){if(remove<=0)break;const take=Math.min(s.woundZones[k],remove);s.woundZones[k]-=take;remove-=take;}s.woundZones.unassigned=0;}s.wounds=total;logEvent(`Wunden gesamt: ${total}`,'status');saveCompanion();renderStatus();renderAdventures();}
  function setZoneWounds(zone,count){const s=activeAdventureStatus();if(!s)return;normalizeStatusWounds(s);count=Math.max(0,Math.min(3,Math.floor(Number(count||0))));const before=s.woundZones[zone]||0;if(before===count)return;s.woundZones[zone]=count;s.wounds=zonedWoundTotal(s)+Number(s.woundZones.unassigned||0);const label=({kopf:'Kopf',brust:'Brust',ruecken:'Rücken',bauch:'Bauch',linkerarm:'linker Arm',rechterarm:'rechter Arm',linkesbein:'linkes Bein',rechtesbein:'rechtes Bein'})[zone]||zone;logEvent(`Wunden ${label}: ${before} → ${count} · gesamt ${s.wounds}`,'status');saveCompanion();renderStatus();renderAdventures();}
'''
one("  function refreshAdventureSelectors(){", wound_functions + "  function refreshAdventureSelectors(){", 'wound editing helpers')
one(
"  $('#woundsInput').addEventListener('change',e=>{const s=activeAdventureStatus();if(!s)return;s.wounds=Math.max(0,Number(e.target.value||0));saveCompanion();renderAdventures();});",
"  $('#woundsInput').addEventListener('change',e=>setTotalWounds(e.target.value));",
'wounds event')

# ---------------------------------------------------------------------------
# Klingentänzer: v16 displayed 2W6, but the roll payload still hard-coded 1/3.
# ---------------------------------------------------------------------------
one(
"const iniDice=(calc.ini.dice==='3W6'?[3,6,calc.ini.fixed]:[1,6,calc.ini.fixed]),iniRef=registerRoll",
"const iniCount=Math.max(1,Number((String(calc.ini.dice).match(/^(\\d+)W6$/)||[])[1]||1)),iniDice=[iniCount,6,calc.ini.fixed],iniRef=registerRoll",
'initiative roll dice count')

# Keep dashboard current when selecting another combat set.
one(
"$$('#combatSetTabs .setbtn').forEach(b=>b.addEventListener('click',()=>{state.combatSet=num(b.dataset.setIndex);renderCombat();}));",
"$$('#combatSetTabs .setbtn').forEach(b=>b.addEventListener('click',()=>{state.combatSet=num(b.dataset.setIndex);renderCombat();renderDashboard();}));",
'combat set dashboard refresh')

# ---------------------------------------------------------------------------
# Dashboard renderer
# ---------------------------------------------------------------------------
dashboard_js = r'''
  // ---- v17 Spieltisch -----------------------------------------------------
  const DASHBOARD_ZONES=[
    {key:'ruecken',label:'Rücken'},{key:'kopf',label:'Kopf'},{key:'linkerarm',label:'L. Arm'},{key:'brust',label:'Brust'},
    {key:'bauch',label:'Bauch'},{key:'rechterarm',label:'R. Arm'},{key:'linkesbein',label:'L. Bein'},{key:'rechtesbein',label:'R. Bein'}
  ];
  function dashboardArmor(){
    const sets=state.current?.combatSets||[],set=sets[state.combatSet]||sets[0]||null;
    if(!set){const zones=Object.fromEntries(Object.keys(ARMOR_ZONE_WEIGHTS).map(k=>[k,0]));return {set:null,armor:{zones,rs:0,rawRS:0,baseBE:0,be:0,beReduction:0,pieces:[],unknown:[]},speed:speedInfo(0)};}
    const armor=setArmor(set);return {set,armor,speed:speedInfo(armor.be)};
  }
  function dashboardEnergyModel(){
    const max=energyMaxMap(),s=activeAdventureStatus(),labels=['LeP','AuP','AsP','KaP'].filter(l=>max.has(l)||(s&&s[statusKeyFor(l)]!=null));
    return labels.map(label=>{const m=max.get(label),k=statusKeyFor(label),value=s?.[k]??m??0;return {label,max:m,value,active:!!s};});
  }
  function dashboardEnergyMarkup(e,compact=false){
    if(!e)return '<div class="dashboard-energy"><div class="dashboard-energy-main"><span class="dashboard-energy-name">–</span></div></div>';
    let severity='';if(e.label==='LeP'&&e.max>0){if(e.value<=Math.floor(e.max/4))severity='critical-quarter';else if(e.value<=Math.floor(e.max/3))severity='critical-third';else if(e.value<=Math.floor(e.max/2))severity='critical-half';}
    const thresholds=e.label==='LeP'&&e.max>0?`<div class="dashboard-energy-thresholds">½ ${Math.floor(e.max/2)} · ⅓ ${Math.floor(e.max/3)} · ¼ ${Math.floor(e.max/4)}</div>`:'';
    return `<div class="dashboard-energy ${severity}"><div class="dashboard-energy-main"><span class="dashboard-energy-name">${e.label}</span><span class="dashboard-energy-value">${e.value}${e.max!=null?`/${e.max}`:''}</span></div><div class="dashboard-energy-buttons">${[-5,-1,1,5].map(n=>`<button type="button" data-dashboard-energy="${e.label}" data-delta="${n}" ${e.active?'':'disabled'}>${n>0?'+':''}${n}</button>`).join('')}</div>${compact?'':thresholds}</div>`;
  }
  function renderDashboardEnergies(){
    const host=$('#dashboardEnergyOverlay');if(!host)return;const all=dashboardEnergyModel(),lep=all.find(x=>x.label==='LeP'),aup=all.find(x=>x.label==='AuP'),special=all.filter(x=>x.label==='AsP'||x.label==='KaP');
    host.innerHTML=`<div class="dashboard-energy-slot">${dashboardEnergyMarkup(lep)}</div><div class="dashboard-energy-slot">${dashboardEnergyMarkup(aup)}</div><div class="dashboard-energy-slot ${special.length>1?'special-stack':''}">${special.length?special.map(x=>dashboardEnergyMarkup(x,special.length>1)).join(''):dashboardEnergyMarkup(null)}</div>`;
    host.querySelectorAll('[data-dashboard-energy]').forEach(b=>b.onclick=()=>adjustStatus(b.dataset.dashboardEnergy,Number(b.dataset.delta)));
  }
  function renderDashboardAttributes(){
    const host=$('#dashboardAttributes');if(!host||!state.current)return;const pm=propMap(state.current.props),basis=new Map(deriveBasis(state.current.props).map(x=>[x.name,x.value]));
    const attrs=primaryNames.map(name=>{const p=pm.get(name),v=p?p.value+p.mod:'–',abbr=short[name]||name,ref=p?registerRoll(`dashboard:attr:${name}`,{type:'d20',title:name,subtitle:`Eigenschaft ${abbr} ${v}`,target:v,targetLabel:abbr}):'';return `<div class="dashboard-attr ${p?'rollable':''}" ${p?`tabindex="0" role="button" data-roll-ref="${ref}"`:''}><span>${esc(abbr)}</span><strong>${esc(v)}</strong></div>`;});
    attrs.push(`<div class="dashboard-attr"><span>MR</span><strong>${esc(basis.get('MR')??'–')}</strong></div>`,`<div class="dashboard-attr"><span>SO</span><strong>${esc(basis.get('SO')??'–')}</strong></div>`);host.innerHTML=attrs.join('');
  }
  function renderDashboardBody(){
    if(!state.current||!$('#dashboardBodyImage'))return;const {armor,speed}=dashboardArmor(),s=activeAdventureStatus();if(s)normalizeStatusWounds(s);const zones=s?.woundZones||blankWoundZones(),img=$('#dashboardBodyImage'),female=state.current.gender==='female';
    const wanted=female?'assets/body-female.webp':'assets/body-male.webp';if(!img.getAttribute('src')?.endsWith(wanted))img.src=wanted;img.alt=`Trefferzonen ${female?'weibliche':'männliche'} Silhouette`;
    renderDashboardEnergies();
    $('#dashboardZoneOverlay').innerHTML=DASHBOARD_ZONES.map(z=>{const wounds=Number(zones[z.key]||0),rs=Number(armor.zones?.[z.key]||0);return `<div class="dashboard-zone" data-zone="${z.key}"><div class="dashboard-zone-name">${z.label}</div><div class="dashboard-zone-rs">RS ${rs}</div><div class="dashboard-wounds">${[1,2,3].map(n=>`<button type="button" class="dashboard-wound-dot ${wounds>=n?'active':''}" data-zone-wound="${z.key}" data-wound-count="${n}" aria-label="${z.label}: ${n} Wunden" ${s?'':'disabled'}></button>`).join('')}</div></div>`;}).join('');
    $$('#dashboardZoneOverlay [data-zone-wound]').forEach(b=>b.onclick=()=>{const cur=Number(activeAdventureStatus()?.woundZones?.[b.dataset.zoneWound]||0),target=Number(b.dataset.woundCount);setZoneWounds(b.dataset.zoneWound,cur===target?target-1:target);});
    const wd=woundData(),gbe=armor.baseBE,eff=armor.be;
    $('#dashboardFooterOverlay').innerHTML=`<div title="Gewichteter Rüstungsschutz"><span class="dashboard-foot-label">gRS</span><strong class="dashboard-foot-value">${armor.rs}</strong></div><div title="Gesamtbehinderung${gbe!==eff?` · effektiv nach Rüstungsgewöhnung: ${eff}`:''}"><span class="dashboard-foot-label">gBE</span><strong class="dashboard-foot-value">${gbe}</strong>${gbe!==eff?`<small class="dashboard-foot-sub">eff. ${eff}</small>`:''}</div><div title="Wundschwelle"><span class="dashboard-foot-label">WS</span><strong class="dashboard-foot-value">${wd.threshold}</strong></div><div title="Aktuelle Geschwindigkeit: ${esc(speed.parts.join(' · '))}"><span class="dashboard-foot-label">GS</span><strong class="dashboard-foot-value">${speed.value}</strong></div>`;
    const unassigned=Number(zones.unassigned||0);$('#dashboardWoundHint').textContent=!s?'Wunden und Energien werden mit einem aktiven Abenteuer editierbar.':unassigned?`${unassigned} Wunde${unassigned===1?'':'n'} aus dem bisherigen Spielstand noch keiner Trefferzone zugeordnet.`:'';
  }
  function dashboardCombatButton(label,value,ref){return value==null?'':`<button type="button" class="dashboard-combat-roll" data-roll-ref="${ref}">${label}<strong>${esc(value)}</strong></button>`;}
  function renderDashboardCombat(){
    const host=$('#dashboardCombat');if(!host||!state.current)return;const {set,armor}=dashboardArmor();if(!set){host.innerHTML='<div class="empty-comp">Kein Kampfset vorhanden.</div>';return;}
    const meleeRows=set.entries.filter(e=>e.type==='melee').map(e=>({e,v:meleeValues(e,armor.be)})),loadouts=buildCombatLoadouts(set,armor.be,meleeRows),active=activeLoadout(set,loadouts),calc=computeLoadout(active,armor.be,meleeRows);if(!active||!calc){host.innerHTML='<div class="empty-comp">Keine aktuelle Nahkampf-Kombination.</div>';return;}
    const options=loadouts.map(x=>`<option value="${esc(x.key)}" ${x.key===active.key?'selected':''}>${esc(x.label)}</option>`).join(''),pfx=`dashboard:${set.id}:${active.key}`,m=registerCombatWeaponRolls(`${pfx}:main`,active.main,calc.mainV,armor),main=`${dashboardCombatButton('AT',calc.mainV.at,m.atRef)}${dashboardCombatButton('PA',calc.mainV.pa,m.paRef)}${dashboardCombatButton('TP',diceText(calc.mainV.tp),m.tpRef)}${dashboardCombatButton('TP+Zone','',m.tpZoneRef)}`;
    let side='';if(active.kind==='dual'&&calc.sideV){const o=registerCombatWeaponRolls(`${pfx}:side`,active.side,calc.sideV,armor);side=`<div class="dashboard-combat-weapon"><div class="dashboard-combat-hand">Linke Hand</div><div class="dashboard-combat-name">${esc(active.side.name)}</div><div class="dashboard-combat-rolls">${dashboardCombatButton('AT',calc.sideV.at,o.atRef)}${dashboardCombatButton('PA',calc.sideV.pa,o.paRef)}${dashboardCombatButton('TP',diceText(calc.sideV.tp),o.tpRef)}${dashboardCombatButton('TP+Zone','',o.tpZoneRef)}</div></div>`;}else if((active.kind==='shield'||active.kind==='parry')&&active.side){const paRef=registerRoll(`${pfx}:defense`,{type:'d20',title:`Parade – ${active.side.name}`,subtitle:`PA ${calc.defensePA}`,target:calc.defensePA,targetLabel:'PA'});side=`<div class="dashboard-combat-weapon"><div class="dashboard-combat-hand">Nebenhand · ${loadoutKindLabel(active.kind)}</div><div class="dashboard-combat-name">${esc(active.side.name)}</div><div class="dashboard-combat-rolls">${dashboardCombatButton(active.kind==='shield'?'Schild-PA':'PW-PA',calc.defensePA,paRef)}</div></div>`;}
    const iniCount=Math.max(1,Number((String(calc.ini.dice).match(/^(\d+)W6$/)||[])[1]||1)),iniRef=registerRoll(`${pfx}:ini`,{type:'damage',title:`Initiative – ${active.label}`,subtitle:`${calc.ini.fixed}+${calc.ini.dice}`,dice:[iniCount,6,calc.ini.fixed],resultUnit:'INI'}),aw=dodge(armor.be),dodgeRef=registerRoll(`${pfx}:dodge`,{type:'d20',title:'Ausweichen',subtitle:`Ausweichen ${aw.value}`,target:aw.value,targetLabel:'Ausweichen'});
    host.innerHTML=`<select id="dashboardLoadoutSelect" class="comp-input dashboard-combat-select">${options}</select><div class="dashboard-combat-weapon"><div class="dashboard-combat-hand">${active.kind==='dual'?'Rechte Hand':'Hauptwaffe'} · ${loadoutKindLabel(active.kind)}</div><div class="dashboard-combat-name">${esc(active.main.name)}</div><div class="dashboard-combat-rolls">${main}</div></div>${side}<div class="dashboard-ini"><div><div class="dashboard-combat-hand">Initiative</div><div class="small-note">${esc(active.label)}</div></div><button type="button" class="dashboard-combat-roll ini-main" data-roll-ref="${iniRef}">${calc.ini.fixed}+${calc.ini.dice}</button></div><div class="dashboard-dodge"><span>Ausweichen</span><button type="button" class="dashboard-combat-roll" data-roll-ref="${dodgeRef}"><strong>${aw.value}</strong></button></div>`;
    $('#dashboardLoadoutSelect').onchange=e=>{selectLoadout(set,e.target.value);renderCombat();renderDashboard();};
  }
  function renderDashboardFavorites(){
    const host=$('#dashboardFavorites');if(!host||!state.current)return;const names=favoriteTalentNames(),rows=state.current.talents.filter(t=>names.has(t.name));if(!rows.length){host.innerHTML='<div class="empty-comp">Noch keine Lieblingstalente. In der Talentliste einfach ☆ anklicken.</div>';return;}
    host.innerHTML=`<div class="dashboard-fav-list">${rows.map(t=>{const idx=state.current.talents.indexOf(t),ref=registerRoll(`dashboard:fav:${idx}`,rollPayloadForThreePart(t.name,t.probe,t.value,'talent'));return `<div class="dashboard-fav-row"><button type="button" class="favorite-star active dashboard-fav-remove" data-favorite-talent="${esc(t.name)}" title="Entfernen">★</button><div class="dashboard-fav-roll" tabindex="0" role="button" data-roll-ref="${ref}"><div class="dashboard-fav-name">${esc(t.name)} <span class="roll-mark">◆</span></div><div class="dashboard-fav-probe">${esc(t.probe)}</div></div><div class="dashboard-fav-value">${t.value}</div></div>`;}).join('')}</div>`;host.querySelectorAll('.dashboard-fav-remove').forEach(b=>b.onclick=e=>{e.preventDefault();e.stopPropagation();toggleFavoriteTalent(b.dataset.favoriteTalent);});
  }
  function renderDashboardMoney(){const host=$('#dashboardMoney');if(!host||!companionState.data)return;host.innerHTML=`<div class="dashboard-money-total">${esc(moneyTextFromTotal(moneyTotalK(),true))}</div><button type="button" id="dashboardMoneyBook" class="action-btn">Buchung öffnen</button>`;$('#dashboardMoneyBook').onclick=()=>{const tab=$('.tab[data-tab="inventory"]');tab?.click();setTimeout(()=>$('.money-card')?.scrollIntoView({behavior:'smooth',block:'center'}),30);};}
  function renderDashboardMagic(){
    const host=$('#dashboardMagic');if(!host||!companionState.data)return;const slots=[...(companionState.data.magic?.staffSlots||[])].sort((a,b)=>(a.slot||0)-(b.slot||0));const hasStorage=state.current?.sfSet?.has('Stabzauber: Zauberspeicher');
    const rows=slots.map(x=>`<div class="dashboard-magic-row ${x.loaded?'':'empty-slot'}"><div class="dashboard-magic-title"><span class="slot-badge">Slot ${x.slot}</span>${esc(x.spell)} ${x.loaded?'<span class="loaded-badge">geladen</span>':'<span class="empty-badge">leer</span>'}</div><div class="dashboard-magic-meta">${x.zfp!=null?`ZfP* ${x.zfp} · `:''}${x.asp!=null?`${x.asp} AsP · `:''}${esc(x.note||'')}</div><div class="dashboard-magic-actions"><button type="button" class="action-btn dashboard-toggle-slot" data-slot-id="${x.id}">${x.loaded?'Auslösen':'Wieder laden'}</button></div></div>`).join('');
    host.innerHTML=`<div class="dashboard-magic-list">${rows||(hasStorage?'<div class="empty-comp">Zauberspeicher vorhanden, aber noch nicht belegt.</div>':'<div class="empty-comp">Kein Zauberspeicher erfasst.</div>')}</div><div class="dashboard-artifact-note">Artefakte werden im nächsten Schritt als allgemeine magische Gegenstände ergänzt – nicht als zweites, paralleles Zauberspeicher-System.</div>`;host.querySelectorAll('.dashboard-toggle-slot').forEach(b=>b.onclick=()=>toggleStaffSlot(b.dataset.slotId));
  }
  function renderDashboard(){
    if(!$('#dashboard')||!state.current||!companionState.data||companionState.data.heroKey!==state.current.key)return;const a=activeAdventure();$('#dashboardAdventureState').textContent=a?`Aktiv: ${a.title||'Abenteuer'}`:'kein aktives Abenteuer';renderDashboardAttributes();renderDashboardBody();renderDashboardCombat();renderDashboardFavorites();renderDashboardMoney();renderDashboardMagic();
  }
'''
one("\n\n  // ---- OneDrive / Microsoft Graph (v13 Beta) -----------------------------", "\n" + dashboard_js + "\n\n  // ---- OneDrive / Microsoft Graph (v13 Beta) -----------------------------", 'insert dashboard JS')

# Dashboard fresh on tab open; new tab is placed after Daten for existing saved orders.
one(
"function applyTabOrder(){let order=[];try{order=JSON.parse(localStorage.getItem(TAB_ORDER_KEY)||'[]');}catch(_){order=[];}const nav=$('.tabs'),buttons=new Map",
"function applyTabOrder(){let order=[];try{order=JSON.parse(localStorage.getItem(TAB_ORDER_KEY)||'[]');}catch(_){order=[];}if(!order.includes('dashboard')){const i=order.indexOf('data');order.splice(i>=0?i+1:0,0,'dashboard');}const nav=$('.tabs'),buttons=new Map",
'dashboard tab order')
one(
"$$('.tab').forEach(btn=>btn.addEventListener('click',()=>{if(btn.disabled||$('.tabs').classList.contains('sort-mode'))return;$$('.tab').forEach(b=>b.classList.toggle('active',b===btn));$$('.section').forEach(s=>s.classList.toggle('active',s.id===btn.dataset.tab));}));",
"$$('.tab').forEach(btn=>btn.addEventListener('click',()=>{if(btn.disabled||$('.tabs').classList.contains('sort-mode'))return;$$('.tab').forEach(b=>b.classList.toggle('active',b===btn));$$('.section').forEach(s=>s.classList.toggle('active',s.id===btn.dataset.tab));if(btn.dataset.tab==='dashboard')renderDashboard();}));",
'tab dashboard refresh')

# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------
required = [
    'data-tab="dashboard"', 'id="dashboardBodyMap"', '/* v17 Spieltisch */', 'const COMP_SCHEMA=6;',
    'body-female.webp', 'body-male.webp', 'WOUND_ZONE_KEYS', 'favoriteTalentNames', 'function renderDashboard()',
    "dancer?'2W6':'1W6'", 'Math.max(1,Number((String(calc.ini.dice).match'
]
for token in required:
    if token not in s:
        raise RuntimeError(f'missing v17 token: {token}')
if 'const COMP_SCHEMA=5;' in s:
    raise RuntimeError('old schema remains')
if "calc.ini.dice==='3W6'?[3,6" in s:
    raise RuntimeError('old Klingentänzer roll payload remains')

PATH.write_text(s, encoding='utf-8')
print(f'Applied v17: {len(original)} -> {len(s)} chars')
