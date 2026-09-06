# -*- coding: utf-8 -*-
# Figures v3: Rodin (Regular tier) meshes rigged by UniRig, with bone ROLES detected from bone positions (so any re-rig
# works): legs = lowest chains, tail = rearmost high chain, head = frontmost high chain, arms = widest mid chains.
# Replaces the whole figures block. Pose + gait + rider motion drive roles, not bone numbers.
s = open('index.html', encoding='utf-8').read()
a = s.index('// ===== real 3D figures')
b = s.index('var shadow=new THREE.Mesh(new THREE.CircleGeometry(1.4,16),')
NEW = r"""// ===== real 3D figures (Rodin meshes + UniRig skeletons); roles detected from bone positions; procedural rig = fallback =====
var FIG={kim:null,dia:null,K:null,D:null,hats:null,kimH:2.35,kimY:.05,kimZ:.05,diaH:1.9,diaY:1.22,diaZ:-.45,lean:.08};
var _q1=new THREE.Quaternion(),_q2=new THREE.Quaternion(),_q3=new THREE.Quaternion(),_AX=new THREE.Vector3(1,0,0),_AY=new THREE.Vector3(0,1,0),_AZ=new THREE.Vector3(0,0,1),_m4=new THREE.Matrix4(),_v3=new THREE.Vector3();
function rotW(bone,axis,ang,root){bone.parent.getWorldQuaternion(_q1);root.getWorldQuaternion(_q2);var prel=_q2.invert().multiply(_q1);_q3.setFromAxisAngle(axis,ang);var d=prel.clone().invert().multiply(_q3).multiply(prel);bone.quaternion.copy(d).multiply(bone.userData.rest)}
function boneChains(root){ // normalised bone positions in root space + leaf-to-branch chains
 root.updateMatrixWorld(true);var inv=new THREE.Matrix4().copy(root.matrixWorld).invert(),bones=[];root.traverse(function(x){if(x.isBone){var p=new THREE.Vector3();x.getWorldPosition(p);p.applyMatrix4(inv);x.userData.rest=x.quaternion.clone();x.userData.p=p;bones.push(x)}});
 var bb=new THREE.Box3();bones.forEach(function(x){bb.expandByPoint(x.userData.p)});var sz=bb.getSize(new THREE.Vector3());bones.forEach(function(x){x.userData.n=new THREE.Vector3((x.userData.p.x-bb.min.x)/sz.x,(x.userData.p.y-bb.min.y)/sz.y,(x.userData.p.z-bb.min.z)/sz.z)});
 function kids(x){return x.children.filter(function(c){return c.isBone})}
 var chains=[];bones.forEach(function(x){if(kids(x).length)return;var ch=[x],c=x;while(c.parent&&c.parent.isBone&&kids(c.parent).length===1){c=c.parent;ch.unshift(c)}chains.push(ch)});
 return {bones:bones,chains:chains}}
function dogRoles(root){var R=boneChains(root),ch=R.chains.slice();function leaf(c){return c[c.length-1].userData.n}
 var legs=ch.filter(function(c){return leaf(c).y<.3}).sort(function(p,q){return leaf(p).y-leaf(q).y}).slice(0,4);
 legs.forEach(function(c){var h=c[0].userData.n;c.front=h.z>.5;c.right=h.x>.5});
 var rest=ch.filter(function(c){return legs.indexOf(c)<0});
 var tail=rest.slice().sort(function(p,q){return leaf(p).z-leaf(q).z})[0];                       // rearmost leaf = tail (it may hang low)
 var head=rest.filter(function(c){return c!==tail}).sort(function(p,q){return leaf(q).z-leaf(p).z})[0];   // frontmost leaf = snout
 if(head){head=head.slice();for(var k=0;k<2;k++){var pb=head[0].parent;if(pb&&pb.isBone&&pb.userData.n.y>.45&&pb.userData.n.z>.55)head.unshift(pb);else break}}   // snout chain + head + neck
 var ears=rest.filter(function(c){return c!==tail&&c!==head&&c.length<=3&&leaf(c).y>.6&&leaf(c).z>.5});
 return {legs:legs,tail:tail||[],head:head||[],ears:ears}}
function girlRoles(root){var R=boneChains(root),ch=R.chains.slice();function leaf(c){return c[c.length-1].userData.n}
 var legs=ch.sort(function(p,q){return leaf(p).y-leaf(q).y}).slice(0,2).sort(function(p,q){return leaf(p).x-leaf(q).x});legs.forEach(function(c,i){c.right=i===1});   // left/right by relative x
 var rest=ch.filter(function(c){return legs.indexOf(c)<0});
 var arms=rest.slice().sort(function(p,q){return Math.abs(leaf(q).x-.5)-Math.abs(leaf(p).x-.5)}).slice(0,2).sort(function(p,q){return leaf(p).x-leaf(q).x});arms.forEach(function(c,i){c.right=i===1});   // widest chains = arms (T-pose arms can end higher than the head)
 var head=rest.filter(function(c){return arms.indexOf(c)<0}).sort(function(p,q){return leaf(q).y-leaf(p).y})[0];
 var spine=[];var c=head&&head[0];while(c&&c.parent&&c.parent.isBone){c=c.parent;spine.unshift(c)}
 return {legs:legs,head:head||[],arms:arms,spine:spine}}
function pick(chain,i){return chain[Math.min(chain.length-1,Math.max(0,i))]}
function figAnim(sp,run,boost){var t=performance.now()/1000,ph=P.ft*Math.PI,air=P.air?1:0;
 var K=FIG.K;if(K){var r=FIG.kim,sw=Math.sin(ph)*run*.55,kn=Math.max(0,Math.sin(ph+.6))*run*.5,kn2=Math.max(0,-Math.sin(ph+.6))*run*.5;
  K.legs.forEach(function(c){var same=(c.front===c.right),s1=(same?-1:1)*sw,k=same?kn:kn2,tuck=c.front?-.9:.9; // diagonal pairs; negative X = forward for front legs
   rotW(pick(c,0),_AX,s1*(1-air)+tuck*air,r);rotW(pick(c,1),_AX,-k*.8*(1-air)+tuck*.6*air,r);rotW(pick(c,2),_AX,k*.6*(1-air),r)});
  var wag=Math.sin(t*(sp>.4?7:11))*(.22+.1*(boost?1:0)),lift=-.25-.3*(boost?1:0)-.15*run;
  K.tail.forEach(function(bn,i){rotW(bn,_AY,wag*(1+i*.35),r);bn.quaternion.multiply(_q3.setFromAxisAngle(_AX,lift*.25))});
  if(K.head.length){var hb=pick(K.head,Math.floor(K.head.length/2)),nb=pick(K.head,0);rotW(hb,_AX,Math.sin(ph*2)*.08*run-.15*air+Math.sin(t*.9)*.05*(1-run),r);rotW(nb,_AY,Math.sin(t*.7)*.25*(1-run),r);if(K.head.length>2)rotW(K.head[K.head.length-1],_AX,.12*(boost?1:0),r)}
  K.ears.forEach(function(c){rotW(c[0],_AX,-.3*run+Math.sin(ph*2+1)*.25*run,r)});
  if(FIG.hats&&K.head.length){_m4.copy(DOG.matrixWorld).invert();pick(K.head,Math.floor(K.head.length/2)).getWorldPosition(_v3);_v3.applyMatrix4(_m4);FIG.hats.forEach(function(h){h.position.set(_v3.x+.1,_v3.y+.1,_v3.z+.05)})}}
 var D=FIG.D;if(D){var r2=FIG.dia;if(D.head.length){rotW(pick(D.head,D.head.length-1),_AX,Math.sin(ph*2)*.06*run+Math.sin(t*.8)*.05*(1-run),r2);rotW(pick(D.head,0),_AY,Math.sin(t*.6)*.3*(1-run)+Math.max(-.5,Math.min(.5,HS.x*.3)),r2)}
  var ab=Math.sin(ph*2+1)*.07*run;D.arms.forEach(function(c,i){rotW(pick(c,0),_AX,ab*(i?-.8:1),r2);rotW(pick(c,1),_AX,ab*(i?-.5:.6),r2)});
  if(D.spine.length>1){rotW(D.spine[1],_AZ,Math.max(-.25,Math.min(.25,-HS.x*.25)),r2);rotW(D.spine[D.spine.length-1],_AX,Math.max(-.2,Math.min(.2,HS.z*.2))+(1-run)*.01*Math.sin(t*2.2),r2)}
  D.legs.forEach(function(c,i){rotW(pick(c,1),_AX,Math.sin(ph*2)*.05*run*(i?-1:1),r2)})}
}
function fitRoot(root,h,dy,dz){root.updateMatrixWorld(true);var bb=new THREE.Box3().setFromObject(root),sz=bb.getSize(new THREE.Vector3()),c=bb.getCenter(new THREE.Vector3()),sc=h/sz.y;root.scale.setScalar(sc);root.position.set(-c.x*sc,-bb.min.y*sc+(dy||0),-c.z*sc+(dz||0));root.updateMatrixWorld(true)}
function skinMat(mesh,rough){var old=mesh.material;mesh.material=new THREE.MeshStandardMaterial({map:old.map||null,color:0xffffff,roughness:rough,metalness:0,skinning:true});mesh.castShadow=true;mesh.frustumCulled=false}
function dropArm(c,root){if(!c||!c.length)return;var sh=pick(c,0),hand=c[c.length-1],inv=new THREE.Matrix4(),w=new THREE.Vector3(),best=0,bestY=1e9;
 for(var a=-2.6;a<=2.6;a+=.1){sh.quaternion.copy(sh.userData.rest);rotW(sh,_AZ,a,root);root.updateMatrixWorld(true);inv.copy(root.matrixWorld).invert();hand.getWorldPosition(w);w.applyMatrix4(inv);if(w.y<bestY){bestY=w.y;best=a}}
 sh.quaternion.copy(sh.userData.rest);rotW(sh,_AZ,best,root);sh.userData.rest.copy(sh.quaternion);root.updateMatrixWorld(true)}
function bakePose(list,root){list.forEach(function(p){if(!p[0])return;rotW(p[0],p[1],p[2],root);p[0].userData.rest.copy(p[0].quaternion);root.updateMatrixWorld(true)})}
function loadFigures(){
 GL.load('models/kimpoy-rig.glb',function(gl){var root=gl.scene,mesh=null;root.traverse(function(m){if(m.isSkinnedMesh)mesh=m});if(!mesh)return;
  fitRoot(root,FIG.kimH,FIG.kimY,FIG.kimZ);skinMat(mesh,1.0);var wrap=new THREE.Group();wrap.add(root);DOG.add(wrap);FIG.kim=root;FIG.K=dogRoles(root);
  var hats=Object.keys(HATM).map(function(k){return HATM[k]});FIG.hats=hats;DOG.children.forEach(function(ch){if(ch!==wrap&&!ch.userData.rider&&hats.indexOf(ch)<0&&!ch.userData.dianna)ch.visible=false});   // hide the procedural dog only (never the rider's wrap: load order is a race)
 },undefined,function(){});
 GL.load('models/dianna-rig.glb',function(gl){var root=gl.scene,mesh=null;root.traverse(function(m){if(m.isSkinnedMesh)mesh=m});if(!mesh)return;
  fitRoot(root,FIG.diaH,0,0);skinMat(mesh,.85);var wrap=new THREE.Group();wrap.userData.rider=true;wrap.position.set(0,FIG.diaY,FIG.diaZ);wrap.rotation.x=FIG.lean;wrap.add(root);DOG.add(wrap);FIG.dia=root;var D=girlRoles(root);FIG.D=D;
  // riding pose baked into the rest pose: shoulders forward-down (hands on the fur), elbows bent, legs spread over the flanks, knees back
  D.arms.forEach(function(c){dropArm(c,root)});   // whatever the rest pose (T, raised, waving): search the Z angle that hangs the hand lowest
  bakePose([[pick(D.arms[0]||[],0),_AX,.55],[pick(D.arms[1]||[],0),_AX,.55],[pick(D.arms[0]||[],2),_AX,.4],[pick(D.arms[1]||[],2),_AX,.4],
   [pick(D.legs[0]||[],0),_AZ,D.legs[0]&&D.legs[0].right?-.32:.32],[pick(D.legs[1]||[],0),_AZ,D.legs[1]&&D.legs[1].right?-.32:.32],[pick(D.legs[0]||[],1),_AX,-.7],[pick(D.legs[1]||[],1),_AX,-.7]],root);
  DOG.children.forEach(function(ch){if(ch.userData.dianna)ch.visible=false})},undefined,function(){});
}
loadFigures();
"""
s = s[:a] + NEW + s[b:]
open('index.html', 'w', encoding='utf-8').write(s)
print('patch22 ok', len(s))
