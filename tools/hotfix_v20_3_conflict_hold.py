from pathlib import Path

app_path=Path('js/app.js')
smoke_path=Path('tests/smoke.mjs')
app=app_path.read_text(encoding='utf-8')
smoke=smoke_path.read_text(encoding='utf-8')

old="""  async function cloudSaveCurrent(force=false){
    const key=state.current?.key,d=companionState.data;if(!key||!d){return;}if(!cloudIsConnected()){cloudMessage('Nicht mit Microsoft verbunden.','warn','#cloudSyncMessage');return;}if(cloudState.saving)return;cloudState.saving=true;cloudMessage('Speichere Begleitdaten nach OneDrive …','','#cloudSyncMessage');
"""
new="""  async function cloudSaveCurrent(force=false){
    const key=state.current?.key,d=companionState.data;if(!key||!d){return;}if(!cloudIsConnected()){cloudMessage('Nicht mit Microsoft verbunden.','warn','#cloudSyncMessage');return;}if(cloudState.conflictHeroKey===key&&!force){cloudMessage('Konflikt ist noch nicht aufgelöst. Bitte OneDrive-Version laden oder bewusst überschreiben.','warn','#cloudSyncMessage');return;}if(cloudState.saving)return;cloudState.saving=true;cloudMessage('Speichere Begleitdaten nach OneDrive …','','#cloudSyncMessage');
"""
if app.count(old)!=1:
    raise SystemExit(f'cloudSaveCurrent marker count: {app.count(old)}')
app=app.replace(old,new,1)

marker="ok(app.includes(\"lastQualityAudit={version:'20.3'\"), 'quality audit JSON version must be v20.3');"
addition=marker+"\nok(app.includes(\"cloudState.conflictHeroKey===key&&!force\"), 'unresolved OneDrive conflict must block automatic save');"
if smoke.count(marker)!=1:
    raise SystemExit(f'smoke marker count: {smoke.count(marker)}')
smoke=smoke.replace(marker,addition,1)

app_path.write_text(app,encoding='utf-8')
smoke_path.write_text(smoke,encoding='utf-8')
print('prepared v20.3 unresolved conflict guard')
