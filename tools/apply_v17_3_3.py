from pathlib import Path

p = Path('index.html')
text = p.read_text(encoding='utf-8')

text = text.replace('v17.3.2', 'v17.3.3')
text = text.replace("lastQualityAudit={version:'17.3'", "lastQualityAudit={version:'17.3.3'", 1)

needle = "    'Magierstab': {kind:'melee', talent:'Stäbe', dk:'NS', tp:[1,6,1], tpkk:[11,5], ini:0, wm:[-1,-1], bf:null},\n"
insert = needle + "    'Magierstab (kurz)': {kind:'melee', talent:'Stäbe', dk:'N', tp:[1,6,0], tpkk:[11,4], ini:0, wm:[-1,-1], bf:null},\n"
if needle not in text:
    raise SystemExit('Magierstab reference anchor not found')
text = text.replace(needle, insert, 1)

old = """  function spellFavoriteKey(z){return `${z.name}␟${z.rep||''}`;}\n  function favoriteSpellKeys(){const d=companionState.data;return new Set(d&&d.heroKey===state.current?.key?(d.favorites?.spells||[]):[]);}\n  function toggleFavoriteSpell(key){const d=companionState.data;if(!d||d.heroKey!==state.current?.key)return;d.favorites=d.favorites||{talents:[],spells:[]};const set=new Set(d.favorites.spells||[]);if(set.has(key))set.delete(key);else set.add(key);d.favorites.spells=[...set];saveCompanion();renderSpells();}\n"""
new = """  function spellLegacyFavoriteKey(z){return `${z.name}␟${z.rep||''}`;}\n  function spellFavoriteKey(z,index){return `${spellLegacyFavoriteKey(z)}␟${index}`;}\n  function favoriteSpellKeys(){const d=companionState.data,raw=new Set(d&&d.heroKey===state.current?.key?(d.favorites?.spells||[]):[]),out=new Set(raw);if(state.current?.spells)state.current.spells.forEach((z,i)=>{if(raw.has(spellLegacyFavoriteKey(z)))out.add(spellFavoriteKey(z,i));});return out;}\n  function toggleFavoriteSpell(key){const d=companionState.data;if(!d||d.heroKey!==state.current?.key)return;d.favorites=d.favorites||{talents:[],spells:[]};const set=new Set(d.favorites.spells||[]),parts=String(key).split('␟');if(parts.length>=3){const legacy=parts.slice(0,-1).join('␟');if(set.has(legacy)){set.delete(legacy);state.current?.spells?.forEach((z,i)=>{if(spellLegacyFavoriteKey(z)===legacy)set.add(spellFavoriteKey(z,i));});}}if(set.has(key))set.delete(key);else set.add(key);d.favorites.spells=[...set];saveCompanion();renderSpells();}\n"""
if old not in text:
    raise SystemExit('favorite spell block not found')
text = text.replace(old, new, 1)

text = text.replace("key=spellFavoriteKey(z),isFav=fav.has(key)", "key=spellFavoriteKey(z,idx),isFav=fav.has(key)", 1)
text = text.replace("rows=state.current.spells.filter(z=>fav.has(spellFavoriteKey(z)))", "rows=state.current.spells.filter((z,i)=>fav.has(spellFavoriteKey(z,i)))", 1)
text = text.replace("key=spellFavoriteKey(z),specs=", "key=spellFavoriteKey(z,idx),specs=", 1)

old_dup = "qualityIssue(issues,'warn','SPELL_DUPLICATE',`${key} kommt ${rows.length}× vor: ${details}.`,'Zauber');"
new_dup = "qualityIssue(issues,'info','SPELL_DUPLICATE',`${key} kommt ${rows.length}× vor: ${details}. Mehrfache Einträge können bei getrennt gelernten Ausprägungen desselben Zaubers beabsichtigt sein.`,'Zauber');"
if old_dup not in text:
    raise SystemExit('duplicate spell audit anchor not found')
text = text.replace(old_dup, new_dup, 1)

p.write_text(text, encoding='utf-8')
print('patched v17.3.3')
