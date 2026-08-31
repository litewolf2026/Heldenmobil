import fs from 'node:fs';
import vm from 'node:vm';

const index = fs.readFileSync('index.html', 'utf8');
const app = fs.readFileSync('js/app.js', 'utf8');
const vendor = fs.readFileSync('vendor/jszip-3.10.1.min.js', 'utf8');

function ok(condition, message) {
  if (!condition) throw new Error(message);
}

ok(index.includes('<script src="vendor/jszip-3.10.1.min.js"></script>'), 'index must load vendored JSZip');
ok(index.includes('<script src="js/app.js"></script>'), 'index must load app.js');
ok(!index.includes('JSZip v3.10.1 - A JavaScript class'), 'JSZip must no longer be inline');
ok(!index.includes("const state = { heroes:"), 'application code must no longer be inline');
ok(index.includes('Beta v20.0'), 'visible version badge must be v20.0');
ok(index.includes('Begleitdaten v20.0'), 'header version must be v20.0');
ok(index.includes('HeldenMobil Beta v20.0'), 'footer version must be v20.0');
ok(app.includes('function parseHero'), 'HLD parser contract missing');
ok(app.includes('function setArmor'), 'armor rule contract missing');
ok(app.includes('function combatEbe'), 'effective-BE rule contract missing');
ok(app.includes('function parseLiturgySfName'), 'liturgy parser contract missing');
ok(app.includes('function normalizeCompanion'), 'companion migration contract missing');
ok(app.includes("const wd=woundData(),gbe=armor.be"), 'gBE semantic fix must remain');
ok(vendor.includes('JSZip v3.10.1'), 'wrong JSZip vendor payload');

new vm.Script(app, { filename: 'js/app.js' });
new vm.Script(vendor, { filename: 'vendor/jszip-3.10.1.min.js' });
console.log('HeldenMobil v20.0 smoke tests passed');
