// "From paper to place": a masterplan drawn as lines, extruded into a city, then lived in.
import * as THREE from 'three';

function rng(seed){let s=seed>>>0;return()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296}}
const ease=t=>t<0?0:t>1?1:t*t*(3-2*t);
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));

export function paperScene(canvas,state){
  const R=rng(60);
  const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false,powerPreference:'high-performance'});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.75));
  renderer.setClearColor(0x000000,1);
  const scene=new THREE.Scene(); scene.fog=new THREE.FogExp2(0x000000,.034);
  const cam=new THREE.PerspectiveCamera(34,1,.1,200);

  // plan: cells of a grid with a boulevard and a waterfront edge
  const N=17, S=1.0, half=(N-1)/2;
  const blocks=[]; // {x,z,w,d,h,landmark,d0}
  for(let i=0;i<N;i++)for(let j=0;j<N;j++){
    const x=(i-half)*S, z=(j-half)*S, dist=Math.hypot(x,z);
    if(dist>8.4||z>6.3) continue;
    if(Math.abs(x)<.5 && Math.abs(z)<8) continue;      // main boulevard (north-south)
    if(Math.abs(z+1.0)<.5) continue;                    // cross avenue
    if(R()<.06) continue;                               // plazas
    const park=R()<.07;
    const n=R()<.45?2:1;
    for(let k=0;k<n;k++){
      const w=n==2?.38:.74, d=.74, ox=n==2?(k?.2:-.2):0;
      const core=Math.max(0,1-dist/8.4);
      let h=park?.03:.18+R()*.55+core*1.9*R();
      if(Math.abs(x)<1.6) h*=1.15;
      blocks.push({x:x+ox,z,w,d,h,park,dist});
    }
  }
  // landmarks
  const lm=[{x:1,z:-1,h:3.4},{x:-2,z:2,h:2.5},{x:2,z:3,h:2.2}];
  lm.forEach(l=>blocks.push({x:l.x,z:l.z,w:.62,d:.62,h:l.h,landmark:true,dist:Math.hypot(l.x,l.z)}));
  blocks.sort((a,b)=>a.dist-b.dist);

  // lines (plan)
  const pos=[]; const rect=(x,z,w,d)=>{const x0=x-w/2,x1=x+w/2,z0=z-d/2,z1=z+d/2;pos.push(x0,0,z0,x1,0,z0, x1,0,z0,x1,0,z1, x1,0,z1,x0,0,z1, x0,0,z1,x0,0,z0)};
  blocks.forEach(b=>rect(b.x,b.z,b.w,b.d));
  const axes=[]; for(let k=-8;k<=8;k++){ if(k%2==0){pos.push(-8.4,0,k*S*.5-.5, 8.4,0,k*S*.5-.5)} }
  pos.push(0,0,-8.4, 0,0,8.4);
  const lineGeo=new THREE.BufferGeometry(); lineGeo.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  const lines=new THREE.LineSegments(lineGeo,new THREE.LineBasicMaterial({color:0xEF4223,transparent:true,opacity:.85}));
  scene.add(lines);
  const segPerBlock=8; // vertices per block rect
  const blockVerts=blocks.length*8;

  // ground
  const gc=document.createElement('canvas');gc.width=gc.height=512;const g=gc.getContext('2d');
  const grd=g.createRadialGradient(256,256,0,256,256,256);grd.addColorStop(0,'#1a1a1a');grd.addColorStop(.6,'#0d0d0d');grd.addColorStop(1,'#000000');g.fillStyle=grd;g.fillRect(0,0,512,512);
  g.strokeStyle='rgba(98,224,232,.07)';g.lineWidth=1;for(let i=0;i<=32;i++){g.beginPath();g.moveTo(i*16,0);g.lineTo(i*16,512);g.stroke();g.beginPath();g.moveTo(0,i*16);g.lineTo(512,i*16);g.stroke()}
  const ground=new THREE.Mesh(new THREE.CircleGeometry(16,64),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(gc)}));ground.rotation.x=-Math.PI/2;ground.position.y=-.01;scene.add(ground);

  // sea to the north-coast side
  const sc=document.createElement('canvas');sc.width=64;sc.height=256;const sx=sc.getContext('2d');const sg=sx.createLinearGradient(0,0,0,256);sg.addColorStop(0,'#2b2b2b');sg.addColorStop(.25,'#141414');sg.addColorStop(1,'#000000');sx.fillStyle=sg;sx.fillRect(0,0,64,256);
  const sea=new THREE.Mesh(new THREE.PlaneGeometry(40,12),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(sc),fog:true}));sea.rotation.x=-Math.PI/2;sea.position.set(0,.0,12.9);scene.add(sea);
  scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-12,.01,6.9),new THREE.Vector3(-4,.01,7.1),new THREE.Vector3(2,.01,6.8),new THREE.Vector3(12,.01,7.0)]),new THREE.LineBasicMaterial({color:0xffffff,transparent:true,opacity:.6})));
  // buildings (instanced)
  const geo=new THREE.BoxGeometry(1,1,1);geo.translate(0,.5,0);
  const cols=[];const cA=new THREE.Color(0x2e2e2e),cB=new THREE.Color(0xf3f3f3);
  const c=geo.attributes.position;for(let i=0;i<c.count;i++){const y=c.getY(i);const t=Math.pow(y,.8);cols.push(...new THREE.Color().lerpColors(cA,cB,.25+.75*t).toArray())}
  geo.setAttribute('color',new THREE.Float32BufferAttribute(cols,3));
  const mat=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.78,metalness:.05});
  const U={uGlow:{value:0}};
  mat.onBeforeCompile=sh=>{sh.uniforms.uGlow=U.uGlow;
    sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vW;').replace('#include <begin_vertex>','#include <begin_vertex>\nvW=(modelMatrix*instanceMatrix*vec4(position,1.0)).xyz;');
    sh.fragmentShader=sh.fragmentShader.replace('#include <common>','#include <common>\nvarying vec3 vW;uniform float uGlow;float hh(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}')
     .replace('#include <color_fragment>','#include <color_fragment>\n float wy=fract(vW.y*6.0);float wq=fract((vW.x+vW.z)*6.0);float win=step(.2,wy)*step(wy,.74)*step(.16,wq)*step(wq,.84);float sd=1.0-step(.5,abs(vNormal.y));diffuseColor.rgb*=mix(1.0,.5,win*sd);')
     .replace('#include <emissivemap_fragment>','#include <emissivemap_fragment>\n float lit=step(.62,hh(floor(vec2((vW.x+vW.z)*6.0,vW.y*6.0))+floor(vW.xz)));totalEmissiveRadiance+=vec3(1.0,.62,.28)*win*sd*lit*uGlow*.9;');};
  const mesh=new THREE.InstancedMesh(geo,mat,blocks.length);mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);scene.add(mesh);
  const ic=new THREE.Color();
  blocks.forEach((b,i)=>{ if(b.landmark)ic.setHex(0xEF4223); else if(b.park)ic.setHex(0x003737); else ic.setHex(0xffffff).lerp(new THREE.Color(0xd6d6d6),R()*.6); mesh.setColorAt(i,ic) });
  mesh.instanceColor.needsUpdate=true;
  scene.add(new THREE.HemisphereLight(0xffffff,0x1a1a1a,1.15));
  const sun=new THREE.DirectionalLight(0xffffff,2.2);sun.position.set(-6,9,5);scene.add(sun);
  const rim=new THREE.DirectionalLight(0xEF4223,.6);rim.position.set(7,3,-6);scene.add(rim);

  // people: points walking the streets
  const P=260,pp=new Float32Array(P*3),pv=[];
  for(let i=0;i<P;i++){const axis=R()<.5?0:1;const lane=(Math.floor(R()*9)-4)*S+(axis?-0.5:0);pv.push({axis,lane,t:R()*17-8.5,v:(R()<.5?-1:1)*(.25+R()*.5)})}
  const pg=new THREE.BufferGeometry();pg.setAttribute('position',new THREE.BufferAttribute(pp,3));
  const sprite=(()=>{const cv=document.createElement('canvas');cv.width=cv.height=64;const x=cv.getContext('2d');const gr=x.createRadialGradient(32,32,0,32,32,32);gr.addColorStop(0,'rgba(255,230,190,1)');gr.addColorStop(.25,'rgba(255,170,100,.8)');gr.addColorStop(1,'rgba(255,120,60,0)');x.fillStyle=gr;x.fillRect(0,0,64,64);return new THREE.CanvasTexture(cv)})();
  const people=new THREE.Points(pg,new THREE.PointsMaterial({size:.2,map:sprite,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,opacity:0}));scene.add(people);

  // camera keyframes
  const K=[ {p:0,   pos:[0,15.5,.01],  look:[0,0,0],     fov:34},
            {p:.3,  pos:[7,11,10.5],  look:[0,.2,0],    fov:34},
            {p:.62, pos:[6.5,4.2,11.5], look:[0,.7,0],    fov:36},
            {p:1,   pos:[3.2,2.3,10.2],look:[-.2,1.0,-1.5],fov:42} ];
  const lerp=(a,b,t)=>a+(b-a)*t;
  function camAt(p){let i=0;while(i<K.length-2&&p>K[i+1].p)i++;const a=K[i],b=K[i+1];const t=ease((p-a.p)/(b.p-a.p));
    return{pos:a.pos.map((v,k)=>lerp(v,b.pos[k],t)),look:a.look.map((v,k)=>lerp(v,b.look[k],t)),fov:lerp(a.fov,b.fov,t)}}

  let w=0,h=0,mx=0,my=0,smoothP=0,run=false,last=performance.now(),vis=true;
  function size(){const r=canvas.parentElement.getBoundingClientRect();w=Math.max(2,r.width);h=Math.max(2,r.height);renderer.setSize(w,h,false);cam.aspect=w/h;cam.updateProjectionMatrix()}
  new ResizeObserver(size).observe(canvas.parentElement);size();
  window.addEventListener('pointermove',e=>{mx=(e.clientX/innerWidth-.5);my=(e.clientY/innerHeight-.5)},{passive:true});
  const m4=new THREE.Matrix4(),q=new THREE.Quaternion(),v3=new THREE.Vector3(),s3=new THREE.Vector3();
  function frame(now){
    if(!run){return}
    requestAnimationFrame(frame);
    const dt=Math.min(.05,(now-last)/1000);last=now;
    const target=state.p; smoothP+= (target-smoothP)*Math.min(1,dt*5);
    const p=smoothP;
    // lines draw-on over 0-.28
    const dr=clamp(p/.26);lineGeo.setDrawRange(0,Math.floor(lineGeo.attributes.position.count*ease(dr)/2)*2);
    lines.material.opacity=lerp(.9,.28,ease(clamp((p-.35)/.4)));
    // extrude .22-.62 staggered by distance
    for(let i=0;i<blocks.length;i++){const b=blocks[i];const st=clamp((p-.2-b.dist*.028)/.3);const e=ease(st);
      v3.set(b.x,e<.003?-.6:0,b.z);s3.set(b.w*(b.park?1:.98),Math.max(.01,b.h*e),b.d);m4.compose(v3,q,s3);mesh.setMatrixAt(i,m4)}
    mesh.instanceMatrix.needsUpdate=true;
    // people
    U.uGlow.value=ease(clamp((p-.5)/.4));
    people.material.opacity=ease(clamp((p-.55)/.25))*.95;
    if(p>.5){for(let i=0;i<P;i++){const a=pv[i];a.t+=a.v*dt;if(a.t>8.4)a.t=-8.4;if(a.t<-8.4)a.t=8.4;
      pp[i*3]=a.axis?a.t:a.lane;pp[i*3+1]=.08;pp[i*3+2]=a.axis?a.lane:a.t}
      pg.attributes.position.needsUpdate=true}
    // camera
    const cp=camAt(p);const ang=p*.35+mx*.35;
    const cx=cp.pos[0]*Math.cos(ang*.25)-cp.pos[2]*Math.sin(ang*.25),cz=cp.pos[0]*Math.sin(ang*.25)+cp.pos[2]*Math.cos(ang*.25);
    cam.position.set(cx+mx*.5,cp.pos[1]-my*.4,cz);cam.fov=cp.fov;cam.updateProjectionMatrix();
    const ut=ease(clamp(p/.3));cam.up.set(0,Math.max(.0001,ut),-(1-ut)).normalize();
    cam.lookAt(cp.look[0],cp.look[1],cp.look[2]);
    renderer.render(scene,cam);
  }
  const io=new IntersectionObserver(es=>{const on=es[0].isIntersecting;if(on&&!run){run=true;last=performance.now();requestAnimationFrame(frame)}else if(!on){run=false}},{rootMargin:'200px'});
  io.observe(canvas.parentElement);
  return{renderer};
}
