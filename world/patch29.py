# v28: replace the corner clock pill with a game-style day dial at the top centre.
# Canvas, following the minimap pattern (the file's only HUD canvas): fixed backing store,
# context cached once, drawn every frame from step() so the hand sweeps smoothly.
# Segmented ring in the Don't Starve idiom - day / dusk / night / dawn arcs, a marker riding
# the ring, a notch at noon - and the whole face glows warm once night falls.
import io
p = 'index.html'; s = io.open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, ('MISSING/AMBIGUOUS', old[:90], s.count(old))
    s = s.replace(old, new)

OLDCSS = ("#clock{position:fixed;right:14px;top:172px;z-index:6;display:flex;align-items:center;gap:7px;background:rgba(251,247,241,.9);"
          "border:0;border-radius:14px;padding:7px 12px;box-shadow:0 8px 20px rgba(0,0,0,.14),inset 0 -3px 0 rgba(0,0,0,.06);"
          "font:800 12px 'JetBrains Mono',monospace;color:var(--ink);cursor:pointer;-webkit-tap-highlight-color:transparent}"
          "#clock i{font-style:normal;font-size:14px;line-height:1}"
          "#clock b{font-weight:800;letter-spacing:.5px}"
          "#clock small{font:700 9px Inter;opacity:.55;letter-spacing:.6px}"
          "body.mob #clock{top:132px;padding:6px 10px;font-size:11px}"
          "body.photo #clock{display:none}")
NEWCSS = ("#dial{position:fixed;left:50%;top:12px;transform:translateX(-50%);z-index:6;width:84px;height:84px;padding:0;border:0;"
          "border-radius:50%;background:transparent;cursor:pointer;-webkit-tap-highlight-color:transparent;"
          "filter:drop-shadow(0 8px 18px rgba(0,0,0,.28));transition:filter .5s linear}"
          "#dial:hover{transform:translateX(-50%) scale(1.06)}"
          "body.mob #dial{width:62px;height:62px;top:170px}"          # a 375px phone has only a 23px gap on row one
          "body.mob #obj{width:132px}"                                 # narrow the objectives card so it clears the dial
          "body.photo #dial{display:none}")
rep(OLDCSS, NEWCSS)

rep('<button id="clock" title="Day / night"><i id="clkIco">\u2600</i><b id="clkTime">12:00</b><small id="clkMode">AUTO</small></button>',
    '<canvas id="dial" width="240" height="240" title="Day / night - click to change"></canvas>')

# ---- clockText now just computes; the dial draws ----
rep("function clockText(){var h;\n"
    " if(SET.time==='day')h=12.4;else if(SET.time==='night')h=0.6;else h=((SKY.t-.25)*24+12+24)%24;   // t .25 = noon, .75 = midnight\n"
    " var hh=Math.floor(h),mm=Math.floor((h-hh)*60);\n"
    " var e=document.getElementById('clkTime');if(e)e.textContent=(hh<10?'0':'')+hh+':'+(mm<10?'0':'')+mm;\n"
    " var i=document.getElementById('clkIco');if(i)i.textContent=SKY.night>.62?'\\u263D':SKY.night>.22?'\\u2601':'\\u2600';\n"
    " var m=document.getElementById('clkMode');if(m)m.textContent=SET.time.toUpperCase()}",
    "function clockText(){var h;\n"
    " if(SET.time==='day')h=12.4;else if(SET.time==='night')h=0.6;else h=((SKY.t-.25)*24+12+24)%24;   // t .25 = noon, .75 = midnight\n"
    " var hh=Math.floor(h),mm=Math.floor((h-hh)*60);\n"
    " SKY.hhmm=(hh<10?'0':'')+hh+':'+(mm<10?'0':'')+mm;SKY.mode=SET.time.toUpperCase()}")

# ---- the dial ----
rep("function applyTime(){var b=document.getElementById('mTime');if(b)b.textContent='Time: '+SET.time;SKY.shown=-1;skyStep(0);clockText()}",
    "function applyTime(){var b=document.getElementById('mTime');if(b)b.textContent='Time: '+SET.time;SKY.shown=-1;skyStep(0);clockText();dialDraw()}\n"
    "// ---- the day dial: segmented ring + a marker riding it, the Don't Starve read-at-a-glance idiom ----\n"
    "var dialEl=null,dc=null,DIALC={day:'#ffd98a',dusk:'#e8834e',night:'#223a63',dawn:'#f0a2ad'},dialGlowShown=-1;\n"
    "function dAng(t){return (t-.25)*Math.PI*2-Math.PI/2}   // noon at the top, dusk right, midnight bottom, dawn left\n"
    "function dialDraw(){if(!dc){dialEl=document.getElementById('dial');if(!dialEl)return;dc=dialEl.getContext('2d')}\n"
    " var n=SKY.night,t=SET.time==='day'?.25:SET.time==='night'?.75:SKY.t,C=120,R=96,q=dc;\n"
    " q.clearRect(0,0,240,240);\n"
    " q.lineWidth=22;q.lineCap='butt';\n"
    " var bands=[[.05,.45,DIALC.day],[.45,.55,DIALC.dusk],[.55,.95,DIALC.night],[.95,1.05,DIALC.dawn]];\n"
    " for(var i=0;i<bands.length;i++){q.beginPath();q.strokeStyle=bands[i][2];q.arc(C,C,R,dAng(bands[i][0]),dAng(bands[i][1]));q.stroke()}\n"
    " q.strokeStyle='rgba(255,255,255,.85)';q.lineWidth=3;q.beginPath();q.moveTo(C,C-R-13);q.lineTo(C,C-R+13);q.stroke();   // the noon notch\n"
    " q.beginPath();q.fillStyle=n>.5?'rgba(16,26,46,.94)':'rgba(251,247,241,.94)';q.arc(C,C,74,0,7);q.fill();\n"
    " q.save();q.translate(C+Math.cos(dAng(t))*R,C+Math.sin(dAng(t))*R);\n"
    " q.shadowColor='rgba(255,214,140,.95)';q.shadowBlur=26*n;\n"
    " if(n>.55){q.fillStyle='#e9f0ff';q.beginPath();q.arc(0,0,15,0,7);q.fill();q.shadowBlur=0;q.fillStyle=n>.5?'rgba(16,26,46,.94)':'rgba(251,247,241,.94)';q.beginPath();q.arc(6,-4,12,0,7);q.fill()}   // crescent\n"
    " else{q.fillStyle='#fff3c8';q.beginPath();q.arc(0,0,13,0,7);q.fill();q.lineWidth=3.5;q.strokeStyle='#fff3c8';for(var r2=0;r2<8;r2++){var a2=r2/8*Math.PI*2;q.beginPath();q.moveTo(Math.cos(a2)*17,Math.sin(a2)*17);q.lineTo(Math.cos(a2)*23,Math.sin(a2)*23);q.stroke()}}\n"
    " q.restore();q.shadowBlur=0;\n"
    " q.textAlign='center';q.shadowColor='rgba(255,206,128,.9)';q.shadowBlur=20*n;\n"
    " q.fillStyle=n>.5?'#ffe6b0':'#111';q.font=\"700 42px 'JetBrains Mono',monospace\";q.fillText(SKY.hhmm||'12:00',C,C+8);\n"
    " q.shadowBlur=0;q.fillStyle=n>.5?'rgba(255,230,176,.6)':'rgba(17,17,17,.5)';q.font='700 18px Inter,sans-serif';q.fillText(SKY.mode||'AUTO',C,C+34);\n"
    " if(Math.abs(n-dialGlowShown)>.02){dialGlowShown=n;dialEl.style.filter='drop-shadow(0 8px 18px rgba(0,0,0,'+(.28-.16*n).toFixed(2)+'))'+(n>.05?' drop-shadow(0 0 '+(14*n).toFixed(1)+'px rgba(255,198,110,'+(.75*n).toFixed(2)+'))':'')}}")

# ---- draw it every frame, next to the minimap ----
rep("zones(dt);minimap();", "zones(dt);minimap();dialDraw();")
rep("document.getElementById('clock').onclick=function(){grabFocus();cycleTime()};",
    "document.getElementById('dial').onclick=function(){grabFocus();cycleTime()};")
rep("body.photo #hud,body.photo #map,", "body.photo #hud,body.photo #dial,body.photo #map,")

io.open(p, 'w', encoding='utf-8').write(s); print('patch29 applied')
