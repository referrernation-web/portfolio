# v23: mount attachment the way games do it — seat on Kimpoy's spine bone, harness prop, CCD IK for hands (grips) and feet (stirrups)
import re,io
p='index.html'; s=io.open(p,encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    assert s.count(old)==count, ('MISSING/AMBIGUOUS', old[:80], s.count(old))
    s=s.replace(old,new)

# A. CCDIKSolver (ships with three r128, examples/js) — zero new dependencies
rep('<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>',
    '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>\n<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/animation/CCDIKSolver.js"></script>')

# B. state
rep("var FIG={kim:null,dia:null,K:null,D:null,hats:null,kimH:2.35,kimY:.05,kimZ:.05,diaH:1.9,diaY:1.22,diaZ:-.45,lean:.08};",
    "var FIG={kim:null,dia:null,K:null,D:null,hats:null,kimH:2.35,kimY:.05,kimZ:.05,diaH:1.9,diaY:1.22,diaZ:-.45,lean:.08,seat:null,onSeat:false,diaYs:0,diaZs:0,targets:null,ik:null,ikc:null,wv:0,pat:0};")

# C. Kimpoy spine role (parents of the head chain up to the skeleton root) -> mount bone = last one (mid-spine)
rep(" return {legs:legs,tail:tail||[],head:head||[],ears:ears}}",
    " var spine=[];var sc=head&&head[0];while(sc&&sc.parent&&sc.parent.isBone){sc=sc.parent;spine.unshift(sc)}\n return {legs:legs,tail:tail||[],head:head||[],ears:ears,spine:spine}}")

# D. rider wrap: seat-relative offsets once mounted
rep("var wr=FIG.dia.parent;wr.position.y=FIG.diaY+bob;",
    "var wr=FIG.dia.parent;wr.position.y=(FIG.onSeat?FIG.diaYs:FIG.diaY)+bob;if(FIG.onSeat)wr.position.z=FIG.diaZs;")

# E. gallop flexes the spine bones (the seat rides on bone_1, so Dianna moves WITH the back, not above it)
rep("  if(K.head.length>1){rotW(K.head[0],_AX,-Math.sin(cyc*Math.PI*2)*.18*gallop*run,r)}   // neck dips with the gallop",
    "  if(K.head.length>1){rotW(K.head[0],_AX,-Math.sin(cyc*Math.PI*2)*.18*gallop*run,r)}   // neck dips with the gallop\n  if(K.spine)K.spine.forEach(function(b,i){rotW(b,_AX,Math.sin(cyc*Math.PI*2+.4)*.06*(i+1)*gallop*run+Math.sin(ph)*.02*run,r)});   // back flexes with the gallop (rider sits on this bone)")

# F. expose wave/pat so the IK can let go of the handle during gestures
rep("   if(D.spine.length>1){rotW(D.spine[1],_AZ,Math.sin(it*.9)*.04*(1-run),r2)}   // weight shift   // arms fly up in the air",
    "   FIG.wv=wv;FIG.pat=pat;if(D.spine.length>1){rotW(D.spine[1],_AZ,Math.sin(it*.9)*.04*(1-run),r2)}   // weight shift")

# G. IK last (rotW resets bones from rest every frame; CCD then pins hands to the grips and feet to the stirrups)
rep("  D.legs.forEach(function(c,i){rotW(pick(c,1),_AX,Math.sin(ph*2)*.05*run*(i?-1:1)+air*.4,r2)})}}   // legs swing back in the air (procedural only when there are no clips)\n}",
    "  D.legs.forEach(function(c,i){rotW(pick(c,1),_AX,Math.sin(ph*2)*.05*run*(i?-1:1)+air*.4,r2)})}}   // legs swing back in the air (procedural only when there are no clips)\n"
    " if(FIG.ik){var I=FIG.ikc,hold=!P.air;if(I.armL)I.armL.links[0].enabled=hold&&!(FIG.pat>0);if(I.armR)I.armR.links[0].enabled=hold&&!(FIG.wv>0);if(I.legL)I.legL.links[0].enabled=hold;if(I.legR)I.legR.links[0].enabled=hold;DOG.updateMatrixWorld(true);FIG.ik.update()}   // contact constraints: hands on the handle, feet in the stirrups (off in the air / while waving or patting)\n}")

# H. seat + harness + attach
rep("function loadFigures(){",
'''// ===== mount point: a seat Object3D attached to Kimpoy's mid-spine bone (like a saddle bone in games); harness prop + IK targets hang off it =====
function makeSeat(root,mesh){DOG.updateMatrixWorld(true);var inv=new THREE.Matrix4().copy(DOG.matrixWorld).invert(),pos=mesh.geometry.attributes.position,v=new THREE.Vector3(),top=-1e9,cTop=-1e9,cBot=1e9,cW=0,fW=0;
 for(var i=0;i<pos.count;i++){v.fromBufferAttribute(pos,i);mesh.localToWorld(v);v.applyMatrix4(inv);   // rest pose = bind pose, so vertex -> world is exact
  if(Math.abs(v.x)<.12&&v.z>-.3&&v.z<.1&&v.y>top)top=v.y;
  if(v.z>.4&&v.z<.5){if(Math.abs(v.x)<.15){if(v.y>cTop)cTop=v.y;if(v.y<cBot)cBot=v.y}if(v.y>1.0&&v.y<1.9&&Math.abs(v.x)>cW)cW=Math.abs(v.x)}
  if(v.z>-.2&&v.z<0&&v.y>1.0&&v.y<1.9&&Math.abs(v.x)>fW)fW=Math.abs(v.x)}
 var K=FIG.K,mount=(K.spine&&K.spine.length)?K.spine[K.spine.length-1]:(K.head[0]&&K.head[0].parent);var seat=new THREE.Object3D();seat.position.set(0,top,-.1);DOG.add(seat);DOG.updateMatrixWorld(true);if(mount&&mount.isBone)mount.attach(seat);   // attach() keeps the world pose (undoes the bone's rotation/scale)
 FIG.seat=seat;FIG.seatTop=top;FIG.seatM={top:top,cTop:cTop,cBot:cBot,cW:cW,fW:fW};makeHarness(seat,FIG.seatM)}
function makeHarness(seat,m){var lea=mat(0x2a2118),met=mat(0xb8b8b8);
 var pad=new THREE.Mesh(new THREE.SphereGeometry(1,20,12),mat(0x8a1c2b));pad.scale.set(.5,.11,.46);pad.position.set(0,-.06,.02);seat.add(pad);   // saddle cushion, sunk into the fur
 var arch=new THREE.Mesh(new THREE.TorusGeometry(.12,.024,8,18,Math.PI),lea);arch.position.set(0,.27,.40);seat.add(arch);   // grab handle
 [-1,1].forEach(function(sg){var post=new THREE.Mesh(new THREE.CylinderGeometry(.024,.024,.29,8),lea);post.position.set(sg*.12,.13,.40);seat.add(post)});
 var strap=new THREE.Mesh(new THREE.TorusGeometry(.6,.022,8,28),lea);strap.scale.set((m.cW+.02)/.6,((m.cTop-m.cBot)/2+.02)/.6,1);strap.position.set(0,(m.cTop+m.cBot)/2-m.top,.55);seat.add(strap);   // chest strap behind the front legs
 var T={};[-1,1].forEach(function(sg){var g=new THREE.Bone();g.position.set(sg*.11,.33,.40);seat.add(g);T[sg<0?'gripL':'gripR']=g;
  var x=sg*(m.fW+.05),y=-.5;var st=new THREE.Mesh(new THREE.TorusGeometry(.07,.012,6,14),met);st.rotation.y=Math.PI/2;st.position.set(x,y,-.05);seat.add(st);   // stirrup
  var sb=new THREE.Mesh(new THREE.BoxGeometry(.02,-y-.07,.06),lea);sb.position.set(x,y/2,-.05);seat.add(sb);var sbone=new THREE.Bone();sbone.position.set(x,y+.02,-.05);seat.add(sbone);T[sg<0?'stirL':'stirR']=sbone});
 FIG.targets=T}
function attachRider(){if(!FIG.seat||!FIG.dia||FIG.onSeat)return;var wr=FIG.dia.parent,seat=FIG.seat,D=FIG.D;seat.add(wr);wr.position.set(0,0,0);wr.rotation.set(FIG.lean,0,0);DOG.updateMatrixWorld(true);
 var hip=D.spine[0]||FIG.dia,hp=seat.worldToLocal(hip.getWorldPosition(new THREE.Vector3()));wr.position.y=-(hp.y-.08);wr.position.z=-hp.z;FIG.diaYs=wr.position.y;FIG.diaZs=wr.position.z;FIG.onSeat=true;DOG.updateMatrixWorld(true);   // hips on the cushion
 if(!THREE.CCDIKSolver||!FIG.targets)return;var sm=FIG.dia.getObjectByProperty('type','SkinnedMesh'),bones=sm.skeleton.bones.slice(),T=FIG.targets;function ix(b){var i=bones.indexOf(b);if(i<0){bones.push(b);i=bones.length-1}return i}
 function chain(c,eff,li,target){return {target:ix(target),effector:ix(pick(c,eff)),links:li.map(function(k){return {index:ix(pick(c,k))}}),iteration:10}}
 var iks={};if(D.arms[0])iks.armL=chain(D.arms[0],5,[3,2,1,0],T.gripL);if(D.arms[1])iks.armR=chain(D.arms[1],5,[3,2,1,0],T.gripR);if(D.legs[0])iks.legL=chain(D.legs[0],2,[1,0],T.stirL);if(D.legs[1])iks.legR=chain(D.legs[1],2,[1,0],T.stirR);
 var list=Object.keys(iks).map(function(k){return iks[k]});FIG.ikc=iks;FIG.ik=new THREE.CCDIKSolver({skeleton:{bones:bones}},list);   // the solver only reads mesh.skeleton.bones, so targets can live on Kimpoy's seat
 list.forEach(function(k){k.iteration=80});FIG.ik.update();list.forEach(function(k){k.iteration=10;k.links.forEach(function(l){var b=bones[l.index];b.userData.rest.copy(b.quaternion)})})}   // solve once hard, bake as rest so each frame starts next to the answer
function loadFigures(){''')

# I. Kimpoy loader: build the seat, then mount the rider if she is already there
rep("var wrap=new THREE.Group();wrap.add(root);DOG.add(wrap);FIG.kim=root;FIG.K=dogRoles(root);",
    "var wrap=new THREE.Group();wrap.add(root);DOG.add(wrap);FIG.kim=root;FIG.K=dogRoles(root);makeSeat(root,mesh);")
rep("ch.visible=false});   // hide the procedural dog only (never the rider's wrap: load order is a race)\n },undefined,function(){});",
    "ch.visible=false});   // hide the procedural dog only (never the rider's wrap: load order is a race)\n  attachRider()},undefined,function(){});")

# J. Dianna: legs spread wide enough to clear the flank (knees outside x +-0.42), knees bent; arms only get a starting pose (IK finishes them)
rep("[pick(D.legs[0]||[],0),_AZ,D.legs[0]&&D.legs[0].right?-.32:.32],[pick(D.legs[1]||[],0),_AZ,D.legs[1]&&D.legs[1].right?-.32:.32],[pick(D.legs[0]||[],1),_AX,-.7],[pick(D.legs[1]||[],1),_AX,-.7]],root)}",
    "[pick(D.legs[0]||[],0),_AZ,D.legs[0]&&D.legs[0].right?-.6:.6],[pick(D.legs[1]||[],0),_AZ,D.legs[1]&&D.legs[1].right?-.6:.6],[pick(D.legs[0]||[],1),_AX,-1.1],[pick(D.legs[1]||[],1),_AX,-1.1]],root)}")
rep("  DOG.children.forEach(function(ch){if(ch.userData.dianna)ch.visible=false})}",
    "  DOG.children.forEach(function(ch){if(ch.userData.dianna)ch.visible=false});attachRider()}")

io.open(p,'w',encoding='utf-8').write(s); print('patch23 applied')
