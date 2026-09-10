# v30a: the Philippine flag beside the Rizal monument (Luneta has the Independence Flagpole right there).
# Blue over red, the white equilateral triangle at the hoist as a 3-sided prism (double-visible, no side flag needed), sun disc.
import io
p='index.html'; s=io.open(p,encoding='utf-8').read()
old="placeModel('rizal.glb',-13,-5,8.5,'h',1.2);"
assert s.count(old)==1
new=old+("var fx=-17.5,fz=-8.5,fy=h0;mp(CY(.09,.12,13,8),0xd8dde0,fx,fy+6.5,fz);mp(SP(.2),0xf2c94c,fx,fy+13.1,fz);"
 "mp(BX(2.6,.65,.04),0x0038a8,fx+1.4,fy+12.3,fz);mp(BX(2.6,.65,.04),0xce1126,fx+1.4,fy+11.65,fz);"      # blue over red, 2:1 flag 2.6 x 1.3
 "mp(CY(.75,.75,.05,3),0xffffff,fx+.47,fy+11.975,fz,Math.PI/2,0,0,1,1,1);"                              # white triangle, base on the hoist
 "mp(CY(.14,.14,.07,12),0xfcd116,fx+.42,fy+11.975,fz,Math.PI/2);")                                     # the sun
s=s.replace(old,new); io.open(p,'w',encoding='utf-8').write(s); print('patch33 applied')

# fix: flag moved out of the granite-textured batch (it came out brick-patterned); triangle rz=pi/2 so the apex points along the fly, sun on the hoist side
