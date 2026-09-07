# v27: day/night cycle. One scalar drives the sky (CSS), fog, both lights, and an emissive channel
# carried per-vertex through the merge batcher so windows, lamps, signs and headlights light up.
# The sun DIRECTION stays fixed on purpose: the fake contact shadows and the terrain AO are baked
# once against it (buildShadows), so a moving sun would desync them.
import io
p = 'index.html'; s = io.open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, ('MISSING/AMBIGUOUS', old[:90], s.count(old))
    s = s.replace(old, new)

# ---- 1. lights need handles; today they are created anonymously on one line ----
rep("S.add(new THREE.HemisphereLight(0xfff4e0,0x7a9a6a,.9));var sun=new THREE.DirectionalLight(0xfff6e6,1.1);",
    "var hemi=new THREE.HemisphereLight(0xfff4e0,0x7a9a6a,.9);S.add(hemi);var sun=new THREE.DirectionalLight(0xfff6e6,1.1);")

# ---- 2. the emissive channel through the batcher ----
rep("var MB=null;function mbStart(){MB={p:[],n:[],c:[],u:[]}}",
    "var MB=null,MPE=0,MATS=[];function mbStart(){MB={p:[],n:[],c:[],u:[],e:[]}}")
rep(" var ka=g.attributes.color,kw=ka&&ka.itemSize>3;\n"
    " for(var i=0;i<pa.count;i++){MB.p.push(pa.getX(i),pa.getY(i),pa.getZ(i));MB.n.push(na.getX(i),na.getY(i),na.getZ(i));\n"
    "  if(ka){var t=kw?ka.getW(i):1,kr=ka.getX(i),kg=ka.getY(i),kb=ka.getZ(i);MB.c.push(kr*(1+t*(cc.r-1)),kg*(1+t*(cc.g-1)),kb*(1+t*(cc.b-1)))}   // Blender-baked AO, tinted only where a=1\n",
    " var ka=g.attributes.color,kw=ka&&ka.itemSize>3;\n"
    " for(var i=0;i<pa.count;i++){MB.p.push(pa.getX(i),pa.getY(i),pa.getZ(i));MB.n.push(na.getX(i),na.getY(i),na.getZ(i));var em=MPE;\n"
    "  if(ka){var a=kw?ka.getW(i):1,t=a>.95?1:0,kr=ka.getX(i),kg=ka.getY(i),kb=ka.getZ(i);\n"
    "   if(a>=.05&&a<=.95)em=a<.2?1:((a-.35)/.55*.85+.15);   // kit alpha: .10 = always lit, .35-.90 = a window with that seed\n"
    "   MB.c.push(kr*(1+t*(cc.r-1)),kg*(1+t*(cc.g-1)),kb*(1+t*(cc.b-1)))}   // Blender-baked AO, tinted only where a=1\n")
rep("  MB.u.push((pa.getX(i)+pa.getZ(i))*.25,pa.getY(i)*.25)}}",
    "  MB.e.push(em);MB.u.push((pa.getX(i)+pa.getZ(i))*.25,pa.getY(i)*.25)}}")
rep("bg.setAttribute('uv',new THREE.Float32BufferAttribute(MB.u,2));var mm=new THREE.MeshStandardMaterial({vertexColors:true,roughness:opt.rough||.88,metalness:0,map:opt.map?TEX(opt.map,1):null});mm.flatShading=!opt.map;",
    "bg.setAttribute('uv',new THREE.Float32BufferAttribute(MB.u,2));bg.setAttribute('aEmit',new THREE.Float32BufferAttribute(MB.e,1));var mm=new THREE.MeshStandardMaterial({vertexColors:true,roughness:opt.rough||.88,metalness:0,map:opt.map?TEX(opt.map,1):null});mm.flatShading=!opt.map;nightMat(mm);")

# ---- 3. shared night uniforms + the shader patch (no extra draw calls) ----
rep("var MB=null,MPE=0,MATS=[];",
    "var NU={n:{value:0},cut:{value:.55},glow:{value:new THREE.Color(0xffdca8)}};\n"
    "function nightMat(m){m.onBeforeCompile=function(sh){sh.uniforms.uNight=NU.n;sh.uniforms.uCut=NU.cut;sh.uniforms.uGlow=NU.glow;\n"
    " sh.vertexShader='attribute float aEmit;\\nvarying float vEmit;\\n'+sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\\n vEmit=aEmit;');\n"
    " sh.fragmentShader='uniform float uNight;uniform float uCut;uniform vec3 uGlow;\\nvarying float vEmit;\\n'+sh.fragmentShader.replace('#include <emissivemap_fragment>','#include <emissivemap_fragment>\\n totalEmissiveRadiance+=uGlow*(step(uCut,vEmit)*uNight);');\n"
    "};m.needsUpdate=true;MATS.push(m);return m}\n"
    "var MB=null,MPE=0,MATS=[];")

# ---- 4. the procedural fallback's windows and bulbs opt in the same way ----
rep("mp(BX(w,h,w),c,x,y+h/2,z);for(var f=1;f<h/1.4;f++){mp(BX(w+.06,.35,w*.42),0x2c3e50,x,y+f*1.4,z+w*.3);mp(BX(w+.06,.35,w*.42),0x2c3e50,x,y+f*1.4,z-w*.3)}",
    "mp(BX(w,h,w),c,x,y+h/2,z);for(var f=1;f<h/1.4;f++){MPE=.2+((f*7)%9)/12;mp(BX(w+.06,.35,w*.42),0x2c3e50,x,y+f*1.4,z+w*.3);mp(BX(w+.06,.35,w*.42),0x2c3e50,x,y+f*1.4,z-w*.3);MPE=0}")
rep(" mp(CY(.06,.09,3.2,6),0x2f3b45,x,y+1.6,z);mp(SP(.28),0xfff2b0,x,y+3.35,z)}",
    " mp(CY(.06,.09,3.2,6),0x2f3b45,x,y+1.6,z);MPE=1;mp(SP(.28),0xfff2b0,x,y+3.35,z);MPE=0}")
rep("mp(BX(.3,.3,.5),0xfff1a8,x+Math.cos(ry)*L*.5,y+1.2,z-Math.sin(ry)*L*.5,0,ry);",
    "MPE=1;mp(BX(.3,.3,.5),0xfff1a8,x+Math.cos(ry)*L*.5,y+1.2,z-Math.sin(ry)*L*.5,0,ry);MPE=0;")

# ---- 5. collect glow positions while the world builds (same shape as PALMS) ----
rep("function lamp(x,z){var y=ground(x,z);if(KIT.lamp2){mp(KIT.lamp2,0xffffff,x,y,z,0,(x*3+z)%6.28);return}",
    "function lamp(x,z){var y=ground(x,z);LAMPS.push([x,y+3.3,z,1,.86,.55]);if(KIT.lamp2){mp(KIT.lamp2,0xffffff,x,y,z,0,(x*3+z)%6.28);return}")
rep(" if(KV){mp(KV,c,x,y,z,0,ry,0,L/KL,L/KL,L/KL);COL.push({x:x,z:z,r:2.3});SHB.push([x,z,2.4,2.5]);return}",
    " LAMPS.push([x+Math.cos(ry)*L*.52,y+1.2,z-Math.sin(ry)*L*.52,.85,.9,1]);\n"
    " if(KV){mp(KV,c,x,y,z,0,ry,0,L/KL,L/KL,L/KL);COL.push({x:x,z:z,r:2.3});SHB.push([x,z,2.4,2.5]);return}")
rep("  if(it[6]){COL.push({x:x,z:z,r:it[6]});SHB.push([x,z,it[6]*1.2,2])}});mbEnd()}",
    "  if(it[0]==='stall')LAMPS.push([x,ground(x,z)+2.1,z,1,.82,.45]);\n"
    "  if(it[0]==='busstop')LAMPS.push([x,ground(x,z)+2.4,z,.9,.92,.8]);\n"
    "  if(it[6]){COL.push({x:x,z:z,r:it[6]});SHB.push([x,z,it[6]*1.2,2])}});mbEnd()}")
rep("var KITV='1',KIT={},KITM=null,PALMS=[],kitBuilt=false;","var KITV='2',KIT={},KITM=null,PALMS=[],LAMPS=[],HALO=null,SHM=null,kitBuilt=false;")
rep("function buildAll(){if(kitBuilt)return;kitBuilt=true;buildWorld();buildPalms();buildPaths();buildShadows()}",
    "function buildAll(){if(kitBuilt)return;kitBuilt=true;buildWorld();buildPalms();buildPaths();buildShadows();buildHalos();applyTime()}")

# ---- 6. one additive Points for every lamp, headlight and stall glow ----
rep("function buildPalms(){",
    "function buildHalos(){if(!LAMPS.length)return;var c=document.createElement('canvas');c.width=c.height=64;var q=c.getContext('2d');var gr=q.createRadialGradient(32,32,1,32,32,31);\n"
    " gr.addColorStop(0,'rgba(255,255,255,1)');gr.addColorStop(.35,'rgba(255,255,255,.45)');gr.addColorStop(1,'rgba(255,255,255,0)');q.fillStyle=gr;q.fillRect(0,0,64,64);\n"
    " var g=new THREE.BufferGeometry(),ps=[],cs=[];LAMPS.forEach(function(l){ps.push(l[0],l[1],l[2]);cs.push(l[3],l[4],l[5])});\n"
    " g.setAttribute('position',new THREE.Float32BufferAttribute(ps,3));g.setAttribute('color',new THREE.Float32BufferAttribute(cs,3));\n"
    " HALO=new THREE.Points(g,new THREE.PointsMaterial({map:new THREE.CanvasTexture(c),size:3.2,sizeAttenuation:true,vertexColors:true,transparent:true,opacity:0,depthWrite:false,blending:THREE.AdditiveBlending}));\n"
    " HALO.frustumCulled=false;HALO.visible=false;S.add(HALO)}\n"
    "function buildPalms(){")
rep("im.instanceMatrix.needsUpdate=true;S.add(im);\n // contact AO",
    "im.instanceMatrix.needsUpdate=true;S.add(im);SHM=im;\n // contact AO")

# ---- 7. trees keep their base colour so the cycle can dim them ----
rep("TREES.push(sp);", "sp.userData.c0=sp.material.color.clone();TREES.push(sp);")

# ---- 8. the driver ----
rep("var IDLE={t:0,st:'run',bark:0};",
    "// ===== day/night: one scalar drives sky, fog, both lights and the emissive channel =====\n"
    "var DAYLEN=180,SKY={t:.2,night:0,shown:-1,star:''};\n"
    "var DAYP={sun:0xfff6e6,si:1.1,hs:0xfff4e0,hg:0x7a9a6a,hi:.9,fog:0xcfe8f5,a:0xeef8ff,b:0xcfe8f5,c:0xa8d1ea};\n"
    "var NGTP={sun:0xa9c0ea,si:.30,hs:0x3b5682,hg:0x131d2b,hi:.40,fog:0x152438,a:0x27405f,b:0x172a43,c:0x0a1220};\n"
    "var _c1=new THREE.Color(),_c2=new THREE.Color(),_c3=new THREE.Color();\n"
    "(function(){var st=[];for(var i=0;i<26;i++){var x=(7+i*37)%100,y=(11+i*23)%46;st.push('radial-gradient(1.5px 1.5px at '+x+'% '+y+'%, rgba(255,255,255,A), transparent)')}SKY.star=st.join(',')})();\n"
    "function mixHex(h1,h2,k){_c1.setHex(h1);_c2.setHex(h2);return _c1.lerp(_c2,k)}\n"
    "function applySky(){var n=SKY.night;if(Math.abs(n-SKY.shown)<.006)return;SKY.shown=n;\n"
    " sun.color.copy(mixHex(DAYP.sun,NGTP.sun,n));sun.intensity=DAYP.si+(NGTP.si-DAYP.si)*n;\n"
    " hemi.color.copy(mixHex(DAYP.hs,NGTP.hs,n));hemi.groundColor.copy(mixHex(DAYP.hg,NGTP.hg,n));hemi.intensity=DAYP.hi+(NGTP.hi-DAYP.hi)*n;\n"
    " S.fog.color.copy(mixHex(DAYP.fog,NGTP.fog,n));\n"
    " var A=mixHex(DAYP.a,NGTP.a,n).getStyle(),B=mixHex(DAYP.b,NGTP.b,n).getStyle(),C=mixHex(DAYP.c,NGTP.c,n).getStyle();\n"
    " var g='radial-gradient(circle at 50% 18%,'+A+' 0%,'+B+' 45%,'+C+' 100%)';\n"
    " if(n>.25)g=SKY.star.replace(/A/g,(0.75*(n-.25)/.75).toFixed(2))+','+g;   // stars fade in after dusk\n"
    " document.documentElement.style.background=g+' fixed';document.body.style.background='none';\n"
    " NU.n.value=n;NU.cut.value=.62-.18*n;   // more windows switch on as the night deepens\n"
    " if(HALO){HALO.visible=n>.03;HALO.material.opacity=Math.min(1,n*1.25)}\n"
    " if(SHM)SHM.material.opacity=.1-.075*n;\n"
    " for(var i=0;i<TREES.length;i++){var t0=TREES[i];if(t0.userData.c0)t0.material.color.copy(t0.userData.c0).multiplyScalar(1-.55*n)}}\n"
    "function skyStep(dt){var tgt;\n"
    " if(SET.time==='day')tgt=0;else if(SET.time==='night')tgt=1;\n"
    " else{SKY.t=(SKY.t+dt/DAYLEN)%1;var d=.5+.5*Math.cos((SKY.t-.25)*Math.PI*2),u=1-d;tgt=u*u*(3-2*u)}\n"
    " SKY.night+=(tgt-SKY.night)*Math.min(1,dt*(SET.time==='auto'?4:1.8));applySky()}\n"
    "function applyTime(){var b=document.getElementById('mTime');if(b)b.textContent='Time: '+SET.time;SKY.shown=-1;skyStep(0)}\n"
    "var IDLE={t:0,st:'run',bark:0};")
rep(" occl();stuckCheck(dt,manual);tourStep(dt);idleStep(dt,manual);", " skyStep(dt);occl();stuckCheck(dt,manual);tourStep(dt);idleStep(dt,manual);")

# ---- 9. the menu switch, following the mQ quality pattern exactly ----
rep("<button id=\"mQ\">Quality: auto</button>", "<button id=\"mQ\">Quality: auto</button><button id=\"mTime\">Time: auto</button>")
rep("var SET={sound:true,voice:true,music:true,edge:!TOUCH,quality:'auto',seen:false,hat:'auto',view:'auto'};",
    "var SET={sound:true,voice:true,music:true,edge:!TOUCH,quality:'auto',seen:false,hat:'auto',view:'auto',time:'auto'};")
rep("document.getElementById('mQ').onclick=function(){SET.quality=SET.quality==='auto'?'high':SET.quality==='high'?'low':'auto';saveSet();applyQ()};",
    "document.getElementById('mQ').onclick=function(){SET.quality=SET.quality==='auto'?'high':SET.quality==='high'?'low':'auto';saveSet();applyQ()};\n"
    "document.getElementById('mTime').onclick=function(){SET.time=SET.time==='auto'?'day':SET.time==='day'?'night':'auto';saveSet();applyTime()};")

io.open(p, 'w', encoding='utf-8').write(s); print('patch27 applied')
