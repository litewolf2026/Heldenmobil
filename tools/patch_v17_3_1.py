from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

s = s.replace('<title>HeldenMobil – HLD PoC v17.3</title>', '<title>HeldenMobil – HLD PoC v17.3.1</title>', 1)
s = s.replace('HeldenMobil PoC v17.1.1', 'HeldenMobil PoC v17.3.1')
s = s.replace('HeldenMobil Qualitätsbericht v17.3', 'HeldenMobil Qualitätsbericht v17.3.1')

needle = "  function qualityCounterObject(map){return Object.fromEntries([...map.entries()].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0],'de')));}\n"
insert = needle + "  function qualityInternalEquipmentRecord(record){return /^(?:jagtwaffe|bk\\d+)$/i.test(String(record||'').trim());}\n  function qualityEquipmentName(e){const shown=String(e?.name||e?.base||'').trim(),base=String(e?.base||'').trim();return shown&&base&&shown!==base?`${shown} (Basis: ${base})`:(shown||base||'Unbenannter Gegenstand');}\n  function qualityDedupeIssues(items){\n    const map=new Map();\n    for(const issue of (items||[])){const key=`${issue.severity}\\u001f${issue.code}\\u001f${issue.detail}`,prev=map.get(key);if(!prev)map.set(key,{...issue,_areas:new Set(issue.area?[issue.area]:[])});else if(issue.area)prev._areas.add(issue.area);}\n    return [...map.values()].map(issue=>{const areas=[...issue._areas];delete issue._areas;if(areas.length>1&&areas.every(a=>/^Kampfset \\d+$/.test(a)))issue.area=`Kampfsets ${areas.map(a=>a.replace(/\\D/g,'')).join(', ')}`;else if(areas.length)issue.area=areas.join(' / ');return issue;});\n  }\n"
if needle not in s:
    raise SystemExit('quality helper anchor not found')
s = s.replace(needle, insert, 1)

start = s.index('  function qualityAuditOne(raw,index,catalog){')
end = s.index('  function qualityAuditText(report){', start)
block = s[start:end]

old_other = "      if(e.type==='other'){qualityIssue(issues,'info','EQUIP_UNKNOWN',`${e.record||'Unbekannter Eintrag'} konnte keinem Ausrüstungstyp zugeordnet werden.`,where);continue;}"
new_other = "      if(e.type==='other'){if(!qualityInternalEquipmentRecord(e.record))qualityIssue(issues,'info','EQUIP_UNKNOWN',`${e.record||'Unbekannter Eintrag'} konnte keinem Ausrüstungstyp zugeordnet werden.`,where);continue;}"
if old_other not in block:
    raise SystemExit('other equipment audit line not found')
block = block.replace(old_other, new_other, 1)

block = block.replace('${e.name||e.base}:', '${qualityEquipmentName(e)}:')

old_return = "    return {name:h.name||raw?.name||`Held ${index+1}`,key:h.key||raw?.key||'',race:h.race,gender:h.gender,talentCount:talents.length,spellCount:spells.length,combatSetCount:sets.length,issues};\n"
new_return = "    const cleanIssues=qualityDedupeIssues(issues);\n    return {name:h.name||raw?.name||`Held ${index+1}`,key:h.key||raw?.key||'',race:h.race,gender:h.gender,talentCount:talents.length,spellCount:spells.length,combatSetCount:sets.length,issues:cleanIssues};\n"
if old_return not in block:
    raise SystemExit('quality return line not found')
block = block.replace(old_return, new_return, 1)

s = s[:start] + block + s[end:]

p.write_text(s, encoding='utf-8')
print('patched v17.3.1 audit cleanup')
