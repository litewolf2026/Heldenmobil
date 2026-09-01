import fs from 'node:fs';
import vm from 'node:vm';

const index = fs.readFileSync('index.html', 'utf8');
const app = fs.readFileSync('js/app.js', 'utf8');
const hld = fs.readFileSync('js/hld-parser.js', 'utf8');
const companion = fs.readFileSync('js/companion-core.js', 'utf8');
const combat = fs.readFileSync('js/combat-core.js', 'utf8');
const vendor = fs.readFileSync('vendor/jszip-3.10.1.min.js', 'utf8');

function ok(condition, message) { if (!condition) throw new Error(message); }

const order = ['vendor/jszip-3.10.1.min.js','js/hld-parser.js','js/companion-core.js','js/combat-core.js','js/app.js'].map(x=>index.indexOf(`<script src="${x}"></script>`));
ok(order.every(x=>x>=0) && order.every((x,i)=>i===0||x>order[i-1]), 'core scripts must load before app.js');
ok(!index.includes('JSZip v3.10.1 - A JavaScript class'), 'JSZip must stay external');
ok(index.includes('Beta v20.3.1'), 'visible version badge must be v20.3.1');
ok(index.includes('Begleitdaten v20.3.1'), 'header version must be v20.3.1');
ok(index.includes('HeldenMobil Beta v20.3.1'), 'footer version must be v20.3.1');
ok(hld.includes('function parseHero'), 'HLD parser must live in hld-parser.js');
ok(!app.includes('function parseHero(hero)'), 'HLD parser must no longer live in app.js');
ok(app.includes('HeldenMobilCompanion.normalizeCompanionData'), 'companion core delegate missing');
ok(app.includes('HeldenMobilCombat.combatEbe'), 'combat core delegate missing');
ok(app.includes("function automaticEvent(e){return e?.type==='energy';}"), 'wound/status events must remain manually managed');
ok(app.includes("lastQualityAudit={version:'20.3.1'"), 'quality audit JSON version must be v20.3.1');
ok(app.includes("cloudState.conflictHeroKey===key&&!force"), 'unresolved OneDrive conflict must block automatic save');
ok(app.includes("COMPANION_BACKUP_PREFIX='heldenmobil:backup:v1:'"), 'local companion snapshot storage missing');
ok(index.includes('id="backupRestore"') && index.includes('id="backupExport"'), 'backup restore/export UI missing');
ok(app.includes('Letzter erfolgreicher OneDrive-Sync:'), 'last successful sync timestamp missing');
ok(vendor.includes('JSZip v3.10.1'), 'wrong JSZip vendor payload');
for (const [name,src] of [['app',app],['hld',hld],['companion',companion],['combat',combat],['vendor',vendor]]) new vm.Script(src,{filename:`${name}.js`});
console.log('HeldenMobil v20.3.1 smoke tests passed');
