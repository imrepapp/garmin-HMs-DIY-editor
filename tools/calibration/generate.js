const fs=require('fs');const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1500,height:1000}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+require('path').resolve(__dirname,'../../index.html')+'');await p.waitForTimeout(1000);
const out=await p.evaluate(()=>{
  const dev='Edge 830', res={};
  const start=()=>{ S.device=dev; S.w=DEV[dev][0]; S.h=DEV[dev][1]; S.round=false; S.custom=false; S.designer=null; S.els=[]; S.samples={}; sel=[];
    S.els.push(mkG('RF',{color:'FFFFFF',x2:String(S.w),y2:String(S.h),daynight:'false'},{lock:true})); };
  const T=(text,font,x,y,al)=>S.els.push(mkText({text,font,x:String(x),y:String(y),halignment:al,daynight:'false'}));
  const fin=name=>{ const r=encodeLayout(); res[name]={json:toProject(),str:r.str,warn:r.warn,n:r.n}; };
  const lh=f=>METRICS.fonts[METRICS.dev[dev][MNAMES.indexOf(f)]][0];
  // 1: the nine standard fonts, stacked by their real line height; left-aligned at x=4, right-aligned at x=242
  start(); let y=0;
  for(const f of ['XTINY','TINY','SMALL','MEDIUM','LARGE']){ T('Hxgpj08W%/',f,4,y,'2'); T('Hg0',f,242,y,'0'); y+=lh(f); }
  T('0123456789','NR_MILD',4,y,'2'); T('%',  'NR_MILD',242,y,'0'); y+=lh('NR_MILD');
  T('08.5:-+/A','NR_MEDIUM',4,y,'2'); T('W','NR_MEDIUM',242,y,'0'); y+=lh('NR_MEDIUM');
  T('08.5:-','NR_HOT',4,y,'2'); T('E','NR_HOT',242,y,'0'); y+=lh('NR_HOT');
  T('08:%','NR_THAI_HOT',4,y,'2'); T('_','NR_THAI_HOT',242,y,'0');
  fin('1-fonts');
  // 2: the S_ fonts, whose sizes are unknown: generous spacing, short texts
  start();
  [['S_XTINY',0],['S_TINY',22],['S_SMALL',48],['S_MEDIUM',78],['S_LARGE',112]].forEach(([f,yy])=>T('Hxgp08',f,4,yy,'2'));
  T('08','S_NR_THAI_HOT',242,40,'0');
  T('0859','S_NR_MILD',4,165,'2'); T('0859','S_NR_MEDIUM',4,205,'2'); T('0859','S_NR_HOT',4,255,'2');
  fin('2-fonts-s');
  // 3: graphics with known coordinates
  // some settings apps refuse a string with a backslash, so the last elements are nudged until none is left
  for(let dx=0;dx<40;dx++){ start(); const G=(t,o)=>{ const e=mkG(t,Object.assign({daynight:'false'},o)); S.els.push(e); return e; }, rng=e=>{ const d=attachDyn(e); d.auto=true; d.dc[0].val=1000; d.dc[1].val=0; };
  G('RC',{x:'10',y:'10',x2:'110',y2:'60',stroke:'3'}); G('RF',{color:'AAAAAA',x:'130',y:'10',x2:'230',y2:'60'});
  G('CR',{x:'60',y:'105',radius:'30',stroke:'3'}); G('CF',{color:'AAAAAA',x:'180',y:'105',radius:'30'});
  G('AC',{x:'45',y:'185',radius:'30',x2:'200',y2:'340',stroke:'5'}); G('AC',{x:'123',y:'185',radius:'30',x2:'0',y2:'90',stroke:'1'});
  rng(G('AF',{color:'00AA00',valuetype:'BV',x:'200',y:'185',radius:'30',x2:'200',y2:'340',stroke:'5'}));
  G('LN',{x:'10',y:'230',x2:'110',y2:'250',stroke:'3'}); G('LN',{x:'130',y:'240',x2:'230',y2:'240',stroke:'5'});
  rng(G('RH',{color:'0000FF',valuetype:'BV',x:'10',y:'270',x2:'110',y2:'285'}));
  rng(G('RV',{color:['FF0000','FF5500','AA00FF','00AAAA','555555'][dx%5],valuetype:'BV',x:'130',y:'262',x2:'150',y2:String(317-(dx%7))}));
  G('GB',{color:'AA0000',valuetype:'HR',x:'160',y:'262',x2:String(240-(dx>>3)),y2:'317',radius:'0'});
  S.els.push(mkVal('BV',{font:'SMALL',x:String(60+dx),y:'292',halignment:'1',precision:'0',daynight:'false'}));
  if(!encodeLayout().str.includes('\\')||dx===39){ fin('3-graphics'); res['3-graphics'].dx=dx; break; } }
  return res; });
let txt='HMs DIY calibration layouts for Edge 830\n\nPaste one string at a time into "Default layout string" in the data field settings,\nshow the field as the only field of a data screen (1 Field layout), take a screenshot, then go on to the next.\n';
for(const k in out){ fs.writeFileSync(__dirname+'/edge830-'+k+'.json',out[k].json); txt+='\n=== '+k+' ('+out[k].n+' elements, '+out[k].str.length+' characters) ===\n'+out[k].str+'\n'; console.log(k,out[k].n,out[k].str.length,JSON.stringify(out[k].warn),'backslash:',out[k].str.includes('\\'),'dx',out[k].dx); }
fs.writeFileSync(__dirname+'/edge830-strings.txt',txt);
for(const k in out){ await p.evaluate(j=>{loadText(j);sel=[];refresh()},out[k].json); await p.waitForTimeout(250); await p.locator('#cv').screenshot({path:__dirname+'/edge830-'+k+'.preview.png'}); }
console.log(errs.join('|')||'no errors');await b.close()})();
