# -*- coding: utf-8 -*-
# Procedural animation for the unrigged AI Kimpoy mesh: a vertex-shader "pseudo-skin" (legs swing in diagonal
# pairs, paws lift, tail wags, head bobs/nods, breathing at idle, legs tuck in the air). Driven by the same
# gait phase (P.ft) the procedural rig used. ponytail: no skeleton, no IK; UniRig/skinning if this stops being enough.
s = open('index.html', encoding='utf-8').read()

def rep(a, b):
    global s
    assert a in s, 'MISSING: ' + a[:80]
    s = s.replace(a, b, 1)

rep("function loadFigures(){",
r"""FIG.u={uT:{value:0},uPh:{value:0},uRun:{value:0},uAir:{value:0},uWag:{value:8},uBoost:{value:0},uMin:{value:new THREE.Vector3()},uSize:{value:new THREE.Vector3(1,1,1)}};
function kimShader(mat){mat.onBeforeCompile=function(sh){for(var k in FIG.u)sh.uniforms[k]=FIG.u[k];
 sh.vertexShader='uniform float uT,uPh,uRun,uAir,uWag,uBoost;uniform vec3 uMin,uSize;\n'+sh.vertexShader.replace('#include <begin_vertex>',
 '#include <begin_vertex>\n'+
 'vec3 nn=(position-uMin)/uSize;vec3 p=transformed;float ph=uPh*3.14159;\n'+
 'float lw=smoothstep(.55,.36,nn.y);float fr=step(.5,nn.z)*2.-1.;float lf=step(.5,nn.x)*2.-1.;float sg=fr*lf;\n'+   // legs: diagonal pairs
 'float sw=mix(sin(ph)*uRun*.5*sg,-.6*fr,uAir);float hip=uMin.y+.55*uSize.y;float dy=p.y-hip;\n'+
 'p.z-=dy*sin(sw)*lw;p.y+=dy*(1.-cos(sw))*lw;\n'+
 'p.y+=max(0.,sin(ph)*sg)*.05*uSize.y*uRun*lw*smoothstep(.35,.0,nn.y);\n'+                                         // paw lift
 'float tw=smoothstep(.22,.02,nn.z)*smoothstep(.35,.5,nn.y);float dz=(uMin.z+.22*uSize.z)-p.z;float wag=sin(uT*uWag)*.75;\n'+
 'p.x+=dz*sin(wag)*tw;p.y+=dz*(.35+.4*uBoost)*tw;\n'+                                                              // tail wag + raised
 'float hw=smoothstep(.62,.8,nn.z)*smoothstep(.4,.55,nn.y);float dzh=p.z-(uMin.z+.62*uSize.z);float nod=sin(ph*2.)*.09*uRun;\n'+
 'p.y+=sin(ph*2.)*.02*uSize.y*uRun*hw-dzh*sin(nod)*hw;\n'+                                                          // head bob + nod
 'float br=(1.-uRun)*.012*sin(uT*2.6);p.x*=1.+br*smoothstep(.2,.4,nn.y)*smoothstep(.85,.6,nn.y);\n'+                // breathing at idle
 'transformed=p;')};mat.needsUpdate=true}
function figAnim(sp,run,boost){if(!FIG.kim)return;var u=FIG.u;u.uT.value=performance.now()/1000;u.uPh.value=P.ft;u.uRun.value=run;u.uAir.value=P.air?1:0;u.uWag.value=sp>.4?7:11;u.uBoost.value=boost?1:0}
function loadFigures(){""")

rep(" GL.load('models/kimpoy.glb',function(gl){var mesh=figMesh(gl,FIG.kimH,FIG.kimY,FIG.kimZ);if(!mesh)return;var wrap=new THREE.Group();wrap.add(mesh);",
    " GL.load('models/kimpoy.glb',function(gl){var mesh=figMesh(gl,FIG.kimH,FIG.kimY,FIG.kimZ);if(!mesh)return;var wrap=new THREE.Group();wrap.add(mesh);var bb=mesh.geometry.boundingBox;FIG.u.uMin.value.copy(bb.min);FIG.u.uSize.value.copy(bb.getSize(new THREE.Vector3()));kimShader(mesh.material);")
rep("var s2=new THREE.Mesh(mesh.geometry,SHELLM);s2.userData.shell=true;",
    "var s2=new THREE.Mesh(mesh.geometry,SHELLM.clone());kimShader(s2.material);s2.userData.shell=true;")
rep(" tail.rotation.z=Math.sin(performance.now()*(sp>.4?.012:.02))*.55;",
    " tail.rotation.z=Math.sin(performance.now()*(sp>.4?.012:.02))*.55;figAnim(sp,run,boost);")
open('index.html', 'w', encoding='utf-8').write(s)
print('patch18 ok', len(s))
