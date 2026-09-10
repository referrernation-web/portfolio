# v30: three hero landmarks that were boxes/blobs are now Rodin text-to-3D meshes (Regular tier, slimmed to
# base colour 1024px + Draco): Statue of Liberty 92 KB blob -> 237 KB real statue on the star fort,
# Sphinx six boxes -> 187 KB, Rizal monument four primitives -> 223 KB obelisk with the bronze.
import io
p='index.html'; s=io.open(p,encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    assert s.count(old)==count,('MISSING/AMBIGUOUS',old[:90],s.count(old))
    s=s.replace(old,new)
# Sphinx: the model's front is +Z; it faces WEST toward the pyramids and the arriving rider (the old boxes faced east, so visitors met its rump)
rep("mp(BX(5.5,2.2,2.2),0xd9a86a,qx,qy+1.1,qz);mp(BX(2.2,.9,.9),0xd9a86a,qx+2.6,qy+.45,qz-.7);mp(BX(2.2,.9,.9),0xd9a86a,qx+2.6,qy+.45,qz+.7);mp(BX(1.6,1.9,2.2),0xd9a86a,qx+2.4,qy+2.9,qz);mp(BX(1.5,1.6,1.5),0xe0b97a,qx+2.9,qy+3.1,qz);mp(BX(.9,.3,1.3),0x8a6a3a,qx+3.6,qy+3.1,qz);",
    "placeModel('sphinx.glb',qx+1,qz,8,'w',-Math.PI/2);")
# Rizal: keep the granite plinth in the batch, the Rodin monument stands on it facing the plaza
rep("mp(BX(3,.6,3),0x9aa5a0,-13,h0+.3,-5);mp(BX(1.2,5,1.2),0xbfc7c2,-13,h0+2.8,-5,0,0,0,1,1,1);mp(CY(.35,.35,1.6,7),0x3a3f44,-13,h0+6.1,-5);mp(SP(.35),0x3a3f44,-13,h0+7.2,-5);",
    "mp(BX(4.5,.25,4.5),0x9aa5a0,-13,h0+.125,-5);placeModel('rizal.glb',-13,-5,8.5,'h',1.2);")
# Liberty's star fort is wider than the old blob
rep("SHB.push([s.x,s.z,3.6,16]);COL.push({x:s.x,z:s.z,r:3.8});","SHB.push([s.x,s.z,5,16]);COL.push({x:s.x,z:s.z,r:5.2});")
rep("Lady Liberty by Anna M (CC-BY 3.0), ","Statue of Liberty, Sphinx and Rizal Monument generated with Hyper3D Rodin, ")
io.open(p,'w',encoding='utf-8').write(s); print('patch32 applied')
