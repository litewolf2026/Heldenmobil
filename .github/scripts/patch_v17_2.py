from pathlib import Path

p = Path("index.html")
s = p.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    s = s.replace(old, new, 1)


def replace_block(start: str, end: str, new_block: str, label: str) -> None:
    global s
    a = s.find(start)
    if a < 0:
        raise SystemExit(f"{label}: start marker missing")
    b = s.find(end, a)
    if b < 0:
        raise SystemExit(f"{label}: end marker missing")
    if s.find(start, a + 1) >= 0:
        raise SystemExit(f"{label}: start marker not unique")
    s = s[:a] + new_block + s[b:]


# Release label.
replace_once(
    "<title>HeldenMobil – HLD PoC v17.1.3</title>",
    "<title>HeldenMobil – HLD PoC v17.2</title>",
    "title",
)
replace_once(
    '<div class="sub">DSA 4.1 · HLD + Begleitdaten v17.1.1</div>',
    '<div class="sub">DSA 4.1 · HLD + Begleitdaten v17.2</div>',
    "header sub",
)
replace_once(
    '<div class="badge">Proof of Concept v17.1.1</div>',
    '<div class="badge">Beta v17.2</div>',
    "header badge",
)

# Zauberliste in einen eigenen statischen comp-card-Block legen. Damit greift die
# bereits vorhandene generische Einklapp-Logik automatisch; magicExtras bleibt
# außerhalb und damit sichtbar, wenn die Zauberliste zugeklappt wird.
spell_start = '    <section id="spells" class="section">\n'
magic_marker = '      <div id="magicExtras" class="magic-extras">'
new_spell_prefix = '''    <section id="spells" class="section">
      <div class="section-title"><h3>Zauber</h3></div>
      <div class="comp-card spell-list-card">
        <h4><span>Zaubersprüche</span><span class="count" id="spellCount"></span></h4>
        <div class="spell-list-toolbar"><input class="search" id="spellSearch" placeholder="Zauber filtern …"></div>
        <div id="spellAttrStrip" class="attribute-strip" aria-label="Eigenschaften für Zauberproben"></div>
        <div class="tablewrap"><table><thead><tr><th>Zauber</th><th>Probe</th><th>Rep.</th><th>Spalte</th><th class="num">ZfW</th><th>Bemerkungen</th></tr></thead><tbody id="spellBody"></tbody></table></div>
      </div>
'''
a = s.find(spell_start)
b = s.find(magic_marker, a)
if a < 0 or b < 0:
    raise SystemExit("spell list markup markers missing")
combat_after = s.find('    <section id="combat" class="section">', b)
if combat_after < 0:
    raise SystemExit("combat marker missing after spells")
if s.find(spell_start, a + 1) >= 0:
    raise SystemExit("spell section marker not unique")
s = s[:a] + new_spell_prefix + s[b:]

# Lieblingszauber-Karte am Spieltisch; sie wird nur eingeblendet, wenn es Favoriten gibt.
replace_once(
    '          <div class="comp-card"><h4>Lieblingstalente</h4><div id="dashboardFavorites"></div></div>\n          <div class="comp-card"><h4>Geld</h4><div id="dashboardMoney"></div></div>',
    '          <div class="comp-card"><h4>Lieblingstalente</h4><div id="dashboardFavorites"></div></div>\n          <div class="comp-card hidden" id="dashboardSpellFavoritesCard"><h4>Lieblingszauber</h4><div id="dashboardSpellFavorites"></div></div>\n          <div class="comp-card"><h4>Geld</h4><div id="dashboardMoney"></div></div>',
    "dashboard favorite spell card",
)

# Kleine Darstellungsregeln; vorhandene Tags/Favoriten-Stile werden weiterverwendet.
css_anchor = "/* v17.1.3 final optical alignment */"
css_add = '''/* v17.2 spell favorites and collapsible spell list */
.spell-list-card{margin-bottom:12px}
.spell-list-card>h4{display:flex;align-items:center;gap:8px}
.spell-list-card>h4 .count{margin-left:auto}
.spell-list-toolbar{margin-bottom:10px}
.spell-list-toolbar .search{max-width:100%}
.dashboard-fav-tags{margin-top:5px}
.dashboard-fav-value{display:flex;flex-direction:column;align-items:flex-end;justify-content:center;line-height:1.05}
.dashboard-fav-unit{font-size:.55rem;color:#8994a2;text-transform:uppercase;letter-spacing:.04em;font-weight:700;margin-bottom:2px}

'''
if s.count(css_anchor) != 1:
    raise SystemExit("css anchor missing or duplicated")
s = s.replace(css_anchor, css_add + css_anchor, 1)

# Favoritenmodell additiv erweitern; alte v6-Begleitdaten bleiben kompatibel.
replace_once(
    "adventures:[],advancement:[],favorites:{talents:[]},inventory:",
    "adventures:[],advancement:[],favorites:{talents:[],spells:[]},inventory:",
    "empty favorites schema",
)
replace_once(
    "x.money.transactions=Array.isArray(x.money.transactions)?x.money.transactions:[];x.magic.staffSlots=Array.isArray(x.magic.staffSlots)?x.magic.staffSlots:[];x.favorites.talents=Array.isArray(x.favorites.talents)?[...new Set(x.favorites.talents.map(String).filter(Boolean))]:[];delete x.magic.artifacts;",
    "x.money.transactions=Array.isArray(x.money.transactions)?x.money.transactions:[];x.magic.staffSlots=Array.isArray(x.magic.staffSlots)?x.magic.staffSlots:[];x.favorites.talents=Array.isArray(x.favorites.talents)?[...new Set(x.favorites.talents.map(String).filter(Boolean))]:[];x.favorites.spells=Array.isArray(x.favorites.spells)?[...new Set(x.favorites.spells.map(String).filter(Boolean))]:[];delete x.magic.artifacts;",
    "normalize spell favorites",
)

# Favoriten-Helfer inklusive eindeutiger Kombination aus Zaubername und Repräsentation.
old_helpers = '''  function favoriteTalentNames(){const d=companionState.data;return new Set(d&&d.heroKey===state.current?.key?(d.favorites?.talents||[]):[]);}
  function toggleFavoriteTalent(name){const d=companionState.data;if(!d||d.heroKey!==state.current?.key)return;d.favorites=d.favorites||{talents:[]};const set=new Set(d.favorites.talents||[]);if(set.has(name))set.delete(name);else set.add(name);d.favorites.talents=[...set];saveCompanion();renderTalents();}'''
new_helpers = '''  function favoriteTalentNames(){const d=companionState.data;return new Set(d&&d.heroKey===state.current?.key?(d.favorites?.talents||[]):[]);}
  function toggleFavoriteTalent(name){const d=companionState.data;if(!d||d.heroKey!==state.current?.key)return;d.favorites=d.favorites||{talents:[],spells:[]};const set=new Set(d.favorites.talents||[]);if(set.has(name))set.delete(name);else set.add(name);d.favorites.talents=[...set];saveCompanion();renderTalents();}
  function spellFavoriteKey(z){return `${z.name}␟${z.rep||''}`;}
  function favoriteSpellKeys(){const d=companionState.data;return new Set(d&&d.heroKey===state.current?.key?(d.favorites?.spells||[]):[]);}
  function toggleFavoriteSpell(key){const d=companionState.data;if(!d||d.heroKey!==state.current?.key)return;d.favorites=d.favorites||{talents:[],spells:[]};const set=new Set(d.favorites.spells||[]);if(set.has(key))set.delete(key);else set.add(key);d.favorites.spells=[...set];saveCompanion();renderSpells();}
  function shortRepresentation(rep){const raw=String(rep||'').trim();if(!raw)return '–';if(raw.length<=5)return raw;const n=raw.toLocaleLowerCase('de');const map=[[/gildenmag|magier|magisch/,'Mag'],[/hex/,'Hex'],[/elf/,'Elf'],[/druid/,'Dru'],[/geod/,'Geo'],[/schelm/,'Sch'],[/scharlat/,'Srl'],[/kristall|achaz/,'Ach'],[/borbarad/,'Bor']];for(const [rx,label] of map)if(rx.test(n))return label;return raw.slice(0,4)+'.';}'''
replace_once(old_helpers, new_helpers, "favorite helpers")

# Zaubertabelle: Stern zum Markieren, Ergebniszahl, vorhandene Hauszauber-Anzeige bleibt hier erhalten.
new_render_spells = '''  function renderSpells(){
    const q=$('#spellSearch').value.trim().toLocaleLowerCase('de');const arr=state.current.spells.filter(z=>!q||(`${z.name} ${z.rep} ${z.probe} ${z.specs.join(' ')}`).toLocaleLowerCase('de').includes(q)),fav=favoriteSpellKeys();
    if($('#spellCount'))$('#spellCount').textContent=q?`${arr.length} / ${state.current.spells.length}`:`${state.current.spells.length} Zauber`;
    $('#spellBody').innerHTML=arr.map(z=>{const idx=state.current.spells.indexOf(z),ref=registerRoll(`spell:${idx}`,rollPayloadForThreePart(z.name,z.probe,z.value,'spell')),key=spellFavoriteKey(z),isFav=fav.has(key);return `<tr class="rollable-row" tabindex="0" data-roll-ref="${ref}" title="${esc(z.name)} würfeln"><td><button type="button" class="favorite-star ${isFav?'active':''}" data-favorite-spell="${esc(key)}" title="${isFav?'Von Lieblingszaubern entfernen':'Zu Lieblingszaubern hinzufügen'}">${isFav?'★':'☆'}</button>${esc(z.name)} <span class="roll-mark">◆</span> ${z.house?'<span class="house">★ Hauszauber</span>':''}</td><td>${esc(z.probe)}</td><td>${esc(z.rep)}</td><td>${esc(z.column)}</td><td class="num hot">${z.value}</td><td><div class="tagrow">${z.specs.map(sp=>`<span class="tag spec">Spez.: ${esc(sp)}</span>`).join('')}</div></td></tr>`;}).join('')||'<tr><td colspan="6" class="empty">Keine Treffer</td></tr>';
    $$('#spellBody .favorite-star').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();toggleFavoriteSpell(b.dataset.favoriteSpell);}));
  }
'''
replace_block(
    "  function renderSpells(){\n",
    "  function renderSonderfertigkeiten(){\n",
    new_render_spells + "\n",
    "renderSpells",
)

# Lieblingstalente mit Spezialisierungen + Meisterhandwerk, dazu Lieblingszauber mit
# kurzer Repräsentation, Spezialisierungen und direktem Würfeln. Hauszauber bewusst nicht.
new_dashboard_favorites = '''  function renderDashboardFavorites(){
    const host=$('#dashboardFavorites');if(!host||!state.current)return;const names=favoriteTalentNames(),rows=state.current.talents.filter(t=>names.has(t.name));if(!rows.length){host.innerHTML='<div class="empty-comp">Noch keine Lieblingstalente. In der Talentliste einfach ☆ anklicken.</div>';return;}
    host.innerHTML=`<div class="dashboard-fav-list">${rows.map(t=>{const idx=state.current.talents.indexOf(t),ref=registerRoll(`dashboard:fav:${idx}`,rollPayloadForThreePart(t.name,t.probe,t.value,'talent')),tags=[t.mh?'<span class="tag mh">Meisterhandwerk</span>':'',...t.specs.map(sp=>`<span class="tag spec">Spez.: ${esc(sp)}</span>`)].filter(Boolean).join('');return `<div class="dashboard-fav-row"><button type="button" class="favorite-star active dashboard-fav-remove" data-favorite-talent="${esc(t.name)}" title="Entfernen">★</button><div class="dashboard-fav-roll" tabindex="0" role="button" data-roll-ref="${ref}"><div class="dashboard-fav-name">${esc(t.name)} <span class="roll-mark">◆</span></div><div class="dashboard-fav-probe">${esc(t.probe)}</div>${tags?`<div class="tagrow dashboard-fav-tags">${tags}</div>`:''}</div><div class="dashboard-fav-value"><span class="dashboard-fav-unit">TaW</span>${t.value}</div></div>`;}).join('')}</div>`;host.querySelectorAll('.dashboard-fav-remove').forEach(b=>b.onclick=e=>{e.preventDefault();e.stopPropagation();toggleFavoriteTalent(b.dataset.favoriteTalent);});
  }
  function renderDashboardSpellFavorites(){
    const host=$('#dashboardSpellFavorites'),card=$('#dashboardSpellFavoritesCard');if(!host||!card||!state.current)return;const fav=favoriteSpellKeys(),rows=state.current.spells.filter(z=>fav.has(spellFavoriteKey(z)));card.classList.toggle('hidden',!rows.length);if(!rows.length){host.innerHTML='';return;}
    host.innerHTML=`<div class="dashboard-fav-list">${rows.map(z=>{const idx=state.current.spells.indexOf(z),ref=registerRoll(`dashboard:spellfav:${idx}`,rollPayloadForThreePart(z.name,z.probe,z.value,'spell')),key=spellFavoriteKey(z),specs=z.specs.map(sp=>`<span class="tag spec">Spez.: ${esc(sp)}</span>`).join('');return `<div class="dashboard-fav-row"><button type="button" class="favorite-star active dashboard-spell-fav-remove" data-favorite-spell="${esc(key)}" title="Entfernen">★</button><div class="dashboard-fav-roll" tabindex="0" role="button" data-roll-ref="${ref}"><div class="dashboard-fav-name">${esc(z.name)} <span class="roll-mark">◆</span></div><div class="dashboard-fav-probe">Rep. ${esc(shortRepresentation(z.rep))}${z.probe?` · ${esc(z.probe)}`:''}</div>${specs?`<div class="tagrow dashboard-fav-tags">${specs}</div>`:''}</div><div class="dashboard-fav-value"><span class="dashboard-fav-unit">ZfW</span>${z.value}</div></div>`;}).join('')}</div>`;host.querySelectorAll('.dashboard-spell-fav-remove').forEach(b=>b.onclick=e=>{e.preventDefault();e.stopPropagation();toggleFavoriteSpell(b.dataset.favoriteSpell);});
  }
'''
replace_block(
    "  function renderDashboardFavorites(){\n",
    "  function renderDashboardMoney(){",
    new_dashboard_favorites + "  function renderDashboardMoney(){",
    "dashboard favorites",
)

replace_once(
    "renderDashboardCombat();renderDashboardFavorites();renderDashboardMoney();renderDashboardMagic();",
    "renderDashboardCombat();renderDashboardFavorites();renderDashboardSpellFavorites();renderDashboardMoney();renderDashboardMagic();",
    "dashboard render call",
)

p.write_text(s, encoding="utf-8")

# Statische Vertragschecks.
required = [
    "HeldenMobil – HLD PoC v17.2",
    'class="comp-card spell-list-card"',
    'class="spell-list-toolbar"',
    'id="dashboardSpellFavorites"',
    "data-favorite-spell=",
    "function renderDashboardSpellFavorites()",
    "Meisterhandwerk</span>",
    "Rep. ${esc(shortRepresentation(z.rep))}",
    "favorites:{talents:[],spells:[]}",
    "renderDashboardSpellFavorites();",
]
for token in required:
    if token not in s:
        raise SystemExit(f"missing post-patch token: {token}")

# Wichtige Negativbedingung: Lieblingszauber am Spieltisch dürfen Hauszauber nicht anzeigen.
dash_spell_start = s.index("  function renderDashboardSpellFavorites(){")
dash_spell_end = s.index("  function renderDashboardMoney(){", dash_spell_start)
if "Hauszauber" in s[dash_spell_start:dash_spell_end]:
    raise SystemExit("Hauszauber leaked into dashboard favorite spells")

print("v17.2 patch contract OK")
