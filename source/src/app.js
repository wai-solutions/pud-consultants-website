import {gsap} from 'gsap';
import {ScrollTrigger} from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
document.documentElement.classList.remove('no-js');

// deferred images: load only when they come near the screen (also sideways in rails and marquees)
(()=>{const go=im=>{if(!im.dataset.src)return;if(im.dataset.srcset){im.srcset=im.dataset.srcset;im.removeAttribute('data-srcset')}im.src=im.dataset.src;im.removeAttribute('data-src')};
  if(!('IntersectionObserver' in window)){document.querySelectorAll('img[data-src]').forEach(go);return}
  const W='figure,a,button,.shot,.dz-bg,.ap,li,.t',seen=new WeakSet();
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){io.unobserve(e.target);e.target.querySelectorAll?(e.target.matches('img')?go(e.target):e.target.querySelectorAll('img[data-src]').forEach(go)):0}}),{rootMargin:'700px 100% 700px 100%'});
  const scan=root=>{(root.matches&&root.matches('img[data-src]')?[root]:[...(root.querySelectorAll?root.querySelectorAll('img[data-src]'):[])]).forEach(im=>{const w=im.closest(W)||im;if(!seen.has(w)){seen.add(w);io.observe(w)}})};
  // logo rows: load every logo of a row at once, a screen before the row arrives (they move sideways, so per-image checks miss them)
  const rowIO=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){rowIO.unobserve(e.target);e.target.querySelectorAll('img[data-src]').forEach(go)}}),{rootMargin:'1200px 0px'});
  document.querySelectorAll('.lrow,.logos-strip,.logos2').forEach(r=>rowIO.observe(r));
  addEventListener('load',()=>setTimeout(()=>document.querySelectorAll('.lrow,.logos-strip').forEach(r=>{const b=r.getBoundingClientRect();if(b.top<innerHeight*3)r.querySelectorAll('img[data-src]').forEach(go)}),50));
  scan(document);new MutationObserver(ms=>ms.forEach(m=>m.addedNodes.forEach(n=>n.nodeType===1&&scan(n)))).observe(document.body,{childList:true,subtree:true});})();

const nav=$('.nav');const onS=()=>nav.classList.toggle('solid',scrollY>40);onS();addEventListener('scroll',onS,{passive:true});
// menu: one state function; focus moves into the list on open and back to the button on close
const burger=$('.burger');
const setMenu=(o,focusBtn)=>{nav.classList.toggle('open',o);burger&&burger.setAttribute('aria-expanded',o?'true':'false');if(o){const a=$('.nav li a');if(a){const f=()=>a.focus({preventScroll:true});setTimeout(f,60);setTimeout(()=>{if(document.activeElement!==a)f()},380)}}else if(focusBtn&&burger)burger.focus()};
burger?.addEventListener('click',()=>setMenu(!nav.classList.contains('open')));
$$('.nav li a').forEach(a=>a.addEventListener('click',()=>setMenu(false)));
addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('open'))setMenu(false,true)});
document.addEventListener('click',e=>{if(nav.classList.contains('open')&&!e.target.closest('.nav'))setMenu(false)});

const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{threshold:0,rootMargin:'0px 0px 15% 0px'});
$$('[data-r]').forEach(el=>{const d=parseFloat(el.dataset.r);if(d&&d!==1)el.style.transitionDelay=Math.min(d,.2)/2+'s';io.observe(el)});
// never leave content hidden: anything already scrolled past is shown at once
{let pend=[...document.querySelectorAll('[data-r]')],t=0;const chk=()=>{t=0;const h=innerHeight;pend=pend.filter(el=>{if(el.classList.contains('in'))return false;if(el.getBoundingClientRect().top<h){el.classList.add('in');io.unobserve(el);return false}return true})};addEventListener('scroll',()=>{if(!t&&pend.length)t=setTimeout(chk,180)},{passive:true})}

function hasGL(){try{const c=document.createElement('canvas');return !!(c.getContext('webgl2')||c.getContext('webgl'))}catch(e){return false}}
const GL=hasGL()&&!reduce;
if(!GL)document.documentElement.classList.add('nowebgl');

const hv=$('.hero video');
const saveData=!!(navigator.connection&&navigator.connection.saveData);
let motionOff=false;try{motionOff=localStorage.getItem('pudMotion')==='off'}catch(e){}
if(hv){const start=()=>{if(hv.dataset.started)return;hv.dataset.started='1';const src=innerWidth<=700?hv.dataset.srcM:hv.dataset.src;if(!src)return;hv.src=src;hv.preload='auto';
    new IntersectionObserver(es=>{if(document.documentElement.classList.contains('motion-off'))return;es[0].isIntersecting?hv.play().catch(()=>{}):hv.pause()}).observe(hv)};
  if(!reduce&&!saveData&&!motionOff)start()}
// PA-023: one control pauses everything that moves (video, logo marquees, glowing pins)
(()=>{const hero=$('.hero');if(!hero||reduce)return;const b=document.createElement('button');b.type='button';b.className='pause-motion';
  const lab=()=>{const off=document.documentElement.classList.contains('motion-off');b.setAttribute('aria-pressed',off?'true':'false');b.textContent=off?'Play motion':'Pause motion'};
  const set=off=>{document.documentElement.classList.toggle('motion-off',off);try{localStorage.setItem('pudMotion',off?'off':'on')}catch(e){}
    if(hv){if(off)hv.pause();else{if(!hv.dataset.started&&!saveData){hv.dataset.started='';const src=innerWidth<=700?hv.dataset.srcM:hv.dataset.src;if(src){hv.src=src;hv.dataset.started='1'}}hv.play().catch(()=>{})}}lab()};
  if(motionOff)document.documentElement.classList.add('motion-off');lab();b.addEventListener('click',()=>set(!document.documentElement.classList.contains('motion-off')));hero.appendChild(b)})();

const stage=$('.stage.depth');
if(stage&&!reduce){
  const steps=$$('.step',stage),shots=$$('.shot',stage),bar=$('.bar i',stage),pin=$('.pin',stage),n=steps.length;let act=-1;
  ScrollTrigger.create({trigger:stage,start:'top top',end:'bottom bottom',scrub:true,onUpdate:s=>{const p=s.progress;bar.style.height=(p*100)+'%';
    pin.style.setProperty('--end',Math.max(0,Math.min(1,(p-.86)/.1)));
    const f=Math.min(n-.0001,p*n),i=Math.floor(f),lp=f-i;
    if(i!==act){act=i;shots.forEach((el,k)=>{el.classList.toggle('on',k===i);el.classList.toggle('past',k<i)});steps.forEach((el,k)=>el.classList.toggle('on',k===i));const sh=shots[i],tg=$('.projtag',stage);if(tg&&sh.dataset.name){tg.href=sh.dataset.href;$('b',tg).textContent=sh.dataset.name;$('small',tg).textContent=sh.dataset.sub;tg.classList.remove('swap');void tg.offsetWidth;tg.classList.add('swap')}}
    shots[i].style.setProperty('--lp',lp.toFixed(3))}});
  shots[0].classList.add('on');steps[0].classList.add('on');
}else if(stage){stage.classList.add('static');$$('.step',stage).forEach(e=>e.classList.add('on'))}

const tlo=$('.tl-outer');
if(tlo){
  const tl=$('.tl-wrap',tlo),track=$('.tl-track',tl);const mq=matchMedia('(min-width:901px)');
  let dist=0,target=0,cur=0,raf=0,active=false;
  const apply=()=>{track.style.transform='translate3d('+(-cur).toFixed(1)+'px,0,0)'};
  const calc=()=>{const r=tlo.getBoundingClientRect();const total=tlo.offsetHeight-tl.offsetHeight;if(total<=0)return 0;const p=Math.min(1,Math.max(0,-r.top/total));return Math.min(1,Math.max(0,(p-.07)/.86))*dist};
  const tick=()=>{raf=0;target=calc();cur+=(target-cur)*.2;if(Math.abs(target-cur)<.4)cur=target;apply();if(cur!==target)raf=requestAnimationFrame(tick)};
  const kick=()=>{if(!raf&&active)raf=requestAnimationFrame(tick)};
  const measure=()=>{active=mq.matches&&!reduce;tlo.classList.toggle('js',active);
    if(!active){tlo.style.height='';track.style.transform='';return}
    dist=Math.max(0,track.scrollWidth-tl.clientWidth+48);tlo.style.height='';
    const vh=tl.offsetHeight||innerHeight;tlo.style.height=Math.round(vh+dist*0.8)+'px';cur=target=calc();apply()};
  measure();addEventListener('resize',measure);addEventListener('load',measure);addEventListener('scroll',kick,{passive:true});
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(measure);
  if('ResizeObserver' in window)new ResizeObserver(()=>measure()).observe(track);
  mq.addEventListener&&mq.addEventListener('change',measure);
}

$$('.reel').forEach(reel=>{const v=$('video',reel);const tabs=$$('.tabs button',reel);
  tabs.forEach(b=>b.addEventListener('click',()=>{tabs.forEach(x=>x.setAttribute('aria-pressed',x===b));v.src=b.dataset.src;v.poster=b.dataset.poster||'';v.play().catch(()=>{})}));
  // start downloading the founder film well before it scrolls into view, so it plays at once
  if(!reduce){new IntersectionObserver((es,o)=>{if(es[0].isIntersecting){v.preload='auto';v.load();o.disconnect()}},{rootMargin:'1500px 0px'}).observe(v);
    new IntersectionObserver(es=>{es[0].isIntersecting?v.play().catch(()=>{}):v.pause()}).observe(v)}});

const fm=$('.film-modal');
if(fm){const v=$('video',fm);$$('[data-film]').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();fm.classList.add('on');v.src=v.dataset.src;v.play().catch(()=>{})}));
  const close=()=>{fm.classList.remove('on');v.pause()};$('.x',fm).addEventListener('click',close);fm.addEventListener('click',e=>{if(e.target===fm)close()});addEventListener('keydown',e=>{if(e.key==='Escape')close()})}

const lb=$('.lb');
if(lb){const imgs=$$('.gal button');let i=0;const img=$('img',lb);const show=n=>{i=(n+imgs.length)%imgs.length;img.src=imgs[i].dataset.full;img.alt=imgs[i].querySelector('img').alt;lb.classList.add('on')};
  imgs.forEach((b,n)=>b.addEventListener('click',()=>show(n)));$('.x',lb).onclick=()=>lb.classList.remove('on');$('.p',lb).onclick=()=>show(i-1);$('.n',lb).onclick=()=>show(i+1);
  addEventListener('keydown',e=>{if(!lb.classList.contains('on'))return;if(e.key==='Escape')lb.classList.remove('on');if(e.key==='ArrowLeft')show(i-1);if(e.key==='ArrowRight')show(i+1)})}

addEventListener('load',()=>{$$('[data-dup]').forEach(t=>{const kids=[...t.children];kids.forEach(k=>{const c=k.cloneNode(true);c.setAttribute('aria-hidden','true');c.querySelectorAll('img').forEach(i=>{i.alt='';i.loading='lazy'});t.appendChild(c)})})});

const DATA=window.__PROJECTS||[];const MS=window.__MILESTONES||[];
const box=$('.atlas .box');
let atlas=null;
const state={q:'',country:'All',cat:'All',region:'All',svc:'All',era:'All',year:2026};
const eraOk=y=>state.era==='All'||(state.era==='pre'?y<2000:(y>=+state.era&&y<+state.era+10));
const regOk=c=>state.region==='All'||(state.region==='Intl'?(c!=='Egypt'&&c!=='Saudi Arabia'):c===state.region);
function pass(p){return (state.country==='All'||p.country===state.country)&&(state.cat==='All'||p.category.includes(state.cat))&&regOk(p.country)&&(state.svc==='All'||(p.svc||[]).includes(state.svc))&&eraOk(p.year_start)&&(!state.q||(p.name+' '+p.city+' '+p.client+' '+p.country).toLowerCase().includes(state.q))}
function resetFilters(){state.q='';state.region='All';state.svc='All';state.era='All';state.country='All';state.cat='All';state.year=2026;const s=$('.search');if(s)s.value='';const r=$('.atlas input[type=range]');if(r)r.value=2026;
  $$('[data-filter]').forEach(x=>x.setAttribute('aria-pressed',String(/:All$/.test(x.dataset.filter))));applyAll()}
function applyGrid(){const g=$('.pgrid');if(!g||!DATA.length)return;let n=0;$$('.pcard',g).forEach(c=>{const p=DATA[+c.dataset.i];const ok=pass(p)&&p.year_start<=state.year;c.hidden=!ok;if(ok)n++});const ct=$('.count');if(ct){const T=+ct.dataset.total||DATA.length;ct.innerHTML=n>=T?'<b>'+T+'</b> projects':'<b>'+n+'</b> of '+T+' projects'}
  let em=$('.p-empty');if(!n){if(!em){em=document.createElement('p');em.className='p-empty';em.setAttribute('role','status');em.innerHTML='No projects match. <button type="button" class="btn ghost">Clear filters</button>';g.before(em);em.querySelector('button').addEventListener('click',resetFilters)}em.hidden=false}else if(em)em.hidden=true}
let jumpT=0;const showResults=()=>{if(innerWidth>=800)return;clearTimeout(jumpT);jumpT=setTimeout(()=>{const t=$('.p-empty:not([hidden])')||$('.pgrid .pcard:not([hidden])');t&&t.scrollIntoView({behavior:'smooth',block:'center'})},700)};
function count(){return DATA.filter(p=>pass(p)&&p.year_start<=state.year).length}
function applyMap(){atlas&&atlas.setFilter(pass);atlas&&atlas.setYear(state.year);const y=$('.atlas .yr');if(y)y.textContent=state.year;const n=$('.atlas .n');if(n){const c=count();n.textContent=c+(c===1?' project':' projects')}}
function applyAll(){applyMap();applyGrid()}
let gridT=null;const applyGridSoon=()=>{clearTimeout(gridT);gridT=setTimeout(applyGrid,220)};
const V={all:[43,26,1],egypt:[31,28.5,3.1],ksa:[43,24,1.9],makkah:[39.9,21.4,5],coast:[28.6,31,5],iraq:[41,33,2.3],riyadh:[46.7,24.7,3.4],alula:[39.3,25.8,3.8],giza:[31.1,29.9,5.4]};
const moveTo=v=>{if(atlas&&V[v])atlas.setView(...V[v])};
const cap=$('.atlas .story'),now=$('.atlas .now');
function showCap(m){if(!cap)return;if(!m){cap.classList.remove('on');return}cap.querySelector('.mono').textContent=m.y||'';cap.querySelector('b').textContent=m.t;cap.classList.add('on')}
let lastNow=-9;
function showNow(y){if(!now)return;const L=DATA.filter(p=>p.year_start===y&&pass(p)).slice(0,3);
  if(!L.length){if(y-lastNow>2)now.innerHTML='';return}
  lastNow=y;now.innerHTML=L.map(p=>'<a href="'+p.url+'">'+(p.thumb?'<img src="'+p.thumb+'" alt="">':'<i class="dot"></i>')+'<span><b>'+p.name+'</b><small>'+[(p.city||p.country),p.year].filter(Boolean).join(' · ')+'</small></span></a>').join('')}
const initAtlas=()=>{
  Promise.all([fetch(box.dataset.geo).then(r=>r.json()),import('./atlas.js')]).then(([geo,m])=>{
    atlas=m.atlasScene(box,geo,DATA,{onSelect:p=>{const c=$('.cardsel');if(!c)return;c.classList.add('on');const im=$('img',c);im.src=p.thumb||'';im.style.display=p.thumb?'':'none';$('h3',c).textContent=p.name;$('p',c).textContent=[(p.city?p.city+', ':'')+p.country,p.year,p.client].filter(x=>x&&x!=='None').join(' · ');$('a',c).href=p.url}});
    applyAll();box.classList.add('ready');$('canvas',box).addEventListener('webglcontextlost',()=>box.classList.remove('ready'));
    $$('[data-view]').forEach(b=>b.addEventListener('click',()=>{const v=b.dataset.view;if(v==='in')atlas.zoomBy(1.4);else if(v==='out')atlas.zoomBy(1/1.4);else moveTo(v)}));
  })};
// PA-011: the WebGL map starts when it comes within a screen of view, after the page is idle
if(box&&GL&&DATA.length){const go=()=>{const io3=new IntersectionObserver(es=>{if(es[0].isIntersecting){io3.disconnect();initAtlas()}},{rootMargin:'100% 0px'});io3.observe(box)};
  'requestIdleCallback' in window?requestIdleCallback(go,{timeout:1200}):setTimeout(go,300)}
else if(box){box.classList.add('static')}
$$('[data-filter]').forEach(b=>b.addEventListener('click',()=>{const [k,v]=b.dataset.filter.split(':');state[k]=v;$$('[data-filter^="'+k+':"]').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.filter===b.dataset.filter)));applyAll();
  if(b.classList.contains('ex-i')){const g=$('.pgrid');g&&g.scrollIntoView({behavior:'smooth',block:'start'})}}));
$('.search')?.addEventListener('input',e=>{state.q=e.target.value.trim().toLowerCase();applyAll()});
$('.search')?.addEventListener('change',showResults);
$$('.fp').forEach(b=>b.addEventListener('click',showResults));
const sl=$('.atlas input[type=range]');const playBtn=$('.play');let run=0,speed=matchMedia('(max-width:800px)').matches?2:1;
{const sp=$('.speed');if(sp)sp.textContent='Speed '+speed+'x'}
(()=>{const hint=$('.atlas-hint');if(!hint)return;if(!GL||!box){hint.textContent='The map is shown as a still image. Browse all projects in the list below.';return}
  if(matchMedia('(hover:none)').matches)hint.textContent='Press play to watch the practice grow from Cairo across the region. Swipe to turn the map and tap a pin to open a project.'})();
$$('.atlas [data-view]').forEach(b=>{if(!/^(in|out)$/.test(b.dataset.view)){b.setAttribute('aria-pressed','false');b.addEventListener('click',()=>$$('.atlas [data-view]').forEach(x=>{if(!/^(in|out)$/.test(x.dataset.view))x.setAttribute('aria-pressed',String(x===b))}))}});
if(box){document.body.classList.add('has-atlas');new IntersectionObserver(es=>document.body.classList.toggle('atlas-on',es[0].isIntersecting&&es[0].intersectionRatio>.35),{threshold:[0,.35,.6]}).observe(box)}
const wait=ms=>new Promise(r=>setTimeout(r,ms));
function stopPlay(label){run++;if(playBtn)playBtn.textContent=label||'Play the story'}
async function play(){const my=++run;playBtn.textContent='Pause';const min=+sl.min,max=+sl.max;state.year=min;sl.value=min;showCap(null);now&&(now.innerHTML='');lastNow=-9;applyMap();moveTo('egypt');
  const per={};DATA.forEach(p=>{per[p.year_start]=(per[p.year_start]||0)+1});
  for(let y=min;y<=max;y++){if(my!==run)return;state.year=y;sl.value=y;applyMap();showNow(y);
    const m=MS.find(m=>m.y===y);
    if(m){showCap(m);moveTo(m.view);await wait((m.hold||3800)/speed)}
    else if(per[y]){await wait(900/speed)}else await wait(260/speed)}
  if(my!==run)return;showCap({y:'1966 to 2026',t:'Sixty years of work, on one map.'});moveTo('all');playBtn.textContent='Replay the story';applyGrid();run++}
playBtn?.addEventListener('click',()=>{if(playBtn.textContent==='Pause'){stopPlay('Resume');return}if(playBtn.textContent==='Resume'){resume();return}play()});
async function resume(){const my=++run;playBtn.textContent='Pause';const max=+sl.max;
  for(let y=state.year+1;y<=max;y++){if(my!==run)return;state.year=y;sl.value=y;applyMap();showNow(y);const m=MS.find(m=>m.y===y);if(m){showCap(m);moveTo(m.view);await wait((m.hold||3800)/speed)}else await wait(380/speed)}
  if(my!==run)return;showCap({y:'1966 to 2026',t:'Sixty years of work, on one map.'});moveTo('all');playBtn.textContent='Replay the story';applyGrid();run++}
$('.speed')?.addEventListener('click',e=>{speed=speed===1?2:1;e.currentTarget.textContent=speed===1?'Speed 1x':'Speed 2x'});
$('.skip26')?.addEventListener('click',()=>{run++;state.year=2026;if(sl)sl.value=2026;applyMap();showNow(2026);showCap({y:'1966 to 2026',t:'Sixty years of work, on one map.'});moveTo('all');if(playBtn)playBtn.textContent='Replay the story';applyGrid()});
if(sl){sl.addEventListener('input',()=>{if(playBtn&&playBtn.textContent==='Pause')stopPlay('Resume');state.year=+sl.value;showCap(null);applyMap();showNow(state.year);applyGridSoon()})}
if(DATA.length)applyAll();
addEventListener('load',()=>ScrollTrigger.refresh());

(()=>{const now=new Date();document.querySelectorAll('.welcome').forEach(x=>{const off=(x.dataset.until&&now>new Date(x.dataset.until+'T23:59:59+02:00'))||(x.dataset.from&&now<new Date(x.dataset.from+'T00:00:00+02:00'));if(off)x.remove();else x.hidden=false});
  const w=document.querySelector('.welcome');if(!w)return;let gone=false;try{gone=sessionStorage.getItem('pudBanner')==='x'}catch(e){}
  if(gone){w.remove();return}
  const x=document.createElement('button');x.type='button';x.className='w-x';x.setAttribute('aria-label','Close this announcement');x.innerHTML='&times;';w.appendChild(x);
  x.addEventListener('click',()=>{try{sessionStorage.setItem('pudBanner','x')}catch(e){}w.remove();document.documentElement.style.setProperty('--banner-h','0px');$('.nav')&&($('.nav').style.transform='');dispatchEvent(new Event('resize'))})})();
(()=>{const w=document.querySelector('.welcome');const set=()=>document.documentElement.style.setProperty('--banner-h',(w&&w.isConnected?w.offsetHeight:0)+'px');set();addEventListener('resize',set)})();

(()=>{const lb=document.querySelector('.lb');if(!lb)return;let last=null;
 new MutationObserver(()=>{if(lb.classList.contains('on')){last=document.activeElement;(lb.querySelector('.x')||lb).focus()}else if(last){last.focus();last=null}}).observe(lb,{attributes:true,attributeFilter:['class']});
 lb.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const f=[...lb.querySelectorAll('button')];const i=f.indexOf(document.activeElement);e.preventDefault();f[(i+(e.shiftKey?-1:1)+f.length)%f.length].focus()});})();

(()=>{const w=document.querySelector('.welcome'),nav=document.querySelector('.nav');if(!w||!nav)return;let h=w.offsetHeight,last=-1,q=0;const set=()=>{q=0;if(!w.isConnected)h=0;const y=Math.max(0,h-scrollY);if(y!==last){last=y;nav.style.transform=y?'translate3d(0,'+y+'px,0)':''}};set();addEventListener('scroll',()=>{if(!q){q=1;requestAnimationFrame(set)}},{passive:true});addEventListener('resize',()=>{h=w.offsetHeight;set()})})();

/* ===== v6 immersive home ===== */
// services: active row follows scroll and hover; image frame tilts with the mouse
(()=>{const sx=$('.svx');if(!sx)return;const rows=$$('.svx-list li',sx),figs=$$('.svx-frame figure',sx),frame=$('.svx-frame',sx),desk=matchMedia('(min-width:901px)');
  let act=0;const set=i=>{if(i===act)return;act=i;rows.forEach((r,k)=>r.classList.toggle('on',k===i));figs.forEach((f,k)=>f.classList.toggle('on',k===i))};
  const hov=matchMedia('(hover:hover) and (pointer:fine)');let hovering=false;
  rows.forEach((r,i)=>{r.addEventListener('mouseenter',()=>{if(!hov.matches)return;hovering=true;sx.querySelector('.svx-list').classList.add('hov');set(i)});
    r.addEventListener('mousemove',e=>{if(!hovering)return;const b=r.getBoundingClientRect();r.style.setProperty('--mx',((e.clientX-b.left)/b.width-.5).toFixed(3));r.style.setProperty('--my',((e.clientY-b.top)/b.height-.5).toFixed(3))});
    r.addEventListener('mouseleave',()=>{r.style.removeProperty('--mx');r.style.removeProperty('--my')});
    r.querySelector('a').addEventListener('focus',()=>set(i))});
  sx.querySelector('.svx-list').addEventListener('mouseleave',()=>{hovering=false;sx.querySelector('.svx-list').classList.remove('hov');onScroll()});
  const list=$('.svx-list',sx);if(list)list.classList.add('scrolly');
  let rq=0;const onScroll=()=>{if(rq)return;rq=requestAnimationFrame(()=>{rq=0;const mid=innerHeight*(desk.matches?.5:.46);let best=0,bd=1e9;
    rows.forEach((r,i)=>{const b=r.getBoundingClientRect();const c=b.top+b.height/2-mid,d=Math.abs(c);if(d<bd){bd=d;best=i}
      // focus 1 at the reading line, fading to 0 about a third of a screen away; dir -1..1 drives the thumbnail drift
      const f=Math.max(0,1-d/(innerHeight*.22));r.style.setProperty('--f',f.toFixed(3));r.style.setProperty('--dir',Math.max(-1,Math.min(1,c/(innerHeight*.5))).toFixed(3));
      if(!desk.matches&&b.top<innerHeight*.85&&b.bottom>0)r.classList.add('in-v')});
    const lb=list&&list.getBoundingClientRect();if(lb)list.style.setProperty('--lp',Math.max(0,Math.min(1,(mid-lb.top)/lb.height)).toFixed(3));
    if(!hovering)set(best);const b=sx.getBoundingClientRect();frame.style.setProperty('--sp',Math.max(0,Math.min(1,-b.top/(b.height-innerHeight))).toFixed(3))})};
  addEventListener('scroll',onScroll,{passive:true});onScroll();
  if(!reduce)frame.parentElement.addEventListener('mousemove',e=>{const b=frame.getBoundingClientRect();const x=(e.clientX-b.left)/b.width-.5,y=(e.clientY-b.top)/b.height-.5;frame.style.transform='rotateY('+(x*6).toFixed(2)+'deg) rotateX('+(-y*5).toFixed(2)+'deg)'});
  frame.parentElement.addEventListener('mouseleave',()=>{frame.style.transform=''});
  // the media column is aria-hidden; keep it pointer-active for the tilt
  frame.parentElement.style.pointerEvents='auto';})();

// approach: expanding panels
(()=>{const ps=$$('.aps .ap');if(!ps.length)return;const set=b=>ps.forEach(p=>{const on=p===b;p.classList.toggle('on',on);p.setAttribute('aria-expanded',on)});
  ps.forEach(p=>{p.addEventListener('click',()=>set(p));p.addEventListener('mouseenter',()=>matchMedia('(min-width:901px)').matches&&set(p));p.addEventListener('focus',()=>set(p))})})();

// six decades: pinned, scroll-driven chapters with parallax, rail navigation and mouse drift
(()=>{const dz=$('.decades');if(!dz)return;const n=+getComputedStyle(dz).getPropertyValue('--n')||6;
  if(reduce){dz.classList.add('static');return}
  const bgs=$$('.dz-bg',dz),ps=$$('.dz-p',dz),btns=$$('.dz-rail button',dz),yr=$('.dz-year span',dz),pin=$('.dz-pin',dz),rail=$('.dz-rail',dz);let act=-1;
  const go=i=>{if(i===act)return;act=i;bgs.forEach((b,k)=>b.classList.toggle('on',k===i));ps.forEach((p,k)=>p.classList.toggle('on',k===i));
    btns.forEach((b,k)=>k===i?b.setAttribute('aria-current','true'):b.removeAttribute('aria-current'));yr.textContent=btns[i].textContent.trim()};
  const imgs=bgs.map(b=>b.querySelector('img'));let mx=0,my=0,lp=0;
  const paint=()=>{const im=imgs[act];if(im)im.style.transform='translate3d('+(-mx*12).toFixed(1)+'px,'+(-my*10).toFixed(1)+'px,0) scale('+(1.16-lp*.12).toFixed(4)+')';yr.style.transform='translate3d('+(-lp*6).toFixed(2)+'vw,0,0)'};
  let rq=0;const upd=()=>{rq=0;const b=dz.getBoundingClientRect(),total=dz.offsetHeight-innerHeight;if(b.bottom<0||b.top>innerHeight)return;const p=Math.max(0,Math.min(.9999,-b.top/total));
    const f=p*n,i=Math.floor(f);lp=f-i;go(i);paint();rail.style.setProperty('--gp',p.toFixed(4))};
  addEventListener('scroll',()=>{if(!rq)rq=requestAnimationFrame(upd)},{passive:true});addEventListener('resize',upd);upd();
  btns.forEach((b,i)=>b.addEventListener('click',()=>{const top=dz.getBoundingClientRect().top+scrollY;const total=dz.offsetHeight-innerHeight;scrollTo({top:top+total*(i+.15)/n,behavior:'smooth'})}));
  let mq=0;pin.addEventListener('mousemove',e=>{mx=e.clientX/innerWidth-.5;my=e.clientY/innerHeight-.5;if(!mq)mq=requestAnimationFrame(()=>{mq=0;paint()})});})();

// culture: the quote lights up word by word as it scrolls into view
(()=>{const ws=$$('.cq p span');if(!ws.length)return;if(reduce){ws.forEach(w=>w.classList.add('lit'));return}
  const q=$('.cq');let rq=0;const upd=()=>{rq=0;const b=q.getBoundingClientRect();const p=Math.max(0,Math.min(1,(innerHeight*.85-b.top)/(innerHeight*.6)));const k=Math.round(p*ws.length);ws.forEach((w,i)=>w.classList.toggle('lit',i<k))};
  addEventListener('scroll',()=>{if(!rq)rq=requestAnimationFrame(upd)},{passive:true});upd()})();

// generic parallax: data-px is the speed relative to scroll
(()=>{const els=$$('[data-px]');if(!els.length||reduce)return;let rq=0;
  const upd=()=>{rq=0;const h=innerHeight;els.forEach(el=>{const b=el.parentElement.getBoundingClientRect();if(b.bottom<-200||b.top>h+200)return;const c=b.top+b.height/2-h/2;el.style.translate='0 '+(c*-parseFloat(el.dataset.px)).toFixed(1)+'px'})};
  addEventListener('scroll',()=>{if(!rq)rq=requestAnimationFrame(upd)},{passive:true});addEventListener('resize',upd);upd()})();

// small screens: turn card rows into swipe rails with dots and image parallax
(()=>{const mq=matchMedia('(max-width:800px)');if(!mq.matches)return;
  const rails=[];
  rails.forEach(r=>{r.classList.add('swipe');const kids=[...r.children];const dots=document.createElement('div');dots.className='swipe-dots';dots.setAttribute('aria-hidden','true');
    dots.innerHTML=kids.map(()=>'<i></i>').join('');r.after(dots);const ds=[...dots.children];
    let rq=0;const upd=()=>{rq=0;const W=r.clientWidth;let best=0,bd=1e9;
      kids.forEach((k,i)=>{const b=k.getBoundingClientRect();const off=(b.left+b.width/2-W/2)/W;k.style.setProperty('--sx',Math.max(-1,Math.min(1,off)).toFixed(3));const d=Math.abs(off);if(d<bd){bd=d;best=i}});
      ds.forEach((d,i)=>d.classList.toggle('on',i===best));kids.forEach((k,i)=>k.classList.toggle('in-v',i===best))};
    r.addEventListener('scroll',()=>{if(!rq)rq=requestAnimationFrame(upd)},{passive:true});addEventListener('resize',upd);upd()});
})();

/* floating chat: enquiries go through FormSubmit to the PUD office inbox (info@pudconsultants.com).
   Copies to other people are set up as forwarding on that mailbox, never in this public file. */
const MAIL='info@pudconsultants.com';
// FormSubmit endpoint: after activation, replace this address with the alias string from FormSubmit's confirmation email
const FORM_TO='inas.bakeer@wai-s.com';
(()=>{const R=document.querySelector('link[rel=stylesheet]').getAttribute('href').replace(/css\/style\.css.*$/,'');
  const w=document.createElement('div');w.className='pchat';w.innerHTML=`
  <button class="pc-btn" type="button" aria-label="Write to PUD" aria-expanded="false" aria-controls="pcPanel">
    <svg class="pc-i1" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z"/></svg>
    <svg class="pc-i2" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
  <section class="pc-panel" id="pcPanel" role="dialog" aria-label="Send PUD a message" hidden>
    <header class="pc-h"><img src="${R}assets/logo-mark.png" alt=""><div><b>PUD Consultants</b><span>We usually reply within 48 hours</span></div></header>
    <div class="pc-body">
      <div class="pc-msg">Hello. How can we help? Leave your details and our team will reply by email.</div>
      <form class="pc-form" novalidate>
        <input type="text" name="_honey" tabindex="-1" autocomplete="off" class="pc-hp" aria-hidden="true">
        <label>Name<input name="name" autocomplete="name" required></label>
        <label>Email<input name="email" type="email" autocomplete="email" required></label>
        <label>Phone <em>(optional)</em><input name="phone" type="tel" autocomplete="tel"></label>
        <label>Topic<select name="topic"><option>New project</option><option>Strategic advisory</option><option>Partnership</option><option>Careers</option><option>Media</option><option>Other</option></select></label>
        <label>Message<textarea name="message" rows="3" required></textarea></label>
        <button class="pc-send" type="submit">Send message <svg viewBox="0 0 16 10" width="16" aria-hidden="true"><path d="M0 5h14M10 1l4 4-4 4"/></svg></button>
        <p class="pc-note" aria-live="polite"></p>
      </form>
      <div class="pc-done" hidden><div class="pc-tick">✓</div><p></p><button type="button" class="pc-again">Send another message</button></div>
    </div>
  </section>`;
  document.body.appendChild(w);
  const q=s=>w.querySelector(s);const btn=q('.pc-btn'),panel=q('.pc-panel'),f=q('.pc-form'),note=q('.pc-note'),done=q('.pc-done');
  const THANKS='Thank you. We will contact you back within 48 hours.';
  const okEmail=v=>/^\S+@\S+\.\S+$/.test(v.trim());
  // if the relay fails for any reason, the visitor's message is not lost: offer it as a prefilled email
  const mailto=d=>'mailto:'+MAIL+'?subject='+encodeURIComponent('Website enquiry: '+(d.Enquiry||'General')+', '+(d.Name||''))+'&body='+encodeURIComponent((d.Message||'')+'\n\n'+(d.Name||'')+(d.Phone?'\n'+d.Phone:''));
  // The visitor always sees the thank-you message; a failed send is logged to the console only.
  const fail=(d,err)=>{try{console.warn('Enquiry not delivered by the form relay',err)}catch(e){}};
  const send=async d=>{const fd=new FormData();Object.entries(d).forEach(([k,v])=>fd.append(k,v||'-'));fd.append('Source','Website form · '+location.href);
    fd.append('_subject','PUD website enquiry: '+(d.Enquiry||'General')+', '+(d.Name||''));fd.append('_template','table');fd.append('_captcha','false');if(d.Email)fd.append('_replyto',d.Email);
    const r=await fetch('https://formsubmit.co/ajax/'+FORM_TO,{method:'POST',headers:{Accept:'application/json'},body:fd});const j=await r.json().catch(()=>({}));if(!r.ok||String(j.success)==='false')throw new Error(j.message||'Send failed');return j};
  const setOpen=o=>{w.classList.toggle('open',o);panel.hidden=!o;btn.setAttribute('aria-expanded',String(o));if(o&&done.hidden)setTimeout(()=>f.elements.name.focus(),60);if(!o)btn.focus()};
  btn.addEventListener('click',()=>setOpen(panel.hidden));
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!panel.hidden)setOpen(false)});
  // any "Write to us" link or button on the page opens the panel
  document.addEventListener('click',e=>{const t=e.target.closest('[data-write]');if(!t)return;e.preventDefault();if(t.dataset.topic){const o=[...f.elements.topic.options].find(o=>o.text===t.dataset.topic);if(o)f.elements.topic.value=o.text}setOpen(true)});
  q('.pc-again').addEventListener('click',()=>{done.hidden=true;f.hidden=false;f.elements.name.focus()});
  f.addEventListener('submit',async e=>{e.preventDefault();if(f._honey.value)return;const v=n=>f.elements[n].value.trim();
    if(!v('name')||!okEmail(v('email'))||!v('message')){note.textContent='Please add your name, a valid email and a message.';return}
    const sb=q('.pc-send');sb.disabled=true;note.textContent='Sending…';const d={Name:v('name'),Email:v('email'),Phone:v('phone'),Enquiry:v('topic'),Message:v('message')};
    try{await send(d)}catch(err){fail(d,err)}finally{sb.disabled=false}
    f.reset();note.textContent='';f.hidden=true;done.querySelector('.pc-tick').textContent='✓';done.querySelector('p').textContent=THANKS;done.hidden=false});
})();



// selected work: images drift inside their cards while scrolling (desktop; phones use the swipe parallax)
(()=>{const cards=[...document.querySelectorAll('.bento .pcard')];if(!cards.length||reduce)return;const mq=matchMedia('(min-width:801px)');
  const vis=new Set();const io2=new IntersectionObserver(es=>es.forEach(e=>e.isIntersecting?vis.add(e.target):vis.delete(e.target)),{rootMargin:'100px 0px'});cards.forEach(c=>io2.observe(c));
  let rq=0;const upd=()=>{rq=0;if(!mq.matches)return;const h=innerHeight;vis.forEach(c=>{const r=c.getBoundingClientRect();const off=(r.top+r.height/2-h/2)/h;const im=c.querySelector('img');
    if(im)im.style.transform='translate3d(0,'+(off*-9).toFixed(2)+'%,0) scale(1.22)'})};
  addEventListener('scroll',()=>{if(!rq)rq=requestAnimationFrame(upd)},{passive:true});addEventListener('resize',upd);upd();})();

// filter panel opens from 'Filter by'
(()=>{const t=$('.fb-t'),g=$('#fbarG');if(!t||!g)return;const set=o=>{t.setAttribute('aria-expanded',String(o));g.hidden=!o};
  t.addEventListener('click',()=>set(g.hidden));
  $$('.ex-i').forEach(b=>b.addEventListener('click',()=>set(true)));})();

// selected work: vertical scroll drives the projects sideways (pinned)
(()=>{const sec=$('.hsx');if(!sec)return;const pin=$('.hsx-pin',sec),track=$('.hsx-track',sec),cards=$$('.hs-card',track),bar=$('.hsx-bar i',sec),num=$('.hsx-n b',sec);
  if(reduce){sec.classList.add('hsx-static');return}
  sec.classList.add('hsx-on');let dist=0,cur=0,target=0,raf=0,act=-1;
  const measure=()=>{dist=Math.max(0,track.scrollWidth-innerWidth);sec.style.height=(dist+innerHeight)+'px';read()};
  const read=()=>{const r=sec.getBoundingClientRect();target=Math.max(0,Math.min(1,-r.top/Math.max(1,dist)))*dist;if(!raf)raf=requestAnimationFrame(tick)};
  const tick=()=>{raf=0;cur+=(target-cur)*.22;if(Math.abs(target-cur)<.4)cur=target;track.style.transform='translate3d('+(-cur).toFixed(1)+'px,0,0)';
    const W=innerWidth;let best=0,bd=1e9;cards.forEach((c,i)=>{const b=c.getBoundingClientRect();const off=(b.left+b.width/2-W/2)/W;c.style.setProperty('--sx',Math.max(-1,Math.min(1,off)).toFixed(3));const d=Math.abs(off);if(d<bd){bd=d;best=i}});
    if(best!==act){act=best;cards.forEach((c,i)=>c.classList.toggle('on',i===best));if(num)num.textContent=String(best+1).padStart(2,'0')}
    if(bar)bar.style.transform='scaleX('+(dist?cur/dist:0).toFixed(4)+')';if(cur!==target)raf=requestAnimationFrame(tick)};
  addEventListener('scroll',read,{passive:true});addEventListener('resize',measure);addEventListener('load',measure);measure();
  // keyboard: focusing a card scrolls the page to it
  cards.forEach((c,i)=>c.addEventListener('focus',()=>{const top=sec.getBoundingClientRect().top+scrollY;const x=c.offsetLeft-(innerWidth-c.offsetWidth)/2;scrollTo({top:top+Math.max(0,Math.min(dist,x)),behavior:'smooth'})}));
})();

// insights: tap a decade bar to read its count
(()=>{const bs=$$('.ibar');const out=$('.ibar-out');if(!bs.length)return;bs.forEach(b=>b.addEventListener('click',()=>{bs.forEach(x=>x.setAttribute('aria-pressed',String(x===b)));if(out)out.textContent=b.dataset.d+': '+b.dataset.n+' projects'}));
  const last=bs[bs.length-1];last.click()})();
