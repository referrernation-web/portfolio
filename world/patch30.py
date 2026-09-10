# v29: Draco-compressed GLBs (gltf-transform, geometry only - nodes, skins and clips untouched) and
# 1024px character textures. Initial download 4.4 MB -> ~1.6 MB; Eiffel 3.2 MB -> 0.4 MB.
import io
p='index.html'; s=io.open(p,encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    assert s.count(old)==count,('MISSING/AMBIGUOUS',old[:90],s.count(old))
    s=s.replace(old,new)
rep('<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>',
    '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>\n'
    '<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/DRACOLoader.js"></script>')
rep("GL=new THREE.GLTFLoader(),EIF=null;",
    "GL=new THREE.GLTFLoader().setDRACOLoader(new THREE.DRACOLoader().setDecoderPath('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/libs/draco/gltf/')),EIF=null;")
rep("var KITV='2'","var KITV='3'"); rep("var FIGV='26';","var FIGV='27';")
io.open(p,'w',encoding='utf-8').write(s); print('patch30 applied')
