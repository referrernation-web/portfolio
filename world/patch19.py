# -*- coding: utf-8 -*-
# Dianna moves too: hair sways with the acceleration spring (HS, Bruno's antenna trick), she bobs with the gait,
# arms bounce, slight breathing at idle. Same vertex-shader pseudo-skin approach as Kimpoy (patch18).
s = open('index.html', encoding='utf-8').read()

def rep(a, b):
    global s
    assert a in s, 'MISSING: ' + a[:80]
    s = s.replace(a, b, 1)

rep("function figAnim(sp,run,boost){if(!FIG.kim)return;var u=FIG.u;",
r"""FIG.d={uT:{value:0},uPh:{value:0},uRun:{value:0},uSx:{value:0},uSz:{value:0},uMin:{value:new THREE.Vector3()},uSize:{value:new THREE.Vector3(1,1,1)}};
function diaShader(mat){mat.onBeforeCompile=function(sh){for(var k in FIG.d)sh.uniforms[k]=FIG.d[k];
 sh.vertexShader='uniform float uT,uPh,uRun,uSx,uSz;uniform vec3 uMin,uSize;\n'+sh.vertexShader.replace('#include <begin_vertex>',
 '#include <begin_vertex>\n'+
 'vec3 nn=(position-uMin)/uSize;vec3 p=transformed;float ph=uPh*3.14159;\n'+
 'float hw=smoothstep(.45,.2,nn.z)*smoothstep(.5,.7,nn.y);float hy=(nn.y-.55);\n'+                    // hair: back + upper half
 'p.x+=uSx*.6*hw*hy*uSize.y+sin(uT*3.1+nn.y*6.)*.006*uSize.x*hw;p.z+=uSz*.6*hw*hy*uSize.y;\n'+         // sway with acceleration + soft idle drift
 'float aw=smoothstep(.55,.8,nn.z)*smoothstep(.4,.6,nn.y);p.y+=sin(ph*2.+1.)*.03*uSize.y*uRun*aw;\n'+  // arms bounce with the gait
 'p.y+=sin(ph*2.)*.012*uSize.y*uRun*smoothstep(.3,.6,nn.y);\n'+                                       // body bob
 'float br=(1.-uRun)*.01*sin(uT*2.2);p.x*=1.+br*smoothstep(.35,.5,nn.y)*smoothstep(.8,.65,nn.y);\n'+  // breathing at idle
 'transformed=p;')};mat.needsUpdate=true}
function figAnim(sp,run,boost){if(FIG.dia){var d=FIG.d;d.uT.value=performance.now()/1000;d.uPh.value=P.ft;d.uRun.value=run;d.uSx.value=Math.max(-.6,Math.min(.6,-HS.x*.35));d.uSz.value=Math.max(-.6,Math.min(.6,HS.z*.35))}if(!FIG.kim)return;var u=FIG.u;""")
rep(" GL.load('models/dianna.glb',function(gl){var mesh=figMesh(gl,FIG.diaH,0,0);if(!mesh)return;",
    " GL.load('models/dianna.glb',function(gl){var mesh=figMesh(gl,FIG.diaH,0,0);if(!mesh)return;var bb=mesh.geometry.boundingBox;FIG.d.uMin.value.copy(bb.min);FIG.d.uSize.value.copy(bb.getSize(new THREE.Vector3()));diaShader(mesh.material);")
open('index.html', 'w', encoding='utf-8').write(s)
print('patch19 ok', len(s))
