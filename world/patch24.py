# v24: dismount / walk / whistle / remount + ground clamp for the dog (sleep only when parked). Run after patch23.
import io
p='index.html'; s=io.open(p,encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    assert s.count(old)==count,('MISSING/AMBIGUOUS',old[:90],s.count(old)); s=s.replace(old,new)

# ---- figAnim reads a motion object M (P when ridden, KIM when Kimpoy moves on his own) ----
a=s.index('function figAnim(sp,run,boost){'); b=s.index('\nfunction fitRoot(')
body=s[a:b].replace('P.','M.')
body=body.replace('function figAnim(sp,run,boost){','function figAnim(sp,run,boost,M){M=M||P;',1)
s=s[:a]+body+s[b:]
rep("if(FIG.dia&&FIG.dia.parent){var wr=FIG.dia.parent;wr.position.y=(FIG.onSeat?FIG.diaYs:FIG.diaY)+bob;",
    "if(FIG.dia&&FIG.dia.parent&&RIDE.on){var wr=FIG.dia.parent;wr.position.y=(FIG.onSeat?FIG.diaYs:FIG.diaY)+bob;")
rep(" var D=FIG.D;if(D){var r2=FIG.dia;"," var D=FIG.D;if(D){if(RIDE.on){var r2=FIG.dia;")
rep("+air*.4,r2)})}}   // legs swing back in the air","+air*.4,r2)})}}else{walkAnim(D,FIG.dia,t,dt,ph)}}   // legs swing back in the air")
rep(" if(FIG.ik){var I=FIG.ikc,hold=!M.air;"," if(FIG.ik&&RIDE.on){var I=FIG.ikc,hold=!M.air;")

# ---- rest poses: keep the T-pose rest (rest0) so a standing pose can be rebuilt ----
rep("x.userData.rest=x.quaternion.clone();","x.userData.rest=x.quaternion.clone();x.userData.rest0=x.quaternion.clone();")
rep("list.forEach(function(k){k.iteration=10;k.links.forEach(function(l){var b=bones[l.index];b.userData.rest.copy(b.quaternion)})})}   // solve once hard",
    "list.forEach(function(k){k.iteration=10;k.links.forEach(function(l){var b=bones[l.index];b.userData.rest.copy(b.quaternion)})});saveRests(D,FIG.dia)}   // solve once hard")

# ---- main loop ----
rep("tail.rotation.z=Math.sin(performance.now()*(sp>.4?.012:.02))*.55;figAnim(sp,run,boost);",
    "tail.rotation.z=Math.sin(performance.now()*(sp>.4?.012:.02))*.55;rideStep(dt);figAnim(RIDE.on?sp:KIM.speed,RIDE.on?run:Math.min(1,KIM.speed/8),RIDE.on&&boost,RIDE.on?P:KIM);")
rep(" DOG.position.y=(P.air?0:Math.abs(Math.sin(P.ft*Math.PI))*.16*run)-(g<1.02&&!P.air?.55:0);\n DOG.rotation.x=P.air?0:Math.sin(P.ft*Math.PI*2)*.06*run;",
    " if(RIDE.on){DOG.position.y=(P.air?0:Math.abs(Math.sin(P.ft*Math.PI))*.16*run)-(g<1.02&&!P.air?.55:0)+(IDLE.dy||0);DOG.rotation.x=P.air?0:Math.sin(P.ft*Math.PI*2)*.06*run}   // parked: kimPlace() owns DOG")
rep("shadow.position.set(P.x,g+.06,P.z);var sh=Math.max(.35,1-(P.y-g)*.12);shadow.scale.set(sh,sh,1);",
    "shadow.position.set(P.x,g+.06,P.z);var sh=Math.max(.35,1-(P.y-g)*.12);sh*=RIDE.on?1:.45;shadow.scale.set(sh,sh,1);")
rep("BUB.position.set(P.x,P.y+5.4,P.z);","var bp=(!RIDE.on&&IDLE.st!=='run')?KIM:P;BUB.position.set(bp.x,bp.y+5.4,bp.z);")
rep(" // screen axes on the ground plane"," if(RIDE.ph==='off'||RIDE.ph==='mount'){ix=0;iy=0}   // no steering mid-hop\n // screen axes on the ground plane")
rep("var max=boost?26:16;","var max=RIDE.on?(boost?26:16):(boost?8:5.5);")
rep("P.vy=9.2;P.air=true;","P.vy=RIDE.on?9.2:6.5;P.air=true;")
rep("function respawn(){","function respawn(){if(!RIDE.on&&FIG.onSeat)mountNow();")
rep("if(e.code==='KeyB')bark();","if(e.code==='KeyB')bark();if(e.code==='KeyG')mountKey();")
rep("if(pad.buttons[7]&&pad.buttons[7].value>.3)boost=true}",
    "if(pad.buttons[7]&&pad.buttons[7].value>.3)boost=true;if(pad.buttons[1]&&pad.buttons[1].pressed){if(!P.gpb)mountKey();P.gpb=true}else P.gpb=false}")

# ---- idle: sit with a rider, lie down only when parked, and clamp the lowest body point to the ground ----
a=s.index('function idleStep(dt,manual){'); b=s.index('// ===== ambient sound per zone')
s=s[:a]+'''function idleStep(dt,manual){var moving=RIDE.on?(manual||AUTO||P.air||P.speed>.5):(RIDE.ph==='whistle'||KIM.speed>.5);
 if(moving){IDLE.t=0;IDLE.k=0;if(IDLE.st!=='run'){IDLE.st='run';DOG.rotation.x=0;DOG.rotation.z=0}clampDog(dt);return}IDLE.t+=dt;
 var ns=(!RIDE.on&&IDLE.t>20)?'sleep':IDLE.t>6?'sit':'run';   // a mount never lies down with a rider on it (Malbers / RDR2 / BotW) - it sits; it sleeps only when parked
 if(ns!==IDLE.st){IDLE.st=ns;if(ns==='sit')showBub(['Hmm?','Tara na?','...'][Math.floor(Math.random()*3)]);if(ns==='sleep')showBub('Zzz')}
 if(IDLE.st==='sit'){IDLE.k=Math.min(1,(IDLE.k||0)+dt*2.5);DOG.rotation.x=-.28*IDLE.k;DOG.rotation.z=0;IDLE.bark+=dt;if(IDLE.bark>9){IDLE.bark=0;if(Math.random()<.6)bark()}}
 else if(IDLE.st==='sleep'){IDLE.k=Math.min(1,(IDLE.k||0)+dt*1.5);DOG.rotation.x=-.1*IDLE.k;DOG.rotation.z=1.1*IDLE.k;if(Math.random()<dt*.4)showBub('Zzz')}
 clampDog(dt)}
function clampDog(dt){if(!FIG.K||!FIG.kim)return;var w=new THREE.Vector3();
 if(IDLE.st==='run'&&RIDE.on){IDLE.dy=(IDLE.dy||0)*(1-Math.min(1,dt*6));return}   // ridden and standing/moving: the normal ground code places the body
 DOG.updateMatrixWorld(true);var m=1e9;function at(b,r){b.getWorldPosition(w);if(w.y-r<m)m=w.y-r}   // physics proxy: every bone carries a body radius (world units); the lowest one must rest ON the ground
 FIG.K.legs.forEach(function(c){c.forEach(function(b){at(b,.15)})});(FIG.K.spine||[]).forEach(function(b){at(b,.55)});FIG.K.head.forEach(function(b){at(b,.35)});FIG.K.tail.forEach(function(b){at(b,.12)});
 DOG.getWorldPosition(w);var gy=ground(w.x,w.z),sc=RIDE.on?RG.scale.y:1;IDLE.dy=(IDLE.dy||0)+(gy-m)/sc*Math.min(1,dt*8)}
'''+s[b:]

# ---- ride state machine, Kimpoy's own controller, walk cycle ----
rep("var P={x:0,z:10,y:0,vy:0,head:Math.PI,speed:0,frame:0,ft:0,air:false,face:1,vx:0,vz:0,squash:0,slide:0,lastFr:0,dustT:0,gpj:false,turnV:0};",
'''var P={x:0,z:10,y:0,vy:0,head:Math.PI,speed:0,frame:0,ft:0,air:false,face:1,vx:0,vz:0,squash:0,slide:0,lastFr:0,dustT:0,gpj:false,turnV:0};
// ===== mount / dismount (games: rider hops off to one side, the mount stays a living thing; whistle brings it back; hop on = remount) =====
var RIDE={on:true,ph:'ride',t:0,side:-1,from:new THREE.Vector3(),to:new THREE.Vector3()};
var KIM={x:0,z:0,y:0,head:0,ft:0,speed:0,air:false,turnV:0,vy:0,squash:0};DOG.rotation.order='YXZ';   // heading first, then pitch/roll in the body frame (matters once DOG carries its own heading)
var WS={hip:1,knee:1,arm:1};   // walk-cycle signs (verified in the pane)
var shadow2=new THREE.Mesh(shadow.geometry,shadow.material);shadow2.rotation.x=-Math.PI/2;shadow2.visible=false;S.add(shadow2);
function saveRests(D,root){var bones=[];root.traverse(function(b){if(b.isBone)bones.push(b)});bones.forEach(function(b){b.userData.restRide=b.userData.rest.clone();b.userData.rest.copy(b.userData.rest0);b.quaternion.copy(b.userData.rest0)});root.updateMatrixWorld(true);
 D.arms.forEach(function(c){dropArm(c,root)});bones.forEach(function(b){b.userData.restStand=b.userData.rest.clone();b.userData.rest.copy(b.userData.restRide);b.quaternion.copy(b.userData.restRide)});root.updateMatrixWorld(true)}   // standing = T-pose legs/spine + arms hanging
function setRest(root,kind){root.traverse(function(b){if(b.isBone&&b.userData[kind]){b.userData.rest.copy(b.userData[kind]);b.quaternion.copy(b.userData.rest)}})}
function mountTarget(){FIG.seat.updateMatrixWorld(true);return FIG.seat.localToWorld(new THREE.Vector3(0,FIG.diaYs,FIG.diaZs))}
function mountKey(){if(!FIG.onSeat)return;if(RIDE.ph==='ride'){if(!P.air)dismount()}else if(RIDE.ph==='walk'){if(Math.hypot(P.x-KIM.x,P.z-KIM.z)<3.5)mountStart();else{RIDE.ph='whistle';IDLE.st='run';IDLE.t=0;IDLE.k=0;DOG.rotation.x=0;DOG.rotation.z=0;blip(900,1600,.22,'sine',.12);setTimeout(function(){blip(1600,1100,.3,'sine',.12)},240);showBub('Kimpoy!')}}mountUI()}
function dismount(){var wr=FIG.dia.parent;RIDE.ph='off';RIDE.t=0;RIDE.side=(K.KeyD||K.ArrowRight)?1:-1;
 KIM.x=P.x;KIM.z=P.z;KIM.y=P.y;KIM.head=P.head;KIM.speed=0;KIM.ft=P.ft;S.attach(DOG);IDLE.t=0;IDLE.k=0;IDLE.st='run';IDLE.dy=0;DOG.rotation.x=0;DOG.rotation.z=0;
 S.attach(wr);RIDE.from.copy(wr.position);var tx=P.x+Math.cos(P.head)*RIDE.side*1.7,tz=P.z-Math.sin(P.head)*RIDE.side*1.7;RIDE.to.set(tx,ground(tx,tz),tz);setRest(FIG.dia,'restStand');FIG.pat=0;FIG.wv=0;blip(420,260,.15,'triangle',.12);CNT.dismount=(CNT.dismount||0)+1}
function mountStart(){var wr=FIG.dia.parent;S.attach(wr);RIDE.from.copy(wr.position);RIDE.ph='mount';RIDE.t=0;KIM.speed=0;IDLE.st='run';IDLE.t=0;IDLE.k=0;DOG.rotation.x=0;DOG.rotation.z=0;blip(260,440,.15,'triangle',.12)}
function mountNow(){var wr=FIG.dia.parent;P.x=KIM.x;P.z=KIM.z;P.head=KIM.head;P.y=ground(P.x,P.z);P.vx=P.vz=0;P.speed=0;P.ft=KIM.ft;P.air=false;RG.position.set(P.x,P.y,P.z);RG.rotation.set(0,P.head,0);RG.updateMatrixWorld(true);
 RG.add(DOG);DOG.position.set(0,-.25,0);DOG.rotation.set(0,0,0);DOG.scale.setScalar(1);DOG.updateMatrixWorld(true);FIG.seat.add(wr);wr.position.set(0,FIG.diaYs,FIG.diaZs);wr.rotation.set(FIG.lean,0,0);wr.scale.setScalar(1);setRest(FIG.dia,'restRide');
 RIDE.ph='ride';RIDE.on=true;IDLE.t=0;IDLE.k=0;IDLE.st='run';IDLE.dy=0;shadow2.visible=false;mountUI()}
function rideStep(dt){var wr=FIG.dia&&FIG.dia.parent;if(!wr||!FIG.onSeat)return;
 if(RIDE.ph==='off'||RIDE.ph==='mount'){RIDE.t+=dt;var u=Math.min(1,RIDE.t/.6),e=u*u*(3-2*u),to=RIDE.ph==='mount'?mountTarget():RIDE.to;wr.position.lerpVectors(RIDE.from,to,e);wr.position.y+=Math.sin(u*Math.PI)*.8;wr.rotation.set(0,RIDE.ph==='mount'?KIM.head:P.head,0);   // hop = smoothstep arc in world space (the wrap sits under S during the hop)
  if(u>=1){if(RIDE.ph==='off'){P.x=to.x;P.z=to.z;P.y=to.y;P.vx=P.vz=0;P.speed=0;P.squash=.2;RG.position.set(P.x,P.y,P.z);RG.rotation.set(0,P.head,0);RG.updateMatrixWorld(true);RG.attach(wr);wr.position.set(0,0,0);wr.rotation.set(0,0,0);wr.scale.setScalar(1);RIDE.ph='walk';RIDE.on=false;shadow2.visible=true;for(var i=0;i<5;i++)puff(P.x,P.y+.3,P.z,'#cdbfa4',.7,(Math.random()-.5)*2,1,(Math.random()-.5)*2);mountUI()}else mountNow()}}
 if(RIDE.ph==='whistle')kimRun(dt);else if(!RIDE.on)kimIdle(dt);if(!RIDE.on)kimPlace();mountUI()}
function kimRun(dt){var dx=P.x-KIM.x,dz=P.z-KIM.z,d=Math.hypot(dx,dz),tgt=Math.atan2(dx,dz),da=tgt-KIM.head;while(da>Math.PI)da-=2*Math.PI;while(da<-Math.PI)da+=2*Math.PI;KIM.head+=da*Math.min(1,dt*5);KIM.turnV=Math.max(-1,Math.min(1,da));
 if(d>2.2){KIM.speed+=(10-KIM.speed)*Math.min(1,dt*3);KIM.x+=Math.sin(KIM.head)*KIM.speed*dt;KIM.z+=Math.cos(KIM.head)*KIM.speed*dt;KIM.ft+=dt*(6+KIM.speed*.8)}
 else{KIM.speed*=1-Math.min(1,dt*8);if(KIM.speed<.6&&Math.abs(da)<.35){KIM.speed=0;mountStart()}}}
function kimIdle(dt){KIM.speed*=1-Math.min(1,dt*6);KIM.turnV*=1-Math.min(1,dt*6)}
function kimPlace(){KIM.y=ground(KIM.x,KIM.z);var run=Math.min(1,KIM.speed/8),bob=Math.abs(Math.sin(KIM.ft*Math.PI))*.16*run*1.35;DOG.position.set(KIM.x,KIM.y-.34+bob+(IDLE.dy||0),KIM.z);DOG.rotation.y=KIM.head;shadow2.position.set(KIM.x,KIM.y+.06,KIM.z)}
var _mntTxt='';function mountUI(){var t=RIDE.ph==='ride'?'\\uD83D\\uDC15 BABA (G)':RIDE.ph==='walk'?(Math.hypot(P.x-KIM.x,P.z-KIM.z)<3.5?'\\uD83D\\uDC15 SAKAY (G)':'\\uD83D\\uDC15 SIPOL (G)'):RIDE.ph==='whistle'?'\\uD83D\\uDC15 PAPUNTA...':'...';if(t!==_mntTxt){_mntTxt=t;var el=document.getElementById('mnt');if(el)el.textContent=t}}
function walkAnim(D,r2,t,dt,ph){var sp=P.speed,run=Math.min(1,sp/3),air=P.air?1:0,wr=r2.parent;   // on foot: procedural walk on the same skeleton (standing rest pose)
 D.legs.forEach(function(c,i){var o=i?Math.PI:0;rotW(pick(c,0),_AX,WS.hip*Math.sin(ph+o)*.55*run+air*.35,r2);rotW(pick(c,1),_AX,WS.knee*Math.max(0,Math.sin(ph+o+.7))*.95*run+air*.5,r2)});
 D.arms.forEach(function(c,i){var o=i?0:Math.PI;rotW(pick(c,0),_AX,WS.arm*Math.sin(ph+o)*.4*run+Math.sin(t*1.3+i)*.05*(1-run)-air*.5,r2);rotW(pick(c,2),_AX,WS.arm*.25*run,r2)});
 if(D.spine.length>1){rotW(D.spine[1],_AZ,Math.sin(ph)*.05*run,r2);rotW(D.spine[D.spine.length-1],_AX,.08*run+.02*Math.sin(t*2.2)*(1-run),r2)}
 if(D.head.length){rotW(pick(D.head,0),_AY,Math.sin(t*.6)*.4*(1-run),r2);rotW(pick(D.head,D.head.length-1),_AX,Math.sin(ph*2)*.03*run,r2)}
 if(wr&&RIDE.ph==='walk'){wr.position.y=Math.abs(Math.sin(ph))*.05*run;wr.rotation.x=.06*run}}''')

# ---- HUD button ----
rep('<div id="stick"><i></i></div><button id="jump">JUMP</button>','<div id="stick"><i></i></div><button id="jump">JUMP</button><button id="mnt">&#128021; BABA (G)</button>')
rep("document.getElementById('jump').addEventListener('pointerdown',function(e){e.preventDefault();jump()});",
    "document.getElementById('jump').addEventListener('pointerdown',function(e){e.preventDefault();jump()});document.getElementById('mnt').addEventListener('pointerdown',function(e){e.preventDefault();mountKey()});")
css_anchor="#jump{position:fixed;right:26px;bottom:26px;"
i=s.index(css_anchor); j=s.index('}',i)+1
s=s[:j]+"#mnt{position:fixed;right:26px;bottom:106px;height:42px;padding:0 16px;border-radius:21px;background:var(--maroon);color:#fff;border:0;font:800 12px Inter;z-index:5;box-shadow:0 6px 12px rgba(0,0,0,.3);cursor:pointer}body.photo #mnt{display:none}"+s[j:]

io.open(p,'w',encoding='utf-8').write(s); print('patch24 applied')
