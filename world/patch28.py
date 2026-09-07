# v27a: a visible clock under the minimap. It reads the day/night scalar and doubles as the control,
# so the cycle is discoverable instead of buried in the pause menu.
import io
p = 'index.html'; s = io.open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    assert s.count(old) == count, ('MISSING/AMBIGUOUS', old[:90], s.count(old))
    s = s.replace(old, new)

# ---- style: a pill tucked under the minimap, same card look as the rest of the HUD ----
rep("#obj{position:fixed;left:16px;top:74px;",
    "#clock{position:fixed;right:14px;top:172px;z-index:6;display:flex;align-items:center;gap:7px;background:rgba(251,247,241,.9);"
    "border:0;border-radius:14px;padding:7px 12px;box-shadow:0 8px 20px rgba(0,0,0,.14),inset 0 -3px 0 rgba(0,0,0,.06);"
    "font:800 12px 'JetBrains Mono',monospace;color:var(--ink);cursor:pointer;-webkit-tap-highlight-color:transparent}"
    "#clock i{font-style:normal;font-size:14px;line-height:1}"
    "#clock b{font-weight:800;letter-spacing:.5px}"
    "#clock small{font:700 9px Inter;opacity:.55;letter-spacing:.6px}"
    "body.mob #clock{top:132px;padding:6px 10px;font-size:11px}"
    "body.photo #clock{display:none}"
    "#obj{position:fixed;left:16px;top:74px;")

# ---- markup, right after the minimap ----
rep('<div id="sub"></div>',
    '<button id="clock" title="Day / night"><i id="clkIco">\u2600</i><b id="clkTime">12:00</b><small id="clkMode">AUTO</small></button>\n<div id="sub"></div>')

# ---- the clock reads SKY.t; forced modes park it at noon and midnight ----
rep("function applyTime(){var b=document.getElementById('mTime');if(b)b.textContent='Time: '+SET.time;SKY.shown=-1;skyStep(0)}",
    "function clockText(){var h;\n"
    " if(SET.time==='day')h=12.4;else if(SET.time==='night')h=0.6;else h=((SKY.t-.25)*24+12+24)%24;   // t .25 = noon, .75 = midnight\n"
    " var hh=Math.floor(h),mm=Math.floor((h-hh)*60);\n"
    " var e=document.getElementById('clkTime');if(e)e.textContent=(hh<10?'0':'')+hh+':'+(mm<10?'0':'')+mm;\n"
    " var i=document.getElementById('clkIco');if(i)i.textContent=SKY.night>.62?'\\u263D':SKY.night>.22?'\\u2601':'\\u2600';\n"
    " var m=document.getElementById('clkMode');if(m)m.textContent=SET.time.toUpperCase()}\n"
    "function applyTime(){var b=document.getElementById('mTime');if(b)b.textContent='Time: '+SET.time;SKY.shown=-1;skyStep(0);clockText()}")
rep(" SKY.night+=(tgt-SKY.night)*Math.min(1,dt*(SET.time==='auto'?4:1.8));applySky()}",
    " SKY.night+=(tgt-SKY.night)*Math.min(1,dt*(SET.time==='auto'?4:1.8));applySky()}\n"
    "function cycleTime(){SET.time=SET.time==='auto'?'day':SET.time==='day'?'night':'auto';saveSet();applyTime();toast('Time: '+SET.time)}")

# ---- refresh it on the existing quarter-second HUD tick, and wire the click ----
rep(" hudT=(hudT||0)+dt;if(hudT>.25){hudT=0;objUpdate();",
    " hudT=(hudT||0)+dt;if(hudT>.25){hudT=0;objUpdate();clockText();")
rep("document.getElementById('mTime').onclick=function(){SET.time=SET.time==='auto'?'day':SET.time==='day'?'night':'auto';saveSet();applyTime()};",
    "document.getElementById('mTime').onclick=function(){cycleTime()};\n"
    "document.getElementById('clock').onclick=function(){grabFocus();cycleTime()};")

io.open(p, 'w', encoding='utf-8').write(s); print('patch28 applied')
