# -*- coding: utf-8 -*-
# Dianna on her own UniRig skeleton (24 bones): head look/nod, arm bob, spine sway driven from the gait, replacing the
# vertex-shader sway. Kimpoy untouched. rotW() gains a root parameter.
s = open('index.html', encoding='utf-8').read()
def rep(a, b):
    global s
    assert a in s, 'MISSING: ' + a[:90]
    s = s.replace(a, b, 1)
rep("function rotW(bone,axis,ang){bone.parent.getWorldQuaternion(_q1);FIG.kim.getWorldQuaternion(_q2);",
    "function rotW(bone,axis,ang,root){bone.parent.getWorldQuaternion(_q1);(root||FIG.kim).getWorldQuaternion(_q2);")
# Dianna loader: skinned mesh + bones
a = s.index(" GL.load('models/dianna.glb',function(gl){")
b = s.index("},undefined,function(){});", a) + len("},undefined,function(){});")
s = s[:a] + r""" GL.load('models/dianna-rig.glb',function(gl){var root=gl.scene,mesh=null;root.traverse(function(m){if(m.isSkinnedMesh)mesh=m});if(!mesh)return;
  root.updateMatrixWorld(true);var bb=new THREE.Box3().setFromObject(root),sz=bb.getSize(new THREE.Vector3()),c=bb.getCenter(new THREE.Vector3()),sc=FIG.diaH/sz.y;
  root.scale.setScalar(sc);root.position.set(-c.x*sc,-bb.min.y*sc,-c.z*sc);
  var old=mesh.material;mesh.material=new THREE.MeshStandardMaterial({map:old.map||null,color:0xffffff,roughness:.9,metalness:0,skinning:true});mesh.castShadow=true;mesh.frustumCulled=false;
  var B={};root.traverse(function(x){if(x.isBone){B[x.name]=x;x.userData.rest=x.quaternion.clone()}});FIG.dB=B;
  var wrap=new THREE.Group();wrap.position.set(0,FIG.diaY,FIG.diaZ);wrap.rotation.x=FIG.lean;wrap.rotation.y=Math.PI;wrap.add(root);FIG.dia=wrap;DOG.add(wrap);
  DOG.children.forEach(function(ch){if(ch.userData.dianna)ch.visible=false})},undefined,function(){});""" + s[b:]
# animation: replace the shader uniform update with bone motion
rep("function figAnim(sp,run,boost){if(FIG.dia){var d=FIG.d;d.uT.value=performance.now()/1000;d.uPh.value=P.ft;d.uRun.value=run;d.uSx.value=Math.max(-.6,Math.min(.6,-HS.x*.35));d.uSz.value=Math.max(-.6,Math.min(.6,HS.z*.35))}",
    r"""function figAnim(sp,run,boost){if(FIG.dB){var D=FIG.dB,r=FIG.dia,t2=performance.now()/1000,ph2=P.ft*Math.PI;
  // Dianna bones (UniRig): spine 0-3, neck 4, head 5, arms 6-10 / 11-15, legs 16-19 / 20-23. Small, safe rotations.
  rotW(D.bone_5,_AX,Math.sin(ph2*2)*.06*run+Math.sin(t2*.8)*.05*(1-run),r);rotW(D.bone_4,_AY,Math.sin(t2*.6)*.3*(1-run)+Math.max(-.5,Math.min(.5,HS.x*.3)),r);   // head: nod with the gait, look around at idle, turn into the lean
  var ab=Math.sin(ph2*2+1)*.07*run;rotW(D.bone_6,_AX,ab,r);rotW(D.bone_11,_AX,-ab*.8,r);rotW(D.bone_7,_AX,ab*.6,r);rotW(D.bone_12,_AX,-ab*.5,r);          // arms bob with the gait
  rotW(D.bone_2,new THREE.Vector3(0,0,1),Math.max(-.25,Math.min(.25,-HS.x*.25)),r);rotW(D.bone_3,_AX,Math.max(-.2,Math.min(.2,HS.z*.2))+(1-run)*.01*Math.sin(t2*2.2),r);   // spine: sway with acceleration, breathe at idle
  rotW(D.bone_17,_AX,Math.sin(ph2*2)*.05*run,r);rotW(D.bone_21,_AX,-Math.sin(ph2*2)*.05*run,r)}   // legs dangle
 if(FIG.dia){var d=FIG.d;d.uT.value=performance.now()/1000;d.uPh.value=P.ft;d.uRun.value=run}""")
open('index.html', 'w', encoding='utf-8').write(s)
print('patch21 ok', len(s))
