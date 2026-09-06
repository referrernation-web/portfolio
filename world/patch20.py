# -*- coding: utf-8 -*-
# Real skeleton for Kimpoy (UniRig auto-rig: 36 bones, skin weights) + procedural bone animation in three.js:
# diagonal-pair leg swing with knee follow-through, paw tuck in the air, tail wag down a 5-bone chain, head nod/bob,
# ear flap, idle look-around. Replaces the vertex-shader pseudo-skin for Kimpoy (Dianna keeps hers).
s = open('index.html', encoding='utf-8').read()
a = s.index('// ===== real 3D figures: Hunyuan3D-2.1 shapes')
b = s.index('var shadow=new THREE.Mesh(new THREE.CircleGeometry(1.4,16),')
old = s[a:b]
# keep Dianna's shader block and loader from the old text
i0 = old.index('FIG.d={'); i1 = old.index('function figAnim(')
dia_shader = old[i0:i1]
j0 = old.index(" GL.load('models/dianna.glb'"); j1 = old.index('}\nloadFigures();')
dia_loader = old[j0:j1]
NEW = r"""// ===== real 3D figures: Hunyuan3D-2.1 shapes; Kimpoy = UniRig skeleton (36 bones) animated procedurally; Dianna = shader sway =====
var FIG={kim:null,dia:null,B:null,kimH:2.35,kimY:.05,kimZ:.05,diaH:1.8,diaY:1.0,diaZ:-.5,lean:.1};
function figMesh(gl,h,dy,dz){var mesh=null;gl.scene.traverse(function(m){if(m.isMesh&&!mesh)mesh=m});if(!mesh)return null;var g=mesh.geometry;g.computeVertexNormals();g.computeBoundingBox();var bb=g.boundingBox,sz=bb.getSize(new THREE.Vector3()),c=bb.getCenter(new THREE.Vector3()),sc=h/sz.y;
 var old=mesh.material;mesh.material=new THREE.MeshStandardMaterial({vertexColors:!!g.attributes.color,map:old.map||null,color:0xffffff,roughness:.95,metalness:0});mesh.castShadow=true;mesh.position.set(-c.x*sc,-bb.min.y*sc+(dy||0),-c.z*sc+(dz||0));mesh.scale.setScalar(sc);return mesh}
""" + dia_shader + r"""// --- Kimpoy skeleton: bone names from UniRig (verified by screenshot): spine 0-3, neck 4, head 5, snout 6, ears 7/9,
// legs FR 11-15, FL 16-20, BR 21-25, BL 26-30, tail 31-35. rotW() rotates a bone about a model-space axis.
var _q1=new THREE.Quaternion(),_q2=new THREE.Quaternion(),_q3=new THREE.Quaternion(),_AX=new THREE.Vector3(1,0,0),_AY=new THREE.Vector3(0,1,0);
function rotW(bone,axis,ang){bone.parent.getWorldQuaternion(_q1);FIG.kim.getWorldQuaternion(_q2);var prel=_q2.invert().multiply(_q1);_q3.setFromAxisAngle(axis,ang);var d=prel.clone().invert().multiply(_q3).multiply(prel);bone.quaternion.copy(d).multiply(bone.userData.rest)}
function figAnim(sp,run,boost){if(FIG.dia){var d=FIG.d;d.uT.value=performance.now()/1000;d.uPh.value=P.ft;d.uRun.value=run;d.uSx.value=Math.max(-.6,Math.min(.6,-HS.x*.35));d.uSz.value=Math.max(-.6,Math.min(.6,HS.z*.35))}
 var B=FIG.B;if(!B)return;var t=performance.now()/1000,ph=P.ft*Math.PI,air=P.air?1:0;
 var sw=Math.sin(ph)*run*.55,kn=Math.max(0,Math.sin(ph+.6))*run*.5,kn2=Math.max(0,-Math.sin(ph+.6))*run*.5;
 // diagonal pairs: FR + BL swing together, FL + BR opposite; negative X = forward for front legs
 var legs=[['bone_11','bone_12','bone_13',-1,-.9],['bone_26','bone_27','bone_28',-1,.9],['bone_16','bone_17','bone_18',1,-.9],['bone_21','bone_22','bone_23',1,.9]];
 for(var i=0;i<4;i++){var L=legs[i],s1=L[3]*sw,k=L[3]>0?kn2:kn,up=(i<1||i===2)?-.55:.55;rotW(B[L[0]],_AX,s1*(1-air)+L[4]*air);rotW(B[L[1]],_AX,(-k*.8+up*.3*run)*(1-air)+L[4]*.6*air);rotW(B[L[2]],_AX,k*.6*(1-air))}
 var wag=Math.sin(t*(sp>.4?7:11))*(.22+.1*(boost?1:0)),lift=-.25-.3*(boost?1:0)-.15*run;
 ['bone_31','bone_32','bone_33','bone_34','bone_35'].forEach(function(n,i){rotW(B[n],_AY,wag*(1+i*.35));B[n].quaternion.multiply(_q3.setFromAxisAngle(_AX,lift*.25))});   // tail: wag sideways, held up
 rotW(B.bone_5,_AX,Math.sin(ph*2)*.08*run-.15*air+Math.sin(t*.9)*.05*(1-run));rotW(B.bone_4,_AY,Math.sin(t*.7)*.25*(1-run));   // head nod with the gait, look around when idle
 rotW(B.bone_7,_AX,-.3*run+Math.sin(ph*2+1)*.25*run);rotW(B.bone_9,_AX,-.3*run+Math.sin(ph*2+1)*.25*run);                        // ears fold back with speed, flap with the gait
 rotW(B.bone_6,_AX,.12*(boost?1:0));                                                                                              // mouth opens a bit on boost
}
function loadFigures(){
 GL.load('models/kimpoy-rig.glb',function(gl){var root=gl.scene,mesh=null;root.traverse(function(m){if(m.isSkinnedMesh)mesh=m});if(!mesh)return;
  root.updateMatrixWorld(true);var bb=new THREE.Box3().setFromObject(root),sz=bb.getSize(new THREE.Vector3()),c=bb.getCenter(new THREE.Vector3()),sc=FIG.kimH/sz.y;
  root.scale.setScalar(sc);root.position.set(-c.x*sc,-bb.min.y*sc+FIG.kimY,-c.z*sc+FIG.kimZ);
  var old=mesh.material;mesh.material=new THREE.MeshStandardMaterial({vertexColors:!!mesh.geometry.attributes.color,map:old.map||null,color:0xffffff,roughness:.95,metalness:0,skinning:true});mesh.castShadow=true;mesh.frustumCulled=false;
  var shell=new THREE.SkinnedMesh(mesh.geometry,SHELLM.clone());shell.material.skinning=true;shell.userData.shell=true;shell.frustumCulled=false;shell.scale.setScalar(1.03);mesh.parent.add(shell);shell.bind(mesh.skeleton,mesh.bindMatrix); // fur shell rides the same skeleton
  var B={};root.traverse(function(x){if(x.isBone){B[x.name]=x;x.userData.rest=x.quaternion.clone()}});FIG.B=B;
  var hats=Object.keys(HATM).map(function(k){return HATM[k]});DOG.children.forEach(function(ch){if(ch!==FIG.dia&&hats.indexOf(ch)<0&&!ch.userData.dianna)ch.visible=false});
  FIG.kim=root;DOG.add(root);
 },undefined,function(){});
""" + dia_loader + """}
loadFigures();
"""
s = s[:a] + NEW + s[b:]
open('index.html', 'w', encoding='utf-8').write(s)
assert 'kimShader' not in s
print('patch20 ok', len(s))
