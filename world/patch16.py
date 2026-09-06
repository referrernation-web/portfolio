# -*- coding: utf-8 -*-
# Real 3D Dianna: Hunyuan3D-2.1 shape from her photo (models/dianna.glb, simplified 537 KB, no UVs) colored by
# front-projecting the same photo onto the mesh as vertex colors. Procedural Dianna stays as fallback.
# Kimpoy stays procedural: the AI shape from his (black-fur) photo came out as a flat slab 3x, no usable depth.
s = open('index.html', encoding='utf-8').read()

def rep(a, b):
    global s
    assert a in s, 'MISSING: ' + a[:80]
    s = s.replace(a, b, 1)

rep("var D=new THREE.Group();D.position.set(0,1.5,-.25);DOG.add(D);",
    "var D=new THREE.Group();D.position.set(0,1.5,-.25);D.userData.dianna=true;DOG.add(D);")

rep("var shadow=new THREE.Mesh(new THREE.CircleGeometry(1.4,16),",
r"""// ===== real 3D Dianna (AI shape from her photo + photo projected as vertex colors); procedural rig = fallback =====
var FIG={dia:null,DIAROT:.35,diaH:1.85,diaY:.95,diaZ:-.3,lean:.12}; // DIAROT verified by screenshot: arms point +z (forward)
function projColors(g,img,y0,y1){var pa=g.attributes.position;g.computeBoundingBox();var b=g.boundingBox,sz=b.getSize(new THREE.Vector3()),c=b.getCenter(new THREE.Vector3());var cv2=document.createElement('canvas');cv2.width=img.width;cv2.height=img.height;var cx=cv2.getContext('2d');cx.drawImage(img,0,0);var px=cx.getImageData(0,0,img.width,img.height).data;var col=new Float32Array(pa.count*3);for(var i=0;i<pa.count;i++){var U=(pa.getX(i)-c.x)/sz.x+.5,V=1-(pa.getY(i)-b.min.y)/sz.y;var ix=Math.max(0,Math.min(img.width-1,Math.round(U*img.width))),iy=Math.max(0,Math.min(img.height-1,Math.round(y0+V*(y1-y0))));var k=(iy*img.width+ix)*4;col[i*3]=px[k]/255;col[i*3+1]=px[k+1]/255;col[i*3+2]=px[k+2]/255}g.setAttribute('color',new THREE.BufferAttribute(col,3))} // ponytail: front projection only, back mirrors the front (hair + jacket back look right anyway)
function loadFigures(){var img=new Image();img.onload=function(){GL.load('models/dianna.glb',function(gl){var o=gl.scene,mesh=null;o.traverse(function(m){if(m.isMesh&&!mesh)mesh=m});if(!mesh)return;
 var g=mesh.geometry;g.rotateY(FIG.DIAROT);g.computeVertexNormals();projColors(g,img,58,512);g.computeBoundingBox();var b=g.boundingBox,sz=b.getSize(new THREE.Vector3()),c=b.getCenter(new THREE.Vector3());var sc=FIG.diaH/sz.y;
 mesh.material=new THREE.MeshStandardMaterial({vertexColors:true,roughness:.85,metalness:0});mesh.castShadow=true;mesh.position.set(-c.x*sc,-b.min.y*sc,-c.z*sc);mesh.scale.setScalar(sc);
 var wrap=new THREE.Group();wrap.position.set(0,FIG.diaY,FIG.diaZ);wrap.rotation.x=FIG.lean;wrap.add(mesh);FIG.dia=wrap;DOG.add(wrap);
 DOG.children.forEach(function(ch){if(ch.userData.dianna)ch.visible=false})},undefined,function(){})};img.src='tex/proj-dianna-fill.jpg'}
loadFigures();
var shadow=new THREE.Mesh(new THREE.CircleGeometry(1.4,16),""")
open('index.html', 'w', encoding='utf-8').write(s)
print('patch16 ok', len(s))
