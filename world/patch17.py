# -*- coding: utf-8 -*-
# Real 3D figures v2: both GLBs now carry BAKED vertex colours (bake.py: Kimpoy = multi-view Hunyuan3D shape +
# his real face/fur from Mark's videos; Dianna = shape + the Pragmata Diana render). Runtime just loads them.
# Procedural rig stays as fallback. Replaces the patch16 runtime-projection block.
s = open('index.html', encoding='utf-8').read()

def rep(a, b):
    global s
    assert a in s, 'MISSING: ' + a[:80]
    s = s.replace(a, b, 1)

# tag procedural body parts to hide when the real Kimpoy loads (legs, tail, tongue keep animating)
rep(" shell(fs(.62,0,1.05,0,1.05,.95,1.55),2);           // body",
    " DOG.userData.bodyStart=DOG.children.length;shell(fs(.62,0,1.05,0,1.05,.95,1.55),2);           // body")
rep(" TONGUE=bx(.22,.08,.3,0xd2546e,0,1.3,1.5);           // tongue (shows on boost)",
    " DOG.userData.bodyEnd=DOG.children.length;TONGUE=bx(.22,.08,.3,0xd2546e,0,1.3,1.5);           // tongue (shows on boost)")

rep(" var SHELLM=new THREE.MeshStandardMaterial({map:TEX('fur-shell.png',2.4)", " var SHELLM=window.SHELLM=new THREE.MeshStandardMaterial({map:TEX('fur-shell.png',2.4)")  # expose the fur-shell material to the loader
a = s.index('// ===== real 3D Dianna (AI shape')
b = s.index('var shadow=new THREE.Mesh(new THREE.CircleGeometry(1.4,16),')
NEW = r"""// ===== real 3D figures: Hunyuan3D-2.1 shapes with baked vertex colours (world/bake.py); procedural rig = fallback =====
var FIG={kim:null,dia:null,kimH:2.35,kimY:.05,kimZ:.05,diaH:1.8,diaY:1.0,diaZ:-.5,lean:.1};
function figMesh(gl,h,dy,dz){var mesh=null;gl.scene.traverse(function(m){if(m.isMesh&&!mesh)mesh=m});if(!mesh)return null;var g=mesh.geometry;g.computeVertexNormals();g.computeBoundingBox();var bb=g.boundingBox,sz=bb.getSize(new THREE.Vector3()),c=bb.getCenter(new THREE.Vector3()),sc=h/sz.y;
 mesh.material=new THREE.MeshStandardMaterial({vertexColors:!!g.attributes.color,color:0xffffff,roughness:.95,metalness:0});mesh.castShadow=true;mesh.position.set(-c.x*sc,-bb.min.y*sc+(dy||0),-c.z*sc+(dz||0));mesh.scale.setScalar(sc);return mesh}
function loadFigures(){
 GL.load('models/kimpoy.glb',function(gl){var mesh=figMesh(gl,FIG.kimH,FIG.kimY,FIG.kimZ);if(!mesh)return;var wrap=new THREE.Group();wrap.add(mesh);
  for(var i=1;i<=2;i++){var s2=new THREE.Mesh(mesh.geometry,SHELLM);s2.userData.shell=true;s2.position.copy(mesh.position);s2.scale.copy(mesh.scale).multiplyScalar(1+i*.03);wrap.add(s2)} // fur shells on the real mesh
  FIG.kim=wrap;DOG.add(wrap);var ch=DOG.children;for(var i=DOG.userData.bodyStart;i<DOG.userData.bodyEnd;i++)ch[i].visible=false; // hide procedural body/mane/head/ears
 },undefined,function(){});
 GL.load('models/dianna.glb',function(gl){var mesh=figMesh(gl,FIG.diaH,0,0);if(!mesh)return;var wrap=new THREE.Group();wrap.position.set(0,FIG.diaY,FIG.diaZ);wrap.rotation.x=FIG.lean;wrap.add(mesh);FIG.dia=wrap;DOG.add(wrap);
  DOG.children.forEach(function(ch){if(ch.userData.dianna)ch.visible=false})},undefined,function(){});
}
loadFigures();
"""
s = s[:a] + NEW + s[b:]
open('index.html', 'w', encoding='utf-8').write(s)
assert 'projColors' not in s
print('patch17 ok', len(s))
