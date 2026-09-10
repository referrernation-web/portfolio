# v30: the wave reads. Mixamo's Waving Gesture is a STANDING clip, so retargeting every bone stood Dianna up on the
# saddle for 1.5 s; blend_retarget.py now takes hips + legs from the seated idle for clips tagged ':upper'. The clip
# is also only 45 frames, so it plays twice.
import io
p='index.html'; s=io.open(p,encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    assert s.count(old)==count,('MISSING/AMBIGUOUS',old[:90],s.count(old))
    s=s.replace(old,new)
rep("if(st==='wave'||st==='talk'){to.setLoop(THREE.LoopOnce,1);to.clampWhenFinished=false;FIG.landmarkHit=false;FIG.idleT=0;FIG.lockT=t+to.getClip().duration}",
    "if(st==='wave'||st==='talk'){var reps=st==='wave'?2:1;to.setLoop(reps>1?THREE.LoopRepeat:THREE.LoopOnce,reps);to.clampWhenFinished=false;FIG.landmarkHit=false;FIG.idleT=0;FIG.lockT=t+to.getClip().duration*reps}")
rep("var FIGV='27';","var FIGV='28';")
io.open(p,'w',encoding='utf-8').write(s); print('patch31 applied')
# (applied inline) landmark models: GL.load('models/'+file  ->  GL.load('models/'+file+'?v='+FIGV
