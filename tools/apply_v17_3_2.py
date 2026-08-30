from pathlib import Path
import re
import subprocess

path = Path('index.html')
text = path.read_text(encoding='utf-8')

text = text.replace('v17.3.1', 'v17.3.2')

reference_block = r'''  // DSA 4.1 standard fallbacks used when the HLD omits invariant weapon data.
  // HLD/XML-specific values always win. Nah- und Fernkampf sind getrennt,
  // weil mehrere Gegenstaende (z.B. Speer/Wurfmesser) beide Profile besitzen.
  const MELEE_REF = {
    'Kurzschwert': {kind:'melee', dk:'HN', tp:[1,6,2], tpkk:[11,4], ini:0, wm:[0,-1], bf:1},
    'Streitkolben': {kind:'melee', talent:'Hiebwaffen', dk:'N', tp:[1,6,4], tpkk:[11,3], ini:0, wm:[0,-1], bf:1},
    'Spitzhacke': {kind:'melee', talent:'Zweihandhiebwaffen', dk:'N', tp:[1,6,6], tpkk:[13,2], ini:-3, wm:[-2,-4], bf:5},
    'Fackel': {kind:'melee', talent:'Hiebwaffen', dk:'HN', tp:[1,6,0], tpkk:[11,5], ini:-2, wm:[-2,-3], bf:8},
    'Magierstab': {kind:'melee', talent:'Stäbe', dk:'NS', tp:[1,6,1], tpkk:[11,5], ini:0, wm:[-1,-1], bf:null},
    'Magierstab als Stab': {kind:'melee', talent:'Stäbe', dk:'NS', tp:[1,6,1], tpkk:[11,5], ini:0, wm:[-1,-1], bf:null},
    'Langdolch': {kind:'melee', dk:'H', tp:[1,6,2], tpkk:[12,4], ini:0, wm:[0,0], bf:1},
    'Hakendolch': {kind:'melee', talent:'Dolche', dk:'HN', tp:[1,6,1], tpkk:[12,4], ini:0, wm:[0,1], bf:-2},
    'Borndorn': {kind:'melee', talent:'Dolche', dk:'H', tp:[1,6,2], tpkk:[12,5], ini:0, wm:[0,-1], bf:1},
    'Wurfmesser': {kind:'melee', talent:'Dolche', dk:'H', tp:[1,6,-1], tpkk:[12,6], ini:-1, wm:[-2,-3], bf:2},
    'Wurfbeil': {kind:'melee', talent:'Hiebwaffen', dk:'H', tp:[1,6,3], tpkk:[10,4], ini:-1, wm:[0,-2], bf:2},
    'Säbel': {kind:'melee', talent:'Säbel', dk:'N', tp:[1,6,3], tpkk:[12,4], ini:1, wm:[0,0], bf:2},
    'Haumesser': {kind:'melee', dk:'HN', tp:[1,6,3], tpkk:[13,3], ini:-1, wm:[0,-2], bf:3},
    '(Lang-)Schwert': {kind:'melee', talent:'Schwerter', dk:'N', tp:[1,6,4], tpkk:[11,4], ini:0, wm:[0,0], bf:1},
    'Warunker Hammer': {kind:'melee', dk:'NS', tp:[1,6,6], tpkk:[14,3], ini:-1, wm:[0,-1], bf:2},
    'Beil': {kind:'melee', talent:'Hiebwaffen', dk:'N', tp:[1,6,3], tpkk:[11,4], ini:-1, wm:[-1,-2], bf:5},
    'Byakka': {kind:'melee', talent:'Hiebwaffen', dk:'N', tp:[1,6,5], tpkk:[14,2], ini:-1, wm:[0,-2], bf:3},
    'Schmiedehammer': {kind:'melee', talent:'Hiebwaffen', dk:'N', tp:[1,6,4], tpkk:[14,2], ini:-1, wm:[-1,-1], bf:1},
    'Skraja': {kind:'melee', talent:'Hiebwaffen', dk:'N', tp:[1,6,3], tpkk:[11,3], ini:0, wm:[0,0], bf:4},
    'Zwergenskraja': {kind:'melee', talent:'Hiebwaffen', dk:'HN', tp:[1,6,3], tpkk:[11,3], ini:0, wm:[0,0], bf:1},
    'Kriegslanze': {kind:'melee', dk:'P', tp:[1,6,3], tpkk:[12,5], ini:-2, wm:[-2,-4], bf:5},
    'Speer': {kind:'melee', talent:'Speere', dk:'S', tp:[1,6,5], tpkk:[12,4], ini:-1, wm:[0,-2], bf:5},
    'Wurfspeer': {kind:'melee', talent:'Speere', dk:'N', tp:[1,6,3], tpkk:[11,5], ini:-2, wm:[-1,-3], bf:4},
    'Rondrakamm': {kind:'melee', talent:'Zweihandschwerter/-säbel', dk:'NS', tp:[2,6,2], tpkk:[12,3], ini:0, wm:[0,0], bf:1},
    'Zweihänder': {kind:'melee', talent:'Zweihandschwerter/-säbel', dk:'NS', tp:[2,6,4], tpkk:[12,3], ini:-1, wm:[0,-1], bf:2},
    'Magierdegen': {kind:'melee', talent:'Fechtwaffen', dk:'N', tp:[1,6,2], tpkk:[13,5], ini:1, wm:[0,-2], bf:4}
  };
  const RANGED_REF = {
    'Leichte Armbrust': {kind:'ranged', talent:'Armbrust', tp:[1,6,6], ranges:[10,15,25,40,60], rangeTp:[1,0,0,0,-1]},
    'Balestrina': {kind:'ranged', talent:'Armbrust', tp:[1,6,4], ranges:[2,4,8,15,25], rangeTp:[2,1,0,0,-1]},
    'Windenarmbrust': {kind:'ranged', talent:'Armbrust', tp:[2,6,6], ranges:[10,30,60,100,180], rangeTp:[4,2,0,-1,-3]},
    'Kurzbogen': {kind:'ranged', talent:'Bogen', tp:[1,6,4], ranges:[5,15,25,40,60], rangeTp:[1,1,0,0,-1]},
    'Fledermaus': {kind:'ranged', talent:'Schleuder', tp:[1,6,6], ranges:[0,5,10,15,25], rangeTp:['–',0,0,0,-1]},
    'Schleuder': {kind:'ranged', talent:'Schleuder', tp:[1,6,2], ranges:[0,5,15,25,40], rangeTp:['–',0,0,0,0]},
    'Wurfbeil': {kind:'ranged', talent:'Wurfbeile', tp:[1,6,3], ranges:[0,5,10,15,25], rangeTp:['–',1,1,0,-1]},
    'Wurfmesser': {kind:'ranged', talent:'Wurfmesser', tp:[1,6,0], ranges:[2,4,6,8,15], rangeTp:[1,0,0,0,-1]},
    'Borndorn': {kind:'ranged', talent:'Wurfmesser', tp:[1,6,2], ranges:[2,4,6,8,15], rangeTp:[1,0,0,0,-1]},
    'Speer': {kind:'ranged', talent:'Wurfspeere', tp:[1,6,3], ranges:[5,10,15,25,40], rangeTp:[1,0,0,-1,-2]},
    'Wurfspeer': {kind:'ranged', talent:'Wurfspeere', tp:[1,6,4], ranges:[5,10,15,25,40], rangeTp:[3,1,0,-1,-1]},
    'Wurfscheibe': {kind:'ranged', talent:'Wurfmesser', tp:[1,6,1], ranges:[2,4,8,12,20], rangeTp:[1,0,0,0,0]},
    'Wurfstern': {kind:'ranged', talent:'Wurfmesser', tp:[1,6,1], ranges:[2,4,8,12,20], rangeTp:[1,0,0,0,0]}
  };
  const SHIELD_REF = {
    'Holzschild': {ini:-1, wm:[-1,3], bf:3},
    'Mattenschild': {ini:0, wm:[-1,4], bf:6},
    'Thorwaler Rundschild': {ini:-1, wm:[-2,4], bf:3},
    'Großschild': {ini:-2, wm:[-2,5], bf:2},
    'Bock': {ini:0, wm:[-1,1], bf:0},
    'Panzerarm': {ini:0, wm:[-2,1], bf:-2}
  };
  // Parierwaffen liegen in der HLD im gleichen Slot-Typ wie Schilde.
  const PARRY_REF = {
    'Langdolch': {ini:0, wm:[0,1], bf:1},
    'Hakendolch': {ini:0, wm:[-1,3], bf:-2},
    'Linkhand': {ini:1, wm:[0,2], bf:0},
    'Bock': {ini:0, wm:[-1,1], bf:0},
    'Panzerarm': {ini:0, wm:[-2,1], bf:-2}
  };
'''

pattern = re.compile(r"  // HLD speichert viele Standardwerte der Ausrüstung nur über den Gegenstandsnamen\..*?  const PARRY_REF = \{.*?\n  \};\n", re.S)
text, count = pattern.subn(reference_block, text, count=1)
if count != 1:
    raise SystemExit(f'reference block replacement failed: {count}')

text = text.replace("const ref=WEAPON_REF[e.base]||{};const xml=e.item?.nk||{};", "const ref=MELEE_REF[e.base]||{};const xml=e.item?.nk||{};")
text = text.replace("const ref=WEAPON_REF[e.base]||{},tal=e.talent||ref.talent;const t=state.current.talents.find(x=>x.name===tal);", "const ref=RANGED_REF[e.base]||{},tal=e.talent||ref.talent;const t=state.current.talents.find(x=>x.name===tal);")

old_spell_dupes = "    for(const n of qualityDupes(spells.map(z=>`${z.name} [${z.rep||'–'}]`)))qualityIssue(issues,'warn','SPELL_DUPLICATE',`${n} kommt mehrfach vor.`,'Zauber');"
new_spell_dupes = """    const spellGroups=new Map();for(const z of spells){const key=`${z.name} [${z.rep||'–'}]`;if(!spellGroups.has(key))spellGroups.set(key,[]);spellGroups.get(key).push(z);}\n    for(const [key,rows] of spellGroups){if(rows.length<2)continue;const details=rows.map(z=>`ZfW ${z.value} · Spalte ${z.column||'–'} · Probe ${z.probe||'–'}${z.house?' · Hauszauber':''}`).join(' | ');qualityIssue(issues,'warn','SPELL_DUPLICATE',`${key} kommt ${rows.length}× vor: ${details}.`,'Zauber');}"""
if old_spell_dupes not in text:
    raise SystemExit('spell duplicate block not found')
text = text.replace(old_spell_dupes, new_spell_dupes, 1)

old_melee = """        const ref=WEAPON_REF[e.base]||{},xml=e.item?.nk||{},tal=e.talent||ref.talent;\n        if(!e.item&&!WEAPON_REF[e.base]){qualityIssue(issues,'warn','MELEE_REFERENCE',`${qualityEquipmentName(e)}: weder HLD-Gegenstand noch Waffenreferenz gefunden.`,where);catalog.unknownCombat.add(e.base);}\n        if(!(xml.tp||ref.tp))qualityIssue(issues,'warn','MELEE_DAMAGE',`${qualityEquipmentName(e)}: Trefferpunkte fehlen.`,where);"""
new_melee = """        const ref=MELEE_REF[e.base]||{},xml=e.item?.nk||{},tal=e.talent||ref.talent;\n        if(!e.item&&!MELEE_REF[e.base]&&!SHIELD_REF[e.base]&&!PARRY_REF[e.base]){qualityIssue(issues,'warn','MELEE_REFERENCE',`${qualityEquipmentName(e)}: weder HLD-Gegenstand noch Nahkampfreferenz gefunden.`,where);catalog.unknownCombat.add(e.base);}\n        if(!(xml.tp||ref.tp)){if(SHIELD_REF[e.base]||PARRY_REF[e.base])qualityIssue(issues,'info','SHIELD_MELEE',`${qualityEquipmentName(e)} erscheint zusätzlich als Nahkampfeintrag; dafür existiert bewusst kein normaler Waffen-TP-Fallback.`,where);else qualityIssue(issues,'warn','MELEE_DAMAGE',`${qualityEquipmentName(e)}: Trefferpunkte fehlen.`,where);}"""
if old_melee not in text:
    raise SystemExit('melee audit block not found')
text = text.replace(old_melee, new_melee, 1)

old_ranged = """        const ref=WEAPON_REF[e.base]||{},tal=e.talent||ref.talent;\n        if(!WEAPON_REF[e.base]){qualityIssue(issues,'warn','RANGED_REFERENCE',`${qualityEquipmentName(e)}: keine Fernkampf-Referenzdaten vorhanden.`,where);catalog.unknownCombat.add(e.base);}\n        if(!tal)qualityIssue(issues,'warn','RANGED_TALENT',`${qualityEquipmentName(e)}: Fernkampftalent fehlt.`,where);\n        else if(!talents.some(t=>t.name===tal)&&!h.combatMap.has(tal))qualityIssue(issues,'warn','RANGED_TALENT_MATCH',`${qualityEquipmentName(e)}: Talent „${tal}“ ist beim Helden nicht vorhanden.`,where);"""
new_ranged = """        const ref=RANGED_REF[e.base]||{},tal=e.talent||ref.talent;\n        if(!RANGED_REF[e.base]){qualityIssue(issues,'warn','RANGED_REFERENCE',`${qualityEquipmentName(e)}: keine Fernkampf-Referenzdaten vorhanden.`,where);catalog.unknownCombat.add(e.base);}\n        if(!tal)qualityIssue(issues,'warn','RANGED_TALENT',`${qualityEquipmentName(e)}: Fernkampftalent fehlt.`,where);\n        else if(!talents.some(t=>t.name===tal)&&!h.combatMap.has(tal))qualityIssue(issues,'info','RANGED_TALENT_ZERO',`${qualityEquipmentName(e)}: Talent „${tal}“ ist beim Helden nicht separat vorhanden; HeldenMobil verwendet dafür TaW 0.`,where);"""
if old_ranged not in text:
    raise SystemExit('ranged audit block not found')
text = text.replace(old_ranged, new_ranged, 1)

if 'WEAPON_REF[' in text:
    raise SystemExit('legacy WEAPON_REF access remains')
for needle in ["const MELEE_REF = {", "const RANGED_REF = {", "'Balestrina':", "'Thorwaler Rundschild':", "RANGED_TALENT_ZERO", "SHIELD_MELEE", "HeldenMobil – HLD PoC v17.3.2"]:
    if needle not in text:
        raise SystemExit(f'missing contract marker: {needle}')

path.write_text(text, encoding='utf-8')

scripts = re.findall(r'<script(?:\\s[^>]*)?>(.*?)</script>', text, re.S | re.I)
if not scripts:
    raise SystemExit('no script blocks found')
check = Path('/tmp/heldenmobil-v17.3.2-check.js')
check.write_text('\n;\n'.join(scripts), encoding='utf-8')
subprocess.run(['node', '--check', str(check)], check=True)
print('v17.3.2 combat reference patch applied and syntax checked')
