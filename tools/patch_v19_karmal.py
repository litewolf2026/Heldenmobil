from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'marker missing: {label}')
    s=s.replace(old,new,1)

if 'v18.0.1' not in s:
    raise SystemExit('expected v18.0.1 base')
s=s.replace('v18.0.1','v19.0')

rep('const COMP_SCHEMA=7;','const COMP_SCHEMA=8;','schema')
rep('adventures:[],advancement:[],favorites:{talents:[],spells:[]},inventory:',
    'adventures:[],advancement:[],favorites:{talents:[],spells:[],liturgies:[]},inventory:',
    'empty favorites')
rep("x.favorites.spells=Array.isArray(x.favorites.spells)?[...new Set(x.favorites.spells.map(String).filter(Boolean))]:[];delete x.magic.artifacts;",
    "x.favorites.spells=Array.isArray(x.favorites.spells)?[...new Set(x.favorites.spells.map(String).filter(Boolean))]:[];x.favorites.liturgies=Array.isArray(x.favorites.liturgies)?[...new Set(x.favorites.liturgies.map(String).filter(Boolean))]:[];delete x.magic.artifacts;",
    'favorite normalization')
rep('for(const v of [6,5,4,3,2,1])','for(const v of [7,6,5,4,3,2,1])','schema migration')

rep('    <button class="tab" data-tab="spells" disabled>Zauber</button>\n    <button class="tab" data-tab="combat" disabled>Kampf</button>',
    '    <button class="tab" data-tab="spells" disabled>Zauber</button>\n    <button class="tab hidden" data-tab="liturgies" disabled>Liturgien</button>\n    <button class="tab" data-tab="combat" disabled>Kampf</button>',
    'liturgy tab')

liturgy_section='''\n    <section id="liturgies" class="section">\n      <div class="section-title"><h3>Liturgien</h3><span class="count" id="liturgyCount"></span></div>\n      <div class="comp-card liturgy-knowledge-card">\n        <h4>Liturgiekenntnis</h4>\n        <div id="liturgyKnowledge"></div>\n      </div>\n      <div class="comp-card liturgy-list-card">\n        <h4><span>Segnungen</span><span class="count" id="blessingCount"></span></h4>\n        <div class="liturgy-toolbar"><input class="search" id="liturgySearch" placeholder="Liturgien und Segnungen filtern …"></div>\n        <div class="tablewrap"><table class="liturgy-table"><thead><tr><th></th><th>Segnung</th><th>Grad</th></tr></thead><tbody id="blessingBody"></tbody></table></div>\n      </div>\n      <div class="comp-card liturgy-list-card">\n        <h4><span>Liturgien</span><span class="count" id="liturgyProperCount"></span></h4>\n        <div class="tablewrap"><table class="liturgy-table"><thead><tr><th></th><th>Liturgie</th><th>Grad</th></tr></thead><tbody id="liturgyBody"></tbody></table></div>\n      </div>\n      <div class="hld-note">Grade werden ausschließlich aus der HLD übernommen. Eine unnummerierte Fassung wird als Grundgrad angezeigt; zusätzliche gelernte Grade stehen in der Heldensoftware als römische Zahl im Namen.</div>\n    </section>\n\n'''
rep('    <section id="combat" class="section">',liturgy_section+'    <section id="combat" class="section">','liturgy section')

rep('          <div class="comp-card hidden" id="dashboardSpellFavoritesCard"><h4>Lieblingszauber</h4><div id="dashboardSpellFavorites"></div></div>\n          <div class="comp-card"><h4>Geld</h4><div id="dashboardMoney"></div></div>',
    '          <div class="comp-card hidden" id="dashboardSpellFavoritesCard"><h4>Lieblingszauber</h4><div id="dashboardSpellFavorites"></div></div>\n          <div class="comp-card hidden" id="dashboardLiturgyFavoritesCard"><h4>Lieblingsliturgien</h4><div id="dashboardLiturgyFavorites"></div></div>\n          <div class="comp-card"><h4>Geld</h4><div id="dashboardMoney"></div></div>',
    'dashboard liturgy card')

css='''\n/* v19 Geweihte / Liturgien */\n.liturgy-knowledge-card,.liturgy-list-card{margin-bottom:12px}.liturgy-toolbar{margin-bottom:10px}.liturgy-table{min-width:520px}.liturgy-table th:first-child,.liturgy-table td:first-child{width:42px;text-align:center}.liturgy-grade{display:inline-block;border:1px solid #625639;color:#e7cc86;background:#252117;border-radius:999px;padding:2px 7px;font-size:.66rem;white-space:nowrap}.liturgy-grade.base{border-color:#46505d;color:#aeb9c8;background:#15191f}.liturgy-knowledge-list{display:flex;flex-direction:column;gap:8px}.liturgy-knowledge-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;align-items:center;border:1px solid #303744;background:#12161b;border-radius:9px;padding:10px}.liturgy-knowledge-title{font-weight:800;color:#f0d58d}.liturgy-knowledge-meta{font-size:.72rem;color:var(--muted);margin-top:3px}.liturgy-knowledge-value{display:flex;align-items:center;gap:8px}.liturgy-knowledge-value strong{font-size:1.18rem;color:#f0d58d}.liturgy-kap{display:inline-block;border:1px solid #5b4f78;color:#d9c8ff;background:#201a2a;border-radius:999px;padding:3px 8px;font-size:.7rem;margin-left:6px}.liturgy-name{font-weight:720}.liturgy-name .roll-mark{margin-left:4px}@media(max-width:600px){.liturgy-knowledge-row{grid-template-columns:1fr}.liturgy-knowledge-value{justify-content:flex-start}.liturgy-table{min-width:430px}}\n\n'''
rep('/* v12 OneDrive / Microsoft Graph beta */',css+'/* v12 OneDrive / Microsoft Graph beta */','liturgy css')

helpers='''\n  const BASIC_BLESSING_NAMES=new Set(['Eidsegen','Feuersegen','Geburtssegen','Glückssegen','Grabsegen','Harmoniesegen','Heilungssegen','Märtyrersegen','Objektsegen','Schutzsegen','Speisesegen','Tranksegen','Weisheitssegen']);\n  function parseLiturgySfName(raw,index=0){\n    const full=String(raw||'').replace(/^Liturgie:\\s*/,'').trim(),m=/^(.*?)\\s+\\(([IVX]+)\\)$/.exec(full),name=(m?m[1]:full).trim(),grade=m?m[2]:'';\n    return {raw:String(raw||''),name,grade,gradeLabel:grade?`Grad ${grade}`:'Grundgrad',blessing:BASIC_BLESSING_NAMES.has(name),key:`${String(raw||'')}␟${index}`};\n  }\n  function liturgyKnowledgeDeity(t){const m=/^Liturgiekenntnis\\s*\\((.*?)\\)\\s*$/.exec(String(t?.name||''));return m?m[1]:String(t?.name||'').replace(/^Liturgiekenntnis\\s*/,'').trim()||'Geweiht';}\n  function primaryLiturgyKnowledge(){return state.current?.liturgyKnowledges?.[0]||null;}\n\n'''
rep('  function parseHero(hero){',helpers+'  function parseHero(hero){','liturgy parser helpers')

rep('    const sfSet=new Set(sf);\n    const talentSpecs=new Map(), spellSpecs=[];',
    "    const sfSet=new Set(sf);\n    const liturgyKnowledges=talents.filter(t=>/^Liturgiekenntnis\\s*\\(/.test(t.name));\n    const liturgies=sfEls.map((el,i)=>({el,name:attr(el,'name'),i})).filter(x=>/^Liturgie:\\s*/.test(x.name)).map(x=>parseLiturgySfName(x.name,x.i));\n    const karmal=liturgyKnowledges.length>0||liturgies.length>0||props.some(x=>x.name==='Karmaenergie'&&(Number(x.mod||0)!==0||Number(x.value||0)!==0))||sfSet.has('Karmalqueste');\n    const talentSpecs=new Map(), spellSpecs=[];",
    'parse karmal data')

rep('props,talents,spells,combat,combatMap,sf,sfEntries,sfSet,vt,advantages,disadvantages,vtNames,vtValues,meisterhandwerke,talentSpecs,combatSets,unarmedBonuses,rg1,items,',
    'props,talents,spells,liturgyKnowledges,liturgies,karmal,combat,combatMap,sf,sfEntries,sfSet,vt,advantages,disadvantages,vtNames,vtValues,meisterhandwerke,talentSpecs,combatSets,unarmedBonuses,rg1,items,',
    'hero return karmal')

old_roll="""  function rollPayloadForThreePart(name,probe,value,kind){\n    const attrs=probeAttributes(probe),pm=propMap(state.current.props),vals=attrs.map(a=>currentAttr(pm,a));\n    return {type:'check3',title:name,subtitle:`${kind==='spell'?'Zauberprobe':'Talentprobe'} · ${probe||'Probe nicht angegeben'}`,attrs,values:vals,skill:Number(value||0),skillLabel:kind==='spell'?'ZfW':'TaW',resultLabel:kind==='spell'?'ZfP*':'TaP*'};\n  }"""
new_roll="""  function rollPayloadForThreePart(name,probe,value,kind){\n    const attrs=probeAttributes(probe),pm=propMap(state.current.props),vals=attrs.map(a=>currentAttr(pm,a)),spell=kind==='spell',liturgy=kind==='liturgy';\n    return {type:'check3',title:name,subtitle:`${spell?'Zauberprobe':liturgy?'Liturgiekenntnisprobe':'Talentprobe'} · ${probe||'Probe nicht angegeben'}`,attrs,values:vals,skill:Number(value||0),skillLabel:spell?'ZfW':liturgy?'LkW':'TaW',resultLabel:spell?'ZfP*':liturgy?'LkP*':'TaP*'};\n  }"""
rep(old_roll,new_roll,'liturgy dice payload')

fav_marker="""  function toggleFavoriteSpell(key){const d=companionState.data;if(!d||d.heroKey!==state.current?.key)return;d.favorites=d.favorites||{talents:[],spells:[]};const set=new Set(d.favorites.spells||[]),parts=String(key).split('␟');if(parts.length>=3){const legacy=parts.slice(0,-1).join('␟');if(set.has(legacy)){set.delete(legacy);state.current?.spells?.forEach((z,i)=>{if(spellLegacyFavoriteKey(z)===legacy)set.add(spellFavoriteKey(z,i));});}}if(set.has(key))set.delete(key);else set.add(key);d.favorites.spells=[...set];saveCompanion();renderSpells();}\n"""
fav_add="""  function toggleFavoriteSpell(key){const d=companionState.data;if(!d||d.heroKey!==state.current?.key)return;d.favorites=d.favorites||{talents:[],spells:[],liturgies:[]};const set=new Set(d.favorites.spells||[]),parts=String(key).split('␟');if(parts.length>=3){const legacy=parts.slice(0,-1).join('␟');if(set.has(legacy)){set.delete(legacy);state.current?.spells?.forEach((z,i)=>{if(spellLegacyFavoriteKey(z)===legacy)set.add(spellFavoriteKey(z,i));});}}if(set.has(key))set.delete(key);else set.add(key);d.favorites.spells=[...set];saveCompanion();renderSpells();}\n  function favoriteLiturgyKeys(){const d=companionState.data;return new Set(d&&d.heroKey===state.current?.key?(d.favorites?.liturgies||[]):[]);}\n  function toggleFavoriteLiturgy(key){const d=companionState.data;if(!d||d.heroKey!==state.current?.key)return;d.favorites=d.favorites||{talents:[],spells:[],liturgies:[]};const set=new Set(d.favorites.liturgies||[]);if(set.has(key))set.delete(key);else set.add(key);d.favorites.liturgies=[...set];saveCompanion();renderLiturgies();}\n"""
rep(fav_marker,fav_add,'liturgy favorites')

render_lit='''\n  function renderLiturgies(){\n    const h=state.current,knowledgeHost=$('#liturgyKnowledge'),blessingBody=$('#blessingBody'),liturgyBody=$('#liturgyBody');if(!h||!knowledgeHost||!blessingBody||!liturgyBody)return;\n    const q=($('#liturgySearch')?.value||'').trim().toLocaleLowerCase('de'),fav=favoriteLiturgyKeys(),active=companionState.data?.heroKey===h.key?activeAdventure():null,maxKaP=new Map(deriveBasis(h.props).map(x=>[x.name,x.value])).get('KaP'),curKaP=active?.status?.kap;\n    knowledgeHost.innerHTML=`<div class="liturgy-knowledge-list">${h.liturgyKnowledges.map((t,i)=>{const ref=registerRoll(`liturgy:knowledge:${i}`,rollPayloadForThreePart(t.name,t.probe,t.value,'liturgy'));return `<div class="liturgy-knowledge-row"><div tabindex="0" role="button" class="rollable" data-roll-ref="${ref}"><div class="liturgy-knowledge-title">${esc(liturgyKnowledgeDeity(t))} <span class="roll-mark">◆</span></div><div class="liturgy-knowledge-meta">${esc(t.probe||'Probe nicht angegeben')}</div></div><div class="liturgy-knowledge-value"><span>LkW</span><strong>${t.value}</strong>${maxKaP!=null?`<span class="liturgy-kap">KaP ${curKaP!=null?`${curKaP} / `:''}${maxKaP}</span>`:''}</div></div>`;}).join('')||'<div class="empty-comp">Keine Liturgiekenntnis in der HLD gefunden.</div>'}</div>`;\n    const rows=h.liturgies.filter(l=>!q||(`${l.name} ${l.gradeLabel}`).toLocaleLowerCase('de').includes(q)),blessings=rows.filter(l=>l.blessing),proper=rows.filter(l=>!l.blessing),primary=primaryLiturgyKnowledge();\n    const rowHtml=l=>{const isFav=fav.has(l.key),ref=primary?registerRoll(`liturgy:${l.key}`,rollPayloadForThreePart(`${l.name} · ${l.gradeLabel}`,primary.probe,primary.value,'liturgy')):'';return `<tr${ref?` class="rollable-row" tabindex="0" data-roll-ref="${ref}" title="${esc(l.name)} würfeln"`:''}><td><button type="button" class="favorite-star ${isFav?'active':''}" data-favorite-liturgy="${esc(l.key)}" title="${isFav?'Von Lieblingsliturgien entfernen':'Zu Lieblingsliturgien hinzufügen'}">${isFav?'★':'☆'}</button></td><td><span class="liturgy-name">${esc(l.name)}${ref?' <span class="roll-mark">◆</span>':''}</span></td><td><span class="liturgy-grade ${l.grade?'':'base'}">${esc(l.gradeLabel)}</span></td></tr>`;};\n    blessingBody.innerHTML=blessings.map(rowHtml).join('')||'<tr><td colspan="3" class="empty">Keine Segnungen gefunden.</td></tr>';\n    liturgyBody.innerHTML=proper.map(rowHtml).join('')||'<tr><td colspan="3" class="empty">Keine Liturgien gefunden.</td></tr>';\n    $('#blessingCount').textContent=`${blessings.length}`;$('#liturgyProperCount').textContent=`${proper.length}`;$('#liturgyCount').textContent=q?`${rows.length} / ${h.liturgies.length}`:`${h.liturgies.length} Einträge`;\n    $$('#liturgies [data-favorite-liturgy]').forEach(b=>b.onclick=e=>{e.preventDefault();e.stopPropagation();toggleFavoriteLiturgy(b.dataset.favoriteLiturgy);});\n  }\n\n'''
rep('  function renderSonderfertigkeiten(){',render_lit+'  function renderSonderfertigkeiten(){','render liturgies')

old_renderhero="""    $('#workspace').classList.add('has-hero');$$('.tab[data-tab]').forEach(b=>{if(b.dataset.tab!=='data')b.disabled=false;});\n    $('#heroName').textContent=h.name;$('#heroMeta').textContent=[h.race,h.culture,h.profession].filter(Boolean).join(' · ');\n    $('#apTotal').textContent=h.ap.toLocaleString('de-DE');$('#apFree').textContent=h.freeAp.toLocaleString('de-DE');\n    renderAttributes();renderBasis();renderAttributeStrips();renderTalents();renderSpells();renderCombat();renderSonderfertigkeiten();renderChips('#advList','#advCount',h.advantages);renderChips('#disadvList','#disadvCount',h.disadvantages);\n    loadCompanionForHero();"""
new_renderhero="""    $('#workspace').classList.add('has-hero');$$('.tab[data-tab]').forEach(b=>{if(b.dataset.tab!=='data')b.disabled=false;});\n    const litTab=$('.tab[data-tab="liturgies"]');if(litTab){litTab.classList.toggle('hidden',!h.karmal);litTab.disabled=!h.karmal;if(!h.karmal&&litTab.classList.contains('active'))$('.tab[data-tab="overview"]')?.click();}\n    $('#heroName').textContent=h.name;$('#heroMeta').textContent=[h.race,h.culture,h.profession].filter(Boolean).join(' · ');\n    $('#apTotal').textContent=h.ap.toLocaleString('de-DE');$('#apFree').textContent=h.freeAp.toLocaleString('de-DE');\n    renderAttributes();renderBasis();renderAttributeStrips();renderTalents();renderSpells();renderLiturgies();renderCombat();renderSonderfertigkeiten();renderChips('#advList','#advCount',h.advantages);renderChips('#disadvList','#disadvCount',h.disadvantages);\n    loadCompanionForHero();"""
rep(old_renderhero,new_renderhero,'render hero karmal')

rep('function renderCompanionAll(){renderStatus();renderAdventures();renderAdvancement();renderInventory();renderMoney();renderMagic();renderDataMeta();refreshAdventureSelectors();refreshWishTargets();if(state.current)renderCombat();renderDashboard();}',
    'function renderCompanionAll(){renderStatus();renderAdventures();renderAdvancement();renderInventory();renderMoney();renderMagic();renderDataMeta();refreshAdventureSelectors();refreshWishTargets();if(state.current){renderCombat();renderLiturgies();}renderDashboard();}',
    'refresh liturgies with companion')

render_dash_lit='''\n  function renderDashboardLiturgyFavorites(){\n    const host=$('#dashboardLiturgyFavorites'),card=$('#dashboardLiturgyFavoritesCard'),h=state.current;if(!host||!card||!h)return;const fav=favoriteLiturgyKeys(),rows=h.liturgies.filter(l=>fav.has(l.key)),knowledge=primaryLiturgyKnowledge();card.classList.toggle('hidden',!rows.length);if(!rows.length){host.innerHTML='';return;}\n    host.innerHTML=`<div class="dashboard-fav-list">${rows.map(l=>{const ref=knowledge?registerRoll(`dashboard:liturgy:${l.key}`,rollPayloadForThreePart(`${l.name} · ${l.gradeLabel}`,knowledge.probe,knowledge.value,'liturgy')):'';return `<div class="dashboard-fav-row"><button type="button" class="favorite-star active dashboard-liturgy-fav-remove" data-favorite-liturgy="${esc(l.key)}" title="Entfernen">★</button><div class="dashboard-fav-roll" ${ref?`tabindex="0" role="button" data-roll-ref="${ref}"`:''}><div class="dashboard-fav-name">${esc(l.name)}${ref?' <span class="roll-mark">◆</span>':''}</div><div class="dashboard-fav-probe">${esc(l.gradeLabel)}${knowledge?` · ${esc(knowledge.probe)}`:''}</div></div><div class="dashboard-fav-value"><span class="dashboard-fav-unit">LkW</span>${knowledge?.value??'–'}</div></div>`;}).join('')}</div>`;host.querySelectorAll('.dashboard-liturgy-fav-remove').forEach(b=>b.onclick=e=>{e.preventDefault();e.stopPropagation();toggleFavoriteLiturgy(b.dataset.favoriteLiturgy);});\n  }\n'''
rep('  function renderDashboardMoney(){',render_dash_lit+'  function renderDashboardMoney(){','dashboard liturgy render')
rep('renderDashboardFavorites();renderDashboardSpellFavorites();renderDashboardMoney();renderDashboardMagic();',
    'renderDashboardFavorites();renderDashboardSpellFavorites();renderDashboardLiturgyFavorites();renderDashboardMoney();renderDashboardMagic();',
    'dashboard liturgy call')

# Hook search field after the normal spell filter setup if present.
rep("$('#spellSearch').addEventListener('input',renderSpells);",
    "$('#spellSearch').addEventListener('input',renderSpells);$('#liturgySearch')?.addEventListener('input',renderLiturgies);",
    'liturgy search hook')

# Contract checks
need=[
    'HeldenMobil – HLD PoC v19.0','const COMP_SCHEMA=8;','data-tab="liturgies"','section id="liturgies"',
    'Grundgrad','Grad ${grade}','favoriteLiturgyKeys','dashboardLiturgyFavoritesCard','renderDashboardLiturgyFavorites()',
    "for(const v of [7,6,5,4,3,2,1])",'Märtyrersegen','Objektsegen'
]
for marker in need:
    if marker not in s:
        raise SystemExit(f'contract marker missing: {marker}')
if 'v18.0.1' in s:
    raise SystemExit('old version marker remains')

p.write_text(s,encoding='utf-8')
print('v19 karmal patch applied')
