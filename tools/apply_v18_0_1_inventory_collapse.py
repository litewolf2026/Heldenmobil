from pathlib import Path

p=Path('index.html')
t=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global t
    if old not in t:
        raise SystemExit(f'missing marker: {label}')
    t=t.replace(old,new,1)

rep('HeldenMobil – HLD PoC v18.0','HeldenMobil – HLD PoC v18.0.1','title')
rep('HeldenMobil Qualitätsbericht v18.0','HeldenMobil Qualitätsbericht v18.0.1','audit text')
rep("lastQualityAudit={version:'18.0'","lastQualityAudit={version:'18.0.1'",'audit json')

old_art='''      <div id="artifactCard" class="comp-card artifact-card">\n        <div class="inv-head"><div><h4>Magische Gegenstände</h4><div class="subtle">Magische Eigenschaften gehören direkt zum Inventargegenstand. Waffen, Rüstungen, Ringe usw. bleiben deshalb ganz normal im Inventar; hier verwaltest du nur ihre Wirkungen.</div></div><span class="count" id="artifactCount"></span></div>\n        <div class="form-grid artifact-form">'''
new_art='''      <div id="artifactCard" class="comp-card artifact-card">\n        <h4><span>Magische Gegenstände</span><span class="count" id="artifactCount"></span></h4>\n        <div class="subtle">Magische Eigenschaften gehören direkt zum Inventargegenstand. Waffen, Rüstungen, Ringe usw. bleiben deshalb ganz normal im Inventar; hier verwaltest du nur ihre Wirkungen.</div>\n        <div class="form-grid artifact-form">'''
rep(old_art,new_art,'artifact header')

old_money='''      <div class="comp-card money-card">\n        <div class="inv-head"><div><h4>Geld</h4><div class="subtle">Kleine Kasse im selben Datensatz. Buchungen können positiv oder negativ sein; Excel-Import übernimmt vorhandene D/S/H-Buchungen.</div></div><span class="count" id="moneyCount"></span></div>\n        <div id="moneySummary" class="money-summary"></div>'''
new_money='''      <div class="comp-card money-card">\n        <h4><span>Geld</span><span class="count" id="moneyHeaderSummary"></span></h4>\n        <div class="subtle">Kleine Kasse im selben Datensatz. Buchungen können positiv oder negativ sein; Excel-Import übernimmt vorhandene D/S/H-Buchungen.</div>\n        <div id="moneySummary" class="money-summary"></div>'''
rep(old_money,new_money,'money header')

rep("$('#moneyCount').textContent=`${tx.length} Buchungen`;","$('#moneyHeaderSummary').textContent=`${moneyTextFromTotal(total,true)} · ${tx.length} Buchungen`;",'money header render')

old_open="row.querySelector('.magic-item-open')?.addEventListener('click',()=>{if($('#artifactItem'))$('#artifactItem').value=id;$('#artifactCard')?.scrollIntoView({behavior:'smooth',block:'start'});});"
new_open="row.querySelector('.magic-item-open')?.addEventListener('click',()=>{if($('#artifactItem'))$('#artifactItem').value=id;const card=$('#artifactCard');if(card?.classList.contains('box-collapsed'))card.querySelector(':scope > h4')?.click();card?.scrollIntoView({behavior:'smooth',block:'start'});});"
rep(old_open,new_open,'inventory magic opener')

old_dash="$('#dashboardMagicManage')?.addEventListener('click',()=>{const tab=$('.tab[data-tab=\"inventory\"]');tab?.click();setTimeout(()=>$('#artifactCard')?.scrollIntoView({behavior:'smooth',block:'start'}),30);});"
new_dash="$('#dashboardMagicManage')?.addEventListener('click',()=>{const tab=$('.tab[data-tab=\"inventory\"]');tab?.click();setTimeout(()=>{const card=$('#artifactCard');if(card?.classList.contains('box-collapsed'))card.querySelector(':scope > h4')?.click();card?.scrollIntoView({behavior:'smooth',block:'start'});},30);});"
rep(old_dash,new_dash,'dashboard magic opener')

css_marker='/* v18 magical inventory items */'
css_insert='''.artifact-card>h4,.money-card>h4{display:flex;align-items:center;justify-content:space-between;gap:10px}\n'''
if css_insert not in t:
    t=t.replace(css_marker,css_marker+'\n'+css_insert,1)

p.write_text(t,encoding='utf-8')
print('patched v18.0.1')
