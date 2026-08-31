(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.HeldenMobilCombat=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  function combatEbe(talent,be,combatMeta={}){const m=combatMeta[talent];return m?Math.max(0,Number(be||0)-Number(m.offset||0)):Number(be||0);}
  function adjustCombatForBE(at,pa,ebe){const e=Number(ebe||0);return {at:Number(at)-Math.floor(e/2),pa:Number(pa)-Math.ceil(e/2)};}
  function finalDamage(tp,tpkk,kk){if(!tp)return null;const out=[...tp];if(tpkk){const [thr,step]=tpkk,delta=Number(kk||0)-Number(thr||0),s=Math.max(1,Number(step||1)),bonus=delta>=0?Math.floor(delta/s):-Math.ceil(Math.abs(delta)/s);out[2]=Number(out[2]||0)+bonus;}return out;}
  function clamp(n,min,max){return Math.max(min,Math.min(max,n));}
  function zoneFromD20(r){r=clamp(Math.round(Number(r)||1),1,20);if(r>=19)return {label:'Kopf',key:'kopf'};if(r>=15)return {label:'Brust',key:'brust'};if(r>=9)return r%2?{label:'Schildarm (links)',key:'linkerarm'}:{label:'Schwertarm (rechts)',key:'rechterarm'};if(r>=7)return {label:'Bauch',key:'bauch'};return r%2?{label:'linkes Bein',key:'linkesbein'}:{label:'rechtes Bein',key:'rechtesbein'};}
  return {combatEbe,adjustCombatForBE,finalDamage,zoneFromD20};
});
