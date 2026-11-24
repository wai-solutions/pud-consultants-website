import {gsap} from 'gsap';
import {ScrollTrigger} from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
document.documentElement.classList.remove('no-js');

const nav=$('.nav');const onS=()=>nav.classList.toggle('solid',scrollY>40);onS();addEventListener('scroll',onS,{passive:true});
$('.burger')?.addEventListener('click',()=>{nav.classList.toggle('open');$('.burger').setAttribute('aria-expanded',nav.classList.contains('open'))});
$$('.nav li a').forEach(a=>a.addEventListener('click',()=>nav.classList.remove('open')));
addEventListener('keydown',e=>{if(e.key==='Escape')nav.classList.remove('open')});

const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{threshold:.1,rootMargin:'0px 0px -5% 0px'});
$$('[data-r]').forEach(el=>{const d=el.dataset.r;if(d&&d!=='1')el.style.transitionDelay=d+'s';io.observe(el)});

function hasGL(){try{const c=document.createElement('canvas');return !!(c.getContext('webgl2')||c.getContext('webgl'))}catch(e){return false}}
const GL=hasGL()&&!reduce;
if(!GL)document.documentElement.classList.add('nowebgl');

const hv=$('.hero video');
if(hv){if(reduce){hv.pause();hv.removeAttribute('autoplay')}else{new IntersectionObserver(es=>{es[0].isIntersecting?hv.play().catch(()=>{}):hv.pause()}).observe(hv)}}

const stage=$('.stage');
if(stage&&GL){
  const st={p:0};const steps=$$('.step',stage);const bar=$('.bar i',stage);
  import('./paper.js').then(m=>m.paperScene($('canvas',stage),st));
  ScrollTrigger.create({trigger:stage,start:'top top',end:'bottom bottom',scrub:true,onUpdate:s=>{st.p=s.progress;bar.style.height=(s.progress*100)+'%';stage.querySelector('.pin').style.setProperty('--end',Math.max(0,Math.min(1,(s.progress-.88)/.12)));
    const idx=Math.min(steps.length-1,Math.floor(s.progress*steps.length*.999));steps.forEach((el,i)=>el.classList.toggle('on',i===idx))}});
  steps[0].classList.add('on');
}else if(stage){$$('.step',stage).forEach(e=>e.classList.add('on'))}

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
  if(!reduce)new IntersectionObserver(es=>{es[0].isIntersecting?v.play().catch(()=>{}):v.pause()}).observe(v)});

const fm=$('.film-modal');
if(fm){const v=$('video',fm);$$('[data-film]').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();fm.classList.add('on');v.src=v.dataset.src;v.play().catch(()=>{})}));
  const close=()=>{fm.classList.remove('on');v.pause()};$('.x',fm).addEventListener('click',close);fm.addEventListener('click',e=>{if(e.target===fm)close()});addEventListener('keydown',e=>{if(e.key==='Escape')close()})}

const lb=$('.lb');
if(lb){const imgs=$$('.gal button');let i=0;const img=$('img',lb);const show=n=>{i=(n+imgs.length)%imgs.length;img.src=imgs[i].dataset.full;img.alt=imgs[i].querySelector('img').alt;lb.classList.add('on')};
  imgs.forEach((b,n)=>b.addEventListener('click',()=>show(n)));$('.x',lb).onclick=()=>lb.classList.remove('on');$('.p',lb).onclick=()=>show(i-1);$('.n',lb).onclick=()=>show(i+1);
  addEventListener('keydown',e=>{if(!lb.classList.contains('on'))return;if(e.key==='Escape')lb.classList.remove('on');if(e.key==='ArrowLeft')show(i-1);if(e.key==='ArrowRight')show(i+1)})}

const DATA=window.__PROJECTS||[];const MS=window.__MILESTONES||[];
const box=$('.atlas .box');
let atlas=null;
const state={q:'',country:'All',cat:'All',year:2026};
function pass(p){return (state.country==='All'||p.country===state.country)&&(state.cat==='All'||p.category.includes(state.cat))&&(!state.q||(p.name+' '+p.city+' '+p.client+' '+p.country).toLowerCase().includes(state.q))}
function applyGrid(){const g=$('.pgrid');if(!g||!DATA.length)return;let n=0;$$('.pcard',g).forEach(c=>{const p=DATA[+c.dataset.i];const ok=pass(p)&&p.year_start<=state.year;c.hidden=!ok;if(ok)n++});const ct=$('.count');if(ct)ct.textContent=n+' project'+(n===1?'':'s')}
function count(){return DATA.filter(p=>pass(p)&&p.year_start<=state.year).length}
function applyMap(){atlas&&atlas.setFilter(pass);atlas&&atlas.setYear(state.year);const y=$('.atlas .yr');if(y)y.textContent=state.year;const n=$('.atlas .n');if(n)n.textContent=count()+' projects'}
function applyAll(){applyMap();applyGrid()}
let gridT=null;const applyGridSoon=()=>{clearTimeout(gridT);gridT=setTimeout(applyGrid,220)};
const V={all:[43,26,1],egypt:[31,28.5,3.1],ksa:[43,24,1.9],makkah:[39.9,21.4,5],coast:[28.6,31,5],iraq:[41,33,2.3],riyadh:[46.7,24.7,3.4],alula:[39.3,25.8,3.8],giza:[31.1,29.9,5.4]};
const moveTo=v=>{if(atlas&&V[v])atlas.setView(...V[v])};
const cap=$('.atlas .story'),now=$('.atlas .now');
function showCap(m){if(!cap)return;if(!m){cap.classList.remove('on');return}cap.querySelector('.mono').textContent=m.y||'';cap.querySelector('b').textContent=m.t;cap.classList.add('on')}
let lastNow=-9;
function showNow(y){if(!now)return;const L=DATA.filter(p=>p.year_start===y&&pass(p)).slice(0,3);
  if(!L.length){if(y-lastNow>2)now.innerHTML='';return}
  lastNow=y;now.innerHTML=L.map(p=>'<a href="'+p.url+'">'+(p.thumb?'<img src="'+p.thumb+'" alt="">':'<i class="dot"></i>')+'<span><b>'+p.name+'</b><small>'+(p.city||p.country)+' · '+p.year+'</small></span></a>').join('')}
if(box&&GL&&DATA.length){
  Promise.all([fetch(box.dataset.geo).then(r=>r.json()),import('./atlas.js')]).then(([geo,m])=>{
    atlas=m.atlasScene(box,geo,DATA,{onSelect:p=>{const c=$('.cardsel');if(!c)return;c.classList.add('on');const im=$('img',c);im.src=p.thumb||'';im.style.display=p.thumb?'':'none';$('h3',c).textContent=p.name;$('p',c).textContent=(p.city?p.city+', ':'')+p.country+' · '+p.year+' · '+p.client;$('a',c).href=p.url}});
    applyAll();
    $$('[data-view]').forEach(b=>b.addEventListener('click',()=>{const v=b.dataset.view;if(v==='in')atlas.zoomBy(1.4);else if(v==='out')atlas.zoomBy(1/1.4);else moveTo(v)}));
  });
}else if(box){box.classList.add('static')}
$$('[data-filter]').forEach(b=>b.addEventListener('click',()=>{const [k,v]=b.dataset.filter.split(':');state[k]=v;$$('[data-filter^="'+k+':"]').forEach(x=>x.setAttribute('aria-pressed',x===b));applyAll()}));
$('.search')?.addEventListener('input',e=>{state.q=e.target.value.trim().toLowerCase();applyAll()});
const sl=$('.atlas input[type=range]');const playBtn=$('.play');let run=0,speed=1;
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
if(sl){sl.addEventListener('input',()=>{if(playBtn&&playBtn.textContent==='Pause')stopPlay('Resume');state.year=+sl.value;showCap(null);applyMap();showNow(state.year);applyGridSoon()})}
if(DATA.length)applyAll();
addEventListener('load',()=>ScrollTrigger.refresh());

(()=>{const w=document.querySelector('.welcome');if(w&&w.dataset.until&&new Date()>new Date(w.dataset.until+'T23:59:59'))w.remove()})();
(()=>{const nav=document.querySelector('.nav'),bg=document.querySelector('.burger');if(!nav||!bg)return;
 const set=o=>{nav.classList.toggle('open',o);bg.setAttribute('aria-expanded',o?'true':'false')};
 addEventListener('keydown',e=>{if(e.key==='Escape'&&nav.classList.contains('open')){set(false);bg.focus()}});})();
(()=>{const lb=document.querySelector('.lb');if(!lb)return;let last=null;
 new MutationObserver(()=>{if(lb.classList.contains('on')){last=document.activeElement;(lb.querySelector('.x')||lb).focus()}else if(last){last.focus();last=null}}).observe(lb,{attributes:true,attributeFilter:['class']});
 lb.addEventListener('keydown',e=>{if(e.key!=='Tab')return;const f=[...lb.querySelectorAll('button')];const i=f.indexOf(document.activeElement);e.preventDefault();f[(i+(e.shiftKey?-1:1)+f.length)%f.length].focus()});})();

(()=>{const w=document.querySelector('.welcome'),nav=document.querySelector('.nav');if(!w||!nav)return;const set=()=>{nav.style.top=Math.max(0,w.offsetHeight-scrollY)+'px'};set();addEventListener('scroll',set,{passive:true});addEventListener('resize',set)})();
