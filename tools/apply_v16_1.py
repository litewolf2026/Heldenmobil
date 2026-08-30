from pathlib import Path

PATH = Path('index.html')
s = PATH.read_text(encoding='utf-8')

if '/* v16.1 klappbare Inhaltskästen */' in s:
    print('v16.1 already applied')
    raise SystemExit(0)

replacements = [
    ('HeldenMobil – HLD PoC v16', 'HeldenMobil – HLD PoC v16.1'),
    ('DSA 4.1 · HLD + Begleitdaten v16', 'DSA 4.1 · HLD + Begleitdaten v16.1'),
    ('Proof of Concept v16', 'Proof of Concept v16.1'),
    ('HeldenMobil PoC v16 · HLD read-only · Begleitdaten + OneDrive-Sync · Würfeltisch',
     'HeldenMobil PoC v16.1 · HLD read-only · Begleitdaten + OneDrive-Sync · Würfeltisch'),
]
for old, new in replacements:
    count = s.count(old)
    if count != 1:
        raise RuntimeError(f'Expected version marker once: {old!r}, found {count}')
    s = s.replace(old, new, 1)

css = r'''
/* v16.1 klappbare Inhaltskästen */
.box-collapse-heading{display:flex;align-items:center;gap:7px;cursor:pointer;user-select:none;outline:none}
.box-collapse-heading:hover{color:#f6dc98}
.box-collapse-heading:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}
.box-collapse-chevron{display:inline-flex;align-items:center;justify-content:center;width:1em;flex:0 0 1em;color:#b9a26b;font-weight:900}
.box-collapse-heading .count{margin-left:auto}
.box-collapsed>.box-collapse-root.box-collapse-heading{margin-bottom:0!important}
.box-collapsed>.box-collapse-root.sf-group-head{margin-bottom:0!important}
.box-collapsed>:not(.box-collapse-root){display:none!important}
.box-collapsed{padding-bottom:10px}
.box-collapsed.sf-group{padding-bottom:10px}
.combat-block.box-collapsed,.combat-card.box-collapsed,.comp-card.box-collapsed,.sf-group.box-collapsed{min-height:42px}
@media(max-width:650px){.box-collapse-heading{min-height:30px}.combat-block.box-collapsed,.combat-card.box-collapsed,.comp-card.box-collapsed,.sf-group.box-collapsed{min-height:44px}}
'''
if s.count('</style>') != 1:
    raise RuntimeError(f'Expected exactly one </style>, found {s.count("</style>")}')
s = s.replace('</style>', css + '\n</style>', 1)

js = r'''
  const CONTENT_BOX_COLLAPSE_KEY='heldenmobil:ui:collapsed-content-boxes:v1';
  function contentBoxState(){try{const a=JSON.parse(localStorage.getItem(CONTENT_BOX_COLLAPSE_KEY)||'[]');return new Set(Array.isArray(a)?a:[]);}catch(_){return new Set();}}
  function saveContentBoxState(set){localStorage.setItem(CONTENT_BOX_COLLAPSE_KEY,JSON.stringify([...set]));}
  function collapseHeadingText(h){const clone=h.cloneNode(true);clone.querySelectorAll('.count,.box-collapse-chevron').forEach(x=>x.remove());return clone.textContent.replace(/\s+/g,' ').trim();}
  function contentBoxKey(card,h,index){const section=card.closest('.section')?.id||'global',title=collapseHeadingText(h).toLocaleLowerCase('de').replace(/[^a-z0-9äöüß]+/g,'-').replace(/^-|-$/g,'')||`box-${index}`;return `${section}:${title}`;}
  function setupCollapsibleContentBoxes(){
    const collapsed=contentBoxState(),seen=new Map();
    const cards=[...document.querySelectorAll('.combat-block,.combat-card,.comp-card,.sf-group')];
    cards.forEach((card,index)=>{
      let heading=card.querySelector(':scope > h4'),root=heading;
      if(!heading&&card.classList.contains('sf-group')){root=card.querySelector(':scope > .sf-group-head');heading=root?.querySelector(':scope > h4')||null;}
      if(!heading||!root||heading.classList.contains('box-collapse-heading'))return;
      const base=contentBoxKey(card,heading,index),n=(seen.get(base)||0)+1;seen.set(base,n);const key=n===1?base:`${base}:${n}`;
      root.classList.add('box-collapse-root');heading.classList.add('box-collapse-heading');heading.setAttribute('role','button');heading.setAttribute('tabindex','0');heading.setAttribute('title','Ein-/ausklappen');
      const chev=document.createElement('span');chev.className='box-collapse-chevron';heading.prepend(chev);
      const apply=()=>{const isCollapsed=collapsed.has(key);card.classList.toggle('box-collapsed',isCollapsed);heading.setAttribute('aria-expanded',isCollapsed?'false':'true');chev.textContent=isCollapsed?'▸':'▾';};
      const toggle=()=>{if(collapsed.has(key))collapsed.delete(key);else collapsed.add(key);saveContentBoxState(collapsed);apply();};
      heading.addEventListener('click',toggle);heading.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle();}});apply();
    });
  }
'''
marker = '  applyTabOrder();initTabSorting();'
if s.count(marker) != 1:
    raise RuntimeError(f'Expected init marker once, found {s.count(marker)}')
s = s.replace(marker, js + '\n  setupCollapsibleContentBoxes();\n' + marker, 1)

for heading in ['Nahkampfwaffen','Fernkampfwaffen','Waffenloser Kampf','Schilde &amp; Parierwaffen','Ausweichen','Wunden &amp; Energien','Rüstung nach Trefferzonen']:
    if heading not in s:
        raise RuntimeError(f'Missing expected combat block: {heading}')

PATH.write_text(s, encoding='utf-8')
print('Applied HeldenMobil v16.1 collapsible content cards')
