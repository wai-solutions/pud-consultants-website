// Atlas: 60 years of projects on a region map. Pins grow in by year; colour ramps from grey (oldest) through white to brand orange (newest).
import * as THREE from 'three';

const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const RAMP=[[1964,0x6b6b6b],[1990,0xbdbdbd],[2010,0xffffff],[2026,0xEF4223]];
function colorFor(y){let i=0;while(i<RAMP.length-2&&y>RAMP[i+1][0])i++;const a=RAMP[i],b=RAMP[i+1];const t=clamp((y-a[0])/(b[0]-a[0]));return new THREE.Color(a[1]).lerp(new THREE.Color(b[1]),t)}
export {colorFor};

export function atlasScene(box,geo,projects,api){
  const canvas=box.querySelector('canvas');
  const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio||1,1.75));renderer.setClearColor(0x000000,0);
  const scene=new THREE.Scene();
  const LON0=26,LON1=60,LAT0=12,LAT1=40; const K=Math.cos(26*Math.PI/180);
  const X=lon=>(lon-(LON0+LON1)/2)*K, Z=lat=>-(lat-(LAT0+LAT1)/2);
  const W=(LON1-LON0)*K, H=(LAT1-LAT0);
  const cam=new THREE.PerspectiveCamera(32,1,.1,400);
  // land
  const land=new THREE.Group();scene.add(land);
  const fillMat=new THREE.MeshBasicMaterial({color:0x141414,transparent:true,opacity:.9,side:THREE.DoubleSide});
  const lineMat=new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:.22});
  const ring2shape=r=>{const s=new THREE.Shape();r.forEach((c,i)=>{const x=X(c[0]),z=Z(c[1]);i?s.lineTo(x,-z):s.moveTo(x,-z)});return s};
  const inWin=r=>r.some(c=>c[0]>LON0-4&&c[0]<LON1+4&&c[1]>LAT0-4&&c[1]<LAT1+4);
  geo.features.forEach(f=>{const g=f.geometry;if(!g)return;const polys=g.type==='Polygon'?[g.coordinates]:g.coordinates;
    polys.forEach(poly=>{const outer=poly[0];if(!inWin(outer))return;
      const m=new THREE.Mesh(new THREE.ShapeGeometry(ring2shape(outer)),fillMat);m.rotation.x=-Math.PI/2;m.position.y=-.02;land.add(m);
      const pts=outer.map(c=>new THREE.Vector3(X(c[0]),0,Z(c[1])));land.add(new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(pts),lineMat))})});
  // graticule
  const gm=new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:.04});
  for(let lon=LON0;lon<=LON1;lon+=4){land.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(X(lon),-.03,Z(LAT0)),new THREE.Vector3(X(lon),-.03,Z(LAT1))]),gm))}
  for(let lat=LAT0;lat<=LAT1;lat+=4){land.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(X(LON0),-.03,Z(lat)),new THREE.Vector3(X(LON1),-.03,Z(lat))]),gm))}
  // pins (jitter overlapping)
  const seen={};const pins=[];
  const stem=new THREE.CylinderGeometry(.03,.03,1,6);stem.translate(0,.5,0);
  const head=new THREE.SphereGeometry(.11,14,10);
  projects.forEach((p,i)=>{if(p.lat==null||p.lon==null)return;const key=p.lat.toFixed(1)+','+p.lon.toFixed(1);const n=seen[key]=(seen[key]||0)+1;
    const ang=n*2.399,rad=n>1?.12*Math.sqrt(n):0;const x=X(p.lon)+Math.cos(ang)*rad,z=Z(p.lat)+Math.sin(ang)*rad;
    const col=colorFor(p.year_start||2000);const m=new THREE.MeshBasicMaterial({color:col,transparent:true});
    const s=new THREE.Mesh(stem,m.clone());const hd=new THREE.Mesh(head,m);const g=new THREE.Group();g.add(s,hd);g.position.set(x,0,z);scene.add(g);
    const hh=.25+(p.featured?.55:.0)+Math.min(.35,(n%5)*.06);
    hd.userData.p=p;pins.push({g,s,hd,hh,p,t:0,vis:true,x,z,mat:m})});
  const ringGeo=new THREE.RingGeometry(.16,.2,40);ringGeo.rotateX(-Math.PI/2);
  pins.forEach(a=>{const m=new THREE.Mesh(ringGeo,new THREE.MeshBasicMaterial({color:a.mat.color,transparent:true,opacity:0,depthWrite:false}));m.position.set(a.x,.03,a.z);m.visible=false;scene.add(m);a.ring=m;a.pulse=0;a.was=undefined});
  const heads=pins.map(a=>a.hd);

  let tapAt=0,w=1,h=1,run=false,last=performance.now(),mx=0,my=0,drag=false,rot=0,tilt=0,zoom=1,hover=null,vx=0,vz=2,tvx=0,tvz=2,tz=1,yearTo=2026,yearCur=2026,filt=()=>true,sel=null;
  const ray=new THREE.Raycaster(),mouse=new THREE.Vector2(9,9);
  function size(){const r=box.getBoundingClientRect();w=Math.max(2,r.width);h=Math.max(2,r.height);renderer.setSize(w,h,false);cam.aspect=w/h;cam.updateProjectionMatrix()}
  new ResizeObserver(size).observe(box);size();
  const tip=box.querySelector('.tip');
  function place(){vx+=(tvx-vx)*.08;vz+=(tvz-vz)*.08;zoom+=(tz-zoom)*.08;const ar=w/h,d=(ar<1.1?46*Math.min(2.3,Math.max(1.39,1.5/ar)):46)/zoom;const a=-0.0+rot*.0;const el=.95-tilt*.0;
    cam.position.set(vx+Math.sin(rot)*d*.35+mx*1.2,d*Math.sin(el)-my*1.2,vz+d*Math.cos(el)*.62);cam.lookAt(vx,0,vz)}
  box.addEventListener('pointermove',e=>{const r=box.getBoundingClientRect();mouse.x=((e.clientX-r.left)/r.width)*2-1;mouse.y=-((e.clientY-r.top)/r.height)*2+1;mx=mouse.x*.6;my=mouse.y*.6;
    if(drag){rot=clamp(rot-e.movementX*.003,-.9,.9)} });
  box.addEventListener('pointerdown',e=>{drag=true;if(e.pointerType==='touch'||e.pointerType==='pen'){const r=box.getBoundingClientRect();mouse.x=((e.clientX-r.left)/r.width)*2-1;mouse.y=-((e.clientY-r.top)/r.height)*2+1;tapAt=performance.now()}});addEventListener('pointerup',()=>{drag=false});addEventListener('pointercancel',()=>{drag=false});
  box.addEventListener('pointerleave',()=>{mouse.set(9,9)});
  box.addEventListener('wheel',e=>{if(e.ctrlKey||e.metaKey){e.preventDefault();tz=clamp(tz*(e.deltaY>0?.92:1.08),.7,4)}},{passive:false});
  box.addEventListener('click',()=>{if(hover&&hover.p&&api.onSelect){sel=hover.p;api.onSelect(hover.p)}});
  box.addEventListener('pointerup',e=>{if(e.pointerType==='touch'&&performance.now()-tapAt<350){setTimeout(()=>{if(hover&&hover.p&&api.onSelect){sel=hover.p;api.onSelect(hover.p)}},60)}});
  const v=new THREE.Vector3();
  function frame(now){
    if(!run)return;requestAnimationFrame(frame);
    const dt=Math.min(.05,(now-last)/1000);last=now;
    yearCur+= (yearTo-yearCur)*Math.min(1,dt*6);
    place();
    ray.setFromCamera(mouse,cam);const hit=ray.intersectObjects(heads,false)[0];
    hover=hit?pins.find(a=>a.hd===hit.object):null;
    canvas.style.cursor=hover?'pointer':'grab';
    for(const a of pins){const show=a.p.year_start<=yearCur+.01&&filt(a.p);a.vis=show;a.t+=((show?1:0)-a.t)*Math.min(1,dt*7);
      const t=a.t,isH=a===hover||(sel&&sel===a.p);const sc=t*(isH?1.35:1);
      a.s.scale.set(1,Math.max(.0001,a.hh*t),1);a.hd.position.y=a.hh*t;a.hd.scale.setScalar(Math.max(.0001,sc*(a.p.featured?1.5:1)));
      a.mat.opacity=clamp(t*(isH?1:.92));a.s.material.opacity=a.mat.opacity*.7;a.g.visible=t>.01;
      if(a.was!==undefined&&show&&!a.was)a.pulse=1;a.was=show;
      if(a.pulse>0){a.pulse=Math.max(0,a.pulse-dt*.55);const k=1-a.pulse;a.ring.visible=true;a.ring.scale.setScalar(1+k*(a.p.featured?9:6));a.ring.material.opacity=a.pulse*.85}else a.ring.visible=false}
    if(tip){if(hover){v.set(hover.x,hover.hh,hover.z).project(cam);const r=box.getBoundingClientRect();tip.style.left=((v.x*.5+.5)*r.width)+'px';tip.style.top=((-v.y*.5+.5)*r.height)+'px';tip.style.opacity=1;tip.innerHTML='<b></b><span></span>';tip.firstChild.textContent=hover.p.name;tip.lastChild.textContent=(hover.p.city||hover.p.country)+' · '+hover.p.year}else tip.style.opacity=0}
    renderer.render(scene,cam);
  }
  new IntersectionObserver(es=>{const on=es[0].isIntersecting;if(on&&!run){run=true;last=performance.now();requestAnimationFrame(frame)}else if(!on)run=false},{rootMargin:'200px'}).observe(box);
  return{setView(lon,lat,z){tvx=X(lon);tvz=Z(lat);tz=z},zoomBy(f){tz=clamp(tz*f,.7,4)},setYear(y){yearTo=y},setFilter(f){filt=f},select(p){sel=p},count(){return pins.filter(a=>a.p.year_start<=yearTo&&filt(a.p)).length}};
}
