# v25: load the Blender kit (models/kit.glb) and feed its detailed, AO-baked geometry through the
# existing merge batcher, so buildings/props gain real detail at zero extra draw calls.
# Falls back to today's primitives when the kit is missing. Run after patch24.
import io
p = 'index.html'; s = io.open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, ('MISSING/AMBIGUOUS', old[:90], s.count(old))
    s = s.replace(old, new)

# ---- 1. mp(): honour the kit's baked COLOR_0. a=1 -> tint with the palette colour, a=0 -> keep it ----
rep("function mp(g,col,x,y,z,rx,ry,rz,sx,sy,sz){if(g.index)g=g.toNonIndexed();",
    "function mp(g,col,x,y,z,rx,ry,rz,sx,sy,sz){if(g.index)g=g.toNonIndexed();else if(g.userData.kit)g=g.clone();   // kit geometry is reused, applyMatrix4 below mutates\n")
rep(" for(var i=0;i<pa.count;i++){var f=maxY>minY?.8+.2*((ys[i]-minY)/(maxY-minY)):1;MB.p.push(pa.getX(i),pa.getY(i),pa.getZ(i));MB.n.push(na.getX(i),na.getY(i),na.getZ(i));MB.c.push(cc.r*f,cc.g*f,cc.b*f);MB.u.push((pa.getX(i)+pa.getZ(i))*.25,pa.getY(i)*.25)}}",
    " var ka=g.attributes.color,kw=ka&&ka.itemSize>3;\n"
    " for(var i=0;i<pa.count;i++){MB.p.push(pa.getX(i),pa.getY(i),pa.getZ(i));MB.n.push(na.getX(i),na.getY(i),na.getZ(i));\n"
    "  if(ka){var t=kw?ka.getW(i):1,kr=ka.getX(i),kg=ka.getY(i),kb=ka.getZ(i);MB.c.push(kr*(1+t*(cc.r-1)),kg*(1+t*(cc.g-1)),kb*(1+t*(cc.b-1)))}   // Blender-baked AO, tinted only where a=1\n"
    "  else{var f=maxY>minY?.8+.2*((ys[i]-minY)/(maxY-minY)):1;MB.c.push(cc.r*f,cc.g*f,cc.b*f)}\n"
    "  MB.u.push((pa.getX(i)+pa.getZ(i))*.25,pa.getY(i)*.25)}}")

# ---- 2. placeModel(): cache parsed GLBs (pyramid.glb is fetched 4x today) + report failures ----
rep("function placeModel(file,x,z,size,fit,ry,cb){GL.load('models/'+file,function(g){var o=g.scene;",
    "var GCACHE={};\nfunction placeModel(file,x,z,size,fit,ry,cb){function put(src){var o=src.clone(true);")
rep("S.add(o);if(cb)cb(o)})}",
    "S.add(o);if(cb)cb(o)}\n"
    " if(GCACHE[file])return put(GCACHE[file]);\n"
    " GL.load('models/'+file,function(g){GCACHE[file]=g.scene;put(g.scene)},undefined,function(){console.warn('placeModel: models/'+file+' failed to load')})}")

# ---- 3. kit loader + deferred world build (the batches must exist before SHB/AO are consumed) ----
rep("(function build(){\n", "var KITV='1',KIT={},KITM=null,PALMS=[],kitBuilt=false;\n"
    "function buildAll(){if(kitBuilt)return;kitBuilt=true;buildWorld();buildPalms();buildPaths();buildShadows()}\n"
    "function buildWorld(){\n")
rep("\n})();\nfunction lampsAround(", "\n}\nfunction lampsAround(")
rep("(function(){var pts=[];ST.slice(1).forEach(", "function buildPaths(){var pts=[];ST.slice(1).forEach(")
rep(" im.instanceMatrix.needsUpdate=true;S.add(im);})();\n", " im.instanceMatrix.needsUpdate=true;S.add(im);}\n")
rep("(function(){var im=new THREE.InstancedMesh(new THREE.CircleGeometry(1,14)",
    "function buildShadows(){var im=new THREE.InstancedMesh(new THREE.CircleGeometry(1,14)")
rep("mm.rotation.y=Math.random()*3;S.add(mm)}})();",
    "mm.rotation.y=Math.random()*3;S.add(mm)}}\n"
    "// palms are identical, so one InstancedMesh replaces what used to be 7 meshes x 22 calls\n"
    "function buildPalms(){if(!KIT.palm2||!PALMS.length)return;var im=new THREE.InstancedMesh(KIT.palm2,KITM,PALMS.length),m4=new THREE.Matrix4(),q=new THREE.Quaternion(),e=new THREE.Euler(),v=new THREE.Vector3(),sc=new THREE.Vector3();\n"
    " PALMS.forEach(function(p,i){e.set(0,p[3],0);q.setFromEuler(e);v.set(p[0],p[1],p[2]);sc.setScalar(p[4]);m4.compose(v,q,sc);im.setMatrixAt(i,m4)});\n"
    " im.instanceMatrix.needsUpdate=true;im.castShadow=im.receiveShadow=true;im.frustumCulled=false;S.add(im)}\n"
    "KITM=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.9,metalness:0,flatShading:true});\n"
    "GL.load('models/kit.glb?v='+KITV,function(g){g.scene.traverse(function(m){if(m.isMesh){m.geometry.userData.kit=1;KIT[m.name]=m.geometry}});buildAll()},undefined,function(){console.warn('kit.glb missing - procedural fallback');buildAll()});\n"
    "setTimeout(buildAll,3000);   // never let a slow kit keep the world empty")

# ---- 4. builders use the kit when it loaded, today's primitives when it did not ----
rep("function tower(x,z,w,h,c,roofc){var y=ground(x,z);mp(BX(w,h,w),c,x,y+h/2,z);",
    "function kpick(x,z,a){return a[Math.abs(Math.round(x*7+z*13))%a.length]}\n"
    "function tower(x,z,w,h,c,roofc){var y=ground(x,z);var KB=KIT[kpick(x,z,['sky_a','sky_b','sky_c'])];\n"
    " if(KB){mp(KB,c,x,y,z,0,0,0,w/3,h/12,w/3);var KT=KIT[kpick(x+1,z,['sky_top_a','sky_top_b'])];if(KT)mp(KT,c,x,y+h,z,0,0,0,w/3,1,w/3);\n"
    "  mp(BX(w+.34,.14,w+.34),roofc||0x8a1c2b,x,y+h+.36,z);SHB.push([x,z,w*.9,h]);COL.push({x:x,z:z,r:w*.75});return}\n"
    " mp(BX(w,h,w),c,x,y+h/2,z);")
rep("function hut(x,z,ry,sc){sc=sc||1;var y=ground(x,z);mp(BX(2.4*sc,1.6*sc,2.2*sc),0xa9814f,x,y+1.2*sc,z,0,ry);",
    "function hut(x,z,ry,sc){sc=sc||1;var y=ground(x,z);\n"
    " if(KIT.hut2){mp(KIT.hut2,0xffffff,x,y,z,0,ry,0,sc,sc,sc);COL.push({x:x,z:z,r:1.6*sc});SHB.push([x,z,1.8*sc,3*sc]);return}\n"
    " mp(BX(2.4*sc,1.6*sc,2.2*sc),0xa9814f,x,y+1.2*sc,z,0,ry);")
rep("function lamp(x,z){var y=ground(x,z);mp(CY(.06,.09,3.2,6),0x2f3b45,x,y+1.6,z);",
    "function lamp(x,z){var y=ground(x,z);if(KIT.lamp2){mp(KIT.lamp2,0xffffff,x,y,z,0,(x*3+z)%6.28);return}\n"
    " mp(CY(.06,.09,3.2,6),0x2f3b45,x,y+1.6,z);")
rep("function vehicle(x,z,ry,c,len){var y=ground(x,z);var L=len||4.2;mp(BX(L,1.1,2),c,x,y+1.15,z,0,ry);",
    "function vehicle(x,z,ry,c,len){var y=ground(x,z);var L=len||4.2;\n"
    " var KV=L>4.4?KIT.jeep:KIT.car2,KL=L>4.4?5:4;\n"
    " if(KV){mp(KV,c,x,y,z,0,ry,0,L/KL,L/KL,L/KL);COL.push({x:x,z:z,r:2.3});SHB.push([x,z,2.4,2.5]);return}\n"
    " mp(BX(L,1.1,2),c,x,y+1.15,z,0,ry);")
rep("function palm(x,z){var y=ground(x,z);SHB.push([x,z,1.4,5]);",
    "function palm(x,z){var y=ground(x,z);SHB.push([x,z,1.4,5]);\n"
    " if(KIT.palm2){PALMS.push([x,y,z,Math.random()*6.28,.85+Math.random()*.3]);COL.push({x:x,z:z,r:.5});return}\n")

# ---- 5. street dressing: one extra batch per zone, so still one draw call each ----
rep("\nfunction lampsAround(",
    "\nfunction dress(items){var any=items.some(function(it){return KIT[it[0]]});if(!any)return;mbStart();\n"
    " items.forEach(function(it){var g=KIT[it[0]];if(!g)return;var x=it[1],z=it[2];mp(g,it[4]||0xffffff,x,ground(x,z),z,0,it[3]||0,0,it[5]||1,it[5]||1,it[5]||1);\n"
    "  if(it[6]){COL.push({x:x,z:z,r:it[6]});SHB.push([x,z,it[6]*1.2,2])}});mbEnd()}\n"
    "function lampsAround(")
rep(" placeModel('torii.glb',0,-22,7,'h',0);COL.push({x:-2.5,z:-22,r:.6});COL.push({x:2.5,z:-22,r:.6});",
    " placeModel('torii.glb',0,-22,7,'h',0);COL.push({x:-2.5,z:-22,r:.6});COL.push({x:2.5,z:-22,r:.6});\n"
    " // street dressing - Manila and New York, the two zones Mark asked to start with\n"
    " dress([['bench',6,10,1.6],['bench',-7,12,.4],['planter',9,7,0,0,1.1],['planter',-9,7,0,0,1.1],['bollard',11,3,0],['bollard',11,6,0],\n"
    "  ['busstop',-12,14,1.2,0xfbf7f1,1,1.6],['stall',13,-6,-.5,0,1,1.2],['shop_a',-20,-3,1.57,0xe6e2da,1,2.2],['shop_b',-20,3,1.57,0xd8d2c8,1,1.9],\n"
    "  ['mid_a',16,-9,0,0xcfd6dd,1,2.4],['mid_a',-17,-13,.6,0xdedbd3,1,2.4],['car2',8,-14,1.1,0x2f8fd6],['tree2',5,16,0],['tree2',-5,17,0],\n"
    "  ['bench',ST[6].x-4,ST[6].z+6,0],['bench',ST[6].x+4,ST[6].z+6,3.14],['planter',ST[6].x-8,ST[6].z+5,0,0,1.2],['planter',ST[6].x+8,ST[6].z+5,0,0,1.2],\n"
    "  ['busstop',ST[6].x-13,ST[6].z+4,1.57,0xfbf7f1,1,1.6],['bollard',ST[6].x-2,ST[6].z+9,0],['bollard',ST[6].x+2,ST[6].z+9,0],\n"
    "  ['mid_a',ST[6].x-19,ST[6].z-4,0,0x8d99a6,1,2.4],['mid_a',ST[6].x+14,ST[6].z-2,.4,0x9aa6b3,1,2.4],['car2',ST[6].x+7,ST[6].z+12,2.2,0xc0392b]]);")

io.open(p, 'w', encoding='utf-8').write(s); print('patch25 applied')
